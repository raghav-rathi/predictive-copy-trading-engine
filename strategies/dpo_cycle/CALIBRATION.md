# Detrended Price Oscillator — Calibration

**Shipped:** DPO(21) = C − SMA(21)[i−11] (causal displacement),
zero-cross entries, 2xATR stop, 2.5xATR trail, 72-bar max hold.

**What the numbers say:** −$5,835 combined, 24.8% win rate. The causal
displacement turns DPO into a lagged momentum oscillator — the cycle
timing that makes textbook DPO useful lives in the centered average
we had to remove for causality. Entries fire mid-swing.

**Next experiment (only if revisited):** stop using DPO as a trigger
entirely; use it for cycle-length estimation as regime context for
other systems (e.g. scale max-hold by measured cycle length). The
indicator's value is descriptive, not predictive, in causal form.

**Do not:** "fix" it by shortening N — shorter N just makes it a
noisier momentum oscillator with extra steps.
