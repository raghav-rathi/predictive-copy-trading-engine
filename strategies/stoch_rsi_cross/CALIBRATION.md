# Stochastic RSI Crossover — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| RSI | RSI(14) of close (Wilder) | Chande & Kroll StochRSI base input. |
| Stochastic window | 14 bars of RSI | Canonical StochRSI(14, 14) lookback. |
| %K | 100 x (RSI − min RSI last 14) / (max RSI last 14 − min RSI last 14); zero-range window scores 50; clipped to [0, 100] | Batch spec; zero-range guard per spec, clip against float error (raw ratio can print 100.00000000000001). |
| %D | SMA(3) of %K | Batch spec; StochRSI(14, 14, 3, 3) smoothing. |
| Long entry | %K crosses up through %D while %K < 20 (transition only) | Batch spec; oversold-zone cross. |
| Short entry | %K crosses down through %D while %K > 80 (transition only) | Batch spec; overbought-zone cross. |
| Long exit / short exit | %K crosses down / up through %D | Batch spec; opposite cross. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 40 | RSI window (14) + stochastic window (14) + %D smoothing (3) = first %D at bar 15; 40 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped StochRSI(14,14,3,3)** | **1493** | **-14863.94** | **0.48** | **8664.52** |
| Alt-A stochastic window 10 | 1475 | -14313.41 | 0.52 | 8959.59 |
| Alt-B %D SMA(5) | 969 | -11982.20 | 0.48 | 6244.49 |

Per-coin, Alt-A: BTC -5781.87, ETH -3718.30, HYPE -4813.24.
Per-coin, Alt-B: BTC -4481.34, ETH -3266.60, HYPE -4234.27.
Both alternates lose less than the shipped config but still lose
heavily on every coin (best case −$11,982.20, PF 0.48). A slower
%D cuts the trade count by a third and the loss by ~19%, which
points at churn as the mechanism, but no alternate turns the
strategy green — and neither was adopted, since the spec shipped
as written and the alternates were robustness checks only.

## Spec decisions / ambiguities

1. **%K is the raw stochastic value, %D is SMA(3) of %K.** Some
   platforms smooth the raw stochastic into %K with a 3-bar SMA
   and smooth again into %D (i.e. %K = SMA3(raw), %D = SMA3(%K)).
   The batch spec defines %K directly as the 100 x (RSI − min) /
   (max − min) value and %D as SMA(3) of %K, so that ships. The
   smoothed-%K variant would lag one step further and trade even
   less often (directionally like Alt-B, which still loses).
2. **Zero-range window scores 50, not 0 or 100.** Per spec. A flat
   RSI window (e.g. flat closes, RSI = 0) therefore sits at %K =
   50, %D = 50, and generates no cross.
3. **Entry requires the cross AND the zone on the same bar.**
   A cross that happens while %K is mid-range (20–80) is not an
   entry, though it is still an exit for the opposite side.
4. **base.rsi fills pre-window values with 0.0** (no gains yet),
   so %K is first defined at bar 13 rather than bar 26; WARMUP 40
   still covers it with margin.

## What the exits actually did

Shipped run (1,493 trades): 1,296 trades ended on the opposite
%K/%D cross and only 197 on the harness stop/trail. Positions
barely survive past the entry bar — the exit cross fires almost
as fast as the entry cross, so the strategy pays the round-trip
fee on nearly every RSI wiggle.

No bug fixes requiring re-runs, no PnL-selected tuning.
