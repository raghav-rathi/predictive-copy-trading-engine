# Ichimoku Kumo Breakout — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=80 bars.

## Results (shipped config: Ichimoku tenkan 9 / kijun 26 /
senkou 52; long on a close crossing above the cloud top with
tenkan > kijun, short on a close crossing below the cloud
bottom with tenkan < kijun, exit when close comes back into
the cloud, 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 181 | 21.5% | -$2,851 | -27.6% | -2.51 | -33.2% | -$15.75 | 0.60 |
| ETH | 176 | 24.4% | -$2,983 | -29.1% | -2.66 | -32.8% | -$16.95 | 0.59 |
| HYPE | 183 | 24.6% | -$1,012 | -8.2% | -0.58 | -14.2% | -$5.53 | 0.85 |
| **Combined** | **540** | **23.5%** | **-$6,846** | **-21.6%** | **-2.65** | **-25.8%** | **-$12.68** | **0.68** |

Fees: BTC $1,802, ETH $1,382, HYPE $891 (total $4,074).
Exits: BTC signal 90 / stop 91; ETH signal 80 / stop 96;
HYPE signal 90 / stop 93. Net % is the final-equity return
(it includes the mark-to-market of any position still open at
the window end); Net $ is the sum of closed-trade PnL.

## Verdict: the worst loser of this batch's three — the cloud
breakout buys the top of every range

Combined -$6,846 on 540 trades, the largest loss of the
three strategies in this batch. The mechanism is the
problem, not the market: the Kumo cloud is built from
52-bar extremes shifted 26 bars forward, so on 1h crypto
it is a very slow support/resistance band — price crosses
it only after the move is well underway, and the 120-bar
max hold then lets the position ride the reversal back
through the cloud. Half of all exits are the 2xATR hard
stop (91/181 on BTC, 96/176 on ETH, 93/183 on HYPE), i.e.
the breakout entry is routinely followed by an immediate
reversal that stops the trade out. Win rate 21.5–24.6% —
the lowest of the three — profit factor 0.59–0.85, Sharpe
-2.51 on BTC and -2.66 on ETH. BTC and ETH each lose
~28–29% of the account. HYPE loses least (-8.2%) only
because its cloud is wider relative to its volatility, not
because the entries work. There is no coin, no sub-period,
no reading in which the shipped config works on this
window: it is a breakout system that buys breakouts after
they have already broken.

## Calibration note

Shipped the specified senkou period 52. A 26/52/78
senkou-period sweep on this batch-46 window is in
CALIBRATION.md: 26 is the least bad combined (-$3,707, 564
trades) and even prints a +$839 HYPE read (PF 1.11) — but
that is an in-sample observation on a knob that only moves
the cloud's lag, and BTC (-$3,198) and ETH (-$1,347) are
still losers at 26. The 52 config was fixed before any
backtest was run; no in-sample adoption — the shipped config
stays 52 and the verdict stays: loser.

## Mechanism

Goichi Hosoda's Ichimoku Kinkō Hyō (Wikipedia): tenkan =
(highest high(9) + lowest low(9))/2; kijun = (highest
high(26) + lowest low(26))/2; senkou A = (tenkan + kijun)/2
plotted 26 bars ahead; senkou B = (highest high(52) +
lowest low(52))/2 plotted 26 bars ahead. The Kumo cloud is
the space between senkou A and B. Long = close crosses
above the cloud top (max(senkou_a, senkou_b)) with tenkan >
kijun; short = close crosses below the cloud bottom
(min(senkou_a, senkou_b)) with tenkan < kijun; exit when
close comes back into the cloud (long: close < cloud top;
short: close > cloud bottom). The chikou span is NEVER read
— it is close shifted −26 (lookahead). The harness 2xATR
hard stop / 3xATR chandelier trail sit behind the cloud exit
as a safety net for gap-through-cloud moves; 120-bar max
hold.

Source: Wikipedia, "Ichimoku Kinkō Hyō" —
https://en.wikipedia.org/wiki/Ichimoku_Kink%C5%8D_Hy%C5%8D
(verified via search 2026-11-25; confirms Hosoda as the
developer, tenkan (9) / kijun (26) / senkou A and B (52,
plotted 26 ahead) formulas, the Kumo as the space between
the senkou spans, and chikou as today's close projected
back 26 periods — hence excluded here).

## Limitations

- Single ~8.4-month crypto window; 540 trades — the failure
  is overwhelming and consistent, not a sample-size artefact.
- The cloud's 52-bar lookback plus 26-bar shift makes it
  far too slow for 1h crypto: breakouts are recognised
  after the move, and the 120-bar hold rides the reversal.
- The calibration sweep shows a shorter senkou helps a lot
  in-sample (26 → -$3,707 combined, HYPE +$839) — but
  adopting it would be in-sample selection, and BTC/ETH
  still lose at 26.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped senkou period on this window.
