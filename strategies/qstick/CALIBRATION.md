# Qstick — Calibration

**Shipped:** SMA(8) of (close−open), zero-cross entries, 2xATR stop,
2.5xATR trail, 96-bar max hold.

**What the numbers say:** −$17,746 combined, 2,571 trades, 26.6% win
rate. The zero cross of an 8-bar body average is a noise trigger on
1h — it fires on every minor drift reversal. No coin, no regime, no
parameter saves a trigger this indiscriminate.

**Next experiment (only if revisited):** demote Qstick from trigger
to filter — e.g. require Qstick > 0 for longs of a slower breakout
system. As a bias gauge it is fine; as an entry trigger it is dead.

**Do not:** lengthen N hoping for fewer whipsaws — longer N just
makes it a worse, later version of a moving-average cross.
