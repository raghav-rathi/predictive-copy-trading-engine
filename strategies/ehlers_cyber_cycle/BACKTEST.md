# Cyber Cycle — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-18
(~5,224 bars each; the disk cache covers exactly this window).
Note: the coordinator's example epoch constants (1741910400000–1760828400000)
decode to 2025 dates — a year off — so the correct 2026 bounds
(1773525600000–1792328400000) were used instead, matching the stated window.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; would not change the sign of this result).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: Cyber Cycle alpha=0.07 of (h+l)/2, entries on
cycle/trigger cross, exits on opposite cross, 2xATR stop, 20-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 2,308 | 29.4% | -$9,742 | -97.4% | -17.45 | -97.4% | -$4.22 | 0.45 |
| ETH | 2,328 | 31.1% | -$9,345 | -93.4% | -13.12 | -93.6% | -$4.01 | 0.55 |
| HYPE | 2,197 | 35.4% | -$8,972 | -89.8% | -12.53 | -89.9% | -$4.08 | 0.54 |
| **Combined** | **6,833** | **31.9%** | **-$28,060** | — | — | — | -$4.11 | — |

## Verdict: LOSER (decisive)

The equity curve is wiped out on all three coins (-90% to -97%). The
mechanism is the failure: crossing the cycle against its own 1-bar lag
is a turning-point detector that fires on every wiggle of 1h crypto —
~2,300 trades per coin, a new position every ~2.3 bars, 30–35% win rate
with profit factor 0.45–0.55. The gross book is deeply underwater before
fees, so this is an edge failure, not a cost failure. Ehlers designed the
Cyber Cycle as a cycle *measurement* tool on much smoother (daily)
data; used naively as a 1h cross trigger it is a churn machine. Nothing
about these numbers is borderline.

## Calibration note

Shipped exactly the specified parameters (alpha=0.07, cross entries,
opposite-cross exits, 2xATR stop, 20-bar max hold, WARMUP=60). A
one-variant sweep (alpha=0.10) is reported in CALIBRATION.md — it loses
identically. The variant does not rescue the strategy; the failure is
the trigger logic, not the smoothing constant.

## Mechanism

smooth = (h+l)/2; cycle_i = (1-a/2)^2*(smooth_i - 2*smooth_{i-1} +
smooth_{i-2}) + 2(1-a)*cycle_{i-1} - (1-a)^2*cycle_{i-2}, a=0.07, seeded
with 0. trigger = cycle lagged 1 bar. Long when cycle crosses above
trigger, short when it crosses below; exit on the opposite cross.

Source: John Ehlers, *Cybernetic Analysis for Stocks and Futures* — code —
https://www.mql5.com/en/articles/288

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (immaterial vs -97% drawdowns).
- Next-bar-open execution vs idealized signal-bar entry.
- Only the naive cross trigger was tested; Ehlers' dominant-cycle period
  measurement was not used.
