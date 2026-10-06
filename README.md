# Blaque Baux Backwards

**Risk-managed (vol-scaled) momentum — a reverse test. Does scaling the book by inverse volatility cure the momentum crash, and *only* momentum's?**

Backwards doesn't hunt a new signal — it stress-tests a claim. The corpus already carries momentum (`boom`, `beyond`)
and has flagged its crash risk red. The literature (Barroso–Santa-Clara, Daniel–Moskowitz) says the cure is to lever
the momentum book by the inverse of its own recent volatility — because momentum's vol *spikes* right before it
crashes. The sharp, falsifiable part: this is supposed to help **momentum specifically**, not non-momentum strategies.
So we vol-scale a momentum factor *and* two non-momentum controls the same way, and check whether the repair is
momentum-specific or generic.

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/backwards_1_riskmanaged_momentum.py   # needs Alpaca data keys in the environment
```

## The finding (direction confirmed, magnitude immaterial)

[`research/backwards_1_riskmanaged_momentum.py`](research/backwards_1_riskmanaged_momentum.py) — a cross-sectional
multi-asset momentum factor (WML, 12-1 month, 20 liquid ETFs, dollar-neutral) vs the market and a 1-month reversal
book, each vol-scaled (lever = target / trailing realized vol, causal, capped). Compared at an equal 10% risk budget
(Sharpe & skew are scale-free).

| strategy | Sharpe raw→scaled | **skew** raw→scaled | maxDD@10% raw→scaled |
|---|---|---|---|
| **MOMENTUM** (WML 12-1) | +0.10 → +0.15 | **−0.59 → −0.50** ✅ *improves* | −20% → −19% |
| market (SPY) | +0.88 → +0.87 | −0.35 → **−0.75** ✗ worsens | −20% → −18% |
| reversal (1-month) | +0.45 → +0.37 | +0.16 → **−0.07** ✗ worsens | −20% → −20% |

**The asymmetry the claim predicts is present**: vol-scaling is the *only* lever that *improves* momentum's left skew,
and it *worsens* both non-momentum controls' — momentum-specific, exactly as advertised. **But the magnitude is
immaterial** (ΔSharpe +0.05, Δskew +0.09): over 2016–26 multi-asset momentum barely crashed *and* barely earned (raw
Sharpe +0.10), so there's little crash for the cure to repair.

## Verdict

**PARTIAL — direction confirmed, magnitude immaterial in this window.** Not falsified: the mechanism shows the right
sign (vol-scaling helps momentum's crash skew, hurts the non-momentum controls'). But not actionable here, because the
canonical **2009 momentum crash — where risk-managed momentum actually earns its keep — predates Alpaca's data (hard
floor 2016-01)**, and the in-window momentum stress (2020–21 rotations, the Jan-21 squeeze) is far milder. So we keep
momentum's crash risk flagged, and treat vol-scaling as a **validated-but-dormant overlay** for `boom`/`beyond` — the
right insurance to carry, even if this sample can't price it. A conclusive test needs pre-2016 single-name WML data: a
`backwards_2`.

## Status

**Research.** Honest partial — a reverse test that confirms a mechanism's *sign* while being candid that the sample
can't prove its *size*. Scale-free scorecard (Sharpe, skew) plus equal-risk drawdown, causal vol-scaling, Alpaca SIP
daily total return. No live capital.

## Planned v2 leg — inverse-vol mean-reversion (inversion B)

Backwards showed vol-scaling helps *momentum* (de-lever when vol is high). The mirror test (`backwards_2`): apply the
*inverse* to a mean-reversion book (short-term reversal / pairs), **scaling position size UP when realized vol spikes
above its 6-month average** — momentum needs calm to trend, but mean-reversion often thrives in high vol. Honest null: if
it fails, the friction/decay assumptions hold; if it succeeds, it's a regime-dependent sizing alpha. (Folded from the
batch-3 inversion set.)
