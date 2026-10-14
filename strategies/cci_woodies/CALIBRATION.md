# Woodies CCI — hook-threshold sweep calibration

Swept the extreme threshold HOOK over {80, 100, 150} on the same
data/costs/sizing as BACKTEST.md (HL 1h, BTC+ETH+HYPE, 2026-03-14 →
present, 0.045%+0.01% costs, 1% risk, $10k start). Monkeypatched the
module constant via a throwaway script (`/tmp/sweep_cci.py`, not
committed); no code change in the strategy itself.

| Hook | Trades | Combined net $ | BTC net / Sharpe | ETH net / Sharpe | HYPE net / Sharpe |
|---|---|---|---|---|---|
| ±80 | 1,389 | −$9,843 | −$4,791 / −3.06 | −$5,897 / −5.06 | +$844 / +0.66 |
| ±100 | 1,176 | −$8,612 | −$5,016 / −4.15 | −$5,482 / −4.78 | +$1,886 / +1.22 |
| ±150 | 678 | −$4,366 | −$3,448 / −3.12 | −$3,593 / −3.40 | +$2,674 / +1.91 |

## Takeaway

**Shipped the classic ±100.** The improvement with tighter filtering is
monotonic and real — fewer, more extreme hooks lose less on BTC/ETH and
win more on HYPE — but it does not create a stable winning region:
BTC/ETH stay deeply negative at every threshold. ±150 is "dramatically
better" in magnitude (−$8,612 → −$4,366) yet still a combined loser, so
switching the shipped config would just be a better-dressed loss. The
±100 line is also definitional to Woodies' system (the 0.015 constant is
calibrated around it). The honest read: the mechanism wants rarer
entries than any classic CCI parameterization gives on 1h crypto —
HYPE-only follow-up, or a slower timeframe, is the direction worth
testing next.
