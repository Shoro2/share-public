# scripting — Static vs. dynamic linkage of scripts and modules

> Two CMake cache variables, `-DSCRIPTS=` and `-DMODULES=`, decide whether the in-tree `src/server/scripts/*` content and the `modules/*` content compile *into* `worldserver` or as separate shared libraries loaded at startup. Both default to `static` (also the project's recommended setting). For module discovery see [`05-module-discovery.md`](./05-module-discovery.md); for the loader callback wiring see [`01-script-mgr.md`](./01-script-mgr.md).

## Critical files

| File | Role |
|---|---|
| `conf/dist/config.cmake:14` | `set(SCRIPTS_AVAILABLE_OPTIONS none static dynamic minimal-static minimal-dynamic)` |
| `conf/dist/config.cmake:15` | `set(MODULES_AVAILABLE_OPTIONS none static dynamic)` |
| `conf/dist/config.cmake:19` | `set(SCRIPTS "static" CACHE STRING "Build core with scripts")` |
| `conf/dist/config.cmake:20` | `set(MODULES "static" CACHE STRING "Build core with modules")` |
| `conf/dist/config.cmake:29-45` | error if value not in `SCRIPTS_AVAILABLE_OPTIONS` / `MODULES_AVAILABLE_OPTIONS` |
| `conf/dist/config.cmake:65-79` | per-module / per-script cache variables (`SCRIPTS_<NAME>=default`, `MODULE_<NAME>=default`) |
| `conf/dist/config.cmake:105` | `option(WITH_DYNAMIC_LINKING "Enable dynamic library linking." 0)` |
| `conf/dist/config.cmake:113-118` | `IsDynamicLinkingRequired` / `IsDynamicLinkingModulesRequired` force `WITH_DYNAMIC_LINKING_FORCED` if any script/module is dynamic |
| `conf/dist/config.cmake:120-124` | sets `BUILD_SHARED_LIBS` based on the resolved dynamic-linking flag |
| `modules/CMakeLists.txt:23-29` | `MODULES_DEFAULT_LINKAGE = dynamic | static | disabled` based on `-DMODULES` |
| `modules/CMakeLists.txt:67-100` | per-module decision (default → take from `MODULES_DEFAULT_LINKAGE`); legacy-API modules forced to `static` (line 76) |
| `modules/CMakeLists.txt:184-256` | `disabled` → uninstall .so/.dll; `static` → append sources to umbrella `modules` library; `dynamic` → `add_library(... SHARED)`, link `acore-core-interface` private and `game` public |
| `modules/CMakeLists.txt:266` | umbrella static loader: `ConfigureScriptLoader("static" ... OFF ${STATIC_SCRIPT_MODULES})` |
| `modules/CMakeLists.txt:317-327` | install code that removes shared libs corresponding to disabled modules |
| `modules/ModulesLoader.cpp.in.cmake:21` | `#cmakedefine ACORE_IS_DYNAMIC_SCRIPTLOADER` — toggles `extern "C"` block |
| `modules/ModulesLoader.cpp.in.cmake:34-46` | dynamic-only: `extern "C" { GetScriptModule(); ... }` |
| `modules/ModulesLoader.cpp.in.cmake:49` | `AC_MODULES_API void AddModulesScripts()` — `AC_MODULES_API` resolves to `AC_API_EXPORT` (dynamic) or empty (static) |
| `modules/ModulesLoader.cpp.in.cmake:57` | `AC_MODULES_API char const* GetModulesBuildDirective()` (so the loader can verify ABI) |
| `src/server/scripts/ScriptLoader.cpp.in.cmake` | analogous template for the in-tree scripts (`AddScripts()`, `GetScriptModule()`, `GetScriptModuleRevisionHash()`) |
| `src/cmake/macros/ConfigureScripts.cmake:91-99` | `GetNativeSharedLibraryName` — `<name>.dll` / `lib<name>.dylib` / `lib<name>.so` |
| `src/cmake/macros/ConfigureScripts.cmake:101-108` | `GetInstallOffset` — Windows `<prefix>/scripts`, Unix `<prefix>/bin/scripts` |
| `src/server/apps/worldserver/Main.cpp:265` | `sScriptMgr->SetScriptLoader(AddScripts);` (statically-resolved symbol from in-tree `AddScripts`) |
| `src/server/apps/worldserver/Main.cpp:266` | `sScriptMgr->SetModulesLoader(AddModulesScripts);` (statically-resolved symbol from `modules/ModulesScriptLoader.h`) |
| `src/cmake/showoptions.cmake:48-55` | startup banner that prints the resolved `SCRIPTS` and `MODULES` linkage |

## Key concepts

- **`-DSCRIPTS`** controls `src/server/scripts/*` (the in-tree scripts: spell scripts, dungeon scripts, GM commands, world events). Allowed values: `none`, `static`, `dynamic`, `minimal-static`, `minimal-dynamic`.
- **`-DMODULES`** controls `modules/*` (custom modules in this fork). Allowed values: `none`, `static`, `dynamic`.
- **Per-module override** — `cmake .. -DSCRIPTS_EASTERNKINGDOMS=dynamic -DMODULE_MOD_PARAGON=disabled`. Each item gets its own `<NAME>=default` cache variable; `default` follows the global setting.
- **`static`** — sources compile into the main `worldserver` binary (or into a `libmodules` umbrella library that links to `worldserver`). Symbols are resolved at link time. **Recommended** because it gives the smallest startup time and the simplest debug experience.
- **`dynamic`** — each script module / each module gets its own `.so`/`.dylib`/`.dll`. The library is loaded by `worldserver` at startup, and three exported `extern "C"` symbols are looked up: `GetScriptModule()`, `GetModulesBuildDirective()`, `AddModulesScripts()`. The build directive must match the host binary or the load is rejected (ABI guard).
- **`none`** — no scripts/modules at all. Useful for an absolutely minimal `worldserver` (test/perf only).
- **`minimal-*`** (scripts only) — compile only the bare `src/server/scripts/Commands` set, skipping content (zone/dungeon scripts). Used by CI smoke builds.
- **Default to `static`** — the project's `mkdir build && cmake .. -DSCRIPTS=static -DMODULES=static && make` recipe (see [`../../02-architecture.md#build-commands`](../../02-architecture.md)). With `-Werror`, dynamic builds catch ABI mismatches at link time only — static is friendlier.
- **`MODULES_DEFAULT_LINKAGE`** — derived from `-DMODULES` at `modules/CMakeLists.txt:23`; written into per-module variables that are still `default`.

## Trade-offs

| Mode | Pros | Cons |
|---|---|---|
| `static` (default) | one binary, no `dlopen` ABI hazards, fastest startup, easiest to debug | rebuilding any script forces relinking `worldserver` |
| `dynamic` | per-module rebuild touches only the module library; module enable/disable at install time without recompiling core | three `extern "C"` symbols must match (`GetScriptModule`, build directive); load failures only at startup; slightly slower boot; cross-compiler ABI gotchas |
| `none` | smallest possible binary | no game content / no modules — only useful for sanity testing |
| `minimal-static` | fast CI build with `Commands` only | unplayable: no zone, dungeon or spell scripts |
| `minimal-dynamic` | as above + dynamic | rarely used |

Mixing is allowed: `cmake .. -DSCRIPTS=static -DMODULES=dynamic` is fine; the `_script_loader_callback` and `_modules_loader_callback` are independent (`ScriptMgr.h:131-146`).

## Dynamic-build internals

The generated `ModulesLoader.cpp` (template at `modules/ModulesLoader.cpp.in.cmake:34-63`) for a dynamic module looks like:

```cpp
#define ACORE_IS_DYNAMIC_SCRIPTLOADER       // injected by CMake
// forward declarations of every Add<modulename>Scripts() in this .so
void Addmod_foo_loader();
extern "C" {
    AC_MODULES_API char const* GetScriptModule()         { return "mod_foo"; }
    AC_MODULES_API void        AddModulesScripts()       { Addmod_fooScripts(); }
    AC_MODULES_API char const* GetModulesBuildDirective(){ return AC_BUILD_TYPE; }
}
```

The static umbrella version drops `extern "C"` and `AC_MODULES_API` resolves to nothing (line 45). `worldserver` then `dlopen`s the `.so`, looks up the three symbols, refuses to load on missing/mismatched directive, and registers the module's scripts via the discovered `AddModulesScripts`.

## Hooks & extension points

- Authors don't write the loader code — CMake generates it. Just provide `Add<modulename>Scripts()` somewhere in your module's `src/`.
- For modules that need to perform pre-`Initialize` setup (rare), see `modules/CMakeLists.txt:301-303` (per-module inline `<name>.cmake`).

## Cross-references

- Engine-side: [`01-script-mgr.md`](./01-script-mgr.md), [`05-module-discovery.md`](./05-module-discovery.md), [`../architecture/00-index.md`](../architecture/00-index.md), [`../server-apps/00-index.md`](../server-apps/00-index.md)
- Project-side: [`../../02-architecture.md#build-commands`](../../02-architecture.md)
- Fork-specific: `azerothcore-wotlk/functions.md` (build recipe and `DISABLED_AC_MODULES`)
- External: `wiki/installation`, `wiki/install-with-docker`, Doxygen for `AddScripts` / `AddModulesScripts`
