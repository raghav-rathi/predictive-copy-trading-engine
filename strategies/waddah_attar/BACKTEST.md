# Waddah Attar Explosion — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,271 bars BTC/ETH, 5,269 HYPE
(HYPE history starts 2026-03-15 00:00 UTC; BTC/ETH cache opens
2026-03-14 22:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=130 bars.

## Results (shipped config: sensitivity 150, explosion 2×stdev(hist,20),
dead zone 3.7×ATR(100), author's entry/exit rules, 2xATR stop,
3xATR trail, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 236 | 27.1% | -$2,664 | -26.6% | -3.44 | -26.6% | -$11.29 | 0.56 |
| ETH | 236 | 31.8% | -$1,282 | -12.8% | -1.27 | -16.9% | -$5.43 | 0.79 |
| HYPE | 247 | 29.1% | -$1,866 | -18.7% | -2.99 | -18.7% | -$7.56 | 0.64 |
| **Combined** | **719** | **29.3%** | **-$5,813** | — | — | — | -$8.08 | 0.67 |

## Verdict: loser — the explosion entries chase, the exits can't save them

The entries fire on momentum acceleration, which on 1h crypto mostly
means buying the local top of a burst: 27–32% win rates with profit
factors of 0.56–0.79. The explosion-line exit is conceptually right
(momentum died → get out) but in practice the 2xATR stop and 3xATR
trail do most of the exiting, and they exit at losses. 719 trades is
not a thin sample — this is a genuine failure on the window. Fees
($5,310 combined) are large but the gross edge is negative regardless;
this is not a cost problem.

## Calibration note

Shipped the author's specified sensitivity 150. A 100/150/200 sweep
is in CALIBRATION.md: all settings lose on all three coins (100 least
negative at -$5,273 combined, 200 worst at -$6,087). Keeping 150 —
adopting the in-sample best would be cherry-picking a still-losing
setting.

## Mechanism

hist = 150 × (EMA(C,20) − EMA(C,40) delta) measures momentum
acceleration; the explosion line = 2×stdev(hist,20) is a
volatility-scaled momentum band; the dead zone = 3.7×ATR(100) filters
out weak momentum. Long when hist > 0, rising, above a rising
explosion line, both above the dead zone (mirror for shorts). Exit
when the histogram crosses back under the explosion line — i.e., when
|hist| < explosion again. 2xATR hard stop, 3xATR chandelier trail, no
fixed target, 200-bar max hold.

Source: Waddah Attar Explosion (ctrader.com, author's own entry/exit
rules) — https://ctrader.com/products/3133

## Limitations

- Single 7-month crypto window; WAE was designed for forex sessions
  where momentum bursts follow through more cleanly.
- Entry conditions are strict conjunctions — on quiet regimes the
  strategy sits out; on burst regimes it buys tops.
- The 3xATR trail is wide relative to 1h noise, so it often hands
  back open profit before the explosion-line exit can trigger.
- Funding unmodeled; next-bar-open execution vs idealized entry.
