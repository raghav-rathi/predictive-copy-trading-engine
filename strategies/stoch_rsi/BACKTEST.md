# Stochastic RSI — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
window ms `[1773446400000, 1792590766516)` (2026-03-14 00:00 UTC →
2026-10-21 13:52:46 UTC, END computed at run time): 5,296 bars
BTC/ETH (first available bar 2026-03-14 22:00 UTC), 5,294 HYPE
(first available bar 2026-03-15 00:00 UTC); last closed bar
2026-10-21 13:00 UTC on all three.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: RSI(14), stoch window 14, %K/%D = SMA(3)/SMA(3),
long on %K crossing above 20, short on %K crossing below 80, exits on
the 50-midline cross, 2xATR stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 312 | 30.1% | -$4,524 | -44.8% | -3.44 | -45.9% | -$14.50 | 0.64 |
| ETH | 301 | 38.9% | -$1,286 | -12.1% | -0.67 | -31.1% | -$4.27 | 0.90 |
| HYPE | 278 | 37.8% | +$1,305 | +12.5% | +0.86 | -13.7% | +$4.69 | 1.10 |
| **Combined** | **891** | **35.5%** | **-$4,505** | — | — | — | -$5.06 | — |

## Verdict: loser — one green leg does not save a -$4,505 book

This is a clear loser. BTC is catastrophic: -$4,524 (-44.8% of the
$10k book), Sharpe **-3.44**, MaxDD **-45.9%** — a drawdown that deep
on 312 trades is not bad luck, it is the signal failing. ETH loses
(-$1,286, PF 0.90). Only HYPE is green (+$1,305, Sharpe +0.86,
PF 1.10), but even there fees ($1,482) exceed the net profit
($1,305) — the one green leg is fee-fragile.

The honest decomposition, gross of fees:

- BTC: gross **-$1,924** — loses even fee-free. No edge on BTC at all.
- ETH: gross +$1,181 — a real gross edge, but $2,467 of fees eat it
  and turn it into -$1,286 net. The signal is not tradeable at
  0.045%+0.01% per side with 301 trades.
- HYPE: gross +$2,787 — the only coin with a genuine net edge after
  costs, and even it is thin (PF 1.10).

Mechanism failure: %K leaving the 20/80 zones marks *exhaustion*, and
on 1h crypto exhaustion is usually a pause, not a reversal. Entries
get run over by the resuming move, the 2xATR stop takes the loss,
and %K whipsaws back across 50 to exit whatever survived — 891
trades of churn at 35.5% win rate. The classic StochRSI trap, priced
in dollars.

## Calibration note

Shipped the specified (k,d)=(3,3). A (2,2)/(3,3)/(5,5) smoothing
sweep is in CALIBRATION.md: no setting is profitable combined;
(2,2) is best on ETH (+$304) but worst on BTC (-$5,106) and HYPE
(-$1,144); (5,5) just trades less and still loses everywhere except
a near-flat HYPE (-$104). The parameter is not the problem — the
signal is. The (3,3) config was fixed before any backtest was run;
no in-sample adoption.

## Mechanism

Chande & Kroll Stochastic RSI: RSI(14) is normalized by its own
14-bar range into a 0..100 oscillator, %K = SMA(3) of that
(normalized) line, %D = SMA(3) of %K. Long when %K crosses above 20
(momentum leaves the oversold zone — buying exhaustion, not the
dump itself); short when %K crosses below 80 (leaves overbought).
Exits on the 50-midline cross (the bounce leg is done). 2xATR hard
stop, 3xATR chandelier trail, 60-bar max hold. The 0/0 guard: a
dead-flat market pins the raw line to 50 (neutral); a
one-directional run with RSI pinned at its floor/ceiling pins to the
informative extreme (0/100).

Source: Stochastic RSI (Chande & Kroll) —
https://blockspot.io/what-is-stochastic-rsi/

## Limitations

- Single 7-month crypto window; even 891 trades come from one regime.
- BTC leg is a strategy-killer (-45.9% MaxDD); the signal has no edge
  there, gross or net.
- The HYPE green leg is fee-fragile (fees > net) and the thinnest
  sample of the three.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped (k,d) on this window (see CALIBRATION.md).
