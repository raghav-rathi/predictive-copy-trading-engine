# Coppock Curve Bull — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=600 bars.

## Results (shipped config: Coppock = WMA(240) of ROC(336) +
ROC(264), long on the below-zero hook, short on the mirror
extension, exit on opposite turn or zero cross against the
position, 2xATR stop, 3xATR trail, 240-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 95 | 21.1% | -$1,021 | -10.2% | -0.94 | -17.0% | -$10.75 | 0.76 |
| ETH | 87 | 26.4% | -$853 | -8.5% | -0.95 | -18.9% | -$9.81 | 0.77 |
| HYPE | 80 | 30.0% | +$163 | +1.6% | +0.26 | -11.4% | +$2.03 | 1.05 |
| **Combined** | **262** | **25.6%** | **-$1,712** | — | — | — | -$6.53 | — |

Fees: BTC $1,099, ETH $835, HYPE $418 (total $2,352).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: loser combined — a monthly-scale hook, drowned in hourly noise

Combined -$1,712 on 262 trades. The adaptation is honest but
the timeframe is hostile: a curve built to catch multi-month
bottoms turns up and down 262 times on 1h bars, because the
240h WMA still wiggles on every 2-week swing. Win rate
21.1–30.0% and profit factor 0.76–0.77 on BTC and ETH say the
hooks fire into counter-trend bounces as often as into real
turns, and the 2xATR stop takes the trade out 44 times on BTC
alone. HYPE is the lone positive coin (+$163, PF 1.05) — a
breakeven read, not an edge. The losses are modest (-10.2% BTC,
-8.5% ETH) because the indicator is slow and trades rarely;
the verdict is a slow bleed, not a blow-up.

## Calibration note

Shipped the specified WMA window 240. A 120/240/480 WMA-window
sweep on this batch-46 window is in CALIBRATION.md: 240 is the
least negative combined (-$1,712), 120 is the worst (-$4,526,
415 trades) and 480 is in between (-$3,390, 218 trades). The
240 config was fixed before any backtest was run; no in-sample
adoption — the shipped config stays 240 and the verdict stays:
loser.

## Mechanism

ROC(336) and ROC(264) of close, summed, then a front-weighted
WMA over 240 bars (newest weight 240 down to 1). Turn-up =
Coppock > Coppock[1] and Coppock[1] <= Coppock[2]; turn-down
the mirror. Long on turn-up while Coppock < 0 (the canonical
below-zero hook); short on turn-down while Coppock > 0 (the
non-canonical extension). Exit on the opposite turn or on the
curve crossing zero against the position. The harness 2xATR
hard stop / 3xATR chandelier trail sit behind the signal exits
as a safety net for gap-through moves; 240-bar max hold.

Source: Edwin Coppock, Coppock Curve (Barron's, Oct 15, 1962) —
https://en.wikipedia.org/wiki/Coppock_curve (URL given in the
batch-46 brief; the monthly 14/11/10 formula and the Oct 15,
1962 Barron's origin are as documented there).

## Limitations

- Single ~8.4-month crypto window; 262 trades — the failure is
  consistent on BTC and ETH, with HYPE only breakeven.
- A monthly indicator translated to hours is an adaptation, not
  the original: the 336h/264h/240h lookbacks are 14/11/10 *days*,
  not months, and the signal fires far more often than Coppock's
  monthly hooks ever did.
- The calibration sweep shows the shipped 240 window is the
  least negative in-sample — but "least negative" is not an
  edge, and adopting it on that basis would be in-sample
  selection (it was fixed before backtesting anyway).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped WMA window on this window.
