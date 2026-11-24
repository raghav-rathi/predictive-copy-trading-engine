# Three-Bar Reversal — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
window ms `[1773525600000, 1795525200000)` (2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC, exclusive): 6,111 bars BTC/ETH, 6,109 HYPE.
Last closed bar 2026-11-24 13:00 UTC on all three. Batch-45 pinned
window — the Nov-14 numbers this file previously carried are deleted,
not preserved alongside.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=5 bars.

## Results (shipped config: confirmation = close above/below the
hook bar's high/low, exits on the opposite reversal, 2xATR stop,
3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 350 | 27.43% | -$5,737.97 | -57.49% | -4.70 | -59.91% | -$16.39 | 0.55 | $2,692.45 |
| ETH | 275 | 32.36% | -$1,036.27 | -10.27% | -0.48 | -29.77% | -$3.77 | 0.91 | $1,989.91 |
| HYPE | 357 | 37.25% | -$914.07 | -9.62% | -0.38 | -21.78% | -$2.56 | 0.94 | $1,804.89 |
| **Combined** | **982** | **32.38%** | **-$7,688.32** | — | — | — | **-$7.83** | — | **$6,487.25** |

## Verdict: loser on all three coins — the hook doesn't hold

Negative everywhere: combined -$7,688.32 on 982 trades, win rate
**32.38%**, profit factor 0.55–0.94 on every coin. BTC is the worst
of the three (Sharpe -4.70, MaxDD -59.91% — the $10k book lost well
over half). The extra hook condition vs the 2-bar version does
filter trades (982 vs 1,175 for the 2-bar) but buys nothing: the
pattern fires as designed (~350 trades per coin) and the
"reversal" is still usually a pause inside a trend that resumes —
the win rate is low on both sides, so there is no directional
asymmetry to exploit either.

The one honest nuance: gross of fees the book is mixed, not
uniformly negative — BTC -$3,045.52 gross (negative even before
costs), ETH +$953.64, HYPE +$890.82; combined gross -$1,201.07.
So on ETH/HYPE the pattern is approximately *zero-edge* before
costs and $6,487.25 of fees turn it into a loser; on BTC it loses
gross too. Either way there is nothing to rescue by tuning: the
calibration sweep (see CALIBRATION.md) shows looser confirmation
only multiplies the trade count and the losses, and the stricter
3-bar filter does not beat the simpler 2-bar version (combined
-$7,688.32 vs -$7,381.81).

The 10 extra days vs the stale Nov-14 window (238 more bars, 28
more trades) added +$320.68 net — mildly positive, and it does not
change the verdict: the loss is consistent across coins, sides,
and both windows.

## Calibration note

Shipped the specified confirmation="high". A high/close/none
sweep is in CALIBRATION.md: "close" is worse on every coin
(combined -$11,221.40, 1,387 trades) and "none" is worst
(combined -$19,492.89, 3,031 trades, BTC -75.05%). The confirmation
bar is doing real work — it filters out most of the noise — but
even the strictest version has no edge. The "high" config was
fixed before any backtest was run; no in-sample adoption.

## Mechanism

Joe Ross' 3-bar reversal ("Trading by the Book"): a down bar,
then a bar that undercuts the down bar's low but closes back
above the down bar's close — the hook that says sellers failed
to hold the new low — confirmed by the next bar closing above
the hook bar's high. Long on the confirmation, short on the
mirror. Exits on the opposite reversal signal. 2xATR hard stop,
3xATR chandelier trail, 60-bar max hold — a two-bar setup plus
one confirmation bar goes stale fast, so a position that has not
played out in ~2.5 days is a drift, not the pattern.

Source: Joe Ross, "Trading by the Book" (three-bar reversal).
https://www.luxalgo.com/library/concept/1-2-3-reversal/ — documents
Ross's 1-2-3 formation and the follow-on Ross hook.

## Audit (batch 45 refresh)

No code changes were needed. Audit of indicators.py / signals.py /
risk.py found no lookahead (every comparison uses backward shifts
only; the truncation test passes), no NaN poisoning (all signal
columns are boolean after `fillna(False)`; the row-0 NaN in
`lower_low`/`higher_high` from the 1-bar shift is handled), and
the exit logic is the specified opposite-reversal exit. Parameters
unchanged from the original build. 14/14 unit tests pass.

## Limitations

- Single 8.5-month crypto window; 982 trades is a decent sample
  and the loss is consistent across coins and sides.
- 32.38% win rate with PF < 1 on all three coins — the edge is
  ~zero gross on ETH/HYPE, negative gross on BTC; no confirmation
  setting rescues it (see CALIBRATION.md).
- The 3-bar pattern has no trend or volatility context: it fires
  into strong trends as readily as at range extremes, and the
  stop exits show the trend usually wins. The extra hook condition
  over the 2-bar version adds selectivity without adding edge.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped confirmation mode on this window.
