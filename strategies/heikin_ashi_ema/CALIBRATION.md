# Heikin Ashi EMA — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| HA close | (open + high + low + close) / 4 | Standard Heikin Ashi definition. |
| HA open | (prev HA open + prev HA close) / 2, seeded (open + close) / 2 on bar 0 | Standard Heikin Ashi recursion; forward-only, no lookahead. |
| EMA filter | EMA(9) vs EMA(21), trend EMA(50) | The spec's filter: fast above mid and close above slow for longs. |
| Entry | state condition (HA bullish AND EMA9 > EMA21 AND close > EMA50), not a transition | The spec's wording ("Long when ..."); every qualifying bar signals entry, the harness enters when flat. |
| Exit | HA candle flips direction OR EMA(9)/EMA(21) cross turns against | The spec's exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | EMA(50) needs 50 bars; 60 gives margin. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped EMA 9/21/50** | **2895** | **-24287.26** | **0.51** | **10697.88** |
| Alt-A EMA 5/13/50 | 2901 | -24031.03 | 0.53 | 11138.76 |
| Alt-B EMA 9/21/100 | 2554 | -23008.23 | 0.52 | 10318.20 |

Per-coin, Alt-A: BTC -9035.16, ETH -8406.70, HYPE -6589.17.
Per-coin, Alt-B: BTC -8666.24, ETH -8015.76, HYPE -6326.23.
Faster EMAs and a stricter trend filter barely move the result —
the loss is driven by the state-entry + HA-flip-exit pairing
churning, not by the EMA lengths. Nothing was changed as a result
of the sweep. (Alt-B's EMA(100) is first valid at bar 99, so its
effective warmup is 99 bars despite WARMUP 60; entries before that
are blocked by NaN comparisons.)

## Spec decisions / ambiguities

1. **Entry is a state, not a transition.** The spec says "Long
   when HA close > HA open AND EMA(9) > EMA(21) AND close >
   EMA(50)" with no "crosses" language, so the shipped signals
   are True on every qualifying bar. This is the direct cause of
   the churn documented in BACKTEST.md (immediate re-entry after
   each HA-flip exit).
2. **HA high/low are not published.** Only HA open/close are
   needed by the signals; HA high/low would require the same
   recursion and add nothing to the entry/exit logic.
3. **HA open seed is (open + close) / 2 on bar 0**, the standard
   seed; its influence washes out within a few bars.
4. **Exit uses the current bar's HA direction and EMA ordering**,
   both known at the close, so the exit signal is causal.

## What the exits actually did

Shipped run (2,895 trades): 2,153 trades ended on a signal exit
(HA flip or EMA cross against) and 742 on the harness stop / trail.
The signal exit dominates — positions are exited almost as fast as
they are entered, which is the churn signature of pairing a
state entry with a per-bar flip exit.

No bug fixes requiring re-runs, no PnL-selected tuning.
