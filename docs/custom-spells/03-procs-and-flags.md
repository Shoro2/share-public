# Custom Spells — Procs & Flags

> **Status:** TODO (Phase 2). Übernehmen aus [`mod-custom-spells/PROCFLAGS_REFERENCE.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/PROCFLAGS_REFERENCE.md) und [`docs/03-spell-system.md`](../03-spell-system.md).

## `spell_proc` Pflichtfelder

TODO: vollständiges INSERT-Template + Erklärung jedes Felds.

## ProcFlags-Werte

TODO: Tabelle aus `SpellMgr.h` (geprüft).

## SpellTypeMask, SpellPhaseMask, HitMask

TODO.

## SpellFamilyFlags-Verifikation

TODO: warum Online-Quellen (wowhead, wowdb) ungeprüft NICHT übernommen werden dürfen, plus Debug-Log-Pattern.

## Off-by-One BasePoints

TODO: `Spell.dbc` speichert `EffectBasePoints = real_value - 1`. Konsequenzen für `spell_dbc`-Inserts.

## DBC `EffectSpellClassMask` wird ignoriert

TODO: Filterung läuft ausschließlich über `spell_proc` + C++ `CheckProc` bei `SPELL_AURA_PROC_TRIGGER_SPELL`.

## Rekursionsschutz

TODO: `PreventDefaultAction()`, `SPELL_ATTR3_CAN_PROC_FROM_PROCS`, ICDs für AoE-Procs.
