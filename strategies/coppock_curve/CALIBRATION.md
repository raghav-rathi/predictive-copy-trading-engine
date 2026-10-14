# Coppock Curve — Calibration

**Shipped:** WMA(10) of ROC(14)+ROC(11), zero-cross entries, 2xATR stop,
3xATR trail, 720-bar max hold.

**What the numbers say:** HYPE +50.2% (Sharpe 2.61, 220 trades) vs
BTC −21.4% / ETH −14.1%. The 720-bar hold is doing real work on HYPE —
average winning hold stretches into multi-day trends. On BTC/ETH the
same hold just extends whipsaw losses; MaxDD −31.6% on BTC comes from
holding losers, not from the entries.

**Next experiment:** slope-gate the cross — require the curve to be
rising (3-bar slope > 0) at the long cross. The BTC/ETH losses cluster
in crosses that fire while the curve is still falling through zero
(late momentum flips); a slope gate should cut those without hurting
HYPE's clean regime flips.

**Do not:** lengthen the ROC legs — the indicator is already the
slowest in the batch; slower just means later.
