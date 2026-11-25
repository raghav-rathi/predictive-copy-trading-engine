# Chaikin VWAP Combo — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=30 bars.

## Results (shipped config: CMF(20) zero-cross with close on the
VWAP side, exit on CMF zero-cross back or VWAP cross against
the position, 2xATR stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 484 | 25.2% | -$6,704 | -67.0% | -7.84 | -67.4% | -$13.85 | 0.39 |
| ETH | 439 | 28.2% | -$4,250 | -42.5% | -3.56 | -47.7% | -$9.68 | 0.60 |
| HYPE | 427 | 33.3% | -$1,413 | -14.1% | -1.01 | -25.9% | -$3.31 | 0.87 |
| **Combined** | **1,350** | **28.7%** | **-$12,368** | — | — | — | -$9.16 | — |

Fees: BTC $3,420, ETH $2,803, HYPE $2,067 (total $8,289).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: the worst loser of my three by a wide margin — a CMF zero-cross chop machine

Combined -$12,368 on 1,350 trades. The mechanism is the
problem, not the market: CMF(20) on 1h bars oscillates around
zero constantly — every minor shift in where closes land in
their ranges flips the sign — and each flip is a trade that
pays $8,289 in fees across the three coins. The VWAP filter
does not save it: on 1h bars the close crosses the day VWAP
all day long, so the "confirmation" is nearly always satisfied
on one side or the other. BTC loses two-thirds of the account
(-67.0%, Sharpe -7.84, MaxDD -67.4%), ETH nearly half
(-42.5%), HYPE the least bad (-14.1%, PF 0.87). Win rate
25.2–33.3%, profit factor 0.39–0.87 on every coin. There is no
coin, no sub-period, no reading in which the shipped config
works on this window: it is a chop machine, and the chop is
the trade.

## Calibration note

Shipped the specified CMF window 20. A 10/20/40 CMF-window
sweep on this batch-46 window is in CALIBRATION.md: 40 is
less negative combined (-$8,163, 903 trades) but still deeply
negative on every coin, and 10 is worse (-$14,395, 1,900
trades). The 20 config was fixed before any backtest was run;
no in-sample adoption — the shipped config stays 20 and the
verdict stays: loser.

## Mechanism

Money Flow Multiplier = ((Close − Low) − (High − Close)) /
(High − Low), 0 when High == Low; Money Flow Volume =
multiplier × volume; CMF(20) = 20-bar sum of MFV / 20-bar sum
of volume. Session VWAP is the UTC-day anchored VWAP from
base.anchored_vwap. Long on CMF crossing above zero with close
above day VWAP; short on CMF crossing below zero with close
below day VWAP. Exit when CMF crosses back through zero or
the close crosses the day VWAP against the position. The
harness 2xATR hard stop / 3xATR chandelier trail sit behind
the signal exits as a safety net for gap-through moves;
60-bar max hold.

Source: Marc Chaikin, Chaikin Money Flow (StockCharts
ChartSchool) —
https://school.stockcharts.com/doku.php?id=technical_indicators:chaikin_money_flow_cmf
(verified via search 2026-11-25; the three-step formula and
the 20-period default are as documented there and in the TTR
CMF reference, which cites the same ChartSchool page).

## Limitations

- Single ~8.4-month crypto window; 1,350 trades — the failure
  is overwhelming and consistent, not a sample-size artefact.
- CMF(20) zero-crosses far too often on 1h crypto: the
  indicator oscillates around zero and every cross is a
  round-trip fee. The system as shipped is structurally
  unsuited to this timeframe.
- The calibration sweep shows a longer CMF window helps a lot
  in-sample (40 → -$8,163 combined) — but adopting it would
  be in-sample selection, and it is still deeply negative on
  every coin.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped CMF window on this window.
