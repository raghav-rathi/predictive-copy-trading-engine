# OBV Divergence — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:25 UTC
(ms `[1773446400000, 1792589132324)`): 5,296 bars BTC/ETH, 5,294 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: pivot lag k=10, bullish divergence at pivot
lows enters long on the first bar after confirmation, bearish divergence
at pivot highs enters short, 15-bar divergence dedupe, exits on the
opposite pivot print or confirming opposite divergence, 1.5xATR stop,
2.5xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 14 | 35.7% | -$275 | -2.75% | -0.92 | -6.02% | -$19.61 | 0.60 |
| ETH | 20 | 30.0% | -$276 | -2.76% | -0.64 | -6.85% | -$13.81 | 0.66 |
| HYPE | 15 | 26.7% | -$1 | +0.62%* | +0.20 | -8.03% | -$0.04 | 1.00 |
| **Combined** | **49** | **30.6%** | **-$551** | — | — | — | -$11.25 | — |

\* HYPE's equity return (+0.62%) and trade sum (-$1) disagree because one
short was still open at the final bar — the equity curve marks it to
market at the close.

## Verdict: loser — flat on HYPE, negative on BTC/ETH, and too few trades to learn anything

The headline is -$551 on 49 trades across 7 months: the strategy barely
trades. Requiring a confirmed two-pivot divergence (pivot lag 10 + 15-bar
dedupe) produces 14–20 signals per coin over the whole window — the
pattern is real but rare on 1h crypto bars, and the signal set is far too
thin for any verdict about the divergence edge itself.

- **BTC** is the worst leg (-$275, PF 0.60, expectancy -$19.61): only 14
  trades, and most divergences were counter-trend into chop — the tight
  1.5xATR stop did its job (MaxDD only -6.02%), but there is no edge
  visible, just stop-bleed.
- **ETH** mirrors it (-$276, PF 0.66): the same counter-trend entries get
  chopped. 20 trades is noise-sample territory.
- **HYPE is the only non-negative leg** (PF 1.00, expectancy -$0.04 —
  dead flat): its divergences printed closer to actual swings, but 15
  trades at zero expectancy proves nothing either way.
- 49 trades is too thin for any "strategy works / doesn't work" claim;
  what *is* measurable is that this parameterization doesn't trade
  enough to matter, and the trades it took lost.

## Calibration note

Shipped the specified pivot lag k=10. A 6/10/14 lag sweep is in
CALIBRATION.md: k=14 is positive combined (+$742 on just 12–19
trades/coin — in-sample luck territory), k=6 is split (HYPE +$1,068,
BTC -$1,187). The lag is a genuine sensitivity knob, but the sweep
samples are too thin to trust; k=10 shipped a priori, no in-sample
adoption.

## Mechanism

On-Balance Volume (Granville, 1963): obv = cumsum(sign(c − c.shift(1)) *
v), unchanged close adding 0. Pivots are detected with confirmation lag
k=10 (lookahead-free: a pivot at bar i is only readable at the close of
bar i+k). Bullish divergence = a new pivot low at a *lower* price than
the previous pivot low while OBV at the new pivot is *higher* —
sellers pushed price down but volume pressure stopped leaking out.
Entry on the first bar after confirmation (bar i+k+1); bearish mirror at
pivot highs. A divergence signal is skipped if any divergence fired in
the prior 15 bars (dedupe). Exits: long exits when a new pivot high
prints (take the swing) or a bearish divergence confirms; shorts mirror.
1.5xATR hard stop (counter-trend entry, tight), 2.5xATR chandelier trail,
60-bar max hold.

Source: On-Balance Volume divergence (Granville, 1963) —
https://www.ig.com/uk/learn/trading/on-balance-volume-obv-what-it-is-and-how-to-trade-it

## Limitations

- 49 trades over 7 months: far too thin for any robust claim; the
  parameterization may simply be too selective for 1h bars.
- Counter-trend-by-construction: into chop the 1.5xATR stop bleeds;
  the win rate (~30%) needs fat winners that didn't show.
- Pivot highs/lows use strict unique extrema — flat congestion prints
  extra pivots and noise divergences.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped k on this window (see CALIBRATION.md).
