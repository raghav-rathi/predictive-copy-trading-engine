# Laguerre Filter Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC
(ms `[1773525600000, 1792328400000)`): 5,223 bars BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: Laguerre filter gamma=0.8 on hl2, long on a
cross above a rising filter, short on a cross below a falling filter,
exits on the opposite cross, 2xATR stop, 3xATR trail, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 159 | 20.1% | -$2,005 | -20.0% | -1.94 | -20.4% | -$12.61 | 0.66 |
| ETH | 190 | 15.3% | -$3,151 | -31.5% | -4.11 | -34.8% | -$16.58 | 0.45 |
| HYPE | 143 | 18.2% | -$1,306 | -13.1% | -1.46 | -18.8% | -$9.13 | 0.72 |
| **Combined** | **492** | **17.7%** | **-$6,462** | — | — | — | -$13.13 | — |

Signal gates fire on every coin (long entries 80/98/76, short entries
80/94/69 for BTC/ETH/HYPE). Exit reasons are signal-dominated:
96–138 signal exits vs 47–53 stops per coin — positions are cut by
the opposite cross far more often than by the stop, i.e. the filter
crosses back through price almost as soon as a trade is entered.

## Verdict: a clear loser — the filter is too close to price

Combined -$6,462 across 492 trades, negative on all three coins,
win rate 17.7%, Sharpe -1.46 to -4.11, expectancy -$13.13/trade.
ETH is the worst leg (-$3,151, Sharpe -4.11, MaxDD -34.8%). The
Laguerre filter's selling point — minimal lag — is exactly the
problem here: with gamma=0.8 the filter hugs price, so in 1h crypto
chop the close crosses it dozens of times a month and every cross is
a trade that dies on the next cross. The slope filter (enter only
when Filt is moving your way) does not filter chop, because the
filter's slope flips with the same noise that causes the cross.
This is a NO-GO as a standalone trend engine on 1h crypto; it would
need a trend-strength gate (e.g. ADX) or a much slower gamma before
it is worth retesting.

## Calibration note

Shipped the specified gamma=0.8. A gamma=0.5/0.8/0.9 sweep is in
CALIBRATION.md: every setting is combined-negative; gamma=0.9 is the
least bad (-$4,033) only because HYPE flips green (+$854). The
gamma=0.8 setting was fixed a priori — adopted before the sweep,
not because of it.

## Mechanism

Laguerre filter (Ehlers, gamma=0.8) on hl2: four-element recursion,
Filt=(L0+2·L1+2·L2+L3)/6. Long when close crosses above Filt and
Filt is rising; short when close crosses below Filt and Filt is
falling. Exits on the opposite cross. 2xATR hard stop, 3xATR
chandelier trail, 200-bar max hold.

Sources:
- https://efs.kb.esignal.com/hc/en-us/articles/6362941110555-Four-Element-Laguerre-Filter-by-John-Ehlers
- https://www.luxalgo.com/library/concept/laguerre-filter/

## Limitations

- Single 7-month crypto window; 492 trades, all three legs negative
  — the failure is consistent, not a one-coin fluke.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune gamma on this window (see CALIBRATION.md).
