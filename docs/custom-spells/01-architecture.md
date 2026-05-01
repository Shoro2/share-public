# Custom Spells — Architecture

## Repo-Layout (`mod-custom-spells/`)

```
src/
  mod_custom_spells_loader.cpp   — Module-Entry, Addmod_custom_spellsScripts()
  custom_spells.cpp              — Master-Switch (PlayerScript OnPlayerSpellCast)
  custom_spells_common.h         — geteilte Includes/Konstanten/Enums
  custom_spells_global.cpp       — Non-Class Spells (901100–901199)
  custom_spells_<class>.cpp      — pro Klasse: warrior, paladin, dk, shaman,
                                   hunter, rogue, druid, mage, warlock, priest
conf/
  mod_custom_spells.conf.dist    — CustomSpells.Enable
data/sql/db-world/
  mod_custom_spells.sql          — spell_dbc, spell_script_names, spell_proc
```

Der Loader-Funktionsname folgt der AzerothCore-Konvention: Modul-Ordnername mit `-` ersetzt durch `_`, also `Addmod_custom_spellsScripts()`. Der Core findet ihn beim Static-Linking automatisch.

## Drei Hook-Strategien

Für jeden neuen Spell gibt es drei Wege, das gewünschte Verhalten anzubinden. Welcher Weg passt, hängt davon ab, ob der Effekt einen eigenen Spell-Cast braucht oder sich an einen Blizzard-Spell hängt.

### Strategie 1 — Eigene Custom-Spells (eigene ID + SpellScript)

Eigene 900xxx-ID, DBC-Eintrag in `spell_dbc`, C++-Klasse erbt von `SpellScript`. Verknüpfung über `spell_script_names`. Der Spell wird vom Spieler explizit gecastet (oder per `CastSpell` ausgelöst).

Beispiele: Paragon Strike (900106), Bloody Whirlwind Buff (900115).

### Strategie 2 — Hook auf Blizzard-Spells

Die C++-Klasse hängt sich über `spell_script_names` an eine bereits existierende ID (z. B. 1680 Whirlwind, 23881 Bloodthirst, 57823 Revenge, 47502 Thunderclap). Sie wird bei **jedem** Cast dieses Spells ausgeführt — daher Pflicht: `HasAura()`-Check auf einen Marker-Spell, der nur bei Spielern mit der gewünschten Mechanik aktiv ist.

```cpp
void HandleAfterHit()
{
    Player* player = GetCaster()->ToPlayer();
    if (!player || !player->HasAura(SPELL_PROT_REVENGE_AOE_PASSIVE))
        return;
    // Custom-Logik nur für Spieler mit Marker-Aura
}
```

Beispiele: `spell_custom_prot_revenge_aoe` hängt an Revenge, prüft Marker 900169.

### Strategie 3 — AuraScript mit Proc

Passive Aura (DBC-Effekt `SPELL_AURA_PROC_TRIGGER_SPELL` oder `SPELL_AURA_DUMMY`) wird über `spell_proc` scharfgemacht. Bei Trigger-Event ruft die Engine zuerst `CheckProc()` (filtern), dann `HandleProc()` mit `PreventDefaultAction()` und Custom-Cast.

Wichtig: **DBC `EffectSpellClassMask` wird ignoriert** — die Filterung läuft ausschließlich über `spell_proc` + C++-`CheckProc`. Detail siehe [`03-procs-and-flags.md`](./03-procs-and-flags.md).

## OnPlayerSpellCast Master-Switch

`custom_spells.cpp` enthält einen PlayerScript-Hook auf `OnPlayerSpellCast`, der über ein `switch` auf bestimmte Custom-Spell-IDs reagiert (z. B. für Spells, die nur einen einfachen Side-Effect auslösen sollen, ohne dass ein eigenes SpellScript benötigt wird). Für komplexere Fälle ist Strategie 1–3 vorzuziehen.

## Loader-Reihenfolge

`Addmod_custom_spellsScripts()` ruft alle `AddCustomSpells<Class>Scripts()`-Funktionen auf (eine pro Class-File) sowie `AddCustomSpellsGlobalScripts()`. Reihenfolge ist nicht kritisch — alle Registrierungen landen in den Manager-Maps von `SpellMgr` / `ScriptMgr`.

## DBC-Pflege

Jeder Custom-Spell benötigt einen Eintrag in `spell_dbc` (DB-Override für `Spell.dbc`). Der Server lädt beim Start zuerst `Spell.dbc`, dann die `spell_dbc`-Tabelle drüber. Tooltips im Client greifen aber direkt auf die Client-`Spell.dbc` zu — daher müssen sichtbare Spells zusätzlich in der Client-DBC patched werden (`python_scripts/patch_dbc.py` in `share-public`).

Off-by-One BasePoints beachten: `Spell.dbc` speichert `EffectBasePoints = real_value - 1`. Detail siehe [`docs/03-spell-system.md`](../03-spell-system.md#off-by-one-basepoints).

## Build / Install

```bash
cd azerothcore-wotlk/modules
git clone <repo-url> mod-custom-spells
cd ../build && cmake .. -DSCRIPTS=static -DMODULES=static && make -j$(nproc) && make install
```

SQL aus `data/sql/db-world/` in `acore_world` einspielen. Config:

```bash
cp etc/mod_custom_spells.conf.dist etc/mod_custom_spells.conf
```

## Konfiguration

| Option | Default | Zweck |
|--------|---------|-------|
| `CustomSpells.Enable` | `1` | Modul aktiv (1) / aus (0) |

Alle SpellScripts prüfen `sConfigMgr->GetOption<bool>("CustomSpells.Enable", true)` als ersten Schritt, damit das Modul zur Laufzeit hart ausschaltbar ist.

## Querverweise

- [`02-id-blocks.md`](./02-id-blocks.md) — ID-Schema und Allokation pro Spec
- [`03-procs-and-flags.md`](./03-procs-and-flags.md) — spell_proc, ProcFlags, SpellFamilyFlags
- [`04-adding-a-spell.md`](./04-adding-a-spell.md) — Step-by-Step für neue Spells
- [`docs/03-spell-system.md`](../03-spell-system.md) — SpellScript-/AuraScript-Klassen-Hierarchie + Proc-Pipeline
