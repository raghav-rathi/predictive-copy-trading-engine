# Schiff Pitchfork Median-Line Pullback — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 522 | 30.7% | -5344.28 | -3.71 | -56.3% | -10.24 | 0.66 |
| ETH | 507 | 33.7% | -3914.07 | -2.27 | -50.5% | -7.72 | 0.77 |
| HYPE | 568 | 34.2% | -4630.64 | -3.09 | -50.1% | -8.15 | 0.74 |
| **Combined** | **1597** | **32.9%** | **-13888.99** | **-4.54** | **-50.2%** | **-8.70** | **0.73** |

Fees: total $9521.25.
Exits: BTC {'stop': 262, 'signal': 260}; ETH {'signal': 261, 'stop': 246}; HYPE {'signal': 301, 'stop': 267}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$16,160.40.

## Verdict: LOSER (large) — −$13,888.99 on 1,597 trades, combined Sharpe −4.54, MaxDD −50.2%.

All three coins lose heavily and the combined equity curve falls
to $16,160 on a $30k start. The mechanism is the trade count:
1,597 trades — the median line sits close to price by design
(the Schiff anchor flattens the fork), so touches fire
constantly, and with no minimum swing between the anchoring
pivots the fork re-anchors on noise. The system is effectively a
high-frequency mean-reversion-to-a-line trade with a 2xATR stop:
win rate ~33%, expectancy −$8.70/trade, and $9,521.25 of fees
alone exceed two-thirds of the loss. Roughly half the exits are
signal exits (close beyond the far parallel), half are stops —
the exits fire, the entries just do not pay. No parameter was
tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The huge trade count makes the combined loss statistically
  solid (this is a real loser on this window, not noise), but it
  is still one window and three coins.
- The pivot definition, the 5-bar touch arm, and the absence of
  a minimum swing filter are interpretation choices (see
  CALIBRATION.md); a minimum swing between pivots would trade
  far less and is a different system, not a tuning tweak applied
  here.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
