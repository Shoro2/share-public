# 09 — Database table inventory

Overview of all relevant tables across the three AzerothCore databases (`acore_auth`, `acore_world`, `acore_characters`). Custom tables from the modules are listed separately.

> **Full column reference**: `mysqldbextracts/mysql_column_list_all.txt` (304 tables, 4,129 columns). Format per line: `` `table`.`column` ``.

---

## Custom tables (project-specific)

### Characters DB

| Table | Module | Purpose |
|---------|-------|-------|
| `character_paragon` | mod-paragon | Account-wide Level/XP |
| `character_paragon_points` | mod-paragon | Per-character stat distribution (16 stats) |
| `character_paragon_role` | mod-paragon-itemgen | Role + main stat choice |
| `character_paragon_item` | mod-paragon-itemgen | Tracking of enchanted items |
| `character_paragon_spec` | mod-paragon-itemgen | Talent spec selection |
| `character_loot_filter` | mod-loot-filter | Filter rules per character |
| `character_loot_filter_settings` | mod-loot-filter | Master toggle + stats |
| `custom_endless_storage` | mod-endless-storage | Unlimited storage (character_id, item_entry, amount) |

### World DB

| Table | Module | Purpose |
|---------|-------|-------|
| `spell_script_names` | mod-custom-spells | SpellScript ↔ spell ID mapping |
| `spell_proc` | mod-custom-spells | Proc configuration |
| `spellitemenchantment_dbc` | mod-paragon-itemgen | DBC override for 11,323 custom enchantments |
| `paragon_passive_spell_pool` | mod-paragon-itemgen | Pool of available passive spells |
| `paragon_spec_spell_assign` | mod-paragon-itemgen | Spec → spell mappings (weighted) |

---

## AzerothCore tables by category

### Achievement system
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `achievement_category_dbc` | 20 | ID, Name_Lang_* (16 Locales) |
| `achievement_criteria_data` | 5 | criteria_id, ScriptName, type, value1, value2 |
| `achievement_criteria_dbc` | 31 | Achievement_Id, Asset_Id, Description_Lang_* |
| `achievement_dbc` | 62 | Category, Description_Lang_*, Flags, ID, Map |
| `achievement_reward` | 8 | ID, ItemID, MailTemplateID, Sender, Subject |
| `achievement_reward_locale` | 4 | ID, Locale, Subject, Text |

### Creature system
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `creature` | 27 | guid, id1-id3, map, position_x/y/z, spawntimesecs |
| `creature_addon` | 8 | guid, path_id, mount, bytes1, bytes2, emote, auras |
| `creature_template` | 57 | entry, name, minlevel, maxlevel, faction, npcflag, ScriptName, AIName, DamageModifier, HealthModifier |
| `creature_template_addon` | 8 | entry, bytes1, bytes2, emote, auras |
| `creature_template_model` | 6 | CreatureID, Idx, CreatureDisplayID, Probability |
| `creature_template_movement` | 8 | CreatureId, Ground, Flight, Chase |
| `creature_template_resistance` | 4 | CreatureID, School, Resistance |
| `creature_template_spell` | 4 | CreatureID, Index, Spell |
| `creature_template_locale` | 5 | entry, locale, Name, Title |
| `creature_classlevelstats` | 18 | level, class, basehp0-4, basemana, basearmor, attackpower, Agility |
| `creature_equip_template` | 6 | CreatureID, ID, ItemID1-3 |
| `creature_text` | 13 | CreatureID, GroupID, ID, Text, Type, BroadcastTextId |
| `creature_loot_template` | 10 | Entry, Item, Chance, GroupId, MinCount, MaxCount |
| `creature_onkill_reputation` | 10 | creature_id, RewOnKillRepFaction1/2, RewOnKillRepValue1/2 |
| `creature_formations` | 7 | leaderGUID, memberGUID, dist, angle, groupAI |
| `creature_summon_groups` | 11 | entry, groupId, position_x/y/z |
| `creaturedisplayinfo_dbc` | 16 | ID, ModelID, CreatureModelScale, BloodID |
| `creaturefamily_dbc` | 28 | ID, Name_Lang_*, CategoryEnumID |
| `creaturemodeldata_dbc` | 28 | ID, ModelName, CollisionWidth/Height |
| `creaturespelldata_dbc` | 9 | ID, Spells_1-4, Availability_1-4 |
| `creaturetype_dbc` | 19 | ID, Name_Lang_*, Flags |

### Item system
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `item_template` | 138 | entry, class, subclass, name, Quality, ItemLevel, RequiredLevel, stat_type1-10, stat_value1-10, dmg_min1/2, dmg_max1/2, armor, spellid_1-5, socketColor_1-3, ScriptName |
| `item_template_locale` | 5 | ID, locale, Name, Description |
| `item_dbc` | 8 | ID, ClassID, SubclassID, DisplayInfoID, InventoryType |
| `item_enchantment_template` | 3 | entry, ench, chance |
| `item_set_names` | 4 | entry, name, InventoryType |
| `itemdisplayinfo_dbc` | 25 | ID, ModelName, Flags, GeosetGroup |
| `itemextendedcost_dbc` | 16 | ID, HonorPoints, ArenaPoints, ItemID_1-5, ItemCount_1-5 |
| `itemrandomproperties_dbc` | 24 | ID, Name_Lang_*, Enchantment_1-5 |
| `itemrandomsuffix_dbc` | 29 | ID, Name_Lang_*, Enchantment_1-5, AllocationPct_1-5 |
| `itemset_dbc` | 53 | ID, Name_Lang_*, ItemID_1-17, SetSpellID_1-8 |

