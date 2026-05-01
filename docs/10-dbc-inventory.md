# 10 — DBC-Datei-Inventar

Der Ordner `dbc/` enthält alle 246 DBC-Dateien des WoW 3.3.5a Clients im WDBC-Binärformat. Diese definieren die clientseitige Spielmechanik und werden vom Server beim Start in entsprechende Stores (`sSpellStore` etc.) geladen.

> Für DBC-Lade-Mechanik, Override-Pfade über DB-Tabellen (`*_dbc`) und Patching siehe [03-spell-system.md](./03-spell-system.md).

---

## Spell-bezogen (22 Dateien)

| Datei | Server-Store | Inhalt |
|-------|-------------|--------|
| `Spell.dbc` | `sSpellStore` | Alle Spell-Definitionen (234 Felder, 936 Bytes/Record) |
| `SpellCastTimes.dbc` | `sSpellCastTimesStore` | Cast-Zeiten (Base, PerLevel, Minimum) |
| `SpellCategory.dbc` | `sSpellCategoryStore` | Spell-Kategorien (Cooldown-Gruppen) |
| `SpellChainEffects.dbc` | — | Visuelle Ketten-Effekte |
| `SpellDescriptionVariables.dbc` | — | Tooltip-Variablen |
| `SpellDifficulty.dbc` | `sSpellDifficultyStore` | Spell-Varianten nach Dungeon-Schwierigkeit |
| `SpellDispelType.dbc` | — | Dispel-Typen (Magic, Curse, Disease, Poison) |
| `SpellDuration.dbc` | `sSpellDurationStore` | Spell-Dauer (Duration, PerLevel, Max) |
| `SpellEffectCameraShakes.dbc` | — | Kamera-Shake bei Spell-Effekten |
| `SpellFocusObject.dbc` | `sSpellFocusObjectStore` | Benötigte Objekte zum Casten |
| `SpellIcon.dbc` | `sSpellIconStore` | Spell-Icon-Pfade |
| `SpellItemEnchantment.dbc` | `sSpellItemEnchantmentStore` | **Item-Enchantment-Definitionen** (38 Felder, Custom-Patching via `patch_dbc.py`) |
| `SpellItemEnchantmentCondition.dbc` | `sSpellItemEnchantmentConditionStore` | Enchantment-Bedingungen |
| `SpellMechanic.dbc` | — | Spell-Mechaniken (Stun, Root, Silence, etc.) |
| `SpellMissile.dbc` | — | Geschoss-Parameter |
| `SpellMissileMotion.dbc` | — | Geschoss-Bewegungsmuster |
| `SpellRadius.dbc` | `sSpellRadiusStore` | AoE-Radien (Radius, PerLevel, Max) |
| `SpellRange.dbc` | `sSpellRangeStore` | Spell-Reichweiten (Min, Max, Display) |
| `SpellRuneCost.dbc` | `sSpellRuneCostStore` | DK-Runenkosten (Blood, Frost, Unholy, RunicPower) |
| `SpellShapeshiftForm.dbc` | `sSpellShapeshiftFormStore` | Shapeshift-Formen (Druid, etc.) |
| `SpellVisual.dbc` | — | Visuelle Spell-Darstellung |
| `SpellVisualEffectName.dbc` | — | Effekt-Namen |
| `SpellVisualKit.dbc` | — | Visuelle Kit-Zusammenstellungen |
| `SpellVisualKitAreaModel.dbc` | — | Area-basierte visuelle Modelle |
| `SpellVisualKitModelAttach.dbc` | — | Modell-Attachment-Punkte |
| `SpellVisualPrecastTransitions.dbc` | — | Precast-Übergangseffekte |

## Charakter/Spieler (10 Dateien)

