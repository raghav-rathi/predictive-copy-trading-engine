# Vortex Indicator Crossover — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:24 UTC
(ms `[1773446400000, 1792589072292)`; actual data starts 2026-03-14
22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,296 bars
BTC/ETH, 5,294 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: VI(14), long on VI+ cross above VI-, short
on cross below, exits on the opposite cross, 2xATR stop, 3xATR trail,
120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 557 | 28.5% | -$5,326 | -53.3% | -3.85 | -55.5% | -$9.56 | 0.66 |
| ETH | 596 | 31.4% | -$2,511 | -25.1% | -1.29 | -37.9% | -$4.21 | 0.87 |
| HYPE | 523 | 32.1% | -$738 | -7.4% | -0.24 | -21.4% | -$1.41 | 0.96 |
| **Combined** | **1,676** | **30.6%** | **-$8,576** | — | — | — | -$5.12 | — |

Fees paid: BTC $4,616 / ETH $5,046 / HYPE $2,665.

## Verdict: a clear loser — the raw VI cross is a whipsaw machine on 1h

Negative on all three coins, combined -$8,576 over 1,676 trades, win
rate 30.6%, Sharpe deeply negative on BTC (-3.85) with a -55.5% max
drawdown. This is not bad luck, it is a structural mismatch: the
Botes/Siepman cross was designed for daily bars, and on 1h crypto the
VI+/VI- lines cross constantly in chop — 523–596 trades per coin in
7 months is ~2.5 trades a day, so costs eat it alive (BTC fees alone
were $4,616, nearly equal to its net loss). The 2xATR stop fires far
more often than the trend leg it is meant to protect. HYPE is the
least bad leg (PF 0.96, essentially breakeven before costs) but that
is faint praise: no coin clears costs.

What would fix it: the paper trigger needs a trend filter (ADX,
longer lookback) or the cross needs confirmation (e.g. a breakout or a
VI spread threshold) to kill the mid-range flickering. As shipped it
does not earn.

## Calibration note

Shipped the specified n=14. A 10/14/20 window sweep is in
CALIBRATION.md: longer windows uniformly help (fewer, calmer crosses)
— n=20 is the in-sample combined winner at -$3,606 — but BTC is
negative at every setting and no setting is positive combined. The
n=14 window was fixed a priori; it stays the registry config
regardless.

## Mechanism

Vortex Indicator: VM+ = |h − l.shift(1)|, VM− = |l − h.shift(1)|;
VI+(14) = sum14(VM+)/sum14(TR), VI−(14) = sum14(VM−)/sum14(TR). Long
when VI+ crosses above VI−, short on a cross below; the exit is the
opposite cross, so the position always follows whichever line leads.
2xATR hard stop, 3xATR chandelier trail, 120-bar max hold.

Source: Vortex Indicator (Botes & Siepman) —
https://www.investopedia.com/terms/v/vortex-indicator-vi.asp

## Limitations

- Single 7-month crypto window, 1h bars; the indicator was designed
  for daily.
- 1,676 trades across three coins — a large sample of failure, but
  still one regime.
- Fee/slippage modeled per RiskConfig; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped window on this window (see CALIBRATION.md).
