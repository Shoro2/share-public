# handlers — Item handler

> Equip / swap / split / destroy / wrap, vendor buy & sell, buyback, sockets (gem insert), refund, item queries, item-text, ammo. Looting opcodes live separately in `LootHandler.cpp` (cross-link [`../loot/`](../loot/00-index.md)); banking is in `BankHandler.cpp`; mail attachments in `MailHandler.cpp`.

## Critical files

| File | Role |
|---|---|
| `src/server/game/Handlers/ItemHandler.cpp:34` | `WorldSession::HandleSplitItemOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:62` | `WorldSession::HandleSwapInvItemOpcode` (within main backpack) |
| `src/server/game/Handlers/ItemHandler.cpp:100` | `WorldSession::HandleAutoEquipItemSlotOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:115` | `WorldSession::HandleSwapItem` (any-bag swap) |
| `src/server/game/Handlers/ItemHandler.cpp:153` | `WorldSession::HandleAutoEquipItemOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:280` | `WorldSession::HandleDestroyItemOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:389` | `WorldSession::HandleItemQuerySingleOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:548` | `WorldSession::HandleReadItem` |
| `src/server/game/Handlers/ItemHandler.cpp:578` | `WorldSession::HandleSellItemOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:748` | `WorldSession::HandleBuybackItem` |
| `src/server/game/Handlers/ItemHandler.cpp:798` | `WorldSession::HandleBuyItemInSlotOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:833` | `WorldSession::HandleBuyItemOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:844` | `WorldSession::HandleListInventoryOpcode` (vendor open) |
| `src/server/game/Handlers/ItemHandler.cpp:969` | `WorldSession::HandleAutoStoreBagItemOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:1016` | `WorldSession::HandleSetAmmoOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:1063` | `WorldSession::HandleItemNameQueryOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:1087` | `WorldSession::HandleWrapItemOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:1215` | `WorldSession::HandleSocketOpcode` (gem socket apply) |
| `src/server/game/Handlers/ItemHandler.cpp:1406` | `WorldSession::HandleCancelTempEnchantmentOpcode` |
| `src/server/game/Handlers/ItemHandler.cpp:1426` | `WorldSession::HandleItemRefundInfoRequest` |
| `src/server/game/Handlers/ItemHandler.cpp:1440` | `WorldSession::HandleItemRefund` |
| `src/server/game/Handlers/ItemHandler.cpp:1463` | `WorldSession::HandleItemTextQuery` |

## Opcodes covered

All `STATUS_LOGGEDIN`. `PROCESS_INPLACE` for inventory ops, `PROCESS_THREADSAFE` for queries and `WRAP_ITEM`. Source: `Opcodes.cpp:217`–`1335`.

### Inventory manipulation

| Opcode | Handler | Purpose |
|---|---|---|
| `CMSG_SWAP_ITEM` (`0x10C`) | `HandleSwapItem` | Swap items across two arbitrary bag/slot pairs. |
| `CMSG_SWAP_INV_ITEM` (`0x10D`) | `HandleSwapInvItemOpcode` | Swap two main-backpack slots. |
| `CMSG_SPLIT_ITEM` (`0x10E`) | `HandleSplitItemOpcode` | Split a stack into a destination slot. |
| `CMSG_AUTOEQUIP_ITEM` (`0x10A`) | `HandleAutoEquipItemOpcode` | Right-click / drag-to-paperdoll equip; finds destination slot. |
| `CMSG_AUTOEQUIP_ITEM_SLOT` (`0x10F`) | `HandleAutoEquipItemSlotOpcode` | Equip into a specific slot. |
| `CMSG_AUTOSTORE_BAG_ITEM` (`0x10B`) | `HandleAutoStoreBagItemOpcode` | Auto-store a bag (e.g. shift-click from vendor). |
| `CMSG_DESTROYITEM` (`0x111`) | `HandleDestroyItemOpcode` | Destroy a stack. |
| `CMSG_WRAP_ITEM` (`0x1D3`) | `HandleWrapItemOpcode` | Apply gift-wrapping (consumes wrapping paper). |
| `CMSG_SET_AMMO` (`0x268`) | `HandleSetAmmoOpcode` | Set the ranged ammo slot. |

### Vendor

| Opcode | Handler | Purpose |
|---|---|---|
| `CMSG_LIST_INVENTORY` (`0x19E`) | `HandleListInventoryOpcode` | Open vendor (`OnPlayerSendListInventory` hook). |
| `CMSG_BUY_ITEM` (`0x1A2`) | `HandleBuyItemOpcode` | Buy by item-id from vendor. |
| `CMSG_BUY_ITEM_IN_SLOT` (`0x1A3`) | `HandleBuyItemInSlotOpcode` | Buy and place in specific bag slot. |
| `CMSG_SELL_ITEM` (`0x1A0`) | `HandleSellItemOpcode` | Sell to vendor (`OnPlayerCanSellItem` hook). |
| `CMSG_BUYBACK_ITEM` (`0x290`) | `HandleBuybackItem` | Buy back from vendor's 12-slot buyback list. |

### Queries

