# Hikkake False-Breakout — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,276 bars BTC/ETH, 5,274 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=40 bars.

## Results (shipped config: 3-bar confirmation window, 1.5xATR stop,
3.0xATR target, 20-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 140 | 35.0% | -$2,311 | -23.1% | -2.10 | -27.7% | -$16.51 | 0.72 |
| ETH | 134 | 36.6% | -$1,715 | -17.1% | -1.46 | -19.6% | -$12.80 | 0.79 |
| HYPE | 90 | 37.8% | -$341 | -3.4% | -0.31 | -13.6% | -$3.79 | 0.94 |
| **Combined** | **364** | **36.3%** | **-$4,367** | — | — | — | -$12.00 | — |

## Verdict: loser — false breakouts don't resolve on 1h crypto

A clean, high-sample loss: 364 trades, negative on all three coins,
profit factors 0.72–0.94, Sharpe negative everywhere. The win rate sits
at 35–38% against a 2R target — the pattern needs ~34% wins just to
break even before costs, and it can't clear that bar. Fees ($3,988
combined) are roughly equal to the gross loss, i.e. costs roughly
double the damage but the edge is negative even gross of fees. HYPE is
the least bad (PF 0.94, -$341) but still negative. The honest read: on
1h crypto, inside-bar false moves are more often the start of a real
breakdown/breakout than a trap — the "trapped side covering" squeeze
doesn't materialize often enough at this timeframe.

## Calibration note

Shipped the specified 3-bar confirmation window. A 2/3/4-bar sweep is
in CALIBRATION.md: a 2-bar window is dramatically better (combined
+$145, HYPE +$823 at PF 1.31) and a 4-bar window worse (-$4,703). The
window is a genuine sensitivity knob — but adopting the 2-bar winner
now would be pure in-sample selection on this exact window, so the
shipped config stays at 3 bars as specified.

## Mechanism

Inside bar (h < h[1], l > l[1]) at bar i−1; bar i prints a lower low
AND lower high (failed breakdown → long setup) or higher high AND
higher low (failed breakout → short setup). Enter on a close back
through the inside bar's range within 3 bars (the trap bar's own close
may confirm); unconfirmed traps expire. Opposite-direction confirmation
is a structural exit; 1.5xATR stop, 3.0xATR target, 20-bar max hold.

Source: Hikkake pattern (Chesler 2004, via forexracer.com) —
https://www.forexracer.com/hikkake-pattern-indicator-mt5/

## Limitations

- Single 7-month crypto window; results are timeframe-specific (the
  pattern was designed for daily forex/equity bars).
- 1.5xATR stop may be too tight for 1h crypto noise — but widening it
  is a tuning decision for walk-forward work, not this window.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Trap detection uses strict inequalities on h/l; wick-equal bars are
  not counted as inside bars.
