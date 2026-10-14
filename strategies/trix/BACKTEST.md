# TRIX — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → present
(BTC 5,080 bars; ETH 5,080; HYPE 5,078).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: classic TRIX(15) with 9-bar signal line, long on
signal cross below zero, short on the mirror, exit on opposite cross,
2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 171 | 38.0% | −$265 | −1.3% | +0.02 | −17.7% | −$1.55 | 0.97 |
| ETH | 176 | 38.1% | +$55 | +0.6% | +0.16 | −15.8% | +$0.31 | 1.01 |
| HYPE | 179 | 41.3% | +$5,328 | +53.5% | +2.95 | −8.7% | +$29.77 | 1.51 |
| **Combined** | **526** | **39.1%** | **+$5,118** | — | — | — | +$9.73 | — |

## Verdict: MIXED (best combined in the batch, HYPE-concentrated)

HYPE is an outright winner: +$5,328 at Sharpe 2.95, PF 1.51, maxDD only
−8.7% over 179 trades — the strongest single-coin result of this batch.
BTC and ETH are flat-to-slightly-negative (PF 0.97/1.01). The triple
smoothing does its job on HYPE: it filters the hourly chop and only
fires when momentum genuinely turns, and the below/above-zero gate keeps
entries on the right side of the oscillator. Combined +$5,118 is the best
book of the six, but I will not call it a WINNER: two of three coins are
dead flat, so the edge is HYPE-specific, not universal.

## Calibration note

Indicators verified: independent loop recomputation of the triple EMA
matches to 4 decimals; truncation test proves lookahead-freedom. The
period sweep (see CALIBRATION.md) confirms 15 is the best and not on a
knife edge — 21 is also positive combined (+$3,310). Shipped the classic
15.

## Mechanism

e3 = EMA(EMA(EMA(close,15),15),15); TRIX = 100·(e3 − e3[1])/e3[1]; signal
= 9-bar SMA of TRIX. Long when TRIX crosses above its signal line while
below zero (momentum turning up from oversold); short on the mirror cross
above zero. Exit on the opposite signal cross. 2xATR hard stop, 3xATR
chandelier trail, 120-bar (5-day) max hold.

Source: TRIX — triple exponential average momentum —
https://www.investopedia.com/terms/t/trix.asp

## Limitations

- Single 7-month window; the HYPE edge may be regime-specific.
- HYPE concentration: the combined win is ~104% HYPE. A portfolio
  allocation would need the edge to broaden.
- Funding unmodeled.
- Next-bar-open execution; signal crosses on fast turns can slip.
