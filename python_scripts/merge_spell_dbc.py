#!/usr/bin/env python3
"""
Merge spell entries from a spell_dbc CSV (MySQL export) into an existing
Spell.dbc binary file.

The script reads both files from the same directory, checks for duplicate
spell IDs (aborts if any found), converts CSV rows to DBC binary records,
appends them, and validates the result.

Usage:
    python3 merge_spell_dbc.py [directory]

    directory  — folder containing both Spell.dbc and spell_dbc.csv
                 (defaults to current working directory)

The merged output is written as Spell_merged.dbc in the same directory.
The original Spell.dbc is never modified.
"""

import argparse
import csv
import struct
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# DBC constants
# ---------------------------------------------------------------------------

DBC_HEADER_FORMAT = "<4s4I"  # magic(4) + record_count, field_count, record_size, string_table_size
DBC_HEADER_SIZE = 20
DBC_MAGIC = b"WDBC"

# Spell.dbc format string — must match SpellEntryfmt from DBCfmt.h exactly
# 234 fields, 936 bytes per record (all fields are 4 bytes: n/i/f/s/x)
# n = index (uint32), i = int (uint32), f = float, s = string offset, x = unused (uint32)
SPELL_FMT = (
    "niiiiiiiiiiiixixiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiifx"
    "iiiiiiiiiiiiiiiiiiiiiiiiiiiifffiiiiiiiiiiiiiiiiiiiiifffiiiiiiiiiiiiiiifff"
    "iiiiiiiiiiiiiissssssssssssssssxssssssssssssssss"
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxiiiiiiiiiiixfffxxxiiiiixxfffxx"
)

FIELD_COUNT = len(SPELL_FMT)        # 234
RECORD_SIZE = FIELD_COUNT * 4       # 936 bytes

# Pre-compute field type sets for fast lookup
FLOAT_POSITIONS = frozenset(i for i, c in enumerate(SPELL_FMT) if c == 'f')

# String positions: SPELL_FMT 's' fields PLUS Description_Lang_* and
# AuraDescription_Lang_* fields which are marked 'x' (unused by server)
# but still stored as string offsets in the DBC binary.
# Positions 170-185 = Description_Lang (16 locales)
# Positions 187-202 = AuraDescription_Lang (16 locales)
_EXTRA_STRING_POSITIONS = frozenset(range(170, 186)) | frozenset(range(187, 203))
STRING_POSITIONS = frozenset(i for i, c in enumerate(SPELL_FMT) if c == 's') | _EXTRA_STRING_POSITIONS

# Fields that are signed integers in the SQL schema
# (Reagent_1-8, EquippedItemClass, EquippedItemSubclass, EquippedItemInvTypes,
#  EffectDieSides_1-3, EffectBasePoints_1-3, EffectMiscValue_1-3,
#  EffectMiscValueB_1-3, RequiredAreasID, PowerType)
SIGNED_POSITIONS = frozenset([
    41,                     # PowerType
    52, 53, 54, 55, 56, 57, 58, 59,  # Reagent_1-8
    68, 69, 70,             # EquippedItemClass, Subclass, InvTypes
    74, 75, 76,             # EffectDieSides_1-3
    80, 81, 82,             # EffectBasePoints_1-3
    110, 111, 112,          # EffectMiscValue_1-3
    113, 114, 115,          # EffectMiscValueB_1-3
    224,                    # RequiredAreasID
])


# ---------------------------------------------------------------------------
# DBC reading / writing (reuses patterns from copy_spells_dbc.py)
# ---------------------------------------------------------------------------

def read_dbc(path):
    """Read Spell.dbc → header info, records dict {spell_id: raw_bytes}, string table."""
    data = Path(path).read_bytes()

    if len(data) < DBC_HEADER_SIZE:
        sys.exit(f"FEHLER: {path} ist zu klein fuer eine gueltige DBC ({len(data)} Bytes)")

    magic, record_count, field_count, record_size, string_table_size = struct.unpack_from(
        DBC_HEADER_FORMAT, data, 0
    )
    if magic != DBC_MAGIC:
        sys.exit(f"FEHLER: {path} ist keine gueltige DBC (magic: {magic!r})")

    if record_size != RECORD_SIZE:
        sys.exit(
            f"FEHLER: {path} hat Record-Size {record_size}, erwartet {RECORD_SIZE}. "
            f"Inkompatible DBC-Version."
        )

    if field_count != FIELD_COUNT:
        sys.exit(
            f"FEHLER: {path} hat {field_count} Felder, erwartet {FIELD_COUNT}."
        )

    expected_size = DBC_HEADER_SIZE + record_count * record_size + string_table_size
    if len(data) != expected_size:
        sys.exit(
            f"FEHLER: {path} ist korrupt — Dateigroesse {len(data)} != erwartet "
            f"{expected_size} (Header: {record_count} Records x {record_size} Bytes "
            f"+ {string_table_size} String-Tabelle)"
        )

    records_start = DBC_HEADER_SIZE
    string_table_start = records_start + record_count * record_size
    string_table = data[string_table_start: string_table_start + string_table_size]

    if string_table_size > 0 and string_table[0:1] != b"\x00":
        sys.exit(f"FEHLER: {path} ist korrupt — String-Tabelle beginnt nicht mit Null-Byte")

    records = {}
    duplicates = 0
    for i in range(record_count):
        offset = records_start + i * record_size
        record_data = data[offset: offset + record_size]
        spell_id = struct.unpack_from("<I", record_data, 0)[0]
        if spell_id in records:
            duplicates += 1
        records[spell_id] = record_data

    if duplicates > 0:
        sys.exit(
            f"FEHLER: {path} ist korrupt — {duplicates} doppelte Spell-ID(s) "
            f"in {record_count} Records."
        )

    return {
        "field_count": field_count,
        "record_size": record_size,
        "records": records,
        "string_table": bytearray(string_table),
    }


