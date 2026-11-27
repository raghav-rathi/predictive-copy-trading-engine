# Keltner Mean Reversion

A Keltner-channel fade in the Linda Raschke style: price
stretched to a 2.0x ATR band is expected to snap back to
the mean (the EMA midline), and the entry waits for the
first sign of that snap on the tag bar itself.

- **Keltner channel:** EMA(20) midline, ATR(10) bands at
  k=2.0 -- kc_mid / kc_upper / kc_lower (house
  `base.keltner`); ATR(14) also computed for the risk layer
- **Long:** the close CROSSES BELOW the lower band AND the
  entry bar is a bullish candle (close > open)
- **Short:** the close CROSSES ABOVE the upper band AND
  the entry bar is a bearish candle (close < open)
- **Exit:** long exits when the close crosses above the
  midline, short when it crosses below the midline, or on
  the opposite entry
- **Risk:** 2xATR hard stop, 3xATR chandelier trail,
  72-bar max hold, 1% risk/trade, 3x leverage

Parameters: EMA 20, ATR 10, k=2.0. Entries are cross-based
(the close must cross the band on the entry bar, not
merely sit beyond it), so a band tag fires once per
crossing, not every bar price stays outside the band.

Structural finding, documented (see BACKTEST.md): as
specified, this strategy fires ZERO trades on 1h crypto.
The band crosses happen (126/117/138 lower-band crosses
and 111/114/138 upper-band crosses across BTC/ETH/HYPE in
the batch-48 window), but the candle-direction filter
never coincides with one: 0 of 381 lower-band crosses are
bullish candles, 0 of 363 upper-band crosses are bearish
candles. On 24/7 crypto the open chains to the prior close,
so a bar that closes across a band is by construction a
directional bar in the crossing direction (close below the
open on a down-cross). The candle filter and the cross are
nearly mutually exclusive on 1h bars. The rule is shipped
exactly as specified -- the filter was NOT dropped to make
it fire (a diagnostic without the filter also loses,
-$5,296 on 592 trades; see CALIBRATION.md).

Sources: Keltner channel strategy --
https://www.loomiai.io/learn/keltner-channel-strategy-backtest/

Usage:

```python
from strategies.keltner_mean_reversion import indicators, signals, risk

df = indicators.add_indicators(df)  # k=2.0 default
sig = signals.add_signals(df)
```

See BACKTEST.md for the 2026-03-14 → 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-48 pinned window) results and
CALIBRATION.md for the band-multiplier 1.5/2.0/2.5
sensitivity check.
