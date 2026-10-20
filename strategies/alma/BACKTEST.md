# ALMA Dual Cross — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,271 bars BTC/ETH, 5,269 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: ALMA(9)/ALMA(21), sigma=6, offset=0.85,
long on cross-up + new 20-bar high, short on cross-down + new 20-bar
low, exits on the opposite cross, 2xATR stop, 3xATR trail, 200-bar max
hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 82 | 36.6% | +$1,090 | +10.9% | +1.03 | -16.7% | +$13.29 | 1.28 |
| ETH | 80 | 36.3% | +$240 | +2.2% | +0.32 | -9.8% | +$3.00 | 1.06 |
| HYPE | 71 | 38.0% | +$856 | +8.6% | +0.83 | -8.9% | +$12.06 | 1.26 |
| **Combined** | **233** | **36.9%** | **+$2,186** | — | — | — | +$9.38 | — |

## Verdict: positive on all three coins — the first of this batch to do
it, but uneven underneath

Positive everywhere is the headline: combined +$2,186 on 233 trades,
36.9% win rate, profit factor above 1.0 on every coin. HYPE has the
cleanest profile (Sharpe +0.83, MaxDD -8.9%, PF 1.26, expectancy
+$12/trade). But the components are not equally convincing:

- **BTC** carries the return (+$1,090, Sharpe +1.03) and the pain
  (MaxDD **-16.7%**, deepest of the three): the breakout filter
  caught a couple of big legs, and the 200-bar hold let losers
  bleed before the opposite cross printed.
- **ETH is borderline noise** (PF 1.06, expectancy +$3.00/trade,
  Sharpe +0.32). Fees ($699) are nearly 3x its net profit ($240) —
  on ETH, fees are the story, not edge. One of the weakest
  per-coin reads in the batch despite the green sign.
- 233 trades is still a thin sample for any "strategy works" claim,
  and every number here is from one 7-month crypto regime.

## Calibration note

Shipped the specified offset=0.85. A 0.75/0.85/0.95 offset sweep is in
CALIBRATION.md: per-coin in-sample winners split across all three
(HYPE→0.75 +$1,095, ETH→0.95 +$742, BTC→0.85 +$1,090); 0.85 is best
combined (+$2,186) but that is an in-sample observation, not the
reason it shipped. The offset was fixed a priori — no in-sample
adoption.

## Mechanism

Arnaud Legoux Moving Average: Gaussian-weighted close average over
n bars, w_i = exp(-((i - offset*(n-1))^2)/(2*sigma^2)) with sigma=6
and offset=0.85 pulling the bell toward the newest bars, so ALMA hugs
price with less lag than a symmetric smoothing. ALMA(9) vs ALMA(21):
long when the fast crosses above the slow **and** the close prints a
new 20-bar high; short on a cross-down **and** a new 20-bar low. The
breakout filter stops the cross from firing mid-range. Exits are pure
cross-based (the opposite cross closes the trade). 2xATR hard stop,
3xATR chandelier trail, 200-bar max hold.

Source: ALMA dual-cross (Hermes strategy, TradingView) —
https://cn.tradingview.com/script/nhsUBtUD-Hermes/

## Limitations

- Single 7-month crypto window; 233 trades is a thin sample.
- ETH leg is near-noise (PF 1.06, expectancy $3/trade, fees ~3x net)
  — the green sign there is fragile.
- BTC MaxDD -16.7%: the 200-bar hold lets dead breakout positions
  linger; the opposite-cross exit is slow.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped offset on this window (see CALIBRATION.md).
