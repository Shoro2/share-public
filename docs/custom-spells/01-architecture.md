# Custom Spells — Architecture

> **Status:** TODO (Phase 2). Aus [`mod-custom-spells/CLAUDE.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CLAUDE.md) destillieren.

## Repo-Layout (`mod-custom-spells/`)

```
src/
  custom_spells.cpp              — OnPlayerSpellCast Master-Switch
  custom_spells_common.h         — geteilte Helpers/Konstanten
  custom_spells_global.cpp       — Non-Class Buffs (901100–901199)
  custom_spells_<class>.cpp      — pro Klasse: Warrior, Paladin, DK, …
  mod_custom_spells_loader.cpp   — Addmod_custom_spellsScripts()
conf/                            — mod_custom_spells.conf.dist
data/                            — SQL/DBC-Daten (TBD)
```

## Hook-Strategien

TODO: Abgrenzung erklären zwischen

- `OnPlayerSpellCast` (PlayerScript) — Master-Switch in `custom_spells.cpp`
- `SpellScript` (registriert via `spell_script_names`) — eigene Effekt-Logik
- `AuraScript` mit Procs (registriert via `spell_proc`) — passive Buffs

Querverweis: [`docs/03-spell-system.md`](../03-spell-system.md) für die Klassen-Hierarchie.

## Loader

`Addmod_custom_spellsScripts()` in `src/mod_custom_spells_loader.cpp` ruft alle `AddSC_*()`-Funktionen der Class-Files auf. TODO: Reihenfolge / Abhängigkeiten dokumentieren.

## Build / Install

TODO: aus `mod-custom-spells/README.md` übernehmen.

## Konfiguration

TODO: Tabelle aller Optionen aus `mod_custom_spells.conf.dist`.
