# Pretty Good Oscillator — Calibration

Trigger sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing, 2xATR stop,
3xATR trail, 100-bar max hold). The trigger is the breakout width in
average true ranges: 2.0 fires on shallower thrusts (more trades, more
chop), 4.0 only on extreme displacements (few trades, cleaner
breakouts). The sweep re-runs `add_indicators(df, trigger=X)` only —
signals and risk are unchanged.

| Trigger | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 2.0 | BTC | 158 | 28.5% | -$2,186 | -1.85 | 0.71 | -$13.84 |
| 2.0 | ETH | 160 | 33.8% | -$954 | -0.63 | 0.87 | -$5.96 |
| 2.0 | HYPE | 150 | 36.0% | +$186 | +0.25 | 1.03 | +$1.24 |
| 3.0 (shipped) | BTC | 75 | 34.7% | -$456 | -0.46 | 0.87 | -$6.08 |
| 3.0 (shipped) | ETH | 78 | 33.3% | -$797 | -0.79 | 0.80 | -$10.22 |
| 3.0 (shipped) | HYPE | 48 | 39.6% | +$1,535 | +1.72 | 1.69 | +$31.98 |
| 4.0 | BTC | 36 | 38.9% | -$93 | -0.10 | 0.95 | -$2.59 |
| 4.0 | ETH | 38 | 26.3% | -$638 | -0.95 | 0.71 | -$16.80 |
| 4.0 | HYPE | 18 | 50.0% | +$1,412 | +2.01 | 3.70 | +$78.47 |

## One-line verdict

- **2.0:** worst combined (-$2,954): shallower triggers drown in
  chop — 158/160 trades on BTC/ETH for a -$3,140 combined loss. The
  extra HYPE trades add nothing (+$186).
- **4.0:** best combined (+$681) and best on HYPE (+$1,412, PF 3.70,
  expectancy +$78/trade) — but on 18 HYPE trades, and ETH is no better
  (-$638 vs -$797, PF 0.71 vs 0.80). BTC nearly flat at -$93,
  confirming the mechanism intuition: a wider trigger filters the
  majors' chop.
- **3.0:** middle of the pack (+$282 combined), HYPE +$1,535 on 48
  trades.
- **Shipped decision:** keep the specified trigger=3.0 as the
  registry config regardless. The 3.0 trigger was fixed before any
  backtest was run; 4.0 is the in-sample combined winner here, and
  adopting it *because* of that would be in-sample selection on 18–38
  trades per coin. The honest read: the trigger is a real sensitivity
  knob (it moves the chop-vs-breakout tradeoff exactly as theory
  predicts), but 3.0 vs 4.0 needs walk-forward or out-of-sample
  evidence, not this 7-month window.
