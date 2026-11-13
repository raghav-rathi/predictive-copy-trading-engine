# Volume Spread Analysis — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5847, ETH 5847, HYPE 5845.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 424 | 35.6% | -3606.07 | -2.34 | -44.6% | -8.50 | 0.73 |
| ETH | 417 | 40.5% | -2339.70 | -1.47 | -30.9% | -5.61 | 0.84 |
| HYPE | 283 | 39.6% | -2905.96 | -2.49 | -39.0% | -10.27 | 0.69 |
| **Combined** | **1124** | **38.4%** | **-8851.73** | **-3.47** | **-34.4%** | **-7.88** | **0.77** |

Fees: total $8911.60.
Exits: BTC {'stop': 220, 'signal': 204}; ETH {'stop': 216, 'signal': 201}; HYPE {'stop': 171, 'signal': 112}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$21,148.27.

## Verdict: LOSER — -$8,851.73 on 1,124 trades, combined Sharpe -3.47, MaxDD -34.4%.

VSA loses on all three coins with the worst combined drawdown in
this batch series: BTC -$3,606.07 (PF 0.73), ETH -$2,339.70
(PF 0.84), HYPE -$2,905.96 (PF 0.69). Win rate 38.4% with PF 0.77
does not clear $8,911.60 in fees — the system trades far too often
(1,124 trades, the most in the batch) for a per-bar pattern whose
edge, if any, is swamped by the 2xATR stop being hit on noise:
607 of 1,124 trades ended on the stop/trail. The honest read is
that no-supply / no-demand bars on 1h crypto fire constantly
(declining volume on narrow bars is the modal bar in a ranging
market, not a tell), and stopping-volume / upthrust bars catch
climaxes that keep running. The pattern taxonomy is implemented
faithfully to Williams; the market simply does not pay for it on
this window.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,124-trade sample: a large sample, and the loss is consistent
  across all three coins — this is a system-level failure, not
  one bad coin.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
