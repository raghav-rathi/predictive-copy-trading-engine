# Three-Line Break Turnaround

Turnaround entries on a three-line break chart built from 1h closes. A
new white line prints when the close exceeds the high of the last 3
lines during a black sequence (new black line on the mirror); otherwise
the close extends the developing line.

- **Long:** line direction flips −1 → +1 (bullish turnaround)
- **Short:** line direction flips +1 → −1 (bearish turnaround)
- **Exit:** the opposite flip
- **Risk:** 2xATR hard stop, 60-bar max hold, 1% risk/trade, 3x leverage

See BACKTEST.md for the 2026-03-14 → 2026-10-19 Hyperliquid 1h
(BTC/ETH/HYPE) results and CALIBRATION.md for the 2/3/4-line sensitivity
check.
