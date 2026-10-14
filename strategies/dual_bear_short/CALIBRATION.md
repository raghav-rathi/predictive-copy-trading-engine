# Dual-Bear Pullback Short — pullback-gate sweep calibration

Swept the pullback multiplier (trigger bar must close within
PULLBACK_ATR_MULT × ATR(14, 1h) below 4H EMA21) over {0.5, 1.0, 2.0} on
the same data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE,
2026-03-14 → 2026-10-10, 0.045%+0.01% costs, funding accrued, 1% risk,
$10k start, short-only). Monkeypatched module constant via a throwaway
script (`/tmp/dbs_sweep.py`, not committed); no strategy code changed.

| Pullback mult | Total signals/trades | Total net $ | BTC | ETH | HYPE |
|---|---|---|---|---|---|
| 0.5 (author) | 1 / 1 | −$12 | 0t / $0 | 1t / −$12 | 0t / $0 |
| 1.0 | 2 / 2 | −$122 | 1t / −$110 | 1t / −$12 | 0t / $0 |
| 2.0 | 14 / 11 | **+$429** | 6s/4t / −$320, WR 0% | 7s/6t / +$813, WR 33%, PF 3.77 | 1s/1t / −$64 |

## Takeaway

Shipped the author's 0.5x. The sweep shows the author's gate is too
selective to evaluate on a 7-month HL sample (1 trade), and loosening
it does not reveal a stable, transferable edge: at 2.0x the book is
+$429 but that is 6 ETH trades (PF 3.77 on 6 trades is noise) against
BTC going 0W–4L. The pullback multiplier is not a stable tuning knob
here — it trades off "no signal" against "noise". The author's 52
trades/7yr on OKX implies their effective trigger admitted far more
setups than this literal port does; without their exact ATR timeframe
for the pullback gate, the faithful port stays a no-signal system.
