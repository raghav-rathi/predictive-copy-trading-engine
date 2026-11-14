# GoNoGo Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00
UTC (ms `[1773525600000, 1792328400000)`): 5,223 bars BTC/ETH,
5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: published-checklist score, long on
transition into Go with oscillator > 0, short on transition into
NoGo with oscillator < 0, exit on return to neutral or the opposite
state, 2xATR stop, 3xATR trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 332 | 23.5% | -$4,546 | -45.4% | -3.93 | -51.4% | -$13.69 | 0.60 |
| ETH | 373 | 22.8% | -$3,548 | -35.5% | -2.67 | -45.0% | -$9.51 | 0.73 |
| HYPE | 305 | 29.5% | +$590 | +5.9% | +0.50 | -15.5% | +$1.93 | 1.05 |
| **Combined** | **1,010** | **25.0%** | **-$7,505** | — | — | — | -$7.43 | — |

Every signal gate fires on every coin: long entries 159/186/150
and short entries 174/188/155 (BTC/ETH/HYPE) over the window.

## Verdict: a loser — the reconstruction does not survive 1h crypto

Combined −$7,505 across 1,010 trades, 25.0% win rate. BTC is the
worst leg (−$4,546, Sharpe −3.93, max drawdown −51.4%, profit
factor 0.60 — winners are rarer and smaller than losers), ETH is
nearly as bad (−$3,548, PF 0.73). HYPE is the only green coin and
barely (+$590, PF 1.05, expectancy +$1.93 — fees of $1,584 are
2.7x the net). Fees total $8,552 against a −$7,505 net: even
before costs the gross edge is thin.

Exit-reason breakdown (all coins): 603 signal exits vs 407 stops,
0 max-hold exits — the 150-bar cap never binds; positions die by
state flip or by the 2xATR stop, roughly 60/40. The 23–30% win
rates say the transition entry is systematically late: by the
time all five checklist legs agree, the 1h move is mostly spent,
and the state flip back to neutral then exits near the lows.

Treat this as a negative result for the checklist reconstruction
on 1h bars, not as evidence about the commercial GoNoGo indicator
(which this is not).

## Mechanism

Composite −5..+5 score from EMA(9/21/50) alignment, MACD(12,26,9)
histogram sign, ADX(14) > 20 with +DI/−DI, Donchian(50) position,
RSI(14) vs 50. States: ≥ +4 strong Go, +2/+3 weak Go, −1..+1
neutral, −2/−3 weak NoGo, ≤ −4 strong NoGo. Oscillator =
clip(z50(MACD hist) + (RSI−50)/25, −6, +6). Long on transition
into Go with oscillator > 0, short on transition into NoGo with
oscillator < 0; exit on return to neutral or the opposite state.
2xATR stop, 3xATR trail, 150-bar max hold.

Sources: https://www.gonogocharts.com/indicator/gonogo-oscillator/
and https://www.optuma.com/kb/tools/gonogo/gonogo-trend/

## Limitations

- Single 7-month crypto window; 1,010 trades is a reasonable
  sample for the sign, but it is one regime (the 2026 drawdown).
- Reconstruction risk: equal-weighted components and the
  ±4/±2 state thresholds are my choices, not the vendor's.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped thresholds on this window (see
  CALIBRATION.md).
