# dbc — DBCStorage and the global `s*Store` instances

> The typed wrapper around a loaded DBC: `DBCStorage<T>` keeps a flat `T**` index table and exposes `LookupEntry(id)`, `GetNumRows()`, range iteration, and `LoadFromDB(table, fmt)` for the DB override layer. About 90 global `extern DBCStorage<…> s*Store` instances are declared in `DBCStores.h` and defined in `DBCStores.cpp`. Loader internals: [`01-loader.md`](./01-loader.md). Override layer: [`06-db-overrides.md`](./06-db-overrides.md).

## Critical files

| File | Role |
|---|---|
| `src/server/shared/DataStores/DBCStore.h:28` | `class DBCStorageBase` — type-erased base, owns `_dataTable` + `_stringPool` + `_indexTableSize` + `_fileFormat` |
| `src/server/shared/DataStores/DBCStore.h:53` | `template <class T> class DBCStorage : DBCStorageBase` — typed facade |
| `src/server/shared/DataStores/DBCStore.h:69` | `LookupEntry(id)` (returns nullptr for sparse holes) and `AssertEntry(id)` |
| `src/server/shared/DataStores/DBCStore.h:72` | `SetEntry(id, T*)` — extend / overwrite a slot at runtime |
| `src/server/shared/DataStores/DBCStore.h:91` | `GetNumRows()` — returns `_indexTableSize` (max ID + 1, sparse-aware) |
| `src/server/shared/DataStores/DBCStore.h:108-109` | `begin() / end()` over `DBCStorageIterator<T>` |
| `src/server/shared/DataStores/DBCStorageIterator.h:34` | iterator constructor — skips `nullptr` slots so range-for is dense |
| `src/server/shared/DataStores/DBCStore.cpp:32` | `DBCStorageBase::Load(path, indexTable&)` — calls `DBCFileLoader::Load` + `AutoProduceData` + `AutoProduceStrings` |
| `src/server/shared/DataStores/DBCStore.cpp:55` | `LoadStringsFrom(path, indexTable)` — locale overlay |
| `src/server/shared/DataStores/DBCStore.cpp:74` | `LoadFromDB(table, fmt, indexTable&)` — delegates to `DBCDatabaseLoader` |
| `src/server/game/DataStores/DBCStores.h:78-198` | the ~90 `extern DBCStorage<…> s*Store` declarations |
| `src/server/game/DataStores/DBCStores.cpp:60-198` | matching definitions (each constructed with its `*fmt[]` from `DBCfmt.h`) |

## Key concepts

- **Index table is `T**`** — a flat `T*[indexTableSize]`. `LookupEntry(id)` is an O(1) `id < size ? table[id] : nullptr`. Sparse IDs are common (e.g. `sSpellStore` has IDs in the 80 000s with many gaps); empty slots stay `nullptr`.
- **`_indexTableSize`** is the **max-ID plus one**, not the row count. To iterate all *present* entries use range-for (which uses `DBCStorageIterator` and skips nullptrs) — never `for (uint32 i = 0; i < storage.GetNumRows(); ++i)` without a null check.
- **Dual storage model** — strings live separately from the flat record array. `_stringPool` is a `std::vector<char*>` of allocated blocks; locales add new blocks (one per loaded `*.dbc` per locale), all freed by `~DBCStorageBase`.
- **Format string is fixed at construction** — `DBCStorage<T>` is constructed with a `char const*` fmt (e.g. `Itemfmt`) at static-init time (`DBCStores.cpp:101`). The fmt drives the field-size table inside `DBCFileLoader::Load` and is also consumed by `LoadFromDB` when the SQL override layer parses a `_dbc` table.
- **`SetEntry(id, T*)` resizes** the index table on demand (`DBCStore.h:74-85`). Used by the SQL loader and by post-load fixups (e.g. the taxi-node DK fix at `DBCStores.cpp:610`). Note `SetEntry` `delete`s the old `_indexTable.AsT[id]`, so the pointer must be heap-owned by the storage — passing a stack pointer is a use-after-free.
- **Union access** — `_indexTable` is a `union { T** AsT; char** AsChar; }` so `DBCStorageBase` can mutate the table without knowing `T` (`DBCStore.h:112-117`).

### The most-used global stores

Sample of the heaviest consumers; full list in `DBCStores.h:78-198` (about 90 entries).

