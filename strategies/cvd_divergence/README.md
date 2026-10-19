# CVD Divergence

Cumulative Volume Delta divergence on Hyperliquid 1h perps.

**Idea:** when price makes a lower low but the volume delta keeps
rising, sellers are exhausted — fade the move. CVD is built from the
close-location volume approximation (no tick data on 1h candles), and
divergence is measured at 10-bar price pivots against the nearest
earlier pivot within 60 bars.

**Signals:** long on bullish regular divergence (price lower low vs
CVD higher low); short on bearish divergence; exits on the opposite
divergence or a 3xATR chandelier trailing stop. 1% risk/trade.

**Status:** backtested 2026-03-14 → 2026-10-19 on BTC/ETH/HYPE — a
loser on all three (combined -$5,076), closest to breakeven on HYPE
(PF 0.86). Honest caveat: the "volume delta" is an approximation, not
measured order flow. See BACKTEST.md and CALIBRATION.md.
