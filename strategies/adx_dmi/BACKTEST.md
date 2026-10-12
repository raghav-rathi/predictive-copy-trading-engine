# ADX/DMI — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → present
(BTC 5,080 bars; ETH 5,080; HYPE 5,078).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: classic Wilder 14, +DI/-DI cross entries with ADX >= 25,
exit on opposite cross or ADX < 20, 2xATR stop, 3xATR chandelier trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 78 | 26.9% | −$519 | −5.2% | −0.50 | −15.4% | −$6.65 | 0.84 |
| ETH | 68 | 35.3% | −$997 | −9.9% | −1.49 | −16.6% | −$14.66 | 0.62 |
| HYPE | 88 | 22.7% | −$1,178 | −11.8% | −1.87 | −13.3% | −$13.39 | 0.63 |
| **Combined** | **234** | **28.2%** | **−$2,694** | — | — | — | −$11.51 | — |

## Verdict: LOSER

Negative on all three coins with negative Sharpe (−0.50 to −1.87) and
profit factors 0.62–0.84. The classic ADX(14)/25 filter gets chopped up on
1h crypto: the DI cross forms after most of the hourly move has already
printed, so entries buy the late leg of the trend; the ADX-fade exit then
churns in and out of the subsequent range. Fees ($841 combined) are a
drag but the pre-cost book is already negative — this is a structural
misfit, not a cost problem. Shipped the classic 25 anyway (see
CALIBRATION.md): the sweep shows 30 is merely "least bad," not a stable
winning region.

## Calibration note

Indicators verified: hand-checked pure up-move converges to
+DI→100/−DI→0/ADX→100, and the truncation test proves lookahead-freedom.
Win rates 23–35% are far below what a trend-following payoff (PF > 1.5)
needs at these hold lengths. What needs watching: nothing to salvage here
without a mechanism change — e.g. entering on the ADX *turn* (ADX rising
through 20 while DI crosses) rather than the DI cross itself, or moving
to 4h bars so the cross forms before the move is over.

## Mechanism

Wilder smoothing (alpha 1/14) on +DM/−DM/TR. Long when +DI crosses above
−DI with ADX(14) >= 25; short on the mirror cross. Exit on the opposite
DI cross or ADX fading below 20. 2xATR hard stop, 3xATR chandelier trail,
120-bar (5-day) max hold.

Source: J. Welles Wilder — Directional Movement (New Concepts in
Technical Trading Systems, 1978) —
https://www.investopedia.com/terms/a/adx.asp

## Limitations

- Single 7-month crypto window; ADX systems historically prefer slower
  equity-index regimes — this window may be adversarial.
- Funding unmodeled (short book would earn it).
- Next-bar-open execution: on fast DI crosses the fill can be far from
  the cross price.
