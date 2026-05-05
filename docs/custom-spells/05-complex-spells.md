# Custom Spells — Complex spells & cross-cutting topics

Most custom spells are trivial DBC modifiers. A small group is architecturally tricky: recursive procs, exponential DoT spreads, owner-pet aura transfer, custom NPCs, OnRemove detection. This file collects the recurring patterns and lists, per pattern, which spells are affected.

Before implementing such spells: read this through, then go back to the relevant spec file for ID/effect details.

## Contents

- [Recursion guard](#recursion-guard)
- [Target cap & exponential propagation](#target-cap--exponential-propagation)
- [Recommended ICDs per pattern](#recommended-icds-per-pattern)
- [Custom NPCs (creature_template)](#custom-npcs-creature_template)
- [Owner→Pet aura transfer / pet scaling](#ownerpet-aura-transfer--pet-scaling)
- [OnRemove mode discrimination](#onremove-mode-discrimination)
- [Channel vs. cast vs. instant](#channel-vs-cast-vs-instant)
- [Client DBC patches beyond the server override](#client-dbc-patches-beyond-the-server-override)
- [Pet/UnitScript performance](#petunitscript-performance)
- [Aura stacks as a state tracker](#aura-stacks-as-a-state-tracker)
- [Aura of "particularly elaborate" spells](#aura-of-particularly-elaborate-spells)

## Recursion guard

Procs can trigger procs. Ignoring this builds infinite loops.

**Rules:**

1. Call `PreventDefaultAction()` in `HandleProc()`, otherwise both the DBC default trigger and the custom cast fire.
2. Trigger helper spells via `CastSpell(target, ID, true)` (`triggered=true`) — that sets `SPELL_ATTR4_TRIGGERED`, the helper cannot proc the source again itself.
3. For explicitly desired chains: set `SPELL_ATTR3_CAN_PROC_FROM_PROCS` — otherwise triggered spells ignore further procs.
4. For auto-attack procs (`PROC_FLAG_DONE_MELEE_AUTO_ATTACK`): use `SPELL_AURA_ADD_EXTRA_ATTACKS` (engine-side guard) instead of manually `CastSpell` with the auto-attack ID.

**Affected spells:**

| Spell | File | Risk |
|-------|-------|--------|
| 901102 Extra Attack 25 % | [global](./specs/global.md) | repeats the last attack — the extra attack must not proc itself |
| 900304 DK → Death Coil proc | [death-knight-blood](./specs/death-knight-blood.md) | Death Coil has its own proc pipeline |
| 900274 Pala CS/Judge/DS → Exorcism buff | [paladin-retribution](./specs/paladin-retribution.md) | Exorcism cast consumes the buff but must not regrant it |
| 900900 Disc Shield Explosion | [priest-discipline](./specs/priest-discipline.md) | the explosion cast must not trigger another shield removal |
| 901103 Global 10 % AoE proc | [global](./specs/global.md) | damage helper on 10 targets must not trigger 10 more AoE procs |
| 900800 / 900966 DoT → shadow AoE | [warlock-affliction](./specs/warlock-affliction.md), [priest-shadow](./specs/priest-shadow.md) | the AoE damage must not trigger another DoT-tick proc |

## Target cap & exponential propagation

Spells that propagate DoTs/buffs to new targets can grow exponentially.

**Rules:**

1. **Hard cap per cast** — never more than N new targets per tick.
2. **Hard cap per player** — max K active spread DoTs at the same time (e.g. via a counter aura).
3. **"Does NOT have the DoT" filter** — only cast on targets without the spread DoT, otherwise the aura refresh loop becomes infinite renewal.
4. **ICD on the source aura** (not just on the target) — prevents spam when many tick sources fire simultaneously.

**Affected spells:**

| Spell | File | Worst case |
|-------|-------|-----------|
| 900802 Warlock DoT spread | [warlock-affliction](./specs/warlock-affliction.md) | 1 → 3 → 9 → 27 targets in 3 ticks |
| 900967 Priest DoT spread | [priest-shadow](./specs/priest-shadow.md) | identical — code shareable |
| 901103 global AoE proc | [global](./specs/global.md) | 10 targets/hit × many hits/sec |
| 900533 Hunter Auto Shot bounce | [hunter-marksmanship](./specs/hunter-marksmanship.md) | 9 targets per Auto Shot, fast auto-attack frequency |

**Recommended caps:**

```cpp
// In HandleProc
static constexpr int MAX_SPREAD_PER_TICK = 2;
static constexpr int MAX_ACTIVE_SPREADS  = 8;
// Optional: counter aura on the caster, +1 stack per spread apply.
```

## Recommended ICDs per pattern

Proc patterns have established default ICDs. `spell_proc.Cooldown` in ms.

| Pattern | Default ICD | Source |
|---------|-------------|--------|
| DoT tick → AoE damage | 2000 ms | 900800, 900966 |
| AoE proc on hit | 1000 ms | 901103 |
| Block/dodge → counter | 1000 ms | 900172, 901104 |
| Periodic heal → summon | 5000 ms | 901066 Treant |
| Auto-attack → summon | 5000 ms | 900436 Spirit Wolf |
| Crit-streak effects | 0–500 ms | inherently rate-limited |
| Kill proc | 0 ms | naturally rate-limited |
| Low-HP trigger | 60000 ms | 900708 Mage Mana Shield |

ICD of 0 only when the trigger event itself is rare (kill, death). For all damage/heal patterns a non-trivial ICD is mandatory.

## Custom NPCs (creature_template)

Several spells summon NPCs that need their own entries in `creature_template` — plus their own AI/script for non-trivial behavior.

| NPC ID | Name | Source spell | Script | Notes |
|--------|------|--------------|--------|-------|
| 900333 | Frost Wyrm | 900333 | `npc_custom_frost_wyrm` | DisplayID 26752 (Sindragosa), scale 0.5, 2× Gargoyle HP, casts 900368 Frost Breath |
| 900436 | Spirit Wolf (Enh) | 900436 auto-wolf | (no own AI) | DisplayID 27074, 15 s duration |
| 901066 | Healing Treant | 901066 | (no own AI) | 30 s duration, attacks enemies or follows the player |
| TBD | Lesser Demons (Imp/VW/Succ/FH/FG) | 900835 | TBD | one NPC entry per pet type, 50 % HP/damage of the original |

**Required steps for a new summon NPC:**

1. Entry in `creature_template` (DisplayID, MinLevel/MaxLevel, faction, KillCredit=0, ScriptName).
2. If AI: `creature_template_addon` with `auras` (combat auras) and optionally an `npc_<name>` C++ class.
3. Pet type decides whether `creature_template.unit_class` and pet skills are relevant.
4. Test with `.npc spawn <id>` before hook integration.

## Owner→Pet aura transfer / pet scaling

Several spells boost pet damage or grant pet buffs while the aura sits on the owner.

**Three variants:**

1. **`UnitScript::OnDamage` filter** — the aura is a marker on the owner; the UnitScript checks `attacker.IsPet() && attacker.GetOwner()->HasAura(MARKER)` and multiplies damage. **Performance trap**: fires for ALL damage events server-wide. Used by: 900502 (BM Pet +50 %), 900438 (Wolf CL proc).
2. **`Pet::ApplyAllAuras` loop** — on pet summon, owner auras are explicitly mirrored onto the pet. Cleaner, but state drift on aura changes after the summon.
3. **Spell modifier with MaskA on the pet spell family** — when the pet spell has SpellFamilyName != 0, an aura on the owner via `EffectSpellClassMaskA` can directly modify the pet cast. Example 900836 (Imp Firebolt +50 %).

**Performance hint**: variant 1 always with an early-exit check (`if (!attacker || !attacker->IsCreature()) return;`) at the top of the script.

**Affected spells:**

| Spell | Variant | File |
|-------|----------|-------|
| 900435 Shaman summons +50 % | TBD (currently marker only) | [shaman-enhancement](./specs/shaman-enhancement.md) |
| 900502 BM Pet damage +50 % | 1 | [hunter-beast-mastery](./specs/hunter-beast-mastery.md) |
| 900503 BM Pet speed +50 % | PlayerScript tick | [hunter-beast-mastery](./specs/hunter-beast-mastery.md) |
| 900437 Spirit Wolves inherit haste | on summon (3) | [shaman-enhancement](./specs/shaman-enhancement.md) |
| 900836 Imp Firebolt +50 % | 3 | [warlock-demonology](./specs/warlock-demonology.md) |
| 900839 Felguard +50 % | 2 | [warlock-demonology](./specs/warlock-demonology.md) |
| 901067 Druid summons scale with healing power | PlayerScript tick | [druid-restoration](./specs/druid-restoration.md) |

## OnRemove mode discrimination

Auras can be removed for many reasons — expire, dispel, death, cancel, replace. Some spells should fire only on a specific mode.

```cpp
void HandleRemove(AuraEffect const* aurEff, AuraEffectHandleModes mode)
{
    AuraRemoveMode removeMode = GetAura()->GetRemoveMode();
    if (removeMode == AURA_REMOVE_BY_EXPIRE      // duration ran out
     || removeMode == AURA_REMOVE_BY_ENEMY_SPELL // dispelled / broken
     || removeMode == AURA_REMOVE_BY_DEATH)       // caster or target died
    {
        // desired cases
    }
    else if (removeMode == AURA_REMOVE_BY_CANCEL)
    {
        // Player right-click cancel — often NOT desired
        return;
    }
}
```

**Affected spells:**

| Spell | Use case | File |
|-------|----------|-------|
| 900900 Disc Shield Explosion | explosion only on FADE or ENEMY_BREAK, not on right-click cancel | [priest-discipline](./specs/priest-discipline.md) |
| 901068 Druid summon death heal | heal only when the summon dies, not on despawn-by-owner-logout | [druid-restoration](./specs/druid-restoration.md) |
| 900833 Demo Meta duration extend | only on a kill event while the aura is active — OnRemove is irrelevant here, but the duration manipulation must not remove the aura itself | [warlock-demonology](./specs/warlock-demonology.md) |

## Channel vs. cast vs. instant

Three spell categories with different hooks and different behavior on movement/interrupt.

| Category | Example | Hook | Movement check |
|-----------|----------|------|----------------|
| Channel | Evocation 12051, Mind Flay 48156 | `Spell::HandleChannelTick`, `Spell::ChannelInterrupt` | `SPELL_ATTR5_CAN_CHANNEL_WHEN_MOVING` |
| Cast (with cast time) | Frostbolt, Shadow Bolt | `Spell::CheckCast` → `SPELL_FAILED_MOVING` | the channel flag alone is NOT enough |
| Instant | Mortal Strike, Whirlwind | no movement check | irrelevant |

**901100 Cast While Moving** must cover all three categories:

```cpp
// Hook on Spell::CheckCast before SPELL_FAILED_MOVING:
SpellCastResult check = origCheckCast(...);
if (check == SPELL_FAILED_MOVING
    && caster->ToPlayer()
    && caster->HasAura(901100))
    return SPELL_CAST_OK;  // bypass
```

Channels need more — there `SPELL_AURA_CAST_WHILE_WALKING` (aura 330) on the 901100 aura is additionally required. Detail: [global.md](./specs/global.md).

## Client DBC patches beyond the server override

Server `spell_dbc` is not enough in all cases. The following spells need a **client DBC patch** (`python_scripts/patch_dbc.py` in [share-public](https://github.com/Shoro2/share-public)):

| Spell | What must be patched on the client | File |
|-------|--------------------------------------|-------|
| Visible custom spells (tooltip display) | `Spell.dbc` entry with name + description | all spec files |
| 900205/900234/900268 Consecration around you | `Consecration` (48819): TargetA → `TARGET_DEST_CASTER` | [paladin-holy](./specs/paladin-holy.md) |
| 900270 Divine Storm +6 targets | `Divine Storm` (53385): `MaxAffectedTargets` → 10 | [paladin-retribution](./specs/paladin-retribution.md) |
| 900709 Blink target location | `Blink` (1953): TargetType → `TARGET_DEST_DEST` (ground target cursor) | [mage-arcane](./specs/mage-arcane.md) |
| 900737 Fire Blast off-GCD | `Fire Blast` (42873): `StartRecoveryCategory` = 0 | [mage-fire](./specs/mage-fire.md) |
| 900770 Water Elemental permanent | summon duration → -1 or very high | [mage-frost](./specs/mage-frost.md) |

Server spell_dbc is enough for effect logic, but NOT for the target selection cursor and not for client-side GCD behavior (otherwise the client would show wrong cooldowns).

## Pet/UnitScript performance

UnitScripts hook into globally firing events (`OnDamage`, `OnUnitDeath`, ...). They run for **every** unit server-wide — sloppy filters can noticeably slow the server down.

**Mandatory pattern at the top of every UnitScript:**

```cpp
void OnDamage(Unit* attacker, Unit* victim, uint32& damage, ...) override
{
    if (!attacker || !victim) return;
    if (!attacker->IsCreature()) return;        // otherwise hooks on player damage
    Creature* c = attacker->ToCreature();
    if (!c->IsPet()) return;                    // only pets are relevant
    Player* owner = c->GetOwner() ? c->GetOwner()->ToPlayer() : nullptr;
    if (!owner || !owner->HasAura(MARKER)) return;
    // real logic from here
}
```

**Affected spells:**

| Spell | Hook | File |
|-------|------|-------|
| 900438 Wolf CL on hit | `UnitScript::OnDamage` | [shaman-enhancement](./specs/shaman-enhancement.md) |
| 900502 / 900504 BM Pet damage / cleave | `UnitScript::OnDamage` | [hunter-beast-mastery](./specs/hunter-beast-mastery.md) |
| 901068 Druid summon death heal | `UnitScript::OnUnitDeath` | [druid-restoration](./specs/druid-restoration.md) |
| 901069 Druid Thorns → Rejuv | `UnitScript::OnDamage` (on Victim=Player) | [druid-restoration](./specs/druid-restoration.md) |

## Aura stacks as a state tracker

Some spells use aura stack counts as an implicit charge/state counter instead of their own DB or member variables. Works, but has edge cases.

**Pattern (e.g. 900406 LvB two-charges):**

```cpp
// CumulativeAura = 2 in DBC
// AfterCast: stack==1 → reset CD (free second cast); stack==2 → normal CD, decrease stack
```

**Edge cases:**

- Fast casting can race between stack update and CD check.
- External `RemoveAura` calls (dispel, cancel) destroy the state.
- Aura refresh resets duration but not necessarily the stack — depends on the DBC `StackAmount` value and the `OverrideOldestAura` flag.

If the state must survive logout/login: don't use stacks, use a dedicated DB table.

## Aura of "particularly elaborate" spells

Spells that the spec files explicitly mark as _particularly elaborate_ or _strongly balance-relevant_, in one table:

| Spell | Main risk reason | File |
|-------|-------------------|-------|
| 901100 Cast while moving | active for all casters at once — channel + cast + interruptible | [global](./specs/global.md) |
| 901102 Extra Attack 25 % | recursive procs | [global](./specs/global.md) |
| 901103 10 % AoE proc | spam on DoT ticks | [global](./specs/global.md) |
| 900802 Warlock DoT spread | exponential propagation | [warlock-affliction](./specs/warlock-affliction.md) |
| 900835 Lesser demons | custom creature templates per pet type + AI | [warlock-demonology](./specs/warlock-demonology.md) |
| 900840 Sacrifice all bonuses | identify and stack multiple pet-type buffs at once | [warlock-demonology](./specs/warlock-demonology.md) |
| 900833 + 900834 Demo Meta combo | permanently transformed AoE healer-tank hybrid | [warlock-demonology](./specs/warlock-demonology.md) |
| 900900 Disc Shield Explosion | OnRemove detection + damage scaling on the absorb amount | [priest-discipline](./specs/priest-discipline.md) |
| 900933 Heal → Holy Fire AoE | direct-heal-vs-HoT filter | [priest-holy](./specs/priest-holy.md) |
| 900701 Mage mana regen scaling | dynamic computation per regen tick | [mage-arcane](./specs/mage-arcane.md) |
| 900709 Blink target location | client-side ground target cursor | [mage-arcane](./specs/mage-arcane.md) |
| 900738 Pyro → Hot Streak loop | guaranteed instant Pyro chain, balance-critical | [mage-fire](./specs/mage-fire.md) |
| 900771 Frost Comet Shower | entirely new spell with custom visuals | [mage-frost](./specs/mage-frost.md) |
| 900534 Hunter Multi-Shot Barrage | 20 Multi-Shots in 2 s, performance | [hunter-marksmanship](./specs/hunter-marksmanship.md) |
| 900300 / 900301 DK triple DRW + double-cast | aura stacking issues on triggered re-cast | [death-knight-blood](./specs/death-knight-blood.md) |
| 900333 Frost Wyrm | custom NPC + AI + scaled Frost Breath | [death-knight-frost](./specs/death-knight-frost.md) |
| 900274 Pala Exorcism buff | stacking buff with consumption on Exorcism cast | [paladin-retribution](./specs/paladin-retribution.md) |
| 900407 Sham LvB instant via Clearcasting | cast-time modifier on a spell that can already be made instant | [shaman-elemental](./specs/shaman-elemental.md) |
| 901071 Druid HoT 2x ticks/duration | ticks vs. duration trade-off | [druid-restoration](./specs/druid-restoration.md) |

Before implementation: read this document first, then the relevant pattern section above, then the spec file.
