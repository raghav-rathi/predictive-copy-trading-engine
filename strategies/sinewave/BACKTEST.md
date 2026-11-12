# SineWave — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 3099 | 35.2% | -9902.19 | -21.29 | -99.0% | -3.20 | 0.48 |
| ETH | 3130 | 37.1% | -9730.90 | -15.69 | -97.3% | -3.11 | 0.53 |
| HYPE | 3069 | 43.8% | -8879.10 | -10.74 | -88.8% | -2.89 | 0.66 |
| **Combined** | **9298** | **38.7%** | **-28512.19** | **-19.05** | **-95.0%** | **-3.07** | **0.57** |

Fees: total $21546.19.
Exits: BTC {'signal': 2756, 'stop': 343}; ETH {'signal': 2798, 'stop': 332}; HYPE {'signal': 2821, 'stop': 248}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$1,490.64.

## Verdict: LOSER — -$28,512.19 on 9,298 trades, combined Sharpe -19.05, MaxDD -95.0%.

The worst result in the batch by a wide margin, and the failure mode
is structural, not marginal. The Hilbert phase of 1h crypto noise
whipsaws: the system fires ~3,100 trades per coin — roughly one trade
every two bars — so it is almost always in a position and flips
constantly. 8,375 of 9,298 trades end on the opposite-cross signal
exit, i.e. the system reverses itself within a bar or two of entry,
and $21,546.19 of fees alone nearly equals the starting capital. Win
rate 38.7% with PF 0.57 means the losers also outrun the winners; the
edge is absent on every coin (BTC -$9,902.19, ETH -$9,730.90, HYPE
-$8,879.10 — no coin is even close to breakeven). Combined equity
falls to $1,490.64, a -95.0% drawdown: the account is effectively
wiped out. This is Ehlers' own cycle-mode caveat playing out — the
SineWave assumes a dominant cycle, and 1h crypto has no stable
dominant cycle for the phase to lock onto, so the phase rotates at
the energy-weighted frequency of broadband noise and the crosses are
meaningless. Do not trade this system as shipped; any revival would
need a cycle-mode gate (e.g. only trade when a dominant cycle is
actually measurable) rather than parameter tweaks.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 9,298-trade sample: the loss is not sampling noise — PF 0.57
  across all three coins with Sharpe -19.05 is a systematic failure.
- The result is really the raw phase-cross rule on noisy data, not
  Ehlers' full HT_SINE (which adds dominant-cycle period estimation
  and phase smoothing); see CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
