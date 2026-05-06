# dbc — DBCStructure.h tour

> One C++ struct per loaded DBC, defined in a single 2 251-line header. Each struct mirrors the on-disk layout dictated by the matching format string in [`03-format-strings.md`](./03-format-strings.md). The 90-ish `DBCStorage<T>` instances in [`02-stores.md`](./02-stores.md) instantiate the templates over these structs. Field comments embed the on-disk index (`// 12 m_shapeshiftMask`) so a record dump can be cross-referenced back to the WDBC layout.

## Critical files

| File | Role |
|---|---|
| `src/server/shared/DataStores/DBCStructure.h:18-25` | Includes (`AreaDefines.h`, `DBCEnums.h`, `Define.h`, `Util.h`) and `<array>` |
| `src/server/shared/DataStores/DBCStructure.h:1637-1639` | Spell-relevant size constants: `MAX_SPELL_EFFECTS=3`, `MAX_EFFECT_MASK=7`, `MAX_SPELL_REAGENTS=8` |
| `src/server/shared/DataStores/DBCStructure.h:2221` | `struct MapDifficulty` (helper, not a DBC row — built from `MapDifficultyEntry` rows) |
| `src/server/shared/DataStores/DBCStructure.h:2231` | `struct TalentSpellPos` (helper) |
| `src/server/shared/DataStores/DBCStructure.h:2241-2247` | Helper typedefs: `TalentSpellPosMap`, `TaxiPathSetForSource`, `TaxiPathSetBySource`, `TaxiPathNodeList` |
| `src/server/shared/DataStores/DBCEnums.h` | `enum`s referenced from struct fields (Difficulty, MapTypes, AchievementCriteriaTypes, …) |

## Key concepts

- **One struct per loaded DBC.** Struct name = `<DbcBaseName>Entry` (e.g. `Spell.dbc` → `SpellEntry`). The matching `DBCStorage<T>` lives in `DBCStores.{h,cpp}` (see [`02-stores.md`](./02-stores.md)).
- **Field-index comments are load-bearing.** The `// 12 m_shapeshiftMask` annotations next to each member are the on-disk field index; a missing index means the field is **skipped** on disk (matched by `x` or `X` in the format string in [`03-format-strings.md`](./03-format-strings.md)).
- **`std::array<T, N>` for fixed-size runs** — newer code uses `std::array<uint32, MAX_SPELL_EFFECTS>` rather than C arrays (see `SpellEntry`, `TalentEntry::RankID`). Older / smaller structs still use C arrays. Both are byte-compatible with the on-disk layout.
- **Helpers on structs.** Several entries carry inline accessors: `MapEntry::IsDungeon()`, `MapEntry::IsContinent()`, `AreaTableEntry::IsSanctuary()`, `SpellRuneCostEntry::NoRuneCost()`. Always prefer the helper to a hand-rolled flag check.
- **Skipped fields are documented anyway.** Commented-out members (`//uint32 parentAchievement; // 3 ...`) preserve the on-disk field index for future reactivation.

## Tour by category

### Spell-related (the bulk of runtime traffic)

| Struct | Line | Notes |
|---|---|---|
| `SpellEntry` | `DBCStructure.h:1641` | 234-field heavyweight; consumed once by `SpellMgr::LoadSpellInfoStore` (`SpellMgr.cpp:2903`) which builds `SpellInfo` per row. **Do not** read `EffectBasePoints` directly — use cached `Spell::m_currentBasePoints` (see comment at `:1700`). |
| `SpellCastTimesEntry` | `DBCStructure.h:1757` | `CastTime` (ms). Indexed by `SpellEntry::CastingTimeIndex`. |
| `SpellDurationEntry` | `DBCStructure.h:1832` | `Duration[3]` = base/per-level/max. Indexed by `SpellEntry::DurationIndex`. |
| `SpellRadiusEntry` | `DBCStructure.h:1784` | `RadiusMin / RadiusPerLevel / RadiusMax`. Indexed by `SpellEntry::EffectRadiusIndex[i]`. |
| `SpellRangeEntry` | `DBCStructure.h:1792` | `RangeMin[2] / RangeMax[2]` (hostile/friendly). Indexed by `SpellEntry::RangeIndex`. |
| `SpellRuneCostEntry` | `DBCStructure.h:1804` | DK rune cost (blood/frost/unholy + power gain). |
| `SpellShapeshiftFormEntry` | `DBCStructure.h:1816` | Druid forms etc. — flags, stance spells. |
| `SpellItemEnchantmentEntry` | `DBCStructure.h:1840` | Item enchant definition; the project's `mod-paragon-itemgen` overrides via `spellitemenchantment_dbc` (see [`06-db-overrides.md`](./06-db-overrides.md)). |
| `SpellItemEnchantmentConditionEntry` | `DBCStructure.h:1859` | Gem-color match conditions. |
| `SpellDifficultyEntry` | `DBCStructure.h:1771` | Per-difficulty spell variant (`SpellID[4]` indexed by `Difficulty`). Wired up in `LoadDBCStores` at `DBCStores.cpp:462` via `sSpellMgr->SetSpellDifficultyId`. |
| `SpellVisualEntry` | `DBCStructure.h:1870` | Visual data. |