### Spell system
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `spell_dbc` | 234 | ID, Attributes, AttributesEx-Ex7, SpellName_Lang_*, Effects, Targets, CastingTimeIndex, DurationIndex, RangeIndex, SpellFamilyName, SpellFamilyFlags |
| `spell_script_names` | 2 | spell_id, ScriptName |
| `spell_proc` | 16 | SpellId, ProcFlags, SpellTypeMask, Chance, Cooldown, Charges |
| `spell_area` | 10 | spell, area, quest_start/end, aura_spell, gender |
| `spell_bonus_data` | 6 | entry, direct_bonus, dot_bonus, ap_bonus, comments |
| `spell_custom_attr` | 2 | spell_id, attributes |
| `spell_enchant_proc_data` | 5 | entry, customChance, PPMChance, procEx |
| `spell_group` | 2 | id, spell_id |
| `spell_group_stack_rules` | 3 | group_id, stack_rule, description |
| `spell_linked_spell` | 4 | spell_trigger, spell_effect, type, comment |
| `spell_loot_template` | 10 | Entry, Item, Chance, GroupId |
| `spell_ranks` | 3 | first_spell_id, spell_id, rank |
| `spell_required` | 2 | spell_id, req_spell |
| `spell_target_position` | 8 | ID, EffectIndex, MapID, PositionX/Y/Z |
| `spell_threat` | 4 | entry, flatMod, pctMod, apPctMod |
| `spellcasttimes_dbc` | 4 | ID, Base, PerLevel, Minimum |
| `spellcategory_dbc` | 2 | ID, Flags |
| `spelldifficulty_dbc` | 5 | ID, DifficultySpellID_1-4 |
| `spellduration_dbc` | 4 | ID, Duration, DurationPerLevel, MaxDuration |
| `spellitemenchantment_dbc` | 38 | ID, Charges, Effect_1-3, EffectPointsMin_1-3, EffectPointsMax_1-3, EffectArg_1-3, Name_Lang_*, Condition_Id, Flags |
| `spellradius_dbc` | 4 | ID, Radius, RadiusPerLevel, RadiusMax |
| `spellrange_dbc` | 40 | ID, RangeMin/Max, DisplayName_Lang_* |
| `spellrunecost_dbc` | 5 | ID, Blood, Frost, Unholy, RunicPower |

### Quest system
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `quest_template` | 105 | ID, QuestType, Flags, RewardChoiceItemID1-6, RewardItemId1-4, RewardMoney, RewardXPDifficulty |
| `quest_template_addon` | 18 | ID, MaxLevel, AllowableClasses, ExclusiveGroup, BreadcrumbForQuestId |
| `quest_template_locale` | 12 | ID, locale, Title, Details, Objectives |
| `quest_details` | 10 | ID, Emote1-4, EmoteDelay1-4 |
| `quest_offer_reward` | 11 | ID, Emote1-4, RewardText |
| `quest_request_items` | 5 | ID, EmoteOnComplete, EmoteOnIncomplete, CompletionText |
| `quest_poi` | 9 | id, ObjectiveIndex, MapID, Floor, Flags |
| `questxp_dbc` | 11 | ID, Difficulty_1-10 |
| `questsort_dbc` | 18 | ID, SortName_Lang_* |

### NPC & Gossip
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `npc_text` | 90 | ID, BroadcastTextID0-7, text0_0/text0_1 ... text7_0/text7_1 |
| `npc_vendor` | 7 | entry, item, maxcount, incrtime, ExtendedCost |
| `npc_trainer` | 7 | ID, SpellID, MoneyCost, ReqSkillLine, ReqSkillRank, ReqLevel |
| `npc_spellclick_spells` | 4 | npc_entry, spell_id, cast_flags, user_type |
| `gossip_menu` | 2 | MenuID, TextID |
| `gossip_menu_option` | 14 | MenuID, OptionID, OptionIcon, OptionText, ActionMenuID |

### GameObject system
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `gameobject` | 21 | guid, id, map, position_x/y/z |
| `gameobject_template` | 35 | entry, type, displayId, name, Data0-23, AIName, ScriptName |
| `gameobject_loot_template` | 10 | Entry, Item, Chance, GroupId |

### Map & area
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `map_dbc` | 66 | ID, Directory, InstanceType, MapName_Lang_*, MapType |
| `mapdifficulty_dbc` | 23 | ID, MapID, Difficulty, MaxPlayers |
| `areatable_dbc` | 36 | ID, ContinentID, AreaName_Lang_*, Flags, AreaBit |
| `worldmaparea_dbc` | 11 | ID, MapID, AreaID, AreaName |

