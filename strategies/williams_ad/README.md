# Williams Accumulation/Distribution

Larry Williams' A/D pressure series on Hyperliquid 1h perps.

**Idea:** accumulate buying/selling pressure bar by bar — up bars add
(close − true-range-low), down bars add (close − true-range-high) —
then trade the WAD crossing its 20-bar SMA, filtered by a 50-bar price
trend SMA.

**Signals:** long when price > SMA50 and WAD crosses above WAD-SMA20;
short mirrors; exit on the cross back. 2xATR stop, 60-bar max hold,
1% risk/trade.

**Status:** backtested 2026-03-14 → 2026-10-19 on BTC/ETH/HYPE — a
loser on all three (combined -$10,361, PF 0.60–0.75). The cross is too
lagging on 1h crypto. See BACKTEST.md for the full autopsy and
CALIBRATION.md for the SMA-window sweep.
