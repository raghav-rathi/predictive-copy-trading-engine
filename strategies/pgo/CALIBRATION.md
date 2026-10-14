# Pretty Good Oscillator — Calibration

**Shipped:** PGO = (C − SMA(14))/ATR(14); long on cross above +1.0,
short below −1.0; exit on zero cross back; 2xATR stop, 3xATR trail.

**What the numbers say:** −$4,785 combined — least-bad loser in the
batch. HYPE +6.8% (Sharpe 0.54, 37.1% WR, the batch's best win rate)
suggests the thrust-catch mechanism has something; BTC −40.9% says 1h
thrusts mean-revert more than they extend. The zero-line exit is the
suspect: it exits exactly when the thrust's edge is realized.

**Next experiment:** asymmetric exits — replace the zero-line exit
with a 2xATR chandelier trail from the thrust extreme, so winners can
extend. Keep the ±1.0 entries; they are the sound half. Also worth a
4h-bar run, where thrusts persist longer.

**Do not:** lower the entry level to ±0.5 for "more trades" — the
selectivity of ±1.0 is the edge; diluting it just adds chop.
