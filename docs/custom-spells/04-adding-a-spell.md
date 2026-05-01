# Custom Spells — Adding a New Spell

> **Status:** TODO (Phase 2).

Step-by-Step Rezept für einen neuen Custom Spell. Reihenfolge ist wichtig — DBC vor SQL vor C++.

## 1. ID wählen

Nächste freie ID im Spec-Block reservieren — siehe [02-id-blocks.md](./02-id-blocks.md) und das Spec-File. ID in der Spec-Tabelle als `WIP` eintragen.

## 2. DBC-Eintrag

TODO: Workflow aus `python_scripts/copy_spells_dbc.py` und `patch_dbc.py`.

## 3. `spell_dbc` DB-Override

TODO: Beispiel-INSERT, Off-by-One BasePoints beachten (siehe [03-procs-and-flags.md](./03-procs-and-flags.md)).

## 4. `spell_proc` (nur bei Procs)

TODO: Beispiel-INSERT.

## 5. SpellScript / AuraScript

TODO: Skelett-Code, Registrierung via `RegisterSpellScript`.

## 6. SQL-Registrierung

```sql
DELETE FROM `spell_script_names` WHERE `spell_id` = <ID>;
INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES (<ID>, '<class>');
```

## 7. Build & Test

TODO: Verifikation via Debug-Log, In-Game-Test.

## 8. Doku updaten

Spec-Tabelle: Status auf `Live`. Implementation Notes ergänzen falls nicht-trivial.
