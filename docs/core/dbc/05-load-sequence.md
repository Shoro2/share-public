# dbc — `LoadDBCStores` sequence and error handling

> The single startup function that opens every `.dbc`, fills the matching `s*Store`, layers locales, and merges DB overrides. Called once from `World::SetInitialWorldSettings`. Path comes from `worldserver.conf` `DataDir`. Failures fall into two buckets: missing file (logged), or fmt/struct drift (`ASSERT` and `exit(1)`).

## Critical files

| File | Role |
|---|---|
| `src/server/game/World/World.cpp:260` | `dataPath = sConfigMgr->GetOption<std::string>("DataDir", "./")` — origin of the path passed in |
| `src/server/game/World/World.cpp:379` | `LoadDBCStores(_dataPath);` — the single call site |
| `src/server/game/DataStores/DBCStores.h:197` | `void LoadDBCStores(const std::string& dataPath);` declaration |
| `src/server/game/DataStores/DBCStores.cpp:200` | `typedef std::list<std::string> StoreProblemList;` (collected missing/incompatible files) |
| `src/server/game/DataStores/DBCStores.cpp:202` | `uint32 DBCFileCount = 0;` — incremented per `LoadDBC<T>` call |
| `src/server/game/DataStores/DBCStores.cpp:204` | `static bool LoadDBC_assert_print(...)` — diagnostic for the size-check assert |
| `src/server/game/DataStores/DBCStores.cpp:213` | `template<class T> inline void LoadDBC(...)` — per-store loader |
| `src/server/game/DataStores/DBCStores.cpp:216` | `ASSERT(GetFormatRecordSize(fmt) == sizeof(T))` — fmt/struct drift check |
| `src/server/game/DataStores/DBCStores.cpp:222-237` | locale-overlay loop calling `storage.LoadStringsFrom(localizedPath)` |
| `src/server/game/DataStores/DBCStores.cpp:239-240` | `if (dbTable) storage.LoadFromDB(dbTable, storage.GetFormat())` — the override hook |
| `src/server/game/DataStores/DBCStores.cpp:248-258` | bad-file bookkeeping (existed-but-incompatible vs missing) |
| `src/server/game/DataStores/DBCStores.cpp:261` | `void LoadDBCStores(const std::string& dataPath)` — body |
| `src/server/game/DataStores/DBCStores.cpp:265` | `std::string dbcPath = dataPath + "dbc/";` |
| `src/server/game/DataStores/DBCStores.cpp:270` | `#define LOAD_DBC(store, file, dbtable)` — three-arg macro hiding `availableDbcLocales` and `bad_dbc_files` |
| `src/server/game/DataStores/DBCStores.cpp:272-383` | the 113 `LOAD_DBC(...)` calls (load order) |
| `src/server/game/DataStores/DBCStores.cpp:387-621` | post-load fixups (cross-DBC correlations, mask building, fixup data) |
| `src/server/game/DataStores/DBCStores.cpp:624-637` | error reporting — `exit(1)` if all DBCs failed, log + `exit(1)` if any did |
| `src/server/game/DataStores/DBCStores.cpp:640-650` | client-version sentinel checks (last-row-must-exist for 3.3.5a) |
| `src/server/game/DataStores/DBCStores.cpp:652-653` | success log: `Initialized X Data Stores in Y ms` |

## Key concepts

- **Single, monolithic load.** Everything happens inside `LoadDBCStores(dataPath)`; there is no per-store init scattered around the codebase. The function does ~113 `LOAD_DBC` calls, then ~12 cross-correlation passes.
- **`dataPath` resolution.** `World::SetInitialWorldSettings` reads `DataDir` from config (default `./`), normalises to a trailing `/`, and expands a leading `~` on UNIX (`World.cpp:260-271`). `LoadDBCStores` then appends `"dbc/"`. So a config of `DataDir = "/srv/wow/"` looks for `/srv/wow/dbc/Spell.dbc` and friends.
- **`LOAD_DBC` macro.** Defined locally inside `LoadDBCStores` (`DBCStores.cpp:270`) and `#undef`'d at `:385`. Three arguments: target storage, dbc filename, optional override-table name. Captures `availableDbcLocales` and `bad_dbc_files` from the enclosing scope — that is why every macro-call line is ~93 chars and aligned via padding.
- **Per-`LoadDBC<T>` flow.**
  1. Compile-time `ASSERT(GetFormatRecordSize(fmt) == sizeof(T))` — drift check (`:216`).
  2. `++DBCFileCount`.
  3. `storage.Load(dbcPath + filename)` (default-locale `.dbc`).
  4. For each locale bit in `availableDbcLocales`, try `dbcPath + localeNames[i] + "/" + filename` via `LoadStringsFrom`; if missing, clear that locale bit so future stores don't retry it.
  5. If `dbTable` non-null, `storage.LoadFromDB(dbTable, fmt)` → see [`06-db-overrides.md`](./06-db-overrides.md).
  6. If `GetNumRows() == 0`: file existed but was incompatible (extracted from wrong client) **or** missing — push onto `bad_dbc_files`.