| Store | Type | Loaded from | Used by |
|---|---|---|---|
| `sSpellStore` | `SpellEntry` | `Spell.dbc` (custom-patched here) | `SpellMgr::LoadSpellInfoStore` (`SpellMgr.cpp:2903`), every cast |
| `sItemStore` | `ItemEntry` | `Item.dbc` | `ObjectMgr::LoadItemTemplates` correlates with `item_template` |
| `sMapStore` | `MapEntry` | `Map.dbc` | `MapMgr` per-map lookups, instance gating |
| `sAreaTableStore` | `AreaTableEntry` | `AreaTable.dbc` | zone/sub-zone resolution, sanctuary / flyable checks |
| `sCreatureDisplayInfoStore` | `CreatureDisplayInfoEntry` | `CreatureDisplayInfo.dbc` | model lookups for creatures, transmog |
| `sCreatureFamilyStore` | `CreatureFamilyEntry` | `CreatureFamily.dbc` | hunter pets, pet talent eligibility |
| `sFactionStore` / `sFactionTemplateStore` | `FactionEntry` / `FactionTemplateEntry` | `Faction.dbc`, `FactionTemplate.dbc` | reputation, faction relations |
| `sTalentStore` / `sTalentTabStore` | `TalentEntry` / `TalentTabEntry` | `Talent.dbc`, `TalentTab.dbc` | talent tree, learn-talent handler |
| `sAchievementStore` | `AchievementEntry` | `Achievement.dbc` | `AchievementMgr`, criteria progress |
| `sSkillLineStore` / `sSkillLineAbilityStore` | `SkillLineEntry` / `SkillLineAbilityEntry` | `SkillLine.dbc`, `SkillLineAbility.dbc` | profession/spellbook bridge |
| `sSpellItemEnchantmentStore` | `SpellItemEnchantmentEntry` | `SpellItemEnchantment.dbc` | item enchants (the project's `mod-paragon-itemgen` overrides this) |
| `sSpellCastTimesStore` / `sSpellDurationStore` / `sSpellRadiusStore` / `sSpellRangeStore` | sub-tables referenced by `SpellEntry::*Index` | corresponding `Spell*.dbc` | every spell's runtime data |
| `sChrClassesStore` / `sChrRacesStore` | `ChrClassesEntry` / `ChrRacesEntry` | `ChrClasses.dbc`, `ChrRaces.dbc` | character creation, class/race gating |

The remaining `s*Store` entries cover taxi (`sTaxiNodesStore`/`sTaxiPathStore`/`sTaxiPathNodeStore`), vehicle (`sVehicleStore`/`sVehicleSeatStore`), gear-scaling (`sScalingStatValuesStore`/`sRandomPropertiesPointsStore`), combat-rating tables (`sGtCombatRatingsStore`, `sGtChanceToMeleeCritStore`, …), barbershop, holiday, mail-template, dungeon-encounter, glyph and currency. Full list of 246 client DBCs lives in [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md); the inventory marks which ones map to a server `s*Store`.

## Flow / data shape

`DBCStorage<T>` lifecycle, single locale:

```
DBCStorage<T> sFooStore(Foofmt)   // static-init, allocates nothing
  ├─ Load("dbc/Foo.dbc")          → DBCFileLoader::Load + AutoProduceData
  │     _dataTable     ← typed flat array
  │     _indexTable.AsT ← T*[max(id)+1], sparse
  │     _indexTableSize ← max(id)+1
  │     _stringPool[0]  ← AutoProduceStrings result
  ├─ LoadStringsFrom("dbc/<locale>/Foo.dbc")  → _stringPool[1..n] (per loaded locale)
  └─ LoadFromDB("foo_dbc", fmt)   → see 06-db-overrides.md
                                    appends DB rows by SetEntry-equivalent path
```

Idiomatic call sites:

```cpp
// O(1) lookup, returns nullptr on miss (87% of game code uses this form)
SpellEntry const* spellEntry = sSpellStore.LookupEntry(spellId);
if (!spellEntry)
    return SPELL_FAILED_UNKNOWN;

// Hard assertion — abort if the ID must exist (used in startup checks)
MapEntry const* map = sMapStore.AssertEntry(mapId);

// Range-for skips nullptr holes (DBCStorageIterator.h:34)
for (CharStartOutfitEntry const* outfit : sCharStartOutfitStore)
    sCharStartOutfitMap[outfit->Race | (outfit->Class << 8) | (outfit->Gender << 16)] = outfit;
```

`SpellInfo` is the heaviest consumer: `SpellMgr::LoadSpellInfoStore` walks `sSpellStore` once and constructs one heap `SpellInfo` per row, indexed in `mSpellInfoMap` (`SpellMgr.cpp:2903-2911`). After that, every `Unit::CastSpell` / aura tick / proc walks `mSpellInfoMap` rather than `sSpellStore` directly.

## Hooks & extension points

- `DBCStorage<T>::SetEntry(id, T*)` — append/replace a row at runtime. Used by SQL overrides and by a handful of post-load fixups in `LoadDBCStores` (`DBCStores.cpp:609`).
- `LoadFromDB(table, fmt)` — the standard DB-override entry point, fired from inside `LoadDBC` when the third macro argument is non-null. See [`06-db-overrides.md`](./06-db-overrides.md).
- Modules that need a custom DBC-like store usually pick one of three options: a new SQL table loaded by `ObjectMgr` (most modules), `SetEntry` to extend an existing store (rare; `Spell.dbc` does this in this fork via the patched binary, **not** at runtime), or duplicating `DBCStorage<T>` for a custom struct (uncommon — `M2Stores` is the only existing precedent, see `src/server/game/DataStores/M2Stores.{h,cpp}`).

## Cross-references

- Engine-side: [`01-loader.md`](./01-loader.md), [`03-format-strings.md`](./03-format-strings.md), [`04-structures.md`](./04-structures.md), [`05-load-sequence.md`](./05-load-sequence.md), [`06-db-overrides.md`](./06-db-overrides.md), [`../spells/00-index.md`](../spells/00-index.md) (heaviest consumer)
- Project-side: [`../../03-spell-system.md#dbc-system`](../../03-spell-system.md), [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md), [`../../06-custom-ids.md`](../../06-custom-ids.md)
- Fork-specific: `azerothcore-wotlk/CLAUDE.md` (custom Spell.dbc with IDs `100xxx` / `900xxx`)
- External: Doxygen `classDBCStorage.html`, `classDBCStorageBase.html`, `DBCStore_8h.html`
