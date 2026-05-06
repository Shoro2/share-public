# entities — Item

> Run-time `Item` (no map presence; storage-position only) plus shared `ItemTemplate`, the bag specialisation, and the enchantment slot machinery (random properties, gems, prismatic, "bonus enchant" slot used by `mod-paragon-itemgen`). Cross-links: [`10-object-mgr.md`](./10-object-mgr.md), [`../../06-custom-ids.md`](../../06-custom-ids.md).

## Critical files

| File | Role |
|---|---|
| `src/server/game/Entities/Item/Item.h:38` | `enum InventorySlot` (key constants: `NULL_BAG=255`, `NULL_SLOT=255`, `INVENTORY_SLOT_BAG_0`) |
| `src/server/game/Entities/Item/Item.h:45` | `enum InventoryResult : uint8` (`EQUIP_ERR_OK`, `_INVENTORY_FULL`, `_BAG_FULL_*`, …) |
| `src/server/game/Entities/Item/Item.h:167` | `enum EnchantmentSlot : uint8` |
| `src/server/game/Entities/Item/Item.h:190` | `enum EnchantmentOffset` (`ID/DURATION/CHARGES`) |
| `src/server/game/Entities/Item/Item.h:207` | `enum ItemUpdateState { UNCHANGED, CHANGED, NEW, REMOVED }` |
| `src/server/game/Entities/Item/Item.h:219` | `class Item : public Object` (NOT `WorldObject` — items have no map position) |
| `src/server/game/Entities/Item/Container/Bag.h:27` | `class Bag : public Item` (carries up to `MAX_BAG_SIZE = 36` slots) |
| `src/server/game/Entities/Item/Container/Bag.h:67` | `inline Item* NewItemOrBag(ItemTemplate const*)` (factory) |
| `src/server/game/Entities/Item/ItemTemplate.h:25` | `enum ItemModType` (stat-mod IDs) |
| `src/server/game/Entities/Item/ItemTemplate.h:107` | `enum ItemFieldFlags : uint32` (`SOULBOUND`, `WRAPPED`, `BOP_TRADEABLE`, `READABLE`, `REFUNDABLE`) |
| `src/server/game/Entities/Item/ItemTemplate.h:145` | `enum ItemFlags / ItemFlags2 / ItemFlagsCustom` |
| `src/server/game/Entities/Item/ItemTemplate.h:254` | `enum InventoryType` |
| `src/server/game/Entities/Item/ItemTemplate.h:577-616` | `_Damage`, `_ItemStat`, `_Spell`, `_Socket` sub-structs |
| `src/server/game/Entities/Item/ItemTemplate.h:618` | `struct ItemTemplate` (mirrors `item_template`) |
| `src/server/game/Entities/Item/ItemEnchantmentMgr.h:18` | `ItemEnchantmentMgr` (random property / suffix rolls) |
| `src/server/game/Entities/Item/Item.cpp:282` | `Item::Create(LowType, itemId, owner)` |
| `src/server/game/Entities/Item/Item.cpp:336` | `Item::SaveToDB(CharacterDatabaseTransaction)` |
| `src/server/game/Entities/Item/Item.cpp:419` | `Item::LoadFromDB(LowType, ownerGuid, Field*, entry)` |
| `src/server/game/Entities/Item/Item.cpp:518/526` | `Item::DeleteFromDB(...)` (static + member) |
| `src/server/game/Entities/Item/Item.cpp:920` | `Item::SetEnchantment(slot, id, duration, charges, caster)` |
| `src/server/game/Entities/Item/Item.cpp:1087` | `Item::CreateItem(itemId, count, player, clone, randomPropertyId)` (static factory) |
| `src/server/game/Globals/ObjectMgr.cpp:3234` | `ObjectMgr::LoadItemTemplates()` |
| `src/server/game/Globals/ObjectMgr.cpp:3884` | `ObjectMgr::LoadItemSetNames()` |

## Key concepts

