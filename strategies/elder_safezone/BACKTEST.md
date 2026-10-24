# Elder SafeZone — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range, no slicing: BTC 5,335 bars and ETH
5,335 bars from 2026-03-14 22:00 UTC, HYPE 5,333 bars from
2026-03-15 00:00 UTC, all to 2026-10-22 23:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2.0xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: EMA(22) cross + above/below the
SafeZone line, SafeZone-break exit, 2.0xATR stop, 2.5xATR
chandelier trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 410 | 30.7% | -$5,054 | -50.5% | -4.81 | -53.8% | -$12.33 | 0.61 |
| ETH | 406 | 30.5% | -$2,175 | -21.8% | -1.51 | -36.4% | -$5.36 | 0.84 |
| HYPE | 386 | 35.2% | -$1,415 | -14.1% | -0.88 | -21.6% | -$3.67 | 0.89 |
| **Combined** | **1,202** | **32.1%** | **-$8,644** | — | — | — | -$7.19 | — |

Fees: BTC $3,515, ETH $3,408, HYPE $1,740 (total $8,663).
Net % is the harness equity-curve return per leg; combined
net $ is the sum of per-leg trade PnL.

## Verdict: a clear loser on all three legs

Combined -$8,644 across 1,202 trades, 32.1% win rate, profit
factor below 1.0 on every leg (0.61 / 0.84 / 0.89). BTC is the
worst leg (-$5,054, Sharpe -4.81, max drawdown -53.8%) despite
the SafeZone being a trend system — the EMA(22) cross fires
constantly on 1h bars, and the SafeZone condition barely
filters anything: in any sustained move the line trails far
enough behind price that "still above the line" is nearly
always true, so the entry is close to a bare EMA cross with a
slightly delayed exit. The SafeZone-break exit then guarantees
the loss is realized quickly: every range flicker that
triggered entry breaks the line within a few bars, paying
~0.055% round-trip cost for the privilege, and the 2.0xATR
stop rarely gets a chance to matter because the line exits
first.

The deeper problem is structural. Elder designed the SafeZone
as a *stop* for trades entered on other grounds (his triple
screen, his impulse system) — it was never an entry system.
Bolting an EMA cross onto it as the entry inverts the design:
the stop line is doing exit duty it was built for, but the
entry has no edge of its own, so the system inherits the
whipsaw rate of a 22-bar EMA cross on hourly crypto and pays
full fees on every flicker.

Honest read: as specified this is not tradeable. If the idea
is revisited, the SafeZone should return to its intended role
— a trailing exit for entries with their own edge — and any
such pairing must be validated on walk-forward data, not this
window (see CALIBRATION.md: no in-sample tuning was performed).

## Mechanism

EMA(22) of close; SafeZone long = highest low of last 10 bars
minus 2.5x the mean counter-trend penetration (mean over last
10 bars of max(0, prev_low - low)); short line mirrored off
the highs. Long: close crosses above EMA(22) while above the
SafeZone long line; short: mirror. Exit: close below/above the
respective SafeZone line. 2.0xATR stop, 2.5xATR chandelier
trail, 96-bar max hold. All params fixed a priori; no
optimization.

Sources: https://www.incrediblecharts.com/indicators/safezone.php

## Limitations

- Single 7-month crypto window; all three legs negative.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