| Opcode | Handler | Purpose |
|---|---|---|
| `CMSG_ITEM_QUERY_SINGLE` (`0x056`) | `HandleItemQuerySingleOpcode` | Build & send `SMSG_ITEM_QUERY_SINGLE_RESPONSE` for an item template. |
| `CMSG_ITEM_NAME_QUERY` (`0x2C4`) | `HandleItemNameQueryOpcode` | Lightweight name-only query. |
| `CMSG_READ_ITEM` (`0x0AD`) | `HandleReadItem` | Open readable item (book / parchment). |
| `CMSG_ITEM_TEXT_QUERY` (`0x243`) | `HandleItemTextQuery` | Resolve `mail_text` for an item. |

### Sockets, refund, enchantments

| Opcode | Handler | Purpose |
|---|---|---|
| `CMSG_SOCKET_GEMS` (`0x347`) | `HandleSocketOpcode` | Apply gems to an item's sockets; recomputes meta-gem activation, fires socket bonus. |
| `CMSG_CANCEL_TEMP_ENCHANTMENT` (`0x379`) | `HandleCancelTempEnchantmentOpcode` | Cancel a temporary weapon enchant (e.g. shaman imbue). |
| `CMSG_ITEM_REFUND_INFO` (`0x4B3`) | `HandleItemRefundInfoRequest` | Query "refund window" remaining (vendor-purchased items, badge gear). |
| `CMSG_ITEM_REFUND` (`0x4B4`) | `HandleItemRefund` | Execute the refund. |

For the canonical opcode list: [`../network/03-opcodes.md`](../network/03-opcodes.md).

## Key concepts

- **Position encoding**: client packs bag/slot as a `uint16` (`(bag << 8) | slot`). All swap/split helpers reconstruct this with `((bag << 8) | slot)` — see `:38`, `:119`. Slot `INVENTORY_SLOT_BAG_0 == 255` is "main backpack / equipped".
- **Validation pattern**: every inventory handler runs `_player->IsValidPos(...)` and bails with `SendEquipError(EQUIP_ERR_*, …)` on failure. The actual move is then delegated to `Player::SwapItem` / `Player::SplitItem` / `Player::CanEquipItem` / `Player::DestroyItem` (all in `Player.cpp` — see [`../entities/04-player.md`](../entities/04-player.md)).
- **Bank guard**: `CanUseBank()` is checked when source or destination crosses the bank slot range (`:82`, `:144`).
- **Vendor refund window**: managed by `Player`'s refundable-item set; `HandleItemRefund` undoes the purchase and returns currency / honour / arena points.
- **Sockets vs enchants**: gem application uses the enchantment system internally (sockets are `ENCHANTMENT_SLOT_SOCK_1..3`); meta gem requires that all colour requirements are satisfied for activation.

## Flow / data shape

Drag-and-drop equip:

```
client CMSG_AUTOEQUIP_ITEM  (src bag/slot)
        │
        ▼
HandleAutoEquipItemOpcode  (ItemHandler.cpp:153)
        │  GetItemByPos(src) → ItemTemplate
        │  FindEquipSlot → eslot
        │  CanEquipItem
        ▼
Player::SwapItem(src, dest)
        │  AutoUnequip into bag if dest occupied
        │  Apply ItemSetEffect / proc
        ▼
SMSG_INVENTORY_CHANGE_FAILURE / silent success
```

Vendor buy:

```
client CMSG_BUY_ITEM
        │
        ▼
HandleBuyItemOpcode  (:833) → Player::BuyItemFromVendorSlot
        │  cost / reputation / level / faction checks
        │  inventory free-slot check
        ▼
SMSG_BUY_ITEM      (or SMSG_BUY_FAILED)
```

## Hooks & extension points

- `sScriptMgr->OnPlayerCanSellItem` (`:604`) — `HandleSellItemOpcode`. Veto sale.
- `sScriptMgr->OnPlayerSendListInventory` (`:858`) — fires after vendor list is built. Used by mod-loot-filter, mod-itemgen variants.
- Item use & open are in [`04-spell-handler.md`](./04-spell-handler.md) (`HandleUseItemOpcode` → `OnItemUse`, `HandleOpenItemOpcode` → `OnPlayerBeforeOpenItem`).

`PlayerScript`/`ItemScript` definitions: `src/server/game/Scripting/ScriptDefines/PlayerScript.h`, `ItemScript.h`. See [`../scripting/02-hook-classes.md`](../scripting/02-hook-classes.md).

## Cross-references

- Engine-side: [`../entities/07-item.md`](../entities/07-item.md) (`Item` class, enchantment slots), [`../entities/04-player.md`](../entities/04-player.md) (`Player::SwapItem`, `BuyItemFromVendorSlot`), [`../network/05-worldsession.md`](../network/05-worldsession.md) (dispatch), [`../network/03-opcodes.md`](../network/03-opcodes.md). Looting: [`../loot/00-index.md`](../loot/00-index.md). Banking: `src/server/game/Handlers/BankHandler.cpp`. Mail: [`../social/03-mail.md`](../social/03-mail.md).
- Project-side: mod-loot-filter / mod-endless-storage rely on inventory hooks — see [`../../05-modules.md`](../../05-modules.md).
- External: Doxygen `classWorldSession` (look for `HandleSwapItem`, `HandleSocketOpcode`).
