# Williams VIX Fix — Calibration

No parameter was tuned to PnL. Every parameter below was fixed a
priori from the spec, and the backtest numbers were reported as-is.
Two alternates were run after the fact as a robustness check only;
neither was adopted.

| Parameter | Value | A priori rationale |
|---|---|---|
| WVF lookback | 22 bars | Williams' original construction (highest close over 22 bars). |
| Upper band | SMA(20) of WVF + 2.0 x std(20) of WVF | Spec as written; sample std (ddof=1), matching the template's Bollinger construction. |
| Range high | 0.85 x max WVF over trailing 50 bars | Spec as written. |
| Green flash | WVF >= upper band OR WVF >= range high | Spec as written. |
| Inverted WVF | 100 x (high - lowest close over 22) / lowest close over 22, own band + range high | Mirror image of the WVF construction per the spec. |
| Entry | flash transition only (this bar AND NOT previous bar) | The spec's trigger; a flash that persists does not re-enter. |
| Exit | opposite flash, any bar (plus harness stop/trail) | The spec's exit. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 70 | WVF needs 22 bars; the band needs 20 WVF values (first at bar 40); the range high needs 50 WVF values (first at bar 70); 70 covers it exactly. |

## Sweep results (same window, local cache only)

| Config | Trades | Net $ | PF | Fees $ |
|---|---|---|---|---|
| **Shipped WVF22 / band 20, 2.0 / range 50, 0.85** | **1313** | **-8283.67** | **0.83** | **8074.14** |
| Alt-A band_k 1.5 | 1481 | -11466.79 | 0.78 | 8649.43 |
| Alt-B WVF14 / band 14 / range 30 | 1592 | -14758.17 | 0.72 | 9294.93 |

Per-coin, Alt-A: BTC -5280.94, ETH -2699.95, HYPE -3485.90.
Per-coin, Alt-B: BTC -5496.63, ETH -6058.54, HYPE -3202.99.
Both alternates trade more often and lose more — loosening the band
or shortening the lookback only adds fee-churn. Nothing was changed
as a result of the sweep.

## Spec decisions / ambiguities

1. **Std is the pandas sample std (ddof=1).** Williams' original
   work does not pin down the estimator; the template's Bollinger
   construction uses the same convention.
2. **Flash is False while bands are undefined** (first 21 bars for
   WVF, range high first defined at bar 70), so no entry can occur
   before the range high exists — entries effectively start at bar 70.
3. **A flat/zero-volatility regime collapses the band to the WVF
   level** (std 0, range high 0.85 x WVF), so flashes can be
   near-constant there; the transition-only entry rule is what keeps
   that from re-entering every bar. Real 1h crypto data is never
   exactly flat, so this is a test-only edge case.
4. **Exit is any opposite flash bar, not a transition.** A long
   exits on the first inverted-flash bar even if the inverted flash
   was already active when the long was entered.

## What the exits actually did

Shipped run (1313 trades): 811 trades ended on the harness stop /
trail and 502 on the opposite-flash signal. The signal exit is
active here (unlike squeeze-style strategies), but it does not
produce a positive expectancy — the entries have no edge before
fees (gross PnL about -$210) and fees do the rest.

No bug fixes requiring re-runs, no PnL-selected tuning.
