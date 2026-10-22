# Chaikin Volatility Expansion — Backtest

**Data:** local cache CSVs `data/candles/{BTC,ETH,HYPE}_1h.csv`, 1h bars,
sliced to the batch window with ms constants `[1773446400000,
1792627199000)`: 5,301 bars BTC/ETH, 5,299 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (`use_funding=False`, fully offline).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=70 bars.

## Results (shipped config: CV(10,10), trigger=+5.0, SMA50 trend filter,
exit on cv crossing back below the trigger or below zero, 2xATR stop,
1.5xATR chandelier trail, 100-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 305 | 32.5% | -$3,051 | -30.5% | -3.07 | -32.4% | -$10.00 | 0.63 |
| ETH | 315 | 32.7% | -$3,831 | -38.3% | -4.50 | -39.8% | -$12.16 | 0.53 |
| HYPE | 353 | 37.4% | -$3,062 | -30.6% | -3.86 | -31.2% | -$8.67 | 0.64 |
| **Combined** | **973** | **34.3%** | **-$9,944** | — | — | — | **-$10.22** | — |

## Verdict: a loser on all three coins — do not trade this as-is

Combined **-$9,944** across 973 trades. Every coin is red, every
profit factor is well under 1.0 (0.53–0.64), every Sharpe is deeply
negative (-3.07 to -4.50), and max drawdowns run -31% to -40%. This is
not a marginal miss — it is a systematic failure of the entry
hypothesis: buying/selling into a volatility *expansion* with the
trend means entering exactly when realized range is at its widest,
so the 2xATR stop is placed in the middle of climactic chop and the
1.5x trail gets clipped before any leg develops.

The mechanism insight: Chaikin's own read of his indicator is that
volatility spikes precede *reversals* — expansion marks climactic,
emotional participation. This engine trades the expansion *with* the
trend, which is arguably the wrong side of Chaikin's observation: by
the time cv crosses +5.0 the move is already extended and the reversal
leg works against the position. The exit rule (cv rolling back below
the trigger) then dumps the position into the very reversal Chaikin
predicted. If anything, the indicator is signaling what it always
signaled — a turn is coming — and this spec trades into the turn
instead of out of it. A fade-the-spike or a much later re-entry rule
would be the honest next experiment, but that is a different
strategy, not this one.

- 973 trades in one 7-month crypto regime; the loss is consistent
  across all three coins, not a single-coin accident.
- Fees ($2,974 BTC / $2,256 ETH / $1,630 HYPE) are large relative to
  trade count — the entry signal fires ~1.3x per day per coin and most
  of that churn is stopped or trailed out.

## Calibration note

The shipped trigger=5.0 was fixed a priori. A 2.5/5.0/10.0 trigger
sweep is in CALIBRATION.md: **all three trigger settings lose on all
three coins** (combined -$9,951 / -$9,944 / -$9,453) — the threshold
moves the trade count around but does not change the outcome. There is
no in-sample winner to accidentally select.

## Mechanism

cv = 100 × ROC(10) of EMA(10) of the high-low range. Long when cv
crosses above +5.0 with close > SMA50; short when cv crosses above
+5.0 with close < SMA50 (trade WITH the trend into volatility
expansion). Exit when cv crosses back below the trigger or below zero
(the expansion rolls over). 2xATR hard stop, 1.5xATR chandelier trail,
100-bar max hold.

Sources: Chaikin Volatility —
https://www.spread-betting.com/trader-training/chaikin-volatility-oscillator
and https://www.fmz.com/strategy/461363

## Limitations

- Single 7-month crypto window; 973 trades but all in one regime.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped trigger on this window (see CALIBRATION.md)
  — and the sweep says there is nothing worth tuning toward here
  anyway.
