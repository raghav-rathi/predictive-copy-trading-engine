# Golden Cross / Death Cross — Calibration

All parameters were fixed **a priori** from the classic
50/200-day construction, translated to 1h bars — there is no
in-sample sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| Fast / slow averages | SMA(50) / SMA(200) | the canonical Golden Cross pair; on 1h bars this is ~2 days vs ~8 days — the same ratio, compressed |
| Filters | none | the cross is itself the filter: neither average moves fast enough to whipsaw, so a confirmation filter would only add lag to an already-lagging signal |
| ATR window | 14 | canonical |
| Stop | 2.0×ATR | a regime trade needs room — a 1.5×ATR stop would be shaken out by the same chop the cross filters out |
| Trail | 3.0×ATR chandelier | wide, to ride the regime leg; the cross is slow in and should be slow out |
| Max hold | 240 bars (~10 days) | a cross that hasn't paid within ten days on 1h bars is a failed regime call, not a slow winner |
| Risk | 1% / trade, 3× leverage cap | house standard |

The design bet is that the 50/200 cross's famous lag is a
feature on 1h bars: it fires rarely (95 trades across three
coins in ~7 months) but only on genuine regime changes. The
backtest (BACKTEST.md) tests exactly that bet — and on this
window it fails: the rare signals are mostly stopped out
(93 of 95 trades exit on the stop), and the one green leg
(HYPE, +$560) is too small to carry the system. Rarity did
not buy quality here.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers.
