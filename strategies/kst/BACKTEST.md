# KST — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → present
(BTC 5,080 bars; ETH 5,080; HYPE 5,078).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: classic Pring KST = 1·RCMA(ROC10)+2·RCMA(ROC15)
+3·RCMA(ROC20)+4·RCMA(ROC30), 9-bar signal line, cross entries, exit on
opposite cross, 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 267 | 32.2% | −$2,685 | −25.8% | −1.81 | −29.6% | −$10.06 | 0.76 |
| ETH | 273 | 31.9% | −$2,615 | −26.1% | −1.77 | −31.3% | −$9.58 | 0.79 |
| HYPE | 259 | 37.8% | +$3,897 | +40.1% | +2.13 | −17.1% | +$15.05 | 1.26 |
| **Combined** | **799** | **34.0%** | **−$1,403** | — | — | — | −$1.76 | — |

## Verdict: MIXED (HYPE winner, BTC/ETH losers, combined slightly negative)

HYPE is positive for the third momentum system in a row (Sharpe 2.13,
PF 1.26, 259 trades) — at this point the HYPE-momentum edge is a batch
finding, not a strategy fluke. BTC/ETH lose −$2.6k each: the KST
signal-line cross whipsaws on their hourly chop, and KST's slow ROC
legs mean entries arrive late. Combined −$1,403 — honest, no massaging.
Note the sweep (CALIBRATION.md): a slower signal line (13) flips the
combined book positive, but I shipped the classic 9 because the sweep is
monotonic — 13 is not a stable optimum, just "slower is better," and
BTC/ETH stay negative there too.

## Calibration note

Indicators verified: independent loop recomputation of the weighted
smoothed ROCs matches to 4 decimals; signal line verified as the exact
9-bar SMA of KST; truncation test proves lookahead-freedom. Mechanism
quirk worth knowing: on a constant-slope rise, ROC shrinks as the
denominator grows, so KST *decays* through a steady uptrend — the
signal-line cross only fires on acceleration changes.

## Mechanism

ROCn = 100·(close − close[n])/close[n]; KST = 1·SMA(ROC10,10) +
2·SMA(ROC15,10) + 3·SMA(ROC20,10) + 4·SMA(ROC30,15); signal = SMA(KST,9).
Long when KST crosses above its signal; short when it crosses below;
exit on the opposite cross. 2xATR hard stop, 3xATR chandelier trail,
120-bar (5-day) max hold.

Source: Martin Pring — Know Sure Thing (KST) —
https://www.investopedia.com/terms/k/know-sure-thing-kst.asp

## Limitations

- Single 7-month window; HYPE's momentum edge may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; KST crosses on fast turns can slip badly.
- KST's slow legs (ROC30) mean entries lag the fastest hourly turns.