- **Locale propagation.** `availableDbcLocales` starts at `0xFFFFFFFF` and bits are cleared as locales fail. The first DBC's missing locale dirs propagate to every subsequent file (no point retrying), so a client in only `enUS` settles to one open per file fast.
- **Failure modes.**
  - All DBCs missing → wrong `DataDir`. Logs `Incorrect DataDir value … or ALL required *.dbc files (X) not found by path: .../dbc` and `exit(1)` (`:626`).
  - Some DBCs missing/incompatible → logs the list, `exit(1)` (`:635`).
  - Outdated client version → the sentinel block `:640-650` looks up known last-rows (`AreaTable.dbc:4987`, `Spell.dbc:80864`, …); failure logs `You have _outdated_ DBC data. Please extract correct versions from current using client.` and `exit(1)`.
  - fmt vs struct drift → `LoadDBC_assert_print` logs the size mismatch and the `ASSERT` aborts.

### Load order (and why it matters)

Most DBCs are independent. The load order in `DBCStores.cpp:272-383` is broadly **alphabetical inside category**, not dependency-driven, **because the dependencies are resolved in the post-load pass** (`:387-621`), not at load time. Cross-DBC correlations that do matter at post-load:

| Post-load pass | Inputs | Output |
|---|---|---|
| `CharStartOutfit` map (`:387`) | `sCharStartOutfitStore` | `sCharStartOutfitMap[race | class << 8 | gender << 16]` |
| Faction-team lists (`:390`) | `sFactionStore` | `sFactionTeamMap[team] → list<factionId>` |
| `MapDifficulty` (`:412`) | `sMapDifficultyStore` (load-only DBC, not exposed via `s*Store`) | `sMapDifficultyMap[(mapId, diff)]` |
| Spell-by-category (`:419`) | `sSpellStore` | `sSpellsByCategoryStore[Category] → set<(bool,spellId)>` |
| Skill-race-class (`:423`) | `sSkillRaceClassInfoStore`, `sSkillLineStore` | `SkillRaceClassInfoBySkill` multimap |
| Pet-family spells (`:431`) | `sSkillLineAbilityStore`, `sSpellStore`, `sCreatureFamilyStore` | `sPetFamilySpellsStore[family] → set<spellId>` |
| Spell difficulty wiring (`:462`) | `sSpellDifficultyStore`, `sSpellStore` | `sSpellMgr->SetSpellDifficultyId(spellId, difficultyId)` per row |
| Talent maps (`:490`) | `sTalentStore`, `sTalentTabStore` | `sTalentSpellPosMap`, `sPetTalentSpells`, `sTalentTabPages[class][3]` |
| Taxi sets (`:528`–`:611`) | `sTaxiPathStore`, `sTaxiPathNodeStore`, `sTaxiNodesStore`, `sSpellStore` | `sTaxiPathSetBySource`, `sTaxiPathNodesByPath`, `sTaxiNodesMask`, faction/DK masks |
| Transport animations (`:614`) | `sTransportAnimationStore`, `sTransportRotationStore` | `sTransportMgr` per-path tables |
| WMO area lookup (`:620`) | `sWMOAreaTableStore` | `sWMOAreaInfoByTripple[(root, adt, group)]` |

Because the post-load pass runs **after every `LOAD_DBC`**, the order of the macro calls is irrelevant for correctness as long as both inputs of any post-load pass succeeded — but if e.g. `Talent.dbc` is missing, the `sTalentSpellPosMap` build at `:498` simply iterates an empty store, then later code that expects the map will silently misbehave. The bad-files-list check at `:624` is the safety net.

