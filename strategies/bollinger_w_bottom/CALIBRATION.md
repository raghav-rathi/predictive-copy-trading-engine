# Bollinger W-Bottom / M-Top — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Bollinger Bands | BB(20, 2.0), SMA mid, sample SD (ddof=1) | Bollinger's standard; shared `strategies.base.bollinger` primitive, same %B convention as `bollinger_pctb` (zero-width band → %B = 0.5). |
| First low / high | %B < 0 / %B > 1 | Price closed outside the band — the panic spike. |
| Rally / dip | close crosses the middle band | The intervening bounce / fade of the W / M. |
| Second low / high window | within 40 bars of the rally / dip | Spec's window; also the staleness bound for the whole pattern. |
| Second low / high price | lower than or within 1% of the first low's close (mirror for highs) | Spec's tolerance; the retest may print marginally lower. |
| Second low / high %B | strictly higher (long) / lower (short) than the first low's / high's %B | The divergence: same price, weaker push relative to volatility. |
| Entry | first close above / below the middle band after the second low / high | Spec's confirmation. |
| Exits | close below / above the middle band | Back across the middle band: the reversal leg has failed. |
| ATR window / stop / trail / target / max hold | 14 / 2.0x / 2.5x / None / 120 bars | Batch-standard risk layer. |
| Risk frac / leverage / fees / slippage | 0.01 / 3.0x / 0.00045 / 0.0001 | Batch-standard risk layer. |
| WARMUP | 60 | BB(20) needs 20 bars; 60 bars of margin before any signal can fire. |

## Spec deviations

1. **Confirmation is the middle-band close, not the intervening
   high/low.** Bollinger's classic confirmation is a close above the
   high of the bounce between the two lows (below the low of the dip
   for M-tops). The spec explicitly defines entry as the first close
   above/below the middle band after the second low/high, and that
   was implemented exactly.
2. **40-bar staleness bounds.** The spec gives 40 bars for the
   second low ("within 40 bars of the rally") and for the first low
   ("within the last 40 bars"). The same 40-bar bound was applied to
   the rally wait (first low older than 40 bars is dropped) and to
   the confirmation wait (no close across the middle band within 40
   bars of the second low/high drops the pattern), so stale patterns
   cannot fire months later. These are mechanical choices, fixed a
   priori.
3. **Most-extreme low/high wins.** While waiting for the rally, a
   bar with a more extreme %B supersedes the recorded first low/high
   rather than starting a parallel pattern. This keeps one live
   pattern per side and matches the "first low" being the panic
   extreme.
4. **Lows/highs are measured on closes.** The spec's price
   comparison ("whose price is lower than or within 1% of the first
   low's price") is evaluated on closes, consistent with %B also
   being close-based. Intraday lows (bar `l`) are not used.
5. **No swing-low confirmation.** The pattern does not require the
   lows to be confirmed local swing lows (e.g. lower than neighbours);
   the %B-extreme + price + divergence conditions define the lows.

No bug fixes requiring re-runs, no PnL-selected tuning.
