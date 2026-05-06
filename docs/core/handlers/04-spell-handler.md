# handlers — Spell handler

> Cast / cancel / aura-cancel / channel-cancel / self-res / spell-click / use-item / open-item / GO-use / mirror-image / projectile updates. The actual cast lifecycle (prepare → check → cast → hit → effect → finish) is documented in [`../spells/01-cast-lifecycle.md`](../spells/01-cast-lifecycle.md). Talent learn / wipe lives in `SkillHandler.cpp`, pet-cast in `PetHandler.cpp`, totems split between this file and `PetHandler.cpp`.

## Critical files

| File | Role |
|---|---|
| `src/server/game/Handlers/SpellHandler.cpp:35` | `WorldSession::HandleClientCastFlags` (parses `m_cast_flags` extras: missile, dest loc, etc.) |
| `src/server/game/Handlers/SpellHandler.cpp:58` | `WorldSession::HandleUseItemOpcode` (right-click on item) |
| `src/server/game/Handlers/SpellHandler.cpp:204` | `WorldSession::HandleOpenItemOpcode` (lockboxes, scrolls, gift wrap) |
| `src/server/game/Handlers/SpellHandler.cpp:287` | `WorldSession::HandleOpenWrappedItemCallback` |
| `src/server/game/Handlers/SpellHandler.cpp:327` | `WorldSession::HandleGameObjectUseOpcode` |
| `src/server/game/Handlers/SpellHandler.cpp:348` | `WorldSession::HandleGameobjectReportUse` |
| `src/server/game/Handlers/SpellHandler.cpp:376` | `WorldSession::HandleCastSpellOpcode` (entry — see Flow) |
| `src/server/game/Handlers/SpellHandler.cpp:552` | `WorldSession::HandleCancelCastOpcode` |
| `src/server/game/Handlers/SpellHandler.cpp:566` | `WorldSession::HandleCancelAuraOpcode` |
| `src/server/game/Handlers/SpellHandler.cpp:602` | `WorldSession::HandlePetCancelAuraOpcode` |
| `src/server/game/Handlers/SpellHandler.cpp:640` | `WorldSession::HandleCancelGrowthAuraOpcode` (no-op stub) |
| `src/server/game/Handlers/SpellHandler.cpp:644` | `WorldSession::HandleCancelAutoRepeatSpellOpcode` |
| `src/server/game/Handlers/SpellHandler.cpp:651` | `WorldSession::HandleCancelChanneling` |
| `src/server/game/Handlers/SpellHandler.cpp:684` | `WorldSession::HandleTotemDestroyed` |
| `src/server/game/Handlers/SpellHandler.cpp:705` | `WorldSession::HandleSelfResOpcode` |
| `src/server/game/Handlers/SpellHandler.cpp:721` | `WorldSession::HandleSpellClick` |
| `src/server/game/Handlers/SpellHandler.cpp:739` | `WorldSession::HandleMirrorImageDataRequest` |
| `src/server/game/Handlers/SpellHandler.cpp:832` | `WorldSession::HandleUpdateProjectilePosition` |

Talent / glyph training (delegated):

| File | Role |
|---|---|
| `src/server/game/Handlers/SkillHandler.cpp:25` | `WorldSession::HandleLearnTalentOpcode` (`CMSG_LEARN_TALENT 0x251`) |
| `src/server/game/Handlers/SkillHandler.cpp:34` | `WorldSession::HandleLearnPreviewTalents` (`CMSG_LEARN_PREVIEW_TALENTS 0x4C1`) |
| `src/server/game/Handlers/SkillHandler.cpp:58` | `WorldSession::HandleTalentWipeConfirmOpcode` (`MSG_TALENT_WIPE_CONFIRM 0x2AA`) |

Glyph removal: `HandleRemoveGlyph` lives in `CharacterHandler.cpp:1580` (see [`01-character-handler.md`](./01-character-handler.md)).

## Opcodes covered

All `STATUS_LOGGEDIN`. Cast/cancel are `THREADSAFE` (run in `Map::Update`); aura cancellation, item use and most others are `INPLACE`. Source: `Opcodes.cpp:302`–`1349`.

