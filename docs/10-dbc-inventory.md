# 10 — DBC file inventory

The `dbc/` folder contains all 246 DBC files of the WoW 3.3.5a client in WDBC binary format. They define the client-side game mechanics and are loaded into matching stores (`sSpellStore` etc.) by the server at start.

> For DBC loading mechanics, override paths through DB tables (`*_dbc`) and patching, see [03-spell-system.md](./03-spell-system.md).

---

## Spell-related (22 files)

| File | Server store | Contents |
|-------|-------------|--------|
| `Spell.dbc` | `sSpellStore` | all spell definitions (234 fields, 936 bytes/record) |
| `SpellCastTimes.dbc` | `sSpellCastTimesStore` | cast times (base, per level, minimum) |
| `SpellCategory.dbc` | `sSpellCategoryStore` | spell categories (cooldown groups) |
| `SpellChainEffects.dbc` | — | visual chain effects |
| `SpellDescriptionVariables.dbc` | — | tooltip variables |
| `SpellDifficulty.dbc` | `sSpellDifficultyStore` | spell variants by dungeon difficulty |
| `SpellDispelType.dbc` | — | dispel types (Magic, Curse, Disease, Poison) |
| `SpellDuration.dbc` | `sSpellDurationStore` | spell duration (Duration, PerLevel, Max) |
| `SpellEffectCameraShakes.dbc` | — | camera shake on spell effects |
| `SpellFocusObject.dbc` | `sSpellFocusObjectStore` | required objects to cast |
| `SpellIcon.dbc` | `sSpellIconStore` | spell icon paths |
| `SpellItemEnchantment.dbc` | `sSpellItemEnchantmentStore` | **item enchantment definitions** (38 fields, custom patching via `patch_dbc.py`) |
| `SpellItemEnchantmentCondition.dbc` | `sSpellItemEnchantmentConditionStore` | enchantment conditions |
| `SpellMechanic.dbc` | — | spell mechanics (stun, root, silence, etc.) |
| `SpellMissile.dbc` | — | projectile parameters |
| `SpellMissileMotion.dbc` | — | projectile motion patterns |
| `SpellRadius.dbc` | `sSpellRadiusStore` | AoE radii (Radius, PerLevel, Max) |
| `SpellRange.dbc` | `sSpellRangeStore` | spell ranges (Min, Max, Display) |
| `SpellRuneCost.dbc` | `sSpellRuneCostStore` | DK rune costs (Blood, Frost, Unholy, RunicPower) |
| `SpellShapeshiftForm.dbc` | `sSpellShapeshiftFormStore` | shapeshift forms (Druid, etc.) |
| `SpellVisual.dbc` | — | visual spell representation |
| `SpellVisualEffectName.dbc` | — | effect names |
| `SpellVisualKit.dbc` | — | visual kit assemblies |
| `SpellVisualKitAreaModel.dbc` | — | area-based visual models |
| `SpellVisualKitModelAttach.dbc` | — | model attachment points |
| `SpellVisualPrecastTransitions.dbc` | — | precast transition effects |

## Character/player (10 files)

| File | Contents |
|-------|--------|
| `ChrClasses.dbc` | class definitions (name, DisplayPower, flags) |
| `ChrRaces.dbc` | race definitions (name, faction, models) |
| `CharBaseInfo.dbc` | base character info |
| `CharHairGeosets.dbc` | hairstyle geometry |
| `CharHairTextures.dbc` | hairstyle textures |
| `CharSections.dbc` | character sections (skin, face, etc.) |
| `CharStartOutfit.dbc` | starting equipment per class/race |
| `CharTitles.dbc` | available titles |
| `CharVariations.dbc` | character variations |
| `CharacterFacialHairStyles.dbc` | beard styles |

## Item/loot (16 files)

| File | Contents |
|-------|--------|
| `Item.dbc` | item base data (class, subclass, DisplayInfo, InventoryType) |
| `ItemBagFamily.dbc` | bag families (Ammo, Soul, Herb, etc.) |
| `ItemClass.dbc` | item classes (weapon, armor, consumable, etc.) |
| `ItemCondExtCosts.dbc` | extended cost conditions |
| `ItemDisplayInfo.dbc` | visual item display |
| `ItemExtendedCost.dbc` | extended costs (honor, arena, token) |
| `ItemGroupSounds.dbc` | item group sounds |
| `ItemLimitCategory.dbc` | item limit categories (gems, etc.) |
| `ItemPetFood.dbc` | pet food types |
| `ItemPurchaseGroup.dbc` | purchase groups |
| `ItemRandomProperties.dbc` | "of the Bear" random properties |
| `ItemRandomSuffix.dbc` | random suffix enchantments |
| `ItemSet.dbc` | set definitions (items, set bonuses) |
| `ItemSubClass.dbc` | item subclasses |
| `ItemSubClassMask.dbc` | subclass masks |
| `ItemVisualEffects.dbc` / `ItemVisuals.dbc` | visual effects |

