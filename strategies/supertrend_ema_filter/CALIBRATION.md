# Supertrend + EMA(200) Filter — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Supertrend period / multiplier | 10 / 3.0 | Seban's standard Supertrend, identical to the existing `supertrend` strategy in this repo (shared primitive). |
| Regime filter | EMA(200) on close | Long-horizon trend line; 200 bars ≈ 8.3 days on 1h bars, the standard long-trend horizon. |
| Entry gate | long only if close > EMA(200); short only if close < EMA(200) | Trade Supertrend flips only with the long-horizon regime. |
| Exits | Supertrend flip back, ungated by EMA(200) | Exits are trend-state changes; the filter is an entry gate only (documented choice, fixed a priori). |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 250 | EMA(200) needs 200 bars + margin; also covers Supertrend's ATR(10) start-up. |

## Spec deviations

1. **Batch-standard risk, not the parent's risk.** The parent
   `supertrend` strategy uses a 2.5xATR stop, 3.0xATR trail and no
   max hold. This variant uses the batch-standard 2.0x stop, 2.5x
   trail and 120-bar max hold per the batch brief, so its backtest
   is comparable with the rest of batch 33. The signal logic itself
   is unchanged from the parent.
2. **EMA(200) is an EMA, not the SMA(200) of the classic Connors-style
   regime filter.** The spec names EMA(200); the shared
   `strategies.base.ema` primitive was used, consistent with the
   batch convention for trend filters.
3. **Exits ignore the EMA filter.** The spec says entries are gated
   by the regime; it does not gate exits, so a flip back exits even
   if price is still on the "right" side of EMA(200). This keeps
   exits purely trend-state driven.

No bug fixes requiring re-runs, no PnL-selected tuning.
