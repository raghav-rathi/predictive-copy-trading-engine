# Wilder Swing Index / ASI — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-18
(~5,224 bars each). Note: the batch brief's ms window constants were stamped
2025 (they filtered to an empty frame against 2026 data); corrected by +365d
to the intended 2026 window. Cache rows deduplicated in-memory (5 identical
overlap rows per file from cache-extension appends; cache files untouched).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: Wilder SI per bar, ASI = cumsum(SI), long on ASI break above prior 20-bar high / short below prior 20-bar low, exit on opposite break, 2xATR stop, 48-bar max hold, WARMUP=60)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 216 | 27.8% | -$3,449 | -34.5% | -2.03 | -39.0% | -$15.97 | 0.73 |
| ETH | 212 | 25.9% | -$2,027 | -20.4% | -0.92 | -30.8% | -$9.56 | 0.84 |
| HYPE | 209 | 30.1% | -$1,856 | -18.6% | -0.97 | -25.4% | -$8.88 | 0.83 |
| **Combined** | **637** | **27.9%** | **-$7,333** | — | — | — | -$11.51 | — |

## Verdict: LOSER

Loses on every coin: −19% to −34%, profit factors 0.73–0.84, win rates
26–30%. The 20-bar ASI breakout is a pure momentum-chase entry — it buys
the top of the last 20 bars' worth of accumulated swing, and on 1h crypto
that breakout is more often exhaustion than continuation. With a 26–30%
win rate, the 2xATR stop and per-side costs need fat tails to compensate;
the tails are not fat enough (PF < 0.85 everywhere). Honest read: the
classic Wilder breakout rule does not survive 1h crypto chop.

## Calibration note

Shipped exactly the specified parameters (standard Wilder SI, ASI 20-bar
breakout entries, opposite-break exits, 2xATR stop, 48-bar max hold,
WARMUP=60). The one-variant sweep (breakout window 20 → 30) is reported in
CALIBRATION.md — smaller losses, still negative on all three coins. No
further tuning attempted; the edge itself is absent, not mis-sized.

## Mechanism

Per bar: Wilder Swing Index SI = 50 x [(C − Cy) + 0.5(C − O) + K(T − Cy)] / R,
Cy = previous close; K = 0.5 x (max(H,Cy) − min(L,Cy)) / (H − L) (0 if H == L);
T = H if (H − Cy) > (Cy − L) else L; R = (H − Cy) − 0.5(L − Cy) + 0.25(Cy − O)
if (H − Cy) > (Cy − L), = (Cy − L) − 0.5(H − Cy) + 0.25(Cy − O) if
(Cy − L) > (H − Cy), else (H − L) + 0.25(Cy − O); SI = 0 when R = 0.
ASI = cumulative sum of SI. Long when ASI exceeds its prior 20-bar high
(rolling max of the previous 20 ASI values, current bar excluded); short
when ASI falls below its prior 20-bar low; exit on the opposite break.
2xATR hard stop, 48-bar max hold, no trailing, no target.

**Formula note (verified, not assumed):** the brief's SI transcription
("[(C−O)+0.5(C−O)+K(T−L)+L(R)]/R") is garbled — the "+L(R)" term would add a
constant +50 per bar and degenerate the system into always-long. The
canonical Wilder form above was verified two ways: (1) eSignal's own ASI
EFS source (the brief's cited reference) contains no such constant term,
and (2) a limit-up day (O = Cy, C = H = Cy + limit) scores exactly +100
(limit-down −100) under the canonical form — Wilder's documented
calibration, confirmed by unit test.

Source: J. Welles Wilder, *New Concepts in Technical Trading Systems*
(1978) — Swing Index / ASI —
https://efs.kb.esignal.com/hc/en-us/articles/6362864171547-Accumulation-Swing-Index-ASI

## Limitations

- Single 7-month crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- "Significant high/low" in Wilder's original is discretionary; the fixed
  20-bar window is the mechanical proxy (30-bar variant in CALIBRATION.md).
- 1h bars only; Wilder designed the system for daily bars.
