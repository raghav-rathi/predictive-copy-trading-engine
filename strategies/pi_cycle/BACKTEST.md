# Pi Cycle Top — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
window ms `[1773525600000, 1795525200000)` (2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC, last bar 2026-11-24 13:00 UTC): 6,111 bars
BTC/ETH, 6,109 HYPE (HYPE's first bar is 2026-03-15 00:00 UTC).
Batch 45 frozen window — supersedes the Nov-14 window entirely.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=400 bars. No max hold (regime system, see risk.py).

## Results (shipped config: SMA(111) vs 2.0xSMA(350), entries on the
crosses in/out of the top zone, exits on the opposite cross, 2xATR
stop, 3xATR trail, no max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 0 | — | $0.00 | 0.00% | 0.00 | 0.00% | — | — | $0.00 |
| ETH | 0 | — | $0.00 | 0.00% | 0.00 | 0.00% | — | — | $0.00 |
| HYPE | 0 | — | $0.00 | 0.00% | 0.00 | 0.00% | — | — | $0.00 |
| **Combined** | **0** | **—** | **$0.00** | — | — | — | — | — | **$0.00** |

## Verdict: no verdict possible — the indicator never fired once

Zero trades on all three coins, at the shipped multiplier and at
1.9 and 2.1 (see CALIBRATION.md). The system is not a winner or a
loser on this window; it is **untestable** on it. The peak
SMA(111)/SMA(350) ratio reached in the batch-45 window was BTC
1.13, ETH 1.17, HYPE 1.22 — nowhere near the 2.0 top-zone
threshold, let alone 1.9. This is a timeframe mismatch, not a
bug: the Pi Cycle Top was built on *daily* bars over full
multi-year cycles, where SMA(350) spans ~a year and a 2x
separation between the averages means price roughly doubled
against its yearly mean. On 1h bars SMA(350) spans only ~14.6
days, so the ratio would need price to roughly double inside
two weeks — BTC's run from ~$70k to ~$126k took months, and the
early-November selloff only compressed the averages further.
Extending the window by ten days (Nov 14 → Nov 24) changed
nothing: the ratio peaked at 1.22 on HYPE and never approached
the threshold on any coin. No 1h window of eight months can
produce a Pi Cycle cross unless the coin doubles in a fortnight.

The honest read: do not ship this as a 1h strategy. It belongs
on daily bars over multi-year data, or with the multiplier
re-derived for the timeframe — either of which is a different
strategy, not a calibration tweak. The $0 result is reported
as-is; there is no PnL to tune, and no in-sample adoption
happened (the multiplier sweep is uniformly zero).

## Mechanism

Philip Swift's Pi Cycle Top (2019): SMA(111) of the close vs
2.0 × SMA(350) of the close. Long regime while SMA(111) <
2.0×SMA(350); the top zone is SMA(111) ≥ 2.0×SMA(350). Long when
SMA(111) crosses back below the top line (exiting the zone);
short when it crosses above (the top signal); exits on the
opposite cross. 2xATR hard stop, 3xATR chandelier trail, no max
hold — a regime position is held until the opposite cross, which
can be months away; a 60-bar cap would turn the system into a
2.5-day timer.

Source: Philip Swift, Pi Cycle Top Indicator (2019) —
https://charts.perly.io/chart/pi-cycle

## Limitations

- Zero trades: no statistical statement about the edge is
  possible from this window at any multiplier 1.9–2.1.
- Single 8-month window; the indicator's natural horizon is
  multi-year daily data, which this repo's 1h candle files do
  not cover.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the multiplier down to force trades on this window
  — that would be fitting the threshold to the sample.
