# Custom Spells — Complex Spells & Querschnitts-Themen

Die meisten Custom-Spells sind triviale DBC-Modifier. Eine kleine Gruppe ist architektonisch heikel: rekursive Procs, exponentielle DoT-Spreads, Owner-Pet-Aura-Transfer, Custom-NPCs, OnRemove-Detection. Diese Datei sammelt die wiederkehrenden Pattern und listet pro Pattern auf, welche Spells es betreffen.

Vor Implementierung dieser Spells: hier durchgehen, dann zurück zum jeweiligen Spec-File für ID/Effekt-Details.

## Inhalt

- [Rekursionsschutz](#rekursionsschutz)
- [Target-Cap & exponentielle Propagation](#target-cap--exponentielle-propagation)
- [Empfohlene ICDs pro Pattern](#empfohlene-icds-pro-pattern)
- [Custom-NPCs (creature_template)](#custom-npcs-creature_template)
- [Owner→Pet Aura-Transfer / Pet-Scaling](#ownerpet-aura-transfer--pet-scaling)
- [OnRemove-Mode-Discrimination](#onremove-mode-discrimination)
- [Channel vs. Cast vs. Instant](#channel-vs-cast-vs-instant)
- [Client-DBC-Patches über Server-Override hinaus](#client-dbc-patches-über-server-override-hinaus)
- [Pet/UnitScript-Performance](#petunitscript-performance)
- [Aura-Stacks als State-Tracker](#aura-stacks-als-state-tracker)
- [Heiligenschein der "Besonders aufwändig"-Spells](#heiligenschein-der-besonders-aufwändig-spells)

## Rekursionsschutz

Procs können Procs auslösen. Wer das ignoriert, baut Endlosschleifen.

**Regeln:**

1. `PreventDefaultAction()` in `HandleProc()` aufrufen, sonst feuert sowohl der DBC-Default-Trigger als auch der Custom-Cast.
2. Helper-Spells per `CastSpell(target, ID, true)` triggern (`triggered=true`) — das setzt `SPELL_ATTR4_TRIGGERED`, der Helper kann nicht selbst die Quelle erneut procen.
3. Für explizit gewollte Ketten: `SPELL_ATTR3_CAN_PROC_FROM_PROCS` setzen — sonst ignorieren Triggered-Spells alle weiteren Procs.
4. Bei Auto-Attack-Procs (`PROC_FLAG_DONE_MELEE_AUTO_ATTACK`): `SPELL_AURA_ADD_EXTRA_ATTACKS` nutzen (engine-seitiger Schutz) statt manuell `CastSpell` mit Auto-Attack-ID.

**Betroffene Spells:**

| Spell | Datei | Risiko |
|-------|-------|--------|
| 901102 Extra Attack 25 % | [global](./specs/global.md) | wiederholt letzten Angriff — Extra-Attack darf nicht selbst proccen |
| 900304 DK → Death Coil Proc | [death-knight-blood](./specs/death-knight-blood.md) | Death Coil hat eigene Proc-Pipeline |
| 900274 Pala CS/Judge/DS → Exorcism Buff | [paladin-retribution](./specs/paladin-retribution.md) | Exorcism-Cast verbraucht Buff, sollte aber nicht erneut Buff geben |
| 900900 Disc Shield Explosion | [priest-discipline](./specs/priest-discipline.md) | Explosion-Cast darf nicht selbst Shield-Remove triggern |
| 901103 Global 10 % AoE Proc | [global](./specs/global.md) | Damage-Helper auf 10 Targets darf nicht 10 weitere AoE-Procs auslösen |
| 900800 / 900966 DoT → Shadow-AoE | [warlock-affliction](./specs/warlock-affliction.md), [priest-shadow](./specs/priest-shadow.md) | AoE-Damage darf nicht erneut DoT-Tick-Proc triggern |

## Target-Cap & exponentielle Propagation

Spells, die DoTs/Buffs auf neue Targets verbreiten, können exponentiell wachsen.

**Regeln:**

1. **Hard-Cap pro Cast** — nie mehr als N neue Targets pro Tick.
2. **Hard-Cap pro Player** — max. K aktive Spread-DoTs gleichzeitig (z. B. über Counter-Aura).
3. **"DoT NICHT haben"-Filter** — nur auf Targets ohne den Spread-DoT casten, sonst wird die Aura-Refresh-Schleife zur Infinity-Renewal.
4. **ICD auf der Source-Aura** (nicht nur am Target) — verhindert Spam bei vielen Tick-Quellen gleichzeitig.

**Betroffene Spells:**

| Spell | Datei | Worst-Case |
|-------|-------|-----------|
| 900802 Warlock DoT Spread | [warlock-affliction](./specs/warlock-affliction.md) | 1 → 3 → 9 → 27 Targets in 3 Ticks |
| 900967 Priest DoT Spread | [priest-shadow](./specs/priest-shadow.md) | identisch — Code shareable |
| 901103 Global AoE Proc | [global](./specs/global.md) | 10 Targets/Hit × viele Hits/sec |
| 900533 Hunter Auto Shot Bounce | [hunter-marksmanship](./specs/hunter-marksmanship.md) | 9 Targets pro Auto Shot, schnelle Auto-Frequenz |

**Empfohlene Caps:**

```cpp
// In HandleProc
static constexpr int MAX_SPREAD_PER_TICK = 2;
static constexpr int MAX_ACTIVE_SPREADS  = 8;
// Optional: Counter-Aura auf Caster, die pro Spread-Apply +1 Stack bekommt.
```

## Empfohlene ICDs pro Pattern

Proc-Patterns haben sich als Default-ICDs bewährt. `spell_proc.Cooldown` in ms.

| Pattern | Default-ICD | Quelle |
|---------|-------------|--------|
| DoT-Tick → AoE-Damage | 2000 ms | 900800, 900966 |
| AoE-Proc auf Hit | 1000 ms | 901103 |
| Block/Dodge → Counter | 1000 ms | 900172, 901104 |
| Periodic-Heal → Summon | 5000 ms | 901066 Treant |
| Auto-Attack → Summon | 5000 ms | 900436 Spirit Wolf |
| Crit-Streak Effekte | 0–500 ms | inhärent rate-limited |
| Kill-Proc | 0 ms | natürlich rate-limited |
| Low-HP-Trigger | 60000 ms | 900708 Mage Mana Shield |

ICD von 0 nur, wenn das Trigger-Event selbst rare ist (Kill, Death). Für alle Damage-/Heal-Patterns ist ein nicht-trivialer ICD Pflicht.

## Custom-NPCs (creature_template)

Mehrere Spells beschwören NPCs, die eigene Einträge in `creature_template` brauchen — plus eigene AI/Script bei nicht-trivialem Verhalten.

| NPC-ID | Name | Source-Spell | Script | Notes |
|--------|------|--------------|--------|-------|
| 900333 | Frost Wyrm | 900333 | `npc_custom_frost_wyrm` | DisplayID 26752 (Sindragosa), Scale 0.5, 2× Gargoyle HP, castet 900368 Frost Breath |
| 900436 | Spirit Wolf (Enh) | 900436 Auto-Wolf | (keine eigene AI) | DisplayID 27074, 15 s Duration |
| 901066 | Healing Treant | 901066 | (keine eigene AI) | 30 s Duration, attackiert Feinde oder folgt Player |
| TBD | Lesser Demons (Imp/VW/Succ/FH/FG) | 900835 | TBD | Pro Pet-Typ ein NPC-Eintrag, 50 % HP/Damage des Originals |

**Pflicht-Schritte für neuen Summon-NPC:**

1. Entry in `creature_template` (DisplayID, MinLevel/MaxLevel, Faction, KillCredit=0, ScriptName).
2. Falls AI: `creature_template_addon` mit `auras` (Combat-Auras) und ggf. `npc_<name>` C++-Klasse.
3. Pet-Type entscheidet ob `creature_template.unit_class` und Pet-Skills relevant sind.
4. Test mit `.npc spawn <id>` vor Hook-Integration.

## Owner→Pet Aura-Transfer / Pet-Scaling

Mehrere Spells erhöhen Pet-Damage oder geben Pet-Buffs, während die Aura auf dem Owner sitzt.

**Drei Varianten:**

1. **`UnitScript::OnDamage`-Filter** — die Aura ist Marker auf Owner, das UnitScript prüft `attacker.IsPet() && attacker.GetOwner()->HasAura(MARKER)` und multipliziert Damage. **Performance-Falle**: feuert für ALLE Damage-Events server-weit. Verwendung: 900502 (BM Pet +50 %), 900438 (Wolf CL Proc).
2. **`Pet::ApplyAllAuras`-Loop** — beim Pet-Summon werden Owner-Auras explizit auf das Pet gespiegelt. Sauberer, aber State-Drift bei Aura-Changes nach dem Summon.
3. **Spell-Modifier mit MaskA auf Pet-Spell-Family** — wenn der Pet-Spell SpellFamilyName != 0 hat, kann eine Aura auf Owner via `EffectSpellClassMaskA` direkt den Pet-Cast modifizieren. Beispiel 900836 (Imp Firebolt +50 %).

**Performance-Hinweis**: Variante 1 immer mit Early-Exit-Check (`if (!attacker || !attacker->IsCreature()) return;`) am Start des Scripts.

**Betroffene Spells:**

| Spell | Variante | Datei |
|-------|----------|-------|
| 900435 Shaman Summons +50 % | TBD (aktuell nur Marker) | [shaman-enhancement](./specs/shaman-enhancement.md) |
| 900502 BM Pet Damage +50 % | 1 | [hunter-beast-mastery](./specs/hunter-beast-mastery.md) |
| 900503 BM Pet Speed +50 % | PlayerScript-Tick | [hunter-beast-mastery](./specs/hunter-beast-mastery.md) |
| 900437 Spirit Wolves inherit Haste | bei Summon (3) | [shaman-enhancement](./specs/shaman-enhancement.md) |
| 900836 Imp Firebolt +50 % | 3 | [warlock-demonology](./specs/warlock-demonology.md) |
| 900839 Felguard +50 % | 2 | [warlock-demonology](./specs/warlock-demonology.md) |
| 901067 Druid Summons scale with Healing Power | PlayerScript-Tick | [druid-restoration](./specs/druid-restoration.md) |

## OnRemove-Mode-Discrimination

Auras können aus vielen Gründen entfernt werden — Expire, Dispel, Death, Cancel, Replace. Manche Spells sollen nur bei einem bestimmten Mode auslösen.

```cpp
void HandleRemove(AuraEffect const* aurEff, AuraEffectHandleModes mode)
{
    AuraRemoveMode removeMode = GetAura()->GetRemoveMode();
    if (removeMode == AURA_REMOVE_BY_EXPIRE      // Duration abgelaufen
     || removeMode == AURA_REMOVE_BY_ENEMY_SPELL // dispelled / broken
     || removeMode == AURA_REMOVE_BY_DEATH)       // Caster oder Target tot
    {
        // gewollte Cases
    }
    else if (removeMode == AURA_REMOVE_BY_CANCEL)
    {
        // Player hat Right-Click Cancel — oft NICHT gewollt
        return;
    }
}
```

**Betroffene Spells:**

| Spell | Use-Case | Datei |
|-------|----------|-------|
| 900900 Disc Shield Explosion | Explosion nur bei FADE oder ENEMY_BREAK, nicht bei Right-Click-Cancel | [priest-discipline](./specs/priest-discipline.md) |
| 901068 Druid Summon-Death-Heal | Heal nur wenn Summon stirbt, nicht bei Despawn-by-Owner-Logout | [druid-restoration](./specs/druid-restoration.md) |
| 900833 Demo Meta Duration Extend | nur bei Kill-Event während Aura aktiv — OnRemove ist hier irrelevant, aber Duration-Manipulation darf Aura nicht selbst entfernen | [warlock-demonology](./specs/warlock-demonology.md) |

## Channel vs. Cast vs. Instant

Drei Spell-Kategorien mit verschiedenen Hooks und unterschiedlichem Verhalten bei Movement/Interrupt.

| Kategorie | Beispiel | Hook | Movement-Check |
|-----------|----------|------|----------------|
| Channel | Evocation 12051, Mind Flay 48156 | `Spell::HandleChannelTick`, `Spell::ChannelInterrupt` | `SPELL_ATTR5_CAN_CHANNEL_WHEN_MOVING` |
| Cast (mit Cast-Time) | Frostbolt, Shadow Bolt | `Spell::CheckCast` → `SPELL_FAILED_MOVING` | nur Channel-Flag reicht NICHT |
| Instant | Mortal Strike, Whirlwind | kein Movement-Check | irrelevant |

**901100 Cast While Moving** muss alle drei Kategorien abdecken:

```cpp
// Hook auf Spell::CheckCast vor SPELL_FAILED_MOVING:
SpellCastResult check = origCheckCast(...);
if (check == SPELL_FAILED_MOVING
    && caster->ToPlayer()
    && caster->HasAura(901100))
    return SPELL_CAST_OK;  // bypass
```

Für Channels reicht das nicht — dort braucht es zusätzlich `SPELL_AURA_CAST_WHILE_WALKING` (Aura 330) auf der 901100-Aura. Detail: [global.md](./specs/global.md).

## Client-DBC-Patches über Server-Override hinaus

Server-`spell_dbc` reicht nicht für alle Fälle. Folgende Spells brauchen einen **Client-DBC-Patch** (`python_scripts/patch_dbc.py` in [share-public](https://github.com/Shoro2/share-public)):

| Spell | Was muss am Client gepatcht werden | Datei |
|-------|--------------------------------------|-------|
| Sichtbare Custom-Spells (Tooltip-Anzeige) | `Spell.dbc` Eintrag mit Name + Description | alle Spec-Files |
| 900205/900234/900268 Consecration around you | `Consecration` (48819): TargetA → `TARGET_DEST_CASTER` | [paladin-holy](./specs/paladin-holy.md) |
| 900270 Divine Storm +6 Targets | `Divine Storm` (53385): `MaxAffectedTargets` → 10 | [paladin-retribution](./specs/paladin-retribution.md) |
| 900709 Blink Target Location | `Blink` (1953): TargetType → `TARGET_DEST_DEST` (Ground-Target-Cursor) | [mage-arcane](./specs/mage-arcane.md) |
| 900737 Fire Blast off-GCD | `Fire Blast` (42873): `StartRecoveryCategory` = 0 | [mage-fire](./specs/mage-fire.md) |
| 900770 Water Elemental permanent | Summon Duration → -1 oder sehr hoch | [mage-frost](./specs/mage-frost.md) |

Server-spell_dbc reicht für Effekt-Logik, aber NICHT für Target-Selection-Cursor und auch nicht für GCD-Verhalten beim Client (der Client zeigt sonst falsche Cooldowns).

## Pet/UnitScript-Performance

UnitScripts hängen sich an global feuernde Events (`OnDamage`, `OnUnitDeath`, ...). Sie laufen für **alle** Units server-weit — schlampig geschriebene Filter können den Server merklich verlangsamen.

**Pflicht-Pattern am Anfang jedes UnitScripts:**

```cpp
void OnDamage(Unit* attacker, Unit* victim, uint32& damage, ...) override
{
    if (!attacker || !victim) return;
    if (!attacker->IsCreature()) return;        // sonst hooked auf Player-Damage
    Creature* c = attacker->ToCreature();
    if (!c->IsPet()) return;                    // nur Pets relevant
    Player* owner = c->GetOwner() ? c->GetOwner()->ToPlayer() : nullptr;
    if (!owner || !owner->HasAura(MARKER)) return;
    // ab hier echte Logik
}
```

**Betroffene Spells:**

| Spell | Hook | Datei |
|-------|------|-------|
| 900438 Wolf CL on Hit | `UnitScript::OnDamage` | [shaman-enhancement](./specs/shaman-enhancement.md) |
| 900502 / 900504 BM Pet Damage / Cleave | `UnitScript::OnDamage` | [hunter-beast-mastery](./specs/hunter-beast-mastery.md) |
| 901068 Druid Summon Death-Heal | `UnitScript::OnUnitDeath` | [druid-restoration](./specs/druid-restoration.md) |
| 901069 Druid Thorns → Rejuv | `UnitScript::OnDamage` (auf Victim=Player) | [druid-restoration](./specs/druid-restoration.md) |

## Aura-Stacks als State-Tracker

Manche Spells nutzen Aura-Stack-Counts als impliziten Charge-/State-Zähler statt eigener DB- oder Member-Variablen. Funktioniert, hat aber Edge Cases.

**Pattern (z. B. 900406 LvB Two-Charges):**

```cpp
// CumulativeAura = 2 in DBC
// AfterCast: Stack==1 → reset CD (free second cast); Stack==2 → normal CD, decrease stack
```

**Edge Cases:**

- Schnelles Casten kann zwischen Stack-Update und CD-Check eine Race haben.
- `RemoveAura`-Calls von außen (Dispel, Cancel) zerstören den State.
- Aura-Refresh resetet Duration aber nicht zwingend Stack — abhängig vom DBC-`StackAmount`-Wert und `OverrideOldestAura`-Flag.

Wenn der State über Logout/Login überleben muss: nicht Stacks, sondern eigene DB-Tabelle nutzen.

## Heiligenschein der "Besonders aufwändig"-Spells

Spells, die in den Spec-Files explizit als _besonders aufwändig_ oder _stark balance-relevant_ markiert sind, in einer Tabelle:

| Spell | Risiko-Hauptgrund | Datei |
|-------|-------------------|-------|
| 901100 Cast While Moving | für alle Caster gleichzeitig aktiv — Channel + Cast + Interruptible | [global](./specs/global.md) |
| 901102 Extra Attack 25 % | rekursive Procs | [global](./specs/global.md) |
| 901103 10 % AoE Proc | Spam bei DoT-Ticks | [global](./specs/global.md) |
| 900802 Warlock DoT Spread | exponentielle Propagation | [warlock-affliction](./specs/warlock-affliction.md) |
| 900835 Lesser Demons | Custom Creature-Templates pro Pet-Typ + AI | [warlock-demonology](./specs/warlock-demonology.md) |
| 900840 Sacrifice All Bonuses | mehrere Pet-Typ-Buffs gleichzeitig identifizieren und stacken | [warlock-demonology](./specs/warlock-demonology.md) |
| 900833 + 900834 Demo Meta-Combo | permanent transformierter AoE-Healer-Tank-Hybrid | [warlock-demonology](./specs/warlock-demonology.md) |
| 900900 Disc Shield Explosion | OnRemove-Detection + Damage-Skalierung am Absorb-Wert | [priest-discipline](./specs/priest-discipline.md) |
| 900933 Heal → Holy Fire AoE | Direct-Heal-vs-HoT-Filter | [priest-holy](./specs/priest-holy.md) |
| 900701 Mage Mana Regen Scaling | dynamische Berechnung pro Regen-Tick | [mage-arcane](./specs/mage-arcane.md) |
| 900709 Blink Target Location | Client-seitiger Ground-Target-Cursor | [mage-arcane](./specs/mage-arcane.md) |
| 900738 Pyro → Hot Streak Loop | guaranteed Instant-Pyro-Chain, balance-kritisch | [mage-fire](./specs/mage-fire.md) |
| 900771 Frost Comet Shower | komplett neuer Spell mit Custom-Visuals | [mage-frost](./specs/mage-frost.md) |
| 900534 Hunter Multi-Shot Barrage | 20 Multi-Shots in 2 s, Performance | [hunter-marksmanship](./specs/hunter-marksmanship.md) |
| 900300 / 900301 DK Triple DRW + Double-Cast | Aura-Stacking-Issues bei Triggered-Re-Cast | [death-knight-blood](./specs/death-knight-blood.md) |
| 900333 Frost Wyrm | Custom NPC + AI + skalierter Frost Breath | [death-knight-frost](./specs/death-knight-frost.md) |
| 900274 Pala Exorcism Buff | Stacking-Buff mit Konsum bei Exorcism-Cast | [paladin-retribution](./specs/paladin-retribution.md) |
| 900407 Sham LvB Instant via Clearcasting | Cast-Time-Modifier auf einen instant-machbaren Spell | [shaman-elemental](./specs/shaman-elemental.md) |
| 901071 Druid HoT 2x Ticks/Duration | Ticks vs. Duration Trade-off | [druid-restoration](./specs/druid-restoration.md) |

Vor Implementierung: erst dieses Dokument durchgehen, dann den passenden Pattern-Abschnitt oben, dann das Spec-File.
