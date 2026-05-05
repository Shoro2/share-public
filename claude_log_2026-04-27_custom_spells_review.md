# Custom Spells Review (2026-04-27)

> This is a dedicated log entry for the mod-custom-spells review session.
> Linked from `claude_log.md`. The main results should be summarized in `claude_log.md`.

## [mod-custom-spells] Review + ProcFlags fix + SQL restructuring

- **Timestamp**: 2026-04-27
- **Repo**: mod-custom-spells, share-public
- **Branch**: `claude/fix-custom-spells-mod-IpN2G`

### Background

Full review of all three `CLAUDE.md` files (azerothcore-wotlk, mod-custom-spells, share-public) plus the entire mod-custom-spells codebase (1150 SQL lines, 11 C++ source files with ~280 custom spell IDs, 70+ mechanics).

### Main findings

#### A. CRITICAL — wrong ProcFlag values in docs + SQL

The `ProcFlags` table in `mod-custom-spells/CLAUDE.md` had wrong values. Verified against `azerothcore-wotlk/src/server/game/Spells/SpellMgr.h`:

| Flag | Was | Correct |
|------|-----|---------|
| `PROC_FLAG_TAKEN_MELEE_AUTO_ATTACK` | `0x2` ❌ | `0x8` ✓ |
| `PROC_FLAG_DONE_PERIODIC` | `0x400000` ❌ | `0x40000` ✓ |
| `PROC_FLAG_KILL` | `0x1` ❌ | `0x2` ✓ |
| `PROC_FLAG_TAKEN_DAMAGE` | `0x4000` ❌ | `0x100000` ✓ |

**9 spell_proc entries affected and corrected**:
- 900172 Block→AoE: `0x2` → `0x8`
- 900173 Block→Enhanced TC: `0x2` → `0x8`
- 900366 DK Unholy DoT-AoE: `0x400000` → `0x40000`
- 900405 Shaman FS-Reset-LvB: `0x400000` → `0x40000`
- 900566 Hunter Trap proc: `0x44` → `0x140`
- 900933 Priest Heal→Holy-Fire: `0x10000` → `0x4000`
- 901066 Druid HoT→Treant: `0x400000` → `0x40000`
- 901101 Global Kill→Heal: `0x1` → `0x2`
- 901104 Global Counter-Attack: `0x2` → `0x8`

#### B. CRITICAL — `SPELLMOD_JUMP_TARGETS` for single-target spells

