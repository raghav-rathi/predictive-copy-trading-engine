# Harmonic Gartley XABCD — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 00:00 UTC → 2026-10-19 13:00 UTC (5,247 bars BTC/ETH; 5,245 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=120 bars (zigzag spin-up).

## Results (shipped config: 5-bar-confirmed zigzag pivots scanned as
XABCD with AB=0.618·XA, BC∈[0.382,0.886]·AB, CD∈[1.272,1.618]·BC,
AD=0.786·XA, ±6% on the point ratios; long on bullish PRZ completion,
short on bearish; exit on opposite pattern; 2xATR stop, 4xATR target,
100-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1 | 0.0% | -$112 | -1.1% | -1.91 | -1.1% | -$111.88 | 0.00 |
| ETH | 0 | — | $0 | +0.0% | +0.00 | 0.0% | +$0.00 | 0.00 |
| HYPE | 1 | 0.0% | -$105 | -1.0% | -2.01 | -1.0% | -$104.61 | 0.00 |
| **Combined** | **2** | **0.0%** | **-$216** | — | — | — | **-$108.25** | — |

## Verdict: inconclusive — the pattern almost never completes

Two trades in 7 months across three coins cannot validate or reject
anything. The detector itself is verified (unit tests fire it on
exact-ratio synthetic patterns, bullish and bearish), and the zigzag
finds 516–525 pivots per coin — but the classical ±6% ratio stack is an
extremely tight filter: only 2 of ~1,500+ candidate pivot quintuples
complete a textbook Gartley on 1h crypto in this window. That is itself
the empirical finding: the classical Gartley is a drawing-board pattern,
not a tradeable 1h-crypto system, at least not without relaxing the
ratios (which would no longer be the classical pattern). The −$216 is
two stopped-out trades, not a system result.

## Calibration note

Shipped exactly the specified parameters (±6% tolerance, 5-bar zigzag
confirmation, 2xATR stop / 4xATR target / 100-bar max hold, WARMUP=120).
A ±10% tolerance variant is reported in CALIBRATION.md — it finds 8
patterns (−$55 combined) instead of 2, still far too few to validate.
The classical ±6% spec stays; widening the tolerance to chase trade
count would be in-sample selection on an 8-trade sample.

## Mechanism

Zigzag: a bar is a swing high (low) when its high (low) is the extreme
over [i−5, i+5]; consecutive same-type extremes resolve to the most
extreme, so pivots strictly alternate. Per bar, only pivots confirmed
through bar i (index ≤ i−5) are visible — no lookahead. The last 5
confirmed pivots are tested as XABCD with the classical ratios above
(±6% on AB/XA and AD/XA; BC and CD checked against their textbook
ranges). Bullish: X low → A high → B low → C high → D low with
A>X, B<A, C>B, D<C, D>X; bearish mirrored. The "completion bar" is the
first bar where D's pivot confirms (5 bars after D prints) — a causal
necessity of the confirmed zigzag, documented here rather than hidden.
Long on bullish PRZ print, short on bearish; signal exits only on a
fresh opposite pattern; the 4xATR target / 100-bar max hold manage the
trade.

**Stop approximation:** the classical Gartley stop sits beyond X. The
backtest harness cannot express a pattern-anchored stop, so risk.py
uses a 2xATR hard stop as the executable proxy. On the two completed
trades this proxy stop is what exited both positions.

Source: Gartley pattern guide —
https://www.ebc.com/forex/gartley-pattern-explained-a-guide-to-this-powerful-setup

## Limitations

- Two trades: no statistical content; needs multi-year data or a
  relaxed-ratio variant to say anything about the edge.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- The 5-bar confirmation lag means entries print 5 bars after the true
  D extreme — the PRZ is already stale by execution.
- Stop-beyond-X is approximated by 2xATR; a true pattern stop would
  change every trade's risk profile.
- Single 7-month crypto window; no bull-market or multi-year sample.