| Datei | Inhalt |
|-------|--------|
| `ChrClasses.dbc` | Klassen-Definitionen (Name, DisplayPower, Flags) |
| `ChrRaces.dbc` | Rassen-Definitionen (Name, Faction, Models) |
| `CharBaseInfo.dbc` | Basis-Charakter-Info |
| `CharHairGeosets.dbc` | Frisuren-Geometrie |
| `CharHairTextures.dbc` | Frisuren-Texturen |
| `CharSections.dbc` | Charakter-Sektionen (Skin, Face, etc.) |
| `CharStartOutfit.dbc` | Start-Ausrüstung pro Klasse/Rasse |
| `CharTitles.dbc` | Verfügbare Titel |
| `CharVariations.dbc` | Charakter-Variationen |
| `CharacterFacialHairStyles.dbc` | Bart-Stile |

## Item/Loot (16 Dateien)

| Datei | Inhalt |
|-------|--------|
| `Item.dbc` | Item-Basisdaten (Class, Subclass, DisplayInfo, InventoryType) |
| `ItemBagFamily.dbc` | Taschen-Familien (Ammo, Soul, Herb, etc.) |
| `ItemClass.dbc` | Item-Klassen (Weapon, Armor, Consumable, etc.) |
| `ItemCondExtCosts.dbc` | Erweiterte Kosten-Bedingungen |
| `ItemDisplayInfo.dbc` | Visuelle Item-Darstellung |
| `ItemExtendedCost.dbc` | Erweiterte Kosten (Honor, Arena, Token) |
| `ItemGroupSounds.dbc` | Item-Gruppen-Sounds |
| `ItemLimitCategory.dbc` | Item-Limit-Kategorien (Gems, etc.) |
| `ItemPetFood.dbc` | Pet-Futter-Typen |
| `ItemPurchaseGroup.dbc` | Kauf-Gruppen |
| `ItemRandomProperties.dbc` | "of the Bear"-Zufallseigenschaften |
| `ItemRandomSuffix.dbc` | Zufalls-Suffix-Enchantments |
| `ItemSet.dbc` | Set-Definitionen (Items, Set-Boni) |
| `ItemSubClass.dbc` | Item-Unterklassen |
| `ItemSubClassMask.dbc` | Unterklassen-Masken |
| `ItemVisualEffects.dbc` / `ItemVisuals.dbc` | Visuelle Effekte |

## Map/Area/Welt (16 Dateien)

| Datei | Inhalt |
|-------|--------|
| `Map.dbc` | Map-Definitionen (66 Felder, Name, Type, Instance) |
| `MapDifficulty.dbc` | Schwierigkeitsgrade pro Map |
| `AreaTable.dbc` | Gebiets-Definitionen (Name, Flags, Level) |
| `AreaGroup.dbc` | Gebiets-Gruppen |
| `AreaPOI.dbc` | Points of Interest |
| `AreaTrigger.dbc` | Trigger-Zonen (Position, Radius) |
| `WorldMapArea.dbc` | Weltkarten-Gebiete |
| `WorldMapContinent.dbc` | Weltkarten-Kontinente |
| `WorldMapOverlay.dbc` | Weltkarten-Overlays |
| `WorldMapTransforms.dbc` | Weltkarten-Transformationen |
| `WorldSafeLocs.dbc` | Sichere Positionen (Friedhöfe, etc.) |
| `WorldStateUI.dbc` | Welt-Status-UI |
| `WorldStateZoneSounds.dbc` | Zonen-Sounds nach Status |
| `WorldChunkSounds.dbc` | Chunk-basierte Sounds |
| `DungeonMap.dbc` / `DungeonMapChunk.dbc` | Dungeon-Karten |
| `DungeonEncounter.dbc` | Dungeon-Encounter-Definitionen |

## Talent/Skill (7 Dateien)