### Map / area / world

| Struct | Line | Notes |
|---|---|---|
| `MapEntry` | `DBCStructure.h:1324` | Map ID, type, name, expansion, entrance coords, helpers `IsDungeon()`, `IsRaid()`, `IsContinent()`. |
| `MapDifficultyEntry` | `DBCStructure.h:1378` | Per-(map, difficulty) reset time + max players + missing-requirements text. Aggregated into `sMapDifficultyMap` at `DBCStores.cpp:412`. |
| `AreaTableEntry` | `DBCStructure.h:518` | Zone/sub-zone (`mapid`, `zone`, `flags`, level, name). Helpers `IsSanctuary()`, `IsFlyable()`. |
| `AreaGroupEntry` | `DBCStructure.h:548` | Up to 6 area IDs + chained `nextGroup`. |
| `AreaPOIEntry` | `DBCStructure.h:555` | Map points-of-interest (icon, x/y/z, mapId, zoneId). |
| `WMOAreaTableEntry` | `DBCStructure.h:2130` | WMO root/adt/group → area. Looked up by `GetWMOAreaTableEntryByTripple` (see `DBCStores.h:36`). |

### Item / equipment

| Struct | Line | Notes |
|---|---|---|
| `ItemEntry` | `DBCStructure.h:1142` | Class/subclass/material/displayInfoID/inventoryType — minimal client-side row; full template lives in DB `item_template`. |
| `ItemDisplayInfoEntry` | `DBCStructure.h:1161` | Inventory icon path. |
| `ItemExtendedCostEntry` | `DBCStructure.h:1187` | Honor/arena cost + required-item list (5 entries). |
| `ItemRandomPropertiesEntry` | `DBCStructure.h:1209` | "of the Bear" suffix-free random props (5 enchants + 16 locale names). |
| `ItemRandomSuffixEntry` | `DBCStructure.h:1218` | "of the X" — 5 enchants + 5 allocation %. |
| `ItemSetEntry` | `DBCStructure.h:1231` | 10-slot item set + 8 set-bonus spells + skill requirement. |
| `GemPropertiesEntry` | `DBCStructure.h:1016` | Color, gem-enchant link. |

### Creature / NPC

| Struct | Line | Notes |
|---|---|---|
| `CreatureDisplayInfoEntry` | `DBCStructure.h:720` | `ModelId`, `ExtendedDisplayInfoID`, `scale`. |
| `CreatureDisplayInfoExtraEntry` | `DBCStructure.h:738` | Race-bound humanoid display (most fields commented out — only `DisplayRaceID` is used server-side). |
| `CreatureFamilyEntry` | `DBCStructure.h:753` | Hunter pet family — scale curve, two skill lines, food mask, talent type. |
| `CreatureModelDataEntry` | `DBCStructure.h:774` | Collision width/height + mount height. Helper `HasFlag(CREATURE_MODEL_DATA_FLAGS_CAN_MOUNT)`. |
| `CreatureSpellDataEntry` | `DBCStructure.h:809` | 4-slot spell list per creature. |
| `CreatureTypeEntry` | `DBCStructure.h:816` | Type ID only (Beast / Humanoid / …). |

### Talent / skill / achievement

| Struct | Line | Notes |
|---|---|---|
| `TalentEntry` | `DBCStructure.h:1922` | TalentID, TalentTab, Row/Col, `RankID[5]`, `DependsOn`/`DependsOnRank`. Indexed into `sTalentSpellPosMap` at `DBCStores.cpp:498`. |
| `TalentTabEntry` | `DBCStructure.h:1939` | TabID, ClassMask, petTalentMask, tabpage. Class-tab cache built at `DBCStores.cpp:511`. |
| `SkillLineEntry` | `DBCStructure.h:1582` | Skill ID, category, name, spellIcon. |
| `SkillLineAbilityEntry` | `DBCStructure.h:1597` | Skill ↔ Spell binding + race/class mask + min skill rank. Indexed by `sSkillLineAbilityIndexBySkillLine` at `DBCStores.cpp:459`. |
| `SkillTiersEntry` | `DBCStructure.h:1614` | 16 tier values per skill. |
| `AchievementEntry` | `DBCStructure.h:39` | ID, requiredFaction, mapID, name, categoryId, points, flags, count, refAchievement. Most string fields skipped. |
| `AchievementCategoryEntry` | `DBCStructure.h:60` | Just `ID` + `parentCategory`. |
| `AchievementCriteriaEntry` | `DBCStructure.h:69` | Type-discriminated criteria — see `enum AchievementCriteriaTypes` in `DBCEnums.h`. |

