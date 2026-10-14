# Asia Sweep — Backtest

**Data:** Hyperliquid `candleSnapshot` 1h bars, BTC + ETH + HYPE,
2026-03-14 → 2026-10-10 (~5,080 bars each). Bar timestamps in ms UTC drive
all session logic.
**Costs:** 0.045% taker fee + 0.01% slippage per side; funding accrued
hourly from real fundingHistory (second-order at these hold times).
**Sizing:** 1% equity risk per trade on the 1xATR stop, 3x leverage cap,
$10k start. Warmup 60 bars.

## Results (shipped config: 0.10xATR min sweep depth, 1xATR stop / 3R
target, 20:00 UTC flat, 24-bar backstop)

| Coin | Signals L/S | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 18/28 | 45 | 31.1% | −$1,211 | −12.1% | −1.49 | −15.1% | −$26.91 | 0.66 |
| ETH | 15/26 | 41 | 29.3% | −$964 | −9.6% | −1.01 | −15.1% | −$23.50 | 0.71 |
| HYPE | 19/24 | 40 | 27.5% | −$1,314 | −13.1% | −1.75 | −18.4% | −$32.85 | 0.58 |
| **Combined** | **52/78** | **126** | **29.4%** | **−$3,488** | — | — | — | −$27.69 | — |

Fees paid: $2,042 combined — the 1xATR stop / 3R target structure churns.

## Verdict: LOSER

Negative on all three coins with 126 trades — this is not a sample-size
artifact. Exit-reason autopsy: hard stops take 26–29 of 40–45 trades per
coin; only 5–8 reach the 3R target. The sweep-and-reclaim entry does not
follow through on crypto 1h: price keeps traveling through the 1xATR stop
instead of reversing to target. The 20:00 UTC flat and opposite-sweep
exits account for the rest (6–11 per coin).

The honest read: the spec's edge claim (PF 5.35 on XAUUSD M15) is
unvalidated marketing, and the mechanism doesn't transfer to crypto 1h.
Forex session liquidity ("Asia low → London sweep") is a session-open
phenomenon; crypto trades 24/7, so the UTC session boundaries are
arbitrary lines on a continuous flow — there is no session-open liquidity
event to sweep. The depth sweep (CALIBRATION.md) confirms the loss is
structural, not a parameter miss: 0.05x–0.15x ATR all lose on all coins.

## Calibration note

Shipped the spec's 0.10xATR minimum sweep depth. The depth sweep
{0.05, 0.10, 0.15} (same data/costs/sizing) is uniformly negative —
PF 0.53–0.77 across all coins and depths, win rate 26–31% — so 0.10x is
not a knife edge, the mechanism itself fails here. What I verified:
session reference levels match hand-built Asia/London extremes, the
14:00 UTC skip and 20:00 UTC flat fire correctly, bias persistence/flip
logic is exact, and everything is lookahead-free by truncation test.
What this means: do not trade this. The 126-trade sample is large enough
to call it.

## Mechanism

Signal windows 07:00–10:00 and 12:00–15:00 UTC (14:00 skipped). Reference
= prior session's extreme (today's Asia low/high → London window,
today's London low/high → NY window). Long: bar's low sweeps ref_low but
closes back above it as a bullish candle, 30-bar BOS bias bullish, sweep
depth ≥ 0.10xATR(14). Short mirrors. Flat at 20:00 UTC.

DEVIATION (documented in risk.py): the spec's SL = sweep extreme ∓
0.5xATR is anchored at the sweep extreme; the event harness anchors
stops at entry, so the shipped 1.0xATR-from-entry stop is the calibrated
harness-anchored approximation, with TP = 3R kept consistent.

Source: Asia Sweep EA spec — grahamovernightly/edgefindr —
https://github.com/grahamovernightly/edgefindr/blob/HEAD/ea/Asia_Sweep_EA_spec.md

## Limitations

- Single 7-month, mostly bearish/choppy window; no bull-market sample.
- Next-bar-open execution vs the idealized sweep-bar entry.
- The 1xATR stop is a harness approximation of the spec's
  sweep-extreme ∓ 0.5xATR stop (per-trade stop distances aren't
  expressible in the shared harness).
- Session boundaries are a forex fiction on 24/7 crypto — the backtest
  says the market agrees.