| Datei | Inhalt |
|-------|--------|
| `Talent.dbc` | Talent-Definitionen (TabID, Tier, Column, SpellRank_1-9) |
| `TalentTab.dbc` | Talent-Tabs (Name, ClassMask, Background) |
| `SkillLine.dbc` | Skill-Definitionen (Name, Category) |
| `SkillLineAbility.dbc` | Skill-Fähigkeiten (Spell ↔ Skill Zuordnung) |
| `SkillLineCategory.dbc` | Skill-Kategorien |
| `SkillRaceClassInfo.dbc` | Rassen/Klassen-Skill-Info |
| `SkillTiers.dbc` / `SkillCostsData.dbc` | Skill-Stufen und Kosten |

## Kampf-Formeln (gt*.dbc, 12 Dateien)

| Datei | Inhalt |
|-------|--------|
| `gtBarberShopCostBase.dbc` | Friseur-Kosten pro Level |
| `gtChanceToMeleeCrit.dbc` | Melee-Crit-Chance pro Level/Klasse |
| `gtChanceToMeleeCritBase.dbc` | Basis-Melee-Crit |
| `gtChanceToSpellCrit.dbc` | Spell-Crit-Chance pro Level/Klasse |
| `gtChanceToSpellCritBase.dbc` | Basis-Spell-Crit |
| `gtCombatRatings.dbc` | Combat-Rating-Umrechnungen |
| `gtNPCManaCostScaler.dbc` | NPC-Manakosten-Skalierung |
| `gtOCTClassCombatRatingScalar.dbc` | Klassen-Combat-Rating-Skalare |
| `gtOCTRegenHP.dbc` | HP-Regeneration |
| `gtOCTRegenMP.dbc` | MP-Regeneration |
| `gtRegenHPPerSpt.dbc` | HP-Regen pro Spirit |
| `gtRegenMPPerSpt.dbc` | MP-Regen pro Spirit |

## Faction (3 Dateien)

`Faction.dbc`, `FactionGroup.dbc`, `FactionTemplate.dbc`

## Transport/Vehicle (7 Dateien)

`Vehicle.dbc`, `VehicleSeat.dbc`, `VehicleUIIndSeat.dbc`, `VehicleUIIndicator.dbc`, `TransportAnimation.dbc`, `TransportPhysics.dbc`, `TransportRotation.dbc`

## Travel (4 Dateien)

`TaxiNodes.dbc`, `TaxiPath.dbc`, `TaxiPathNode.dbc`, `PvpDifficulty.dbc`

## Audio (12 Dateien)

`SoundEntries.dbc`, `SoundEntriesAdvanced.dbc`, `SoundEmitters.dbc`, `SoundAmbience.dbc`, `SoundFilter.dbc`, `SoundFilterElem.dbc`, `SoundProviderPreferences.dbc`, `SoundSamplePreferences.dbc`, `SoundWaterType.dbc`, `ZoneMusic.dbc`, `ZoneIntroMusicTable.dbc`, `UISoundLookups.dbc`

## Emotes (4 Dateien)

`Emotes.dbc`, `EmotesText.dbc`, `EmotesTextData.dbc`, `EmotesTextSound.dbc`

## Holidays/Events (3 Dateien)

`Holidays.dbc`, `HolidayDescriptions.dbc`, `HolidayNames.dbc`

## Sonstige (restliche Dateien)