### Faction / reputation

| Struct | Line | Notes |
|---|---|---|
| `FactionEntry` | `DBCStructure.h:906` | reputationListID + 4× (race-mask, class-mask, base value, flags), team, spillover rates, name. Helpers `CanHaveReputation()`, `CanBeSetAtWar()`. |
| `FactionTemplateEntry` | `DBCStructure.h:938` | Friend/enemy mask matrix used for hostility checks. |

### Vehicles / taxi / movement

| Struct | Line | Notes |
|---|---|---|
| `VehicleEntry` | `DBCStructure.h:2026` | Up to 8 seats, turn/pitch limits, missile-targeting visuals, locomotion type. |
| `VehicleSeatEntry` | `DBCStructure.h:2063` | Per-seat mount/dismount animation, attachment offset, passenger orientation, flags. |
| `TaxiNodesEntry` | `DBCStructure.h:1952` | Map + xyz + name + 2 mount-creature IDs (Horde/Alliance, Death Knight = 32981). |
| `TaxiPathEntry` | `DBCStructure.h:1964` | from→to + price. Aggregated into `sTaxiPathSetBySource` at `DBCStores.cpp:528`. |
| `TaxiPathNodeEntry` | `DBCStructure.h:1972` | Per-waypoint position + flags. Aggregated into `sTaxiPathNodesByPath` at `DBCStores.cpp:548`. |

### Combat formula tables (`Gt*Entry`)

`gt*.dbc` files are 1-column lookup tables (level → float). Structs at `DBCStructure.h:1044-1099` each hold a single `float ratio;`. Used by stat conversions (`sGtCombatRatingsStore`, `sGtChanceToMeleeCritStore`, `sGtRegenHPPerSptStore`, …). Indexed by `(class - 1) * MAX_LEVEL + (level - 1)` because the DBCs use a `d` (sort) index that is consumed by `DBCFileLoader` but not stored.

## Flow / data shape

Reading a struct's role in two reads:

```
                 ┌────────────────────────────────┐
   I see field?  │ DBCStructure.h:<LINE>         │
                 │   <commented field index>      │
                 └─────────────┬──────────────────┘
                               │ matches by index
                               ▼
                 ┌────────────────────────────────┐
   format char?  │ DBCfmt.h: <Xxxfmt[]>           │
                 │   nth char in the string       │
                 └────────────────────────────────┘
```

Example: `SpellEntry::SpellFamilyName` is `// 208 m_spellClassSet` (`DBCStructure.h:1731`). Counting the 209th char of `SpellEntryfmt` (`DBCfmt.h:108`) is `i`, confirming a 4-byte unsigned. The matching SQL column is `SpellFamilyName` in `spell_dbc` (`spell_dbc.sql:CREATE TABLE`).

## Hooks & extension points

—. New structs are added by extending `DBCStructure.h`, the matching fmt in `DBCfmt.h`, and a new `DBCStorage` declaration + `LOAD_DBC` line (see [`05-load-sequence.md`](./05-load-sequence.md)). Modules may not register new struct types from outside core. To extend an *existing* DBC at runtime use a `*_dbc` override table (see [`06-db-overrides.md`](./06-db-overrides.md)).

## Cross-references

- Engine-side: [`02-stores.md`](./02-stores.md), [`03-format-strings.md`](./03-format-strings.md), [`05-load-sequence.md`](./05-load-sequence.md), [`../spells/00-index.md`](../spells/00-index.md)
- Project-side: [`../../03-spell-system.md#spell_dbc-column-reference-most-relevant-fields`](../../03-spell-system.md), [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md)
- Fork-specific: custom `Spell.dbc` rows live at IDs `100xxx` / `900xxx` — same struct, see `azerothcore-wotlk/CLAUDE.md` and [`../../06-custom-ids.md`](../../06-custom-ids.md)
- External: Doxygen `DBCStructure_8h.html`
