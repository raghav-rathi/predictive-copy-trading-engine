# FFT Dominant Cycle — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=180 bars.

## Results (shipped config: top-3 FFT frequencies, period 8–64 bars,
Hann window 128, SMA(50) filter, 1.5xATR stop, 2.5xATR target,
96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 331 | 34.1% | -$5,283 | -52.3% | -5.20 | -56.1% | -$15.96 | 0.55 | $3,450 |
| ETH | 340 | 36.5% | -$2,774 | -27.3% | -2.10 | -35.1% | -$8.16 | 0.77 | $3,252 |
| HYPE | 315 | 42.2% | -$1,784 | -17.8% | -1.39 | -21.9% | -$5.66 | 0.85 | $1,916 |
| **Combined** | **986** | **37.5%** | **-$9,840** | — | — | — | **-$9.98** | — | **$8,618** |

Signal gates fire on every coin (long entries 167/159/154, short
entries 167/184/162 for BTC/ETH/HYPE). Win rates 34–42% with profit
factors 0.55–0.85: the reconstructed cycle turns after the move has
already happened, so entries chase legs that are half over and the
1.5xATR stop absorbs the reversal.

## Verdict: genuine loser on all three coins

Combined -$9,840 across 986 trades, expectancy -$9.98/trade, and no
coin is green. BTC is the worst (-$5,283, Sharpe -5.20, MaxDD
-56.1%). The FFT's stationarity assumption fails exactly as the
caveat warned: crypto cycles drift, so the "dominant" frequency of
the last 128 bars is a lagging description of the past, not a
forecast. The 2.5xATR target is rarely reached (win rates in the
30s); most trades die on the stop or the slope flip.

## Calibration note

Shipped top_k=3. A top_k 1 – 3 – 5 sweep is in CALIBRATION.md:
top_k=1 is much less bad (combined -$2,635 on 410 trades) but still
red on all three coins; top_k=5 (-$8,937) is no better than shipped.
The shipped top_k=3 was fixed a priori — adopted before the sweep,
not because of it.

## Mechanism

Rolling FFT on detrended log-closes (Hann window, 128 bars);
reconstruct from the top-3 dominant frequencies with period 8–64
bars. Long when the reconstructed-cycle slope turns up and close is
above SMA(50); short on the mirror. Exit on a slope flip or a
price cross of SMA(50) against the position. 1.5xATR stop, 2.5xATR
target, 96-bar max hold.

Source: Fourier Transform Based Trading Strategy (PyQuantLab) —
https://pyquantlab.medium.com/a-fourier-transform-based-trading-strategy-in-backtrader-5e2d5a6d8392

## Limitations

- Single 8-month crypto window; 986 trades but all three legs are
  negative, so the sign is not a small-sample accident.
- BTC leg loses over half the account (-52.3%, MaxDD -56.1%).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped top_k on this window (see CALIBRATION.md).