## Map/area/world (16 files)

| File | Contents |
|-------|--------|
| `Map.dbc` | map definitions (66 fields, name, type, instance) |
| `MapDifficulty.dbc` | difficulty levels per map |
| `AreaTable.dbc` | area definitions (name, flags, level) |
| `AreaGroup.dbc` | area groups |
| `AreaPOI.dbc` | points of interest |
| `AreaTrigger.dbc` | trigger zones (position, radius) |
| `WorldMapArea.dbc` | world map areas |
| `WorldMapContinent.dbc` | world map continents |
| `WorldMapOverlay.dbc` | world map overlays |
| `WorldMapTransforms.dbc` | world map transformations |
| `WorldSafeLocs.dbc` | safe locations (graveyards, etc.) |
| `WorldStateUI.dbc` | world state UI |
| `WorldStateZoneSounds.dbc` | zone sounds by state |
| `WorldChunkSounds.dbc` | chunk-based sounds |
| `DungeonMap.dbc` / `DungeonMapChunk.dbc` | dungeon maps |
| `DungeonEncounter.dbc` | dungeon encounter definitions |

## Talent/skill (7 files)

| File | Contents |
|-------|--------|
| `Talent.dbc` | talent definitions (TabID, tier, column, SpellRank_1-9) |
| `TalentTab.dbc` | talent tabs (name, ClassMask, background) |
| `SkillLine.dbc` | skill definitions (name, category) |
| `SkillLineAbility.dbc` | skill abilities (spell ↔ skill mapping) |
| `SkillLineCategory.dbc` | skill categories |
| `SkillRaceClassInfo.dbc` | race/class skill info |
| `SkillTiers.dbc` / `SkillCostsData.dbc` | skill tiers and costs |

## Combat formulas (gt*.dbc, 12 files)

| File | Contents |
|-------|--------|
| `gtBarberShopCostBase.dbc` | barber costs per level |
| `gtChanceToMeleeCrit.dbc` | melee crit chance per level/class |
| `gtChanceToMeleeCritBase.dbc` | base melee crit |
| `gtChanceToSpellCrit.dbc` | spell crit chance per level/class |
| `gtChanceToSpellCritBase.dbc` | base spell crit |
| `gtCombatRatings.dbc` | combat rating conversions |
| `gtNPCManaCostScaler.dbc` | NPC mana cost scaling |
| `gtOCTClassCombatRatingScalar.dbc` | class combat rating scalars |
| `gtOCTRegenHP.dbc` | HP regeneration |
| `gtOCTRegenMP.dbc` | MP regeneration |
| `gtRegenHPPerSpt.dbc` | HP regen per Spirit |
| `gtRegenMPPerSpt.dbc` | MP regen per Spirit |

## Faction (3 files)

`Faction.dbc`, `FactionGroup.dbc`, `FactionTemplate.dbc`

## Transport/vehicle (7 files)

`Vehicle.dbc`, `VehicleSeat.dbc`, `VehicleUIIndSeat.dbc`, `VehicleUIIndicator.dbc`, `TransportAnimation.dbc`, `TransportPhysics.dbc`, `TransportRotation.dbc`

## Travel (4 files)

`TaxiNodes.dbc`, `TaxiPath.dbc`, `TaxiPathNode.dbc`, `PvpDifficulty.dbc`

## Audio (12 files)

`SoundEntries.dbc`, `SoundEntriesAdvanced.dbc`, `SoundEmitters.dbc`, `SoundAmbience.dbc`, `SoundFilter.dbc`, `SoundFilterElem.dbc`, `SoundProviderPreferences.dbc`, `SoundSamplePreferences.dbc`, `SoundWaterType.dbc`, `ZoneMusic.dbc`, `ZoneIntroMusicTable.dbc`, `UISoundLookups.dbc`

## Emotes (4 files)

`Emotes.dbc`, `EmotesText.dbc`, `EmotesTextData.dbc`, `EmotesTextSound.dbc`

## Holidays/events (3 files)

`Holidays.dbc`, `HolidayDescriptions.dbc`, `HolidayNames.dbc`

## Other (remaining files)

