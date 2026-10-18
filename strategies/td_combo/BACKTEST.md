# TD Combo — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-18
(~5,224 bars each; the disk cache covers exactly this window).
Note: the coordinator's example epoch constants (1741910400000–1760828400000)
decode to 2025 dates — a year off — so the correct 2026 bounds
(1773525600000–1792328400000) were used instead, matching the stated window.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 1xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 9-bar setup on close vs close[4], 13-bar countdown,
enter on countdown 13, exit on price flip, 1xATR stop, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 5 | 60.0% | +$19 | +0.2% | +0.10 | -2.7% | +$3.84 | 1.08 |
| ETH | 4 | 75.0% | +$431 | +4.3% | +1.55 | -1.2% | +$107.84 | 4.63 |
| HYPE | 6 | 50.0% | -$19 | -0.2% | -0.07 | -3.5% | -$3.13 | 0.94 |
| **Combined** | **15** | **60.0%** | **+$432** | — | — | — | +$28.78 | — |

## Verdict: FLAT (inconclusive, not a winner)

DeMark's full Combo sequence — 9 consecutive setup bars AND 13 qualifying
countdown bars — almost never completes on 1h crypto: 15 trades across
three coins in seven months. The +$432 combined net and the ETH Sharpe of
+1.55 are artifacts of a 4-trade sample, not edge; one trade flips the
sign. This is not a loser by mechanism failure (no blowups: max DD -3.5%,
win rate 60%), it is a strategy that barely fires at this bar speed. On
daily bars the countdown would complete more often; on 1h the filter is
too strict to trade. No recommendation either way until a longer or
slower-bar sample exists — honestly, as shipped, this is a research
curiosity, not a tradeable engine.

## Calibration note

Shipped exactly the specified parameters (9/13 core, price-flip exit,
1xATR stop, 24-bar max hold, WARMUP=60). A one-variant sweep (2.0xATR
stop) is reported in CALIBRATION.md — it changes nothing (same 15
trades, ETH drops to +$164, BTC flips to -$90). The sample is too small
for calibration to mean anything; the sweep is diagnostic only.

## Mechanism

Buy setup: 9 consecutive bars with close < close[4]. Buy countdown (starts
the bar after setup, need not be consecutive; a completed setup while the
countdown runs does not restart it): 13 bars each with close <= low[2],
low < prior countdown bar's low, close < prior countdown bar's close
(first countdown bar needs only the close<=low[2] condition). Enter long
on countdown-bar 13. Sell side mirrors. Exits: price flip (longs exit
when close > close[4], shorts when close < close[4]), 1xATR hard stop
(standing in for the 13-count bar's low/high), 24-bar time stop.

Source: Tom DeMark, *The New Science of Technical Analysis* — countdown rules —
https://www.theforex7.com/trade/td-combo-713/

## Limitations

- 15 combined trades: no statistical power; Sharpe/PF are noise.
- Single 7-month crypto window; no bull-market or daily-bar sample.
- Funding unmodeled.
- Next-bar-open execution vs idealized signal-bar entry.
- Stop is 1xATR below/above entry, not the true 13-count extreme.