`AnimationData.dbc`, `AttackAnimKits.dbc`, `AttackAnimTypes.dbc`, `AuctionHouse.dbc`, `BankBagSlotPrices.dbc`, `BannedAddOns.dbc`, `BarberShopStyle.dbc`, `BattlemasterList.dbc`, `CameraShakes.dbc`, `Cfg_Categories.dbc`, `Cfg_Configs.dbc`, `ChatChannels.dbc`, `ChatProfanity.dbc`, `CinematicCamera.dbc`, `CinematicSequences.dbc`, `CreatureDisplayInfo.dbc`, `CreatureDisplayInfoExtra.dbc`, `CreatureFamily.dbc`, `CreatureModelData.dbc`, `CreatureMovementInfo.dbc`, `CreatureSoundData.dbc`, `CreatureSpellData.dbc`, `CreatureType.dbc`, `CurrencyCategory.dbc`, `CurrencyTypes.dbc`, `DanceMoves.dbc`, `DeathThudLookups.dbc`, `DeclinedWord.dbc`, `DeclinedWordCases.dbc`, `DestructibleModelData.dbc`, `DurabilityCosts.dbc`, `DurabilityQuality.dbc`, `EnvironmentalDamage.dbc`, `Exhaustion.dbc`, `FileData.dbc`, `FootprintTextures.dbc`, `FootstepTerrainLookup.dbc`, `GameObjectArtKit.dbc`, `GameObjectDisplayInfo.dbc`, `GameTables.dbc`, `GameTips.dbc`, `GemProperties.dbc`, `GlyphProperties.dbc`, `GlyphSlot.dbc`, `GroundEffectDoodad.dbc`, `GroundEffectTexture.dbc`, `HelmetGeosetVisData.dbc`, `LFGDungeons.dbc`, `LFGDungeonExpansion.dbc`, `LFGDungeonGroup.dbc`, `LanguageWords.dbc`, `Languages.dbc`, `Light.dbc`, `LightFloatBand.dbc`, `LightIntBand.dbc`, `LightParams.dbc`, `LightSkybox.dbc`, `LiquidMaterial.dbc`, `LiquidType.dbc`, `LoadingScreens.dbc`, `LoadingScreenTaxiSplines.dbc`, `Lock.dbc`, `LockType.dbc`, `MailTemplate.dbc`, `Material.dbc`, `Movie.dbc`, `MovieFileData.dbc`, `MovieVariation.dbc`, `NPCSounds.dbc`, `NameGen.dbc`, `NamesProfanity.dbc`, `NamesReserved.dbc`, `ObjectEffect.dbc`, `ObjectEffectGroup.dbc`, `ObjectEffectModifier.dbc`, `ObjectEffectPackage.dbc`, `ObjectEffectPackageElem.dbc`, `OverrideSpellData.dbc`, `Package.dbc`, `PageTextMaterial.dbc`, `PaperDollItemFrame.dbc`, `ParticleColor.dbc`, `PetPersonality.dbc`, `PetitionType.dbc`, `PowerDisplay.dbc`, `QuestFactionReward.dbc`, `QuestInfo.dbc`, `QuestSort.dbc`, `QuestXP.dbc`, `RandPropPoints.dbc`, `Resistances.dbc`, `ScalingStatDistribution.dbc`, `ScalingStatValues.dbc`, `ScreenEffect.dbc`, `ServerMessages.dbc`, `SheatheSoundLookups.dbc`, `SpamMessages.dbc`, `StableSlotPrices.dbc`, `Startup_Strings.dbc`, `Stationery.dbc`, `StringLookups.dbc`, `SummonProperties.dbc`, `TeamContributionPoints.dbc`, `TerrainType.dbc`, `TerrainTypeSounds.dbc`, `TotemCategory.dbc`, `UnitBlood.dbc`, `UnitBloodLevels.dbc`, `VideoHardware.dbc`, `VocalUISounds.dbc`, `WMOAreaTable.dbc`, `WeaponImpactSounds.dbc`, `WeaponSwingSounds2.dbc`, `Weather.dbc`, `WowError_Strings.dbc`, `GMSurveyAnswers.dbc`, `GMSurveyCurrentSurvey.dbc`, `GMSurveyQuestions.dbc`, `GMSurveySurveys.dbc`, `GMTicketCategory.dbc`

## Nicht-DBC-Dateien im dbc/ Ordner

| Datei | Inhalt |
|-------|--------|
| `Map.ini` | Feld-Format-Referenz für Map.dbc (66 Felder, alle ftInteger) |
| `component.wow-enUS.txt` | Client-Komponenten-Version |
