# Clenow Trend Following — Calibration

No parameter sweep was run. Every parameter below was fixed a priori
from the spec, and the backtest numbers were reported as-is.

| Parameter | Value | A priori rationale |
|---|---|---|
| Trend filter | EMA(1200) vs EMA(2400) of close | Clenow's 50-day / 100-day EMAs, 1 day = 24 bars on 1h data. Bullish when fast > slow, bearish when fast < slow. |
| Breakout window | 1200 bars (50 days) | Clenow's 50-day extreme. |
| Long entry | Close breaks above the prior 1200-bar high of `h` while bullish | Closest faithful version of the book's "new 50-day high in the trend direction" (see deviation below). |
| Short entry | Close breaks below the prior 1200-bar low of `l` while bearish | Mirror image of the long entry. |
| Signal exit | Opposite breakout (long exits on a new 1200-bar low while bearish, and vice versa) | Book's breakout-reversal exit; the trailing stop does most exiting in practice. |
| ATR window | 720 bars (30 days) | 30-day ATR, the book's volatility scale. |
| Stop / trail | 3.0x ATR / 3.0x ATR | Clenow's 3x ATR trailing stop; the hard stop is set to the same distance. |
| Target / max hold | None / None | Clenow lets winners run until the trailing stop or the opposite breakout. |
| Risk / leverage | 1% risk per trade, 3x max leverage | Batch-standard risk layer. |
| Fees / slippage | 0.045% / 0.01% per side | Hyperliquid base taker fee + slippage. |
| WARMUP | 2400 bars | The 100-day slow EMA must be fully formed before any signal. |

## Spec deviation (one, and it matters)

**Entry comparison window.** The brief's literal rule — close makes a
new 1200-bar high where the extreme is the rolling max of `h`
*including the current bar* (`close == max high of last 1200 bars
incl. current`) — is degenerate on OHLC data: close <= high on every
bar, so it can only fire when the current bar both sets the 1200-bar
high and closes exactly on it. Verified on the window: it fired **0
times in 17,323 bars** across BTC/ETH/HYPE (close == high on only
59/70/55 bars, and none of those bars set the 1200-bar high). A
zero-trade strategy is not a faithful implementation of a system
whose whole point is to trade 50-day breakouts.

Implemented instead: the close is compared against the **prior**
1200 bars' extreme — long when `close > max high of the previous
1200 bars`, short when `close < min low of the previous 1200 bars`.
Same series (highs/lows), same 1200-bar window, same trend filter;
this is the standard Donchian-breakout definition and the closest
faithful version. It fires 6/4/19 long signals and 1/0/0 short
signals (BTC/ETH/HYPE) before the harness's warmup/flat filters,
producing 3/3/11 executed trades.

**Trend filter strictness.** Bullish is defined as fast EMA strictly
above slow EMA and bearish as strictly below; equal EMAs (flat
price) are neither, so a flat market generates no entry. This follows
from the book's cross-based filter and avoids spurious shorts on
flat data where the close sits on both Donchian edges.

No other spec corrections were needed. The implementation was verified
against hand-computed cases: the EMA recurrence matches an
independent loop to 1e-6, Donchian extremes match hand-computed
values including the peak-pinning behaviour, and the flat-price,
uptrend, and no-lookahead tests all pass.

No bug fixes requiring re-runs, no PnL-selected tuning.