| Opcode | Handler | Purpose |
|---|---|---|
| `CMSG_CAST_SPELL` (`0x12E`) | `HandleCastSpellOpcode` | Begin a player-cast. |
| `CMSG_CANCEL_CAST` (`0x12F`) | `HandleCancelCastOpcode` | Cancel a non-melee cast. |
| `CMSG_CANCEL_AURA` (`0x136`) | `HandleCancelAuraOpcode` | Right-click off a buff. |
| `CMSG_PET_CANCEL_AURA` (`0x26B`) | `HandlePetCancelAuraOpcode` | Right-click off a pet aura. |
| `CMSG_CANCEL_AUTO_REPEAT_SPELL` (`0x26D`) | `HandleCancelAutoRepeatSpellOpcode` | Stop auto-shot. |
| `CMSG_CANCEL_GROWTH_AURA` (`0x29B`) | `HandleCancelGrowthAuraOpcode` | Stub — never cancels growth auras (intentional). |
| `CMSG_CANCEL_CHANNELLING` (`0x13B`) | `HandleCancelChanneling` | Cancel the current channeled spell. |
| `CMSG_USE_ITEM` (`0x0AB`) | `HandleUseItemOpcode` | Use a usable item — may trigger spell, fires `OnItemUse`. |
| `CMSG_OPEN_ITEM` (`0x0AC`) | `HandleOpenItemOpcode` | Open lockbox / scroll / gift; fires `OnPlayerBeforeOpenItem`. |
| `CMSG_GAMEOBJ_USE` (`0x0B1`) | `HandleGameObjectUseOpcode` | Right-click on a `GameObject`. |
| `CMSG_GAMEOBJ_REPORT_USE` (`0x481`) | `HandleGameobjectReportUse` | Achievement-only "I used this" report. |
| `CMSG_TOTEM_DESTROYED` (`0x414`) | `HandleTotemDestroyed` | Right-click off a totem. |
| `CMSG_SELF_RES` (`0x2B3`) | `HandleSelfResOpcode` | Use self-resurrection (Reincarnation, soulstone). |
| `CMSG_SPELLCLICK` (`0x3F8`) | `HandleSpellClick` | Click a unit-spellclick (vehicle entry, NPC interaction). |
| `CMSG_GET_MIRRORIMAGE_DATA` (`0x401`) | `HandleMirrorImageDataRequest` | Mage Mirror Image — request appearance data. |
| `CMSG_UPDATE_PROJECTILE_POSITION` (`0x4BE`) | `HandleUpdateProjectilePosition` | Mid-flight position update for projectile spells. |
| `CMSG_LEARN_TALENT` (`0x251`) | `HandleLearnTalentOpcode` (`SkillHandler.cpp`) | Spend a talent point. |
| `CMSG_LEARN_PREVIEW_TALENTS` (`0x4C1`) | `HandleLearnPreviewTalents` | Apply previewed-talent batch. |
| `MSG_TALENT_WIPE_CONFIRM` (`0x2AA`) | `HandleTalentWipeConfirmOpcode` | Confirm respec at trainer. |

For the canonical list with hex values: [`../network/03-opcodes.md`](../network/03-opcodes.md).

## Key concepts