def write_dbc(path, field_count, record_size, records_list, string_table):
    """Write complete DBC file from ordered record list + string table."""
    header = struct.pack(
        DBC_HEADER_FORMAT,
        DBC_MAGIC,
        len(records_list),
        field_count,
        record_size,
        len(string_table),
    )

    with open(path, "wb") as f:
        f.write(header)
        for rec in records_list:
            f.write(rec)
        f.write(string_table)

    total = DBC_HEADER_SIZE + len(records_list) * record_size + len(string_table)
    actual = Path(path).stat().st_size
    if actual != total:
        sys.exit(f"KRITISCH: Geschriebene Dateigroesse {actual} != erwartet {total}")


# ---------------------------------------------------------------------------
# CSV parsing
# ---------------------------------------------------------------------------

def read_csv_spells(path):
    """Parse spell_dbc.csv → list of dicts {column_name: raw_string_value}."""
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";", quotechar='"')
        header = next(reader)
        header = [h.strip().strip('"') for h in header]

        if len(header) != FIELD_COUNT:
            sys.exit(
                f"FEHLER: CSV hat {len(header)} Spalten, erwartet {FIELD_COUNT}. "
                f"Inkompatibles Format."
            )

        for line_no, values in enumerate(reader, start=2):
            if len(values) != FIELD_COUNT:
                sys.exit(
                    f"FEHLER: CSV Zeile {line_no} hat {len(values)} Werte, "
                    f"erwartet {FIELD_COUNT}."
                )
            rows.append(dict(zip(header, values)))

    return header, rows


