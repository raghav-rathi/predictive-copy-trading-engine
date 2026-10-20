# Cup and Handle Breakout — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,276 bars BTC/ETH, 5,274 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=320 bars.

## Results (shipped config: 1.4x volume confirmation, 1.5xATR stop,
4.0xATR target, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 0 | — | $0 | +0.0% | +0.00 | 0.0% | $0.00 | — |
| ETH | 0 | — | $0 | +0.0% | +0.00 | 0.0% | $0.00 | — |
| HYPE | 0 | — | $0 | +0.0% | +0.00 | 0.0% | $0.00 | — |
| **Combined** | **0** | — | **$0** | — | — | — | — | — |

## Verdict: no-trade — the specified filters are mutually exclusive on 1h crypto

Zero setups on all three coins across 15,826 bars. This is not a code
bug (verified by filter diagnostics): the specified cup-depth rule
requires depth between 8–25% of the rim price AND between 1–4x ATR(14),
and on 1h crypto those two bands do not overlap — median cup depth on
BTC is ~20x ATR (p10–p90: 12x–41x), so the ATR band alone rejects 100%
of candidates. The depth-percentage band alone passes ~40% of
candidates; the ATR band passes none. O'Neil's pattern was specified
for daily bars, where a 15–20% cup is 2–4x the daily ATR; on 1h bars
the same percentage cup is an order of magnitude more ATRs. As
specified, the strategy cannot trade this timeframe — an honest
no-trade, not a hidden loss.

## Calibration note

The one-knob sweep (breakout volume 1.2x/1.4x/1.6x the 20-bar average)
is in CALIBRATION.md: all three settings produce 0 trades on all coins,
so the knob is moot — the binding constraint is the dual depth filter,
documented above. Relaxing the ATR band would be a redesign decision
for walk-forward work, not an in-sample tweak; the shipped config stays
exactly as specified.

## Mechanism

Prior uptrend (close > SMA50 for 30 bars); left rim = highest high in
300 bars; bottom = lowest low after the rim; cup 60–300 bars, depth
8–25% and 1–4x ATR; right rim within 5% of the left rim; handle ≤ 1/3
of cup duration, low in the cup's upper half, depth ≤ 1/3 of cup depth;
entry on a close above the handle high with volume > 1.4x the 20-bar
average. Pattern complete by bar j−1, breakout on bar j. Long-only.

Source: Cup and Handle (O'Neil, via ebc.com) —
https://www.ebc.com/forex/cup-and-handle-pattern-how-to-use-in-forex-trading

## Limitations

- Zero trades: no empirical read on the pattern's edge at all — the
  verdict is about the specification, not the pattern.
- The dual depth constraint (8–25% AND 1–4 ATR) is the binding
  filter; on 1h crypto it admits nothing. A timeframe-aware
  reformulation (e.g. depth in ATR only, or daily bars) is the honest
  next step, out of sample.
- Single 7-month window; HYPE history starts 2026-03-15.
- Funding unmodeled; next-bar-open execution vs idealized entry.
