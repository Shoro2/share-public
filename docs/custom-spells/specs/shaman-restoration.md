# Shaman — Restoration

**Source:** [`custom_spells_shaman.cpp`](https://github.com/Shoro2/mod-custom-spells/blob/master/src/custom_spells_shaman.cpp)
**ID-Range:** 900466-900499
**Status:** Nicht getestet (importiert aus `CustomSpells.md`)

| # | Spell ID | Effekt | Ansatz | Status | Details |
|---|----------|--------|--------|--------|---------|
| 1 | 900466 | Totems follow player | PlayerScript | nicht getestet | DUMMY Marker. Shared `custom_totem_follow_playerscript` prüft auch `HasAura(900466)`. |
| 2 | 900467 | Mana regen +2% per missing mana% | C++/PlayerScript | nicht getestet | DUMMY Marker. `custom_mana_regen_playerscript::OnPlayerUpdate` → alle 5s: missingPct = (1 - curMana/maxMana) × 100 → EnergizeBySpell(maxMana × missingPct × 0.02 / 100). Bei 50% missing → +1% maxMana/5s. Bei 90% missing → +1.8% maxMana/5s. |

> **Hinweis Enhance**: 900435 (Summons +50%) ist aktuell nur ein Marker — die tatsächliche Damage-Erhöhung muss via Pet Scaling oder Owner→Pet Aura Transfer implementiert werden. 900434 (Maelstrom AoE) castet den AoE Helper direkt auf alle Controlled Units bei 5 Stacks — das AoE geht einmalig los, nicht für 5s bei jedem Angriff (simplified). 900438 (Wolf CL) nutzt UnitScript::OnDamage das für ALLE Damage-Events feuert — Performance beobachten.

---

> Original-Quelle: [`mod-custom-spells/CustomSpells.md`](https://github.com/Shoro2/mod-custom-spells/blob/master/CustomSpells.md) Sektion "Shaman — Restoration (900466-900499)".
