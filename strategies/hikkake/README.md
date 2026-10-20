# Hikkake False-Breakout

Daniel L. Chesler's hikkake ("to trick, trap, or ensnare", Active Trader
Magazine, April 2004): a false-breakout pattern built on an inside bar.

- **Inside bar:** `h < h[1]` AND `l > l[1]`
- **Bullish setup:** inside bar at bar i−1, then bar i prints a **lower
  low AND lower high** than the inside bar → a failed breakdown. Long
  when a close prints back **above the inside bar's high** within 3 bars
  (the trapped shorts covering).
- **Bearish setup:** inside bar at i−1, then bar i prints a **higher
  high AND higher low** → a failed breakout. Short when a close prints
  back **below the inside bar's low** within 3 bars.
- The trap bar's own close can confirm (the false-move bar often snaps
  back the same bar). Unconfirmed traps expire after 3 bars.
- **Exits:** opposite-direction confirmation is a structural exit; the
  harness adds a 1.5xATR stop, 3.0xATR target (2R), 20-bar max hold.
- **Risk:** 1% equity risk/trade, 3x leverage cap, 0.045% fee + 0.01%
  slippage per side.

See BACKTEST.md for the 2026-03-14 → 2026-10-20 Hyperliquid 1h
(BTC/ETH/HYPE) results — this one is an honest loser — and
CALIBRATION.md for the confirmation-window sensitivity check.
