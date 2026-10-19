# Murrey Math Octave Reversal

Mean-reversion off the Murrey Math octave grid. A trailing 64-bar
high/low frame is split into 8 equal octaves (L0=[0/8] … L8=[8/8]);
the 4/8 line is the pivot.

- **Long:** bar low touches the 0/8–1/8 zone and the close reclaims L1
- **Short:** bar high touches the 7/8–8/8 zone and the close loses L7
- **Exit:** 4/8 pivot reached, or the opposite extreme zone touched
- **Risk:** 2xATR hard stop, 80-bar max hold, 1% risk/trade, 3x leverage

See BACKTEST.md for the 2026-03-14 → 2026-10-19 Hyperliquid 1h
(BTC/ETH/HYPE) results and CALIBRATION.md for the 32/64/128-bar frame
sensitivity check.
