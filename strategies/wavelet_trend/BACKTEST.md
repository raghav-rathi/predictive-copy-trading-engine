# Wavelet Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=64 bars.

## Results (shipped config: DWT db4 level 3, approximation-only,
5-bar slope, 1.5xATR stop, 2.5xATR target, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 597 | 23.6% | -$7,211 | -72.1% | -8.97 | -72.4% | -$12.08 | 0.43 | $4,822 |
| ETH | 623 | 26.5% | -$6,488 | -64.9% | -7.19 | -65.0% | -$10.41 | 0.50 | $4,287 |
| HYPE | 572 | 31.6% | -$4,702 | -47.0% | -4.75 | -48.8% | -$8.22 | 0.63 | $2,741 |
| **Combined** | **1,792** | **27.2%** | **-$18,401** | — | — | — | **-$10.27** | — | **$11,850** |

Signal gates fire on every coin (long entries 294/312/281, short
entries 303/311/292 for BTC/ETH/HYPE). Win rates 24–32% with profit
factors 0.43–0.63: the approximation slope turns constantly on 1h
noise that level-3 denoising does not remove, so the strategy
whipsaws — 572–623 trades per coin in 8 months, roughly 2.5 trades
a day, and the 1.5xATR stop fires before any leg can pay 2.5R.

## Verdict: the worst of this batch — a genuine loser everywhere

Combined -$18,401 across 1,792 trades, expectancy -$10.27/trade.
BTC loses 72% of the account (Sharpe -8.97, MaxDD -72.4%), ETH 65%,
HYPE 47%. The denoised trend is still a lagging, noisy slope on 1h
crypto: the 5-bar slope of the approximation flips far more often
than real trends last, and the slope-turn entry is systematically
late to every leg it catches. Denoising did not fix the core
problem — it just made a smoother whipsaw.

## Calibration note

Shipped levels=3. A levels 2 – 3 – 4 sweep is in CALIBRATION.md:
levels=4 is less bad (combined -$10,837 on 1,212 trades) and
levels=2 is about as bad as shipped (-$17,293), but no setting is
green on any coin. The shipped levels=3 was fixed a priori —
adopted before the sweep, not because of it.

## Mechanism

DWT (db4, level 3) on closes, pure-numpy filter bank with
half-point symmetric extension; reconstruct the approximation only
(details zeroed). Long when the approximation's 5-bar slope turns
positive and close is above the approximation; short on the mirror.
Exit on a slope flip or a close cross of the approximation against
the position. 1.5xATR stop, 2.5xATR target, 72-bar max hold.

Source: Wavelet Decomposition (LuxAlgo) —
https://www.luxalgo.com/library/concept/wavelet-decomposition/

## Limitations

- Single 8-month crypto window; 1,792 trades, all three legs deeply
  negative, so the sign is not a small-sample accident.
- BTC leg loses 72% of the account; fees ($11,850 combined) are
  two-thirds of the gross loss.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped level count on this window (see
  CALIBRATION.md).