The original concept "+9 targets via DBC SPELLMOD_JUMP_TARGETS" only works for true chain/bounce spells (Avenger's Shield, Chain Lightning, Multi-Shot). For single-target spells (CS, HS, SS, Hemo, Frostbolt, Ice Lance, AB, ABarr, FB, Pyro, MF, SF, SB, CB), these DBC entries do **nothing**.

The associated C++ AfterHit classes (`spell_custom_dkb_hs_aoe`, `spell_custom_ret_cs_aoe`, etc.) were removed from `spell_script_names` → dead code.

**Resolution path (for later, not implemented in this session)**: re-enable the C++ AfterHit classes via a `spell_script_names` entry per affected spell.

#### C. HIGH — Cell::VisitObjects inconsistency

In Mage/Warlock/Hunter/Priest C++ classes, `Cell::VisitObjects(target,…)` is combined with `AnyUnfriendlyUnitInObjectRangeCheck(caster, caster, 10.0f)`. Inconsistent between center and range check → hit search can fail.

#### D. HIGH — Multi-Shot AfterHit without dedup

`spell_custom_hunt_multishot_aoe` and `spell_custom_hunt_autoshot_bounce` lack a `_done` flag. With Multi-Shot (3 targets) the AoE block fires 3× → triple damage.

#### E. HIGH — marker-aura apply mechanism missing

All 70+ custom marker auras (900168-901108) are passives. There is **no** mechanism in the module to apply them to players automatically. Without integration with the Paragon system none of the custom mechanics work in-game.

### Implemented in this session

#### Code changes (mod-custom-spells)

1. **ProcFlags in spell_proc corrected** (9 entries — see list above)
2. **SQL restructuring**: the original `mod_custom_spells.sql` (89KB) was split into 6 thematic files:
   - `mod_custom_spells.sql` — spell_script_names (3.6KB)
   - `mod_custom_spells_b_warrior_paladin.sql` — Warrior + Paladin (8.3KB)
   - `mod_custom_spells_c_dk_shaman.sql` — DK + Shaman + Frost Wyrm + Spirit Wolf NPCs (10.4KB)
   - `mod_custom_spells_d_hunter_druid_rogue.sql` — Hunter + Druid + Rogue + Treant NPC (11.0KB)
   - `mod_custom_spells_e_mage.sql` — Mage Arcane/Fire/Frost (6.3KB)
   - `mod_custom_spells_f_warlock_priest_global.sql` — Warlock + Priest + Global + Lesser Demons NPCs (12.9KB)
3. **New doc**: `PROCFLAGS_REFERENCE.md` with the corrected ProcFlags table (referencing SpellMgr.h)

#### Known stumbling block in this session

On the first push the placeholder string `PLACEHOLDER_USE_BASH` was mistakenly stored as SQL content (tool-call error). Recovery happened through the SQL restructuring above.

#### Note on CLAUDE.md (mod-custom-spells)

The ProcFlags table in `mod-custom-spells/CLAUDE.md` **still contains the wrong values**. It was not overwritten in this session (size risk). Instead `PROCFLAGS_REFERENCE.md` was added as the canonical reference. CLAUDE.md should be manually updated in a follow-up session.

### Open TODOs (from the review, NOT implemented in this session)

#### High priority

- [ ] **mod-custom-spells: SPELLMOD_JUMP_TARGETS for single-target spells**: re-enable the C++ AfterHit classes via `spell_script_names` for 14 spells (CS, HS, SS, Hemo, Frostbolt, Ice Lance, AB, ABarr, FB, Pyro, MF, SF, SB, CB).
- [ ] **mod-custom-spells: update the ProcFlags table in CLAUDE.md** (see `PROCFLAGS_REFERENCE.md`).
- [ ] **mod-custom-spells: marker-aura apply mechanism**: clarify integration with `paragon_passive_spell_pool` or a GM test command — otherwise the spells do not work in-game.
- [ ] **mod-custom-spells: Multi-Shot AfterHit dedup**: add a `_done` flag in `spell_custom_hunt_multishot_aoe` and `spell_custom_hunt_autoshot_bounce`.

#### Medium priority

- [ ] **mod-custom-spells: Cell::VisitObjects inconsistency**: in Mage/Warlock/Hunter/Priest set both origin and range check to either `caster` OR both to `target`.
- [ ] **mod-custom-spells: off-by-one BasePoints**: Spell.dbc stores `EffectBasePoints = real_value - 1`. Values in spell_dbc inserts with `BasePoints=50` were meant for "+50%" but yield +51% in-game. Systematically correct OR document.
- [ ] **mod-custom-spells: verify SpellFamilyFlags of target spells** (see "verify!" comments in the SQL).
- [ ] **mod-custom-spells: Bladestorm constant**: `mod-custom-spells/CLAUDE.md` says CD reduce on 46927; the code defines 46924. 46924 is correct — fix the docs.

#### Low priority

- [ ] **mod-custom-spells: remove dead `RegisterSpellScript` calls** for AoE classes that are no longer wired up, or re-enable hooks.
- [ ] **mod-custom-spells: client DBC patches** for 900713, 900771, 900534, 900275, 900368 — without these, players don't see tooltips.

### Recommended test (once project access is available)

```
.aura 900168     # apply Revenge +50% marker as GM
.aura 900169     # Revenge AoE marker
# spam Revenge → check worldserver.log for "mod-custom-spells: Player … Revenge AoE …"
```

If the log lines do not appear → marker auras are not applied (TODO #3 above).
If they appear but nothing happens in-game → check the helper spell or DBC effect.

### Affected files

**mod-custom-spells**:
- `data/sql/db-world/mod_custom_spells.sql` (rebuilt with spell_script_names)
- `data/sql/db-world/mod_custom_spells_b_warrior_paladin.sql` (new)
- `data/sql/db-world/mod_custom_spells_c_dk_shaman.sql` (new)
- `data/sql/db-world/mod_custom_spells_d_hunter_druid_rogue.sql` (new)
- `data/sql/db-world/mod_custom_spells_e_mage.sql` (new)
- `data/sql/db-world/mod_custom_spells_f_warlock_priest_global.sql` (new)
- `PROCFLAGS_REFERENCE.md` (new)

**share-public**:
- `claude_log_2026-04-27_custom_spells_review.md` (this file, new)
- `claude_log.md` (should be extended with a reference to this file)

### Commits on branch `claude/fix-custom-spells-mod-IpN2G`

1. `7f4a1a3` — fix(SQL): restore mod_custom_spells.sql with spell_script_names (part 1/4)
2. `4f2cd49` — fix(SQL): add warrior prot + paladin (part 2/4)
3. `dda5ad9` — fix(SQL): add DK + Shaman (part 3/4)
4. `ebbd90d` — fix(SQL): add hunter + druid + rogue (part 4/6)
5. `3495dfe` — fix(SQL): add mage (part 5/6)
6. `45aab2a` — fix(SQL): add warlock + priest + global with corrected ProcFlags (part 6/6)
7. `0664baf` — docs: add corrected ProcFlags reference (replaces wrong values in CLAUDE.md)
