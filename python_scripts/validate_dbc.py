#!/usr/bin/env python3
"""
validate_dbc.py — DBC-Datei-Sanity-Check für Pre-Push / CI.

Bricht mit Exit-Code != 0 ab, wenn eine DBC offensichtlich korrupt ist
(Header / String-Table / Duplikat-IDs). Idee: dieses Skript wird als Git
Pre-Push-Hook oder GitHub-Actions-Step laufen und verhindert, dass eine
beschädigte Spell.dbc / SpellItemEnchantment.dbc / Item.dbc ins Repo
gelangt — das hat in der Vergangenheit (siehe `share-public/claude_log.md`,
2026-03-18, "Spell.dbc Korruption") bereits zu schwer reproduzierbaren
Server-Crashes geführt.

Validierungen:
    1. Header: Magic-Bytes ("WDBC"), implied Dateigröße
       == record_count*record_size + 20 + string_block_size
    2. String-Table: erstes Byte muss NUL sein (gültiger leerer String
       am Offset 0 — wird von Records referenziert, die "kein String" sagen)
    3. Optional: Duplikat-Check auf der ersten uint32-Spalte jedes Records.
       ID-keyed DBCs (Spell.dbc, Item.dbc, …) dürfen keine Duplikate haben;
       gt*.dbc / Light.dbc etc. teilweise schon → Auto-Skip per Whitelist.

Usage:
    python3 validate_dbc.py <path>...
    python3 validate_dbc.py --check-duplicates Spell.dbc
    python3 validate_dbc.py --all-known share/dbc/

Exit-Codes:
    0 — alle OK
    1 — Header-Inkonsistenz
    2 — String-Table-Korruption
    3 — Duplikat-IDs in einer ID-keyed DBC
    4 — IO / nicht lesbar
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

WDBC_MAGIC = b"WDBC"
WDBC_HEADER_SIZE = 20

EXIT_OK = 0
EXIT_HEADER_BAD = 1
EXIT_STRING_TABLE_BAD = 2
EXIT_DUPLICATES = 3
EXIT_IO_ERROR = 4

# ID-keyed DBCs — die erste uint32-Spalte jedes Records ist eine eindeutige ID.
# Konservative Liste; bei Bedarf erweitern. Auto-Skip-Liste danach.
ID_KEYED = {
    "Spell.dbc",
    "Item.dbc",
    "ItemSet.dbc",
    "ItemRandomProperties.dbc",
    "ItemRandomSuffix.dbc",
    "SpellItemEnchantment.dbc",
    "ChrClasses.dbc",
    "ChrRaces.dbc",
    "Talent.dbc",
    "TalentTab.dbc",
    "SkillLine.dbc",
    "SkillLineAbility.dbc",
    "Map.dbc",
    "AreaTable.dbc",
    "Faction.dbc",
    "FactionTemplate.dbc",
    "Achievement.dbc",
    "CreatureFamily.dbc",
    "GameObjectDisplayInfo.dbc",
}

# DBCs, bei denen "Duplikate in Spalte 0" KEIN Bug sind (z.B. Tables mit
# zusammengesetztem Schlüssel oder ohne Schlüssel-Konvention).
NOT_ID_KEYED = {
    "AnimationData.dbc",
    "BattlemasterList.dbc",
    "Light.dbc",
    "LightFloatBand.dbc",
    "LightIntBand.dbc",
    "LightParams.dbc",
    "LightSkybox.dbc",
    # gt*.dbc — Game-Tables, oft Wertelisten ohne ID-Spalte
}


def read_header(f) -> tuple[bytes, int, int, int, int]:
    raw = f.read(WDBC_HEADER_SIZE)
    if len(raw) != WDBC_HEADER_SIZE:
        raise ValueError(
            f"header too short: {len(raw)} bytes (expected {WDBC_HEADER_SIZE})"
        )
    magic = raw[:4]
    rc, fc, rs, sbs = struct.unpack("<IIII", raw[4:])
    return magic, rc, fc, rs, sbs


def validate_header(path: Path) -> tuple[int, int, int, int]:
    """Returns (record_count, field_count, record_size, string_block_size)."""
    file_size = path.stat().st_size
    if file_size < WDBC_HEADER_SIZE:
        die(
            f"{path.name}: file size {file_size} < header size {WDBC_HEADER_SIZE}",
            EXIT_HEADER_BAD,
        )

    with path.open("rb") as f:
        try:
            magic, rc, fc, rs, sbs = read_header(f)
        except (struct.error, ValueError) as e:
            die(f"{path.name}: header read error: {e}", EXIT_HEADER_BAD)

    if magic != WDBC_MAGIC:
        die(
            f"{path.name}: bad magic {magic!r} (expected {WDBC_MAGIC!r})",
            EXIT_HEADER_BAD,
        )

    expected = WDBC_HEADER_SIZE + rc * rs + sbs
    if expected != file_size:
        die(
            f"{path.name}: file size {file_size} != header-implied {expected} "
            f"(records={rc}, record_size={rs}, string_block={sbs})",
            EXIT_HEADER_BAD,
        )

    if fc * 4 != rs:
        # Variable-Width-Felder kommen vor (z.B. AreaTable hat sub-uint32-Felder),
        # daher nur ein Hinweis — kein Fail.
        warn(
            f"{path.name}: field_count*4 ({fc*4}) != record_size ({rs}) — variable-width fields?"
        )

    ok(
        f"{path.name}: header valid (records={rc}, record_size={rs}, string_block={sbs})"
    )
    return rc, fc, rs, sbs


def validate_string_table(path: Path, rc: int, rs: int, sbs: int) -> None:
    if sbs == 0:
        return
    offset = WDBC_HEADER_SIZE + rc * rs
    with path.open("rb") as f:
        f.seek(offset)
        first = f.read(1)
    if first != b"\x00":
        die(
            f"{path.name}: string table at offset {offset} doesn't start with NUL "
            f"(found {first!r})",
            EXIT_STRING_TABLE_BAD,
        )
    ok(f"{path.name}: string table starts with NUL")


def check_duplicate_ids(path: Path, rc: int, rs: int) -> None:
    seen: set[int] = set()
    duplicates: list[tuple[int, int]] = []
    with path.open("rb") as f:
        f.seek(WDBC_HEADER_SIZE)
        for i in range(rc):
            record = f.read(rs)
            if len(record) != rs:
                die(f"{path.name}: short read at record {i}", EXIT_IO_ERROR)
            (record_id,) = struct.unpack("<I", record[:4])
            if record_id in seen:
                duplicates.append((i, record_id))
            seen.add(record_id)

    if duplicates:
        msg = [f"{path.name}: {len(duplicates)} duplicate ID(s)"]
        for i, id_ in duplicates[:10]:
            msg.append(f"    record #{i}: ID {id_}")
        if len(duplicates) > 10:
            msg.append(f"    ... and {len(duplicates) - 10} more")
        die("\n".join(msg), EXIT_DUPLICATES)
    ok(f"{path.name}: {rc} records, all first-column IDs unique")


def is_id_keyed(name: str, args) -> bool:
    if args.check_duplicates:
        return True
    if args.all_known:
        if name in ID_KEYED:
            return True
        if name in NOT_ID_KEYED:
            return False
        # Heuristik für unbekannte Tables: nicht prüfen.
        return False
    return False


def validate_one(path: Path, args) -> None:
    if not path.exists() or not path.is_file():
        die(f"{path}: not a file", EXIT_IO_ERROR)
    rc, _fc, rs, sbs = validate_header(path)
    validate_string_table(path, rc, rs, sbs)
    if is_id_keyed(path.name, args):
        check_duplicate_ids(path, rc, rs)


def expand_inputs(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(sorted(p.glob("*.dbc")))
        else:
            files.append(p)
    return files


# --- output helpers ---------------------------------------------------------


def ok(msg: str) -> None:
    print(f"[OK]   {msg}")


def warn(msg: str) -> None:
    print(f"[WARN] {msg}", file=sys.stderr)


def die(msg: str, code: int) -> None:
    print(f"[FAIL] {msg}", file=sys.stderr)
    sys.exit(code)


# --- main -------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate DBC file integrity (pre-push / CI helper)."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="DBC file(s) or directory containing DBC files",
    )
    parser.add_argument(
        "--check-duplicates",
        action="store_true",
        help="Treat ALL given files as ID-keyed and check first-column duplicates.",
    )
    parser.add_argument(
        "--all-known",
        action="store_true",
        help="Auto-pick ID-keyed DBCs from the built-in whitelist (Spell.dbc, "
        "Item.dbc, SpellItemEnchantment.dbc, ...). Files not on either list "
        "are not duplicate-checked.",
    )
    args = parser.parse_args()

    files = expand_inputs(args.paths)
    if not files:
        die("no DBC files found", EXIT_IO_ERROR)

    for f in files:
        validate_one(f, args)

    print(f"\n[OK]   {len(files)} DBC file(s) validated, no corruption detected")


if __name__ == "__main__":
    main()