- **Item is NOT a `WorldObject`.** It has GUID, update fields (64 slots = `ITEM_END = OBJECT_END(6) + 0x003A`), and per-`Player` storage position, but no map / cell / phase. Position is encoded as `pos = (bag << 8) | slot` and accessed via `Player::GetItemByPos` (see [`04-player.md`](./04-player.md)).
- **`Bag` is an Item subclass with extra slots** (`CONTAINER_END = ITEM_END(64) + 0x004A = 138`). Containers are themselves stored in a parent's slot — usually the player's `INVENTORY_SLOT_BAG_0` equipment row. Backpack = bag 0; equipped bags 1-4 plus bank bags 5-11.
- **`EnchantmentSlot`** (12 slots, `Item.h:167`):
  - `0 PERM_ENCHANTMENT_SLOT` — permanent (enchanting profession)
  - `1 TEMP_ENCHANTMENT_SLOT` — temporary (sharpening stones, poisons)
  - `2-4 SOCK_ENCHANTMENT_SLOT[…]` — three gem sockets
  - `5 BONUS_ENCHANTMENT_SLOT` — bonus enchant (used by `mod-paragon-itemgen` for the 5-slot bonus enchant system; see [`../../05-modules.md`](../../05-modules.md))
  - `6 PRISMATIC_ENCHANTMENT_SLOT` — extra prismatic socket added by belt-buckle / blacksmith socket
  - `7-11 PROP_ENCHANTMENT_SLOT_*` — fields driven by `RandomSuffix` / `RandomProperty`
  - Each enchantment slot is 3 update fields (`ID + DURATION + CHARGES`) starting at `ITEM_FIELD_ENCHANTMENT_1_1` — see `Item.h:304-306` getter trio.
- **Random properties** — `Item::SetItemRandomProperties(int32 randomPropId)` (`Item.h:297`) seeds the `PROP_ENCHANTMENT_SLOT_*` slots from `ItemRandomProperties.dbc` / `ItemRandomSuffix.dbc`. Suffix factor stored in `ITEM_FIELD_PROPERTY_SEED`. `ItemEnchantmentMgr` does the rolls.
- **Update queue** — `m_itemUpdateQueue` lives on the owning `Player`; `Item::AddToUpdateQueueOf(Player*)` flips `uState = ITEM_CHANGED` and registers for the next save batch. Items in the queue persist their state through `Player::SaveToDB`'s inventory pass. `IsInUpdateQueue()` = `uQueuePos != -1`.
- **Soulbound trade** — three-day trade window after looting BoP, mediated by `ITEM_FIELD_FLAG_BOP_TRADEABLE`. `SetSoulboundTradeable(allowedLooters)` and `CheckSoulboundTradeExpire` at `Item.h:355-358`.
- **Refund system** — `ITEM_FIELD_FLAG_REFUNDABLE`, `m_refundRecipient`, `m_paidMoney`, `m_paidExtendedCost`. Re-fund window data is split off into `item_refund_instance` (delete via `DeleteRefundDataFromDB`).
- **`ItemTemplate::ScriptId`** — set per-template; resolves to an `ItemScript` (`ScriptMgr::OnItemUse`, `OnItemExpire`, `OnItemRemove`, `OnGossipHello`, `OnGossipSelect`).
- **Custom item entries this fork** — see [`../../06-custom-ids.md`](../../06-custom-ids.md), notably the always-rolled itemgen enchant carrier `920920`.

## Flow / data shape

### Item creation (loot, vendor, mail, spell-effect-create-item)

```
Player::StoreNewItem(pos, itemId, update, randomPropertyId)
  └─ Item::CreateItem(itemId, count, player, clone, randomPropertyId)   // Item.cpp:1087
       └─ NewItemOrBag(proto)                                            // Bag.h:67
            └─ Item::Create(newGuid, itemId, owner)                      // Item.cpp:282
                 ├─ _Create(guid, itemId, HighGuid::Item)
                 ├─ SetUInt32Value(ITEM_FIELD_STACK_COUNT, count)
                 ├─ if randomPropertyId != 0: SetItemRandomProperties(...)
                 └─ initialize duration / charges / spell-charges
  └─ Player::StoreItem(pos, item, update)
       ├─ assign m_container / m_slot
       ├─ SetState(ITEM_NEW)
       └─ if equip pos: ApplyEquipCooldown / VisualizeItem / ApplyItemMods
```