### Character & classes
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `chrclasses_dbc` | 60 | ID, Name_Lang_*, DisplayPower, Flags |
| `chrraces_dbc` | 69 | ID, Name_Lang_*, ClientFilestring, Alliance, BaseLanguage |
| `chartitles_dbc` | 37 | ID, Name1_Lang_*, Mask_ID |
| `charstartoutfit_dbc` | 77 | ClassID, RaceID, SexID, ItemID_1-24 |
| `playercreateinfo` | 8 | race, class, map, position_x/y/z |
| `player_class_stats` | 9 | Class, Level, BaseHP, BaseMana, Strength, Agility, Stamina, Intellect, Spirit |
| `player_race_stats` | 6 | Race, Strength, Agility, Stamina, Intellect, Spirit |
| `player_xp_for_level` | 2 | Level, Experience |

### Talent system
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `talent_dbc` | 23 | ID, TabID, TierID, ColumnIndex, SpellRank_1-9 |
| `talenttab_dbc` | 24 | ID, Name_Lang_*, ClassMask, BackgroundFile |
| `skillline_dbc` | 56 | ID, CategoryID, SkillCostsID, Name_Lang_* |
| `skilllineability_dbc` | 14 | ID, SkillLine, Spell, MinSkillLineRank, ClassMask |

### Loot system
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `creature_loot_template` | 10 | Entry, Item, Reference, Chance, QuestRequired, MinCount, MaxCount, GroupId |
| `gameobject_loot_template` | 10 | (same structure) |
| `item_loot_template` | 10 | (same structure) |
| `fishing_loot_template` | 10 | (same structure) |
| `skinning_loot_template` | 10 | (same structure) |
| `pickpocketing_loot_template` | 10 | (same structure) |
| `milling_loot_template` | 10 | (same structure) |
| `prospecting_loot_template` | 10 | (same structure) |
| `disenchant_loot_template` | 10 | (same structure) |
| `reference_loot_template` | 10 | (same structure) |
| `mail_loot_template` | 10 | (same structure) |
| `spell_loot_template` | 10 | (same structure) |

### Smart AI (SAI)
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `smart_scripts` | 31 | entryorguid, source_type, id, link, event_type, event_phase_mask, event_param1-6, action_type, action_param1-6, target_type, target_param1-4, comment |
| `conditions` | 15 | SourceTypeOrReferenceId, ConditionTypeOrReference, ConditionValue1-3, Comment |

### Vehicle system
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `vehicle_dbc` | 40 | ID, Flags, CameraFade*, CameraPitchOffset, CameraYawOffset |
| `vehicleseat_dbc` | 58 | ID, Flags, AttachmentID, AttachmentOffset* |
| `vehicle_accessory` | 7 | guid, accessory_entry, seat_id |
| `vehicle_template_accessory` | 7 | entry, accessory_entry, seat_id |

### Combat & stats
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `gtchancetomeleecrit_dbc` | 2 | ID, Data |
| `gtchancetomeleecritbase_dbc` | 2 | ID, Data |
| `gtchancetospellcrit_dbc` | 2 | ID, Data |
| `gtchancetospellcritbase_dbc` | 2 | ID, Data |
| `gtcombatratings_dbc` | 2 | ID, Data |
| `gtregenhpperspt_dbc` | 2 | ID, Data |
| `gtregenmpperspt_dbc` | 2 | ID, Data |
| `scalingstatdistribution_dbc` | 22 | ID, StatID_1-10, Bonus_1-10 |
| `scalingstatvalues_dbc` | 24 | ID, Charlevel, various Armor/DPS values |
| `randproppoints_dbc` | 16 | ID, Epic_1-5, Superior_1-5, Good_1-5 |

### Factions
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `faction_dbc` | 57 | ID, ReputationIndex, ReputationRaceMask, Name_Lang_*, Description_Lang_* |
| `factiontemplate_dbc` | 14 | ID, Faction, Flags, FriendGroup, EnemyGroup, Enemies_1-4, Friend_1-4 |

### Other important tables
| Table | Columns | Important fields |
|---------|---------|-----------------|
| `battleground_template` | 13 | ID, MinPlayersPerTeam, MaxPlayersPerTeam, Comment |
| `battlemasterlist_dbc` | 32 | ID, MapID_1-8, InstanceType |
| `game_event` | 10 | eventEntry, start_time, end_time, description |
| `game_tele` | 7 | id, name, map, position_x/y/z |
| `game_graveyard` | 6 | ID, Map, x, y, z, Comment |
| `instance_template` | 4 | map, parent, script, allowMount |
| `dungeonencounter_dbc` | 23 | ID, MapID, Difficulty, Name_Lang_* |
| `gemproperties_dbc` | 5 | ID, Enchant_Id, Type |
| `glyphproperties_dbc` | 4 | ID, SpellID, GlyphSlotFlags |
| `broadcast_text` | 14 | ID, MaleText, FemaleText, EmoteID1-3 |
| `warden_checks` | 8 | id, type, data, address, length |
| `disables` | 6 | sourceType, entry, flags, comment |
| `updates` | 5 | name, hash, state, timestamp, speed |