## Flow / data shape

Startup sequence around DBC loading:

```
worldserver main()
  └─ World::SetInitialWorldSettings()           (World.cpp:~140)
       ├─ ConfigMgr load                       (early)
       ├─ DB pool init
       ├─ ScriptMgr → OnLoadCustomDatabaseTable (custom hook, World.cpp:375)
       ├─ LoadDBCStores(_dataPath)             (World.cpp:379)   ◄── this file
       │    ├─ dbcPath = dataPath + "dbc/"
       │    ├─ for each LOAD_DBC(store, "Foo.dbc", "foo_dbc"):
       │    │    ├─ assert sizeof(T) matches fmt
       │    │    ├─ storage.Load(...)                   → DBCStorageBase::Load → DBCFileLoader
       │    │    ├─ for each locale: LoadStringsFrom(...)
       │    │    └─ if dbTable: storage.LoadFromDB(...) → DBCDatabaseLoader  (06-db-overrides.md)
       │    ├─ post-load correlation passes
       │    ├─ bad-file gate (exit 1 on failure)
       │    └─ client-version sentinel (exit 1 on stale DBC)
       ├─ DetectDBCLang()                      (World.cpp:380)
       ├─ LoadM2Cameras(_dataPath)             (World.cpp:383)
       ├─ ObjectMgr → load templates from DB   (uses sItemStore etc.)
       └─ SpellMgr::LoadSpellInfoStore         (SpellMgr.cpp:2903 — wraps every sSpellStore row in a SpellInfo)
```

Three log lines bracket the work:
- `LOG_INFO("server.loading", "Initialize Data Stores...");` (`World.cpp:378`)
- `LOG_INFO("server.loading", ">> Initialized X Data Stores in Y ms", DBCFileCount, …);` (`DBCStores.cpp:652`)
- `LOG_INFO("server.loading", " ");` (blank-line separator)

The whole load is on the main startup thread; expect ~hundreds of milliseconds on warm cache, longer on cold cache (single-threaded `fread` per file).

## Hooks & extension points

- **Script hook fires before DBC load.** `sScriptMgr->OnLoadCustomDatabaseTable()` runs at `World.cpp:375`, immediately *before* `LoadDBCStores`. Modules that want to inject rows into a `*_dbc` SQL override table at startup do it here so the rows are present when `LoadFromDB` runs (see [`06-db-overrides.md`](./06-db-overrides.md)).
- **Adding a new DBC.**
  1. Drop binary into `data/dbc/` (see this fork's `share/dbc/` install location, plus the source-of-truth in `share-public/dbc/`).
  2. Add struct in `DBCStructure.h`, fmt in `DBCfmt.h`.
  3. Declare `extern DBCStorage<T> sFooStore;` in `DBCStores.h`, define in `DBCStores.cpp`.
  4. Add a `LOAD_DBC(sFooStore, "Foo.dbc", "foo_dbc")` line at the alphabetically-correct slot.
  5. (Optional override) create `data/sql/base/db_world/foo_dbc.sql` with the matching column layout (`DBCDatabaseLoader.cpp:118` asserts column count == fmt length).
- **Sentinel update.** When the WoW client patches an item / spell ID at the upper end, the sentinel block at `DBCStores.cpp:640-650` may need a refreshed reference ID, or the server will refuse to start with the new client.

## Cross-references

- Engine-side: [`01-loader.md`](./01-loader.md), [`02-stores.md`](./02-stores.md), [`03-format-strings.md`](./03-format-strings.md), [`06-db-overrides.md`](./06-db-overrides.md), [`../world/02-config-mgr.md`](../world/02-config-mgr.md) (where `DataDir` is read), [`../spells/00-index.md`](../spells/00-index.md)
- Project-side: [`../../03-spell-system.md#dbc-system`](../../03-spell-system.md), [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md)
- Fork-specific: `azerothcore-wotlk/CLAUDE.md` (custom Spell.dbc → uses the same loader path; rows added in source via `share-public/python_scripts/copy_spells_dbc.py`)
- External: `wiki/common-errors` (`#ace00043`, `#ace00046` are DBC-loading errors), Doxygen `DBCStores_8cpp.html`