- **`SpellCastTargets`**: parsed off the wire by `targets.Read(recvPacket, mover)` (`:441`). Holds unit / GO / item / corpse / src loc / dest loc and the target-flag mask.
- **Cast queueing**: `_player->SpellQueue` allows the client to queue a follow-up spell while the GCD or current cast is still resolving — `HandleCastSpellOpcode` calls `CanExecutePendingSpellCastRequest` / `CanRequestSpellCast` to decide queue vs immediate (`:424`–`:436`). The pending packet is copied into the queue.
- **Mover indirection**: `Unit* mover = _player->m_mover;` (`:392`). Casting from a vehicle / mind-controlled creature uses the seat-flag table to decide whether the player's spellbook or the mover's is consulted (`:479`).
- **Spell-rank auto-pick**: when a positive spell is cast on a friendly target, `SpellInfo::GetAuraRankForLevel(target->GetLevel())` (`:537`) downgrades to the appropriate rank (so high-rank Power Word: Fortitude doesn't waste mana on a level-10 alt).
- **Cast-flag passes**: `HandleClientCastFlags` (`:35`) is invoked from `HandleCastSpellOpcode` and `HandleUseItemOpcode` to extract the optional movement-info / target-string / dest-loc payload that some spells append.
- **Open-wrapped-item callback**: `HandleOpenWrappedItemCallback` (`:287`) is the async DB callback that resolves the original item template after a wrapped-item open — wrap state is stored in `character_gifts`.

## Flow / data shape

`HandleCastSpellOpcode` → `Spell::prepare` chain (this handler is the *entry*; the heavy lifting is in `Spell.cpp` — see [`../spells/01-cast-lifecycle.md`](../spells/01-cast-lifecycle.md)):

```
client CMSG_CAST_SPELL
        │  (castCount, spellId, castFlags, packed targets)
        ▼
HandleCastSpellOpcode  (SpellHandler.cpp:376)
        │  sSpellMgr->GetSpellInfo
        │  SpellQueue check ─► defer if needed
        │  targets.Read(recvPacket, mover)
        │  HandleClientCastFlags
        │  spellbook check (player vs vehicle vs creature)
        │  sScriptMgr->ValidateSpellAtCastSpell           (override spellId)
        │  GetAuraRankForLevel                             (downscale)
        ▼
new Spell(mover, spellInfo, TRIGGERED_NONE, …)
        │  sScriptMgr->ValidateSpellAtCastSpellResult
        ▼
spell->prepare(&targets)        ─► continues in Spell.cpp
```

Item use:

```
client CMSG_USE_ITEM ─► HandleUseItemOpcode (:58)
        │  sScriptMgr->OnItemUse  (veto)
        │  Player::CastItemUseSpell
        │  ItemTemplate::Spells[] iterated
        ▼
new Spell(...) for each on-use spell
```

## Hooks & extension points

- `sScriptMgr->OnItemUse` (`:197`) — veto item use entirely.
- `sScriptMgr->OnPlayerBeforeOpenItem` (`:271`) — gate `HandleOpenItemOpcode`.
- `sScriptMgr->ValidateSpellAtCastSpell` (`:505`) — last-chance to rewrite the spell id (used to redirect e.g. paragon-modded spell variants).
- `sScriptMgr->ValidateSpellAtCastSpellResult` (`:546`) — fired after `Spell` is constructed but before `prepare()`.
- `sScriptMgr->OnGlobalMirrorImageDisplayItem` (`:802`).

For broader spell-event surface (`OnPlayerSpellCast`, proc hooks, `SpellScript`/`AuraScript`), see [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md) and [`../../03-spell-system.md`](../../03-spell-system.md).

## Cross-references

- Engine-side: [`../spells/01-cast-lifecycle.md`](../spells/01-cast-lifecycle.md) (Spell::prepare onward), [`../spells/02-spell-info.md`](../spells/02-spell-info.md), [`../spells/03-aura-system.md`](../spells/03-aura-system.md), [`../spells/05-effects.md`](../spells/05-effects.md), [`../spells/08-script-bindings.md`](../spells/08-script-bindings.md), [`../entities/07-item.md`](../entities/07-item.md) (`CastItemUseSpell`), [`../entities/06-gameobject.md`](../entities/06-gameobject.md), [`../entities/08-pet-vehicle.md`](../entities/08-pet-vehicle.md) (`CMSG_SPELLCLICK` vehicle entry).
- Project-side: [`../../03-spell-system.md`](../../03-spell-system.md), [`../../custom-spells/`](../../custom-spells/00-overview.md) for SpellScript authoring, [`../../05-modules.md`](../../05-modules.md) (which modules use these hooks).
- External: Doxygen `classWorldSession` (`HandleCastSpellOpcode`), `classSpell`.