`AnimationData.dbc`, `AttackAnimKits.dbc`, `AttackAnimTypes.dbc`, `AuctionHouse.dbc`, `BankBagSlotPrices.dbc`, `BannedAddOns.dbc`, `BarberShopStyle.dbc`, `BattlemasterList.dbc`, `CameraShakes.dbc`, `Cfg_Categories.dbc`, `Cfg_Configs.dbc`, `ChatChannels.dbc`, `ChatProfanity.dbc`, `CinematicCamera.dbc`, `CinematicSequences.dbc`, `CreatureDisplayInfo.dbc`, `CreatureDisplayInfoExtra.dbc`, `CreatureFamily.dbc`, `CreatureModelData.dbc`, `CreatureMovementInfo.dbc`, `CreatureSoundData.dbc`, `CreatureSpellData.dbc`, `CreatureType.dbc`, `CurrencyCategory.dbc`, `CurrencyTypes.dbc`, `DanceMoves.dbc`, `DeathThudLookups.dbc`, `DeclinedWord.dbc`, `DeclinedWordCases.dbc`, `DestructibleModelData.dbc`, `DurabilityCosts.dbc`, `DurabilityQuality.dbc`, `EnvironmentalDamage.dbc`, `Exhaustion.dbc`, `FileData.dbc`, `FootprintTextures.dbc`, `FootstepTerrainLookup.dbc`, `GameObjectArtKit.dbc`, `GameObjectDisplayInfo.dbc`, `GameTables.dbc`, `GameTips.dbc`, `GemProperties.dbc`, `GlyphProperties.dbc`, `GlyphSlot.dbc`, `GroundEffectDoodad.dbc`, `GroundEffectTexture.dbc`, `HelmetGeosetVisData.dbc`, `LFGDungeons.dbc`, `LFGDungeonExpansion.dbc`, `LFGDungeonGroup.dbc`, `LanguageWords.dbc`, `Languages.dbc`, `Light.dbc`, `LightFloatBand.dbc`, `LightIntBand.dbc`, `LightParams.dbc`, `LightSkybox.dbc`, `LiquidMaterial.dbc`, `LiquidType.dbc`, `LoadingScreens.dbc`, `LoadingScreenTaxiSplines.dbc`, `Lock.dbc`, `LockType.dbc`, `MailTemplate.dbc`, `Material.dbc`, `Movie.dbc`, `MovieFileData.dbc`, `MovieVariation.dbc`, `NPCSounds.dbc`, `NameGen.dbc`, `NamesProfanity.dbc`, `NamesReserved.dbc`, `ObjectEffect.dbc`, `ObjectEffectGroup.dbc`, `ObjectEffectModifier.dbc`, `ObjectEffectPackage.dbc`, `ObjectEffectPackageElem.dbc`, `OverrideSpellData.dbc`, `Package.dbc`, `PageTextMaterial.dbc`, `PaperDollItemFrame.dbc`, `ParticleColor.dbc`, `PetPersonality.dbc`, `PetitionType.dbc`, `PowerDisplay.dbc`, `QuestFactionReward.dbc`, `QuestInfo.dbc`, `QuestSort.dbc`, `QuestXP.dbc`, `RandPropPoints.dbc`, `Resistances.dbc`, `ScalingStatDistribution.dbc`, `ScalingStatValues.dbc`, `ScreenEffect.dbc`, `ServerMessages.dbc`, `SheatheSoundLookups.dbc`, `SpamMessages.dbc`, `StableSlotPrices.dbc`, `Startup_Strings.dbc`, `Stationery.dbc`, `StringLookups.dbc`, `SummonProperties.dbc`, `TeamContributionPoints.dbc`, `TerrainType.dbc`, `TerrainTypeSounds.dbc`, `TotemCategory.dbc`, `UnitBlood.dbc`, `UnitBloodLevels.dbc`, `VideoHardware.dbc`, `VocalUISounds.dbc`, `WMOAreaTable.dbc`, `WeaponImpactSounds.dbc`, `WeaponSwingSounds2.dbc`, `Weather.dbc`, `WowError_Strings.dbc`, `GMSurveyAnswers.dbc`, `GMSurveyCurrentSurvey.dbc`, `GMSurveyQuestions.dbc`, `GMSurveySurveys.dbc`, `GMTicketCategory.dbc`

## Non-DBC files in the dbc/ folder

| File | Contents |
|-------|--------|
| `Map.ini` | field-format reference for Map.dbc (66 fields, all ftInteger) |
| `component.wow-enUS.txt` | client component version |