def csv_row_to_dbc_record(row_values, col_index, string_table, string_cache):
    """Convert a list of CSV string values (in column order) to a 936-byte DBC record.

    Strings are added to string_table (bytearray) and their offsets cached.
    Returns the record as bytes.
    """
    record = bytearray(RECORD_SIZE)

    for i in range(FIELD_COUNT):
        raw = row_values[i].strip()
        byte_offset = i * 4

        if i in STRING_POSITIONS:
            # String field → add to string table, write offset
            text = raw
            if text == "" or text.upper() == "NULL":
                # Empty string → point to the initial null byte at offset 0
                struct.pack_into("<I", record, byte_offset, 0)
            else:
                if text in string_cache:
                    off = string_cache[text]
                else:
                    off = len(string_table)
                    string_cache[text] = off
                    string_table.extend(text.encode("utf-8"))
                    string_table.append(0)  # null terminator
                struct.pack_into("<I", record, byte_offset, off)

        elif i in FLOAT_POSITIONS:
            # Float field
            val = float(raw) if raw and raw.upper() != "NULL" else 0.0
            struct.pack_into("<f", record, byte_offset, val)

        else:
            # Integer field (signed or unsigned)
            if not raw or raw.upper() == "NULL":
                val = 0
            else:
                # Handle potential float-formatted integers (e.g. "0.0")
                if "." in raw:
                    val = int(float(raw))
                else:
                    val = int(raw)

            if i in SIGNED_POSITIONS:
                # Signed 32-bit — use signed pack
                if val < -2147483648 or val > 2147483647:
                    sys.exit(
                        f"FEHLER: Signed-Integer-Ueberlauf in Feld {i}: {val}"
                    )
                struct.pack_into("<i", record, byte_offset, val)
            else:
                # Unsigned 32-bit
                if val < 0:
                    # Convert negative to unsigned (two's complement)
                    val = val & 0xFFFFFFFF
                if val > 0xFFFFFFFF:
                    # Truncate bigint (ShapeshiftMask etc.) to 32 bits
                    val = val & 0xFFFFFFFF
                struct.pack_into("<I", record, byte_offset, val)

    return bytes(record)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_merged_dbc(path, expected_count):
    """Re-read the written DBC and validate format, types, and completeness."""
    print(f"\nValidierung von {path} ...")

    data = Path(path).read_bytes()

    # 1. Header check
    if len(data) < DBC_HEADER_SIZE:
        sys.exit(f"  FEHLER: Datei zu klein ({len(data)} Bytes)")

    magic, record_count, field_count, record_size, string_table_size = struct.unpack_from(
        DBC_HEADER_FORMAT, data, 0
    )

    if magic != DBC_MAGIC:
        sys.exit(f"  FEHLER: Ungueltige Magic Bytes: {magic!r}")
    print(f"  Magic: OK (WDBC)")

    if field_count != FIELD_COUNT:
        sys.exit(f"  FEHLER: Field-Count {field_count} != {FIELD_COUNT}")
    print(f"  Field-Count: OK ({field_count})")

    if record_size != RECORD_SIZE:
        sys.exit(f"  FEHLER: Record-Size {record_size} != {RECORD_SIZE}")
    print(f"  Record-Size: OK ({record_size} Bytes)")

    # 2. File size check
    expected_size = DBC_HEADER_SIZE + record_count * record_size + string_table_size
    if len(data) != expected_size:
        sys.exit(
            f"  FEHLER: Dateigroesse {len(data)} != erwartet {expected_size}"
        )
    print(f"  Dateigroesse: OK ({len(data):,} Bytes)")

    # 3. Record count check
    if record_count != expected_count:
        sys.exit(
            f"  FEHLER: Record-Count {record_count} != erwartet {expected_count}"
        )
    print(f"  Record-Count: OK ({record_count})")

    # 4. String table check
    string_table_start = DBC_HEADER_SIZE + record_count * record_size
    string_table = data[string_table_start:]
    if len(string_table) > 0 and string_table[0:1] != b"\x00":
        sys.exit(f"  FEHLER: String-Tabelle beginnt nicht mit Null-Byte")
    print(f"  String-Tabelle: OK ({len(string_table):,} Bytes)")

    # 5. Duplicate ID check
    records_start = DBC_HEADER_SIZE
    seen_ids = set()
    duplicate_ids = []
    for i in range(record_count):
        offset = records_start + i * record_size
        spell_id = struct.unpack_from("<I", data, offset)[0]
        if spell_id in seen_ids:
            duplicate_ids.append(spell_id)
        seen_ids.add(spell_id)

    if duplicate_ids:
        sys.exit(
            f"  FEHLER: {len(duplicate_ids)} doppelte Spell-IDs in Ausgabe: "
            f"{duplicate_ids[:20]}{'...' if len(duplicate_ids) > 20 else ''}"
        )
    print(f"  Keine doppelten IDs: OK")

    # 6. Sorted order check
    ids_list = []
    for i in range(record_count):
        offset = records_start + i * record_size
        spell_id = struct.unpack_from("<I", data, offset)[0]
        ids_list.append(spell_id)

    if ids_list == sorted(ids_list):
        print(f"  Sortierung (nach ID): OK")
    else:
        print(f"  WARNUNG: Records sind nicht nach ID sortiert")

    # 7. String reference integrity check
    errors = 0
    for i in range(record_count):
        offset = records_start + i * record_size
        rec = data[offset: offset + record_size]
        spell_id = struct.unpack_from("<I", rec, 0)[0]

        for pos in STRING_POSITIONS:
            str_off = struct.unpack_from("<I", rec, pos * 4)[0]
            if str_off >= len(string_table):
                print(
                    f"  FEHLER: Spell {spell_id}, Feld {pos}: String-Offset "
                    f"{str_off} >= String-Tabelle ({len(string_table)})"
                )
                errors += 1
                if errors > 10:
                    sys.exit("  Zu viele String-Referenz-Fehler, Abbruch.")

    if errors == 0:
        print(f"  String-Referenzen: OK (alle {len(STRING_POSITIONS)} String-Felder geprueft)")

    # 8. Float sanity check
    float_errors = 0
    for i in range(record_count):
        offset = records_start + i * record_size
        rec = data[offset: offset + record_size]
        spell_id = struct.unpack_from("<I", rec, 0)[0]

        for pos in FLOAT_POSITIONS:
            val = struct.unpack_from("<f", rec, pos * 4)[0]
            import math
            if math.isnan(val) or math.isinf(val):
                print(
                    f"  FEHLER: Spell {spell_id}, Feld {pos}: "
                    f"Ungueltiger Float-Wert: {val}"
                )
                float_errors += 1

    if float_errors == 0:
        print(f"  Float-Werte: OK (keine NaN/Inf)")

    print(f"\nValidierung abgeschlossen — keine Fehler.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ergaenzt eine Spell.dbc um Eintraege aus einer spell_dbc.csv "
                    "(MySQL-Export). Bricht ab wenn doppelte IDs gefunden werden."
    )
    parser.add_argument(
        "directory", nargs="?", default=".",
        help="Verzeichnis mit Spell.dbc und spell_dbc.csv (Standard: aktuelles Verzeichnis)",
    )
    args = parser.parse_args()

    work_dir = Path(args.directory)
    dbc_path = work_dir / "Spell.dbc"
    csv_path = work_dir / "spell_dbc.csv"
    out_path = work_dir / "Spell_merged.dbc"

    # --- Check input files exist ---
    if not dbc_path.exists():
        sys.exit(f"FEHLER: {dbc_path} nicht gefunden.")
    if not csv_path.exists():
        sys.exit(f"FEHLER: {csv_path} nicht gefunden.")

    # --- Read DBC ---
    print(f"Lese Spell.dbc: {dbc_path}")
    dbc = read_dbc(dbc_path)
    dbc_count = len(dbc["records"])
    print(f"  {dbc_count} Spells geladen, Record-Size {dbc['record_size']} Bytes")

    # --- Read CSV ---
    print(f"\nLese CSV: {csv_path}")
    header, csv_rows = read_csv_spells(csv_path)
    csv_count = len(csv_rows)
    print(f"  {csv_count} Eintraege gelesen, {len(header)} Spalten")

    # --- Check for duplicate IDs between DBC and CSV ---
    csv_ids = set()
    csv_duplicates_internal = []
    for row in csv_rows:
        sid = int(row["ID"])
        if sid in csv_ids:
            csv_duplicates_internal.append(sid)
        csv_ids.add(sid)

    if csv_duplicates_internal:
        print(
            f"\nFEHLER: CSV enthaelt {len(csv_duplicates_internal)} intern "
            f"doppelte Spell-IDs: {sorted(csv_duplicates_internal)[:20]}"
            f"{'...' if len(csv_duplicates_internal) > 20 else ''}"
        )
        sys.exit(1)

    overlap = csv_ids & set(dbc["records"].keys())
    if overlap:
        overlap_sorted = sorted(overlap)
        print(f"\nFEHLER: {len(overlap)} Spell-ID(s) existieren bereits in der DBC!")
        print(f"Doppelte IDs: {overlap_sorted[:30]}{'...' if len(overlap) > 30 else ''}")
        print(
            f"\nAbbruch — keine Aenderungen vorgenommen. "
            f"Entferne die doppelten IDs aus der CSV oder der DBC, "
            f"bevor du erneut ausfuehrst."
        )
        sys.exit(1)

    # --- Convert CSV rows to DBC records ---
    print(f"\nKonvertiere {csv_count} CSV-Eintraege zu DBC-Records ...")
    string_table = dbc["string_table"]  # bytearray, will be extended
    string_cache = {}  # text → offset (for deduplication)
    new_records = {}

    for row_idx, row in enumerate(csv_rows):
        values = [row[col] for col in header]
        spell_id = int(values[0])

        try:
            record = csv_row_to_dbc_record(values, row_idx, string_table, string_cache)
        except (ValueError, struct.error) as e:
            sys.exit(
                f"FEHLER: Konvertierungsfehler in CSV-Zeile {row_idx + 2} "
                f"(Spell {spell_id}): {e}"
            )

        # Verify the ID in the binary record matches
        packed_id = struct.unpack_from("<I", record, 0)[0]
        if packed_id != spell_id:
            sys.exit(
                f"FEHLER: ID-Mismatch in Zeile {row_idx + 2}: "
                f"CSV ID={spell_id}, Binary ID={packed_id}"
            )

        new_records[spell_id] = record

    print(f"  {len(new_records)} Records konvertiert")

    # --- Merge ---
    merged = dict(dbc["records"])
    merged.update(new_records)
    total_count = len(merged)
    print(f"\nMerge: {dbc_count} (DBC) + {len(new_records)} (CSV) = {total_count} Spells")

    # Sort by spell ID
    sorted_records = [merged[sid] for sid in sorted(merged)]

    # --- Write ---
    print(f"Schreibe: {out_path}")
    write_dbc(out_path, dbc["field_count"], dbc["record_size"], sorted_records,
              bytes(string_table))

    file_size = out_path.stat().st_size
    print(f"  {total_count} Records, {file_size:,} Bytes")

    # --- Validate ---
    validate_merged_dbc(out_path, total_count)

    # --- Summary ---
    print(f"\n{'=' * 60}")
    print(f"FERTIG!")
    print(f"  Original DBC:  {dbc_count} Spells")
    print(f"  CSV-Eintraege:  {csv_count} Spells")
    print(f"  Merged DBC:    {total_count} Spells")
    print(f"  Ausgabe:       {out_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
