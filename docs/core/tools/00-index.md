# tools/ — Build-time / extraction tools

> Standalone executables under `src/tools/` that prepare runtime data (MMaps navmeshes, VMaps collision, map tiles, DBC dumps). Run once after upgrading the WoW client; their output lives outside the repo.

## Topic files

| File | Topic |
|---|---|
| [`01-mmaps-generator.md`](./01-mmaps-generator.md) | `mmaps_generator`, Detour navmesh build, multi-threading |
| [`02-vmaps-extractor.md`](./02-vmaps-extractor.md) | `vmap4_extractor` + `vmap4_assembler`, collision data |
| [`03-map-extractor.md`](./03-map-extractor.md) | `map_extractor`, terrain heightmap extraction from `.MPQ` |
| [`04-dbc-extractor.md`](./04-dbc-extractor.md) | `dbc_extractor`, dumps client `.dbc` files for the server |

## Critical files

| File | Role |
|---|---|
| `src/tools/mmaps_generator/*` | Navmesh tool |
| `src/tools/vmap4_extractor/*`, `vmap4_assembler/*` | Collision tools |
| `src/tools/map_extractor/*` | Heightmap tool |
| `src/tools/dbc_extractor/*` | DBC dumper |
| `apps/extractor/extractor.sh` | Convenience wrapper |

## Cross-references

- Engine-side: [`../maps/06-mmaps.md`](../maps/06-mmaps.md), [`../maps/07-vmaps.md`](../maps/07-vmaps.md), [`../dbc/`](../dbc/00-index.md)
- Project-side: [`../../10-dbc-inventory.md`](../../10-dbc-inventory.md) (the 246 DBC files this fork ships) and `share-public/python_scripts/` (DBC patching tools — for runtime DBC mods, not extraction)
- External: `wiki/installation` (mentions where to put MMaps/VMaps output), Doxygen has limited coverage for the tools