### Save (per-Player tick or on logout)

```
Player::SaveToDB(...)  // PlayerStorage.cpp:7119
  └─ _SaveInventory(trans)
       └─ for each item in m_itemUpdateQueue:
           switch (item->GetState()):
             ITEM_NEW    → CHAR_REP_INVENTORY_ITEM + Item::SaveToDB(trans)
             ITEM_CHANGED → CHAR_UPD_INVENTORY_ITEM + Item::SaveToDB(trans)
             ITEM_REMOVED → CHAR_DEL_INVENTORY_ITEM + Item::DeleteFromDB(trans)
       └─ FSetState(ITEM_UNCHANGED) on all updated items
```

The actual SQL is via `CHAR_*_ITEM_INSTANCE` / `CHAR_*_INVENTORY_ITEM` prepared statements; see `CharacterDatabase.cpp` and [`../database/02-prepared-statements.md`](../database/02-prepared-statements.md).

### Enchantment write

```
Item::SetEnchantment(slot, id, duration, charges, caster)        // Item.cpp:920
  ├─ base = ITEM_FIELD_ENCHANTMENT_1_1 + slot * MAX_ENCHANTMENT_OFFSET
  ├─ SetUInt32Value(base + ENCHANTMENT_ID_OFFSET, id)
  ├─ SetUInt32Value(base + ENCHANTMENT_DURATION_OFFSET, duration)
  ├─ SetUInt32Value(base + ENCHANTMENT_CHARGES_OFFSET, charges)
  └─ SetState(ITEM_CHANGED, owner)   // queues for save + dirty-flag update fields
```

The `BONUS_ENCHANTMENT_SLOT` (`5`) is the integration point for `mod-paragon-itemgen`: see [`../../05-modules.md`](../../05-modules.md).

## Hooks & extension points

- `ItemScript`: `OnUse`, `OnQuestAccept`, `OnExpire`, `OnRemove`, `CanItemRoll`, `CanItemNeed`, `CanSendAuctionHelloOpcode`, `OnGossipHello / OnGossipSelect / OnGossipSelectCode`. Bind via `ItemTemplate::ScriptId` (column `ScriptName` on `item_template`).
- Module-private state on a single item lives in `Object::CustomData` (`Object.h:231`) — Itemgen attaches its rolled-stat array here.
- DB-side overrides: `item_template` is the row source; `item_template_addon` for vendor count caps and refund/disenchant LFG rules; `item_template_locale` for translations; `item_loot_template` for chest-equivalent on-open loot. Custom enchantments register via `spellitemenchantment_dbc` (see [`../03-spell-system.md`](../../03-spell-system.md)).

## Cross-references

- Engine-side: [`04-player.md`](./04-player.md) (storage / equip / bank logic), [`../handlers/03-item-handler.md`](../handlers/03-item-handler.md) (`SwapItem`, `AutoEquip`, `BuyItem`), [`10-object-mgr.md`](./10-object-mgr.md) (template loaders), [`../loot/00-index.md`](../loot/00-index.md), [`03-update-fields.md`](./03-update-fields.md) (`ITEM_END`/`CONTAINER_END` arithmetic)
- Project-side: [`../../05-modules.md`](../../05-modules.md) (`mod-paragon-itemgen` uses `BONUS_ENCHANTMENT_SLOT`; `mod-loot-filter` and `mod-endless-storage` operate on inventory hooks), [`../../06-custom-ids.md`](../../06-custom-ids.md) (custom item id 920920 is the always-rolled enchant carrier), [`../../09-db-tables.md`](../../09-db-tables.md) (`item_template`, `item_instance`, `character_inventory`, `item_template_addon`, `item_template_locale`, `item_set_names`, `item_enchantment_template`, `item_loot_template`, `item_refund_instance`)
- External: Doxygen `classItem`, `classBag`, `structItemTemplate`
