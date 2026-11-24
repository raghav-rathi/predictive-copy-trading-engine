# UT Bot Alerts — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-45 window ms `[1773525600000, 1795525200000)`
(2026-03-14 22:00 UTC → 2026-11-24 14:00 UTC exclusive, last
bar 13:00 UTC): 6,111 bars BTC/ETH, 6,109 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=30 bars.

## Results (shipped config: ATR(10) trailing stop, KeyValue 1.0,
long on close crossing above the stop, short on crossing
below, exit on the opposite flip, 2xATR stop, 3xATR trail,
60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 677 | 30.6% | -$6,338 | -63.4% | -4.11 | -66.1% | -$9.36 | 0.68 |
| ETH | 627 | 32.4% | -$3,285 | -32.8% | -1.44 | -46.8% | -$5.24 | 0.84 |
| HYPE | 704 | 35.7% | -$2,701 | -26.9% | -1.23 | -34.3% | -$3.84 | 0.89 |
| **Combined** | **2,008** | **32.9%** | **-$12,325** | — | — | — | -$6.14 | — |

Fees: BTC $4,762, ETH $3,888, HYPE $2,990 (total $11,640).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: the worst loser of this batch by a wide margin —
a 1.0×ATR trailing stop flips far too often on 1h crypto

Combined -$12,325 on 2,008 trades — more trades and more
loss than the other strategies in this batch put together.
The mechanism is the problem, not the market: with KeyValue
1.0 the trailing stop hugs price at one ATR(10), so every
ordinary 1h wiggle flips it. BTC flips ~677 times, and each
flip is a trade that pays $4,762 in fees on BTC alone. The
result is a near-mechanical bleed: BTC -63.4% (Sharpe -4.11,
MaxDD -66.1% — the account loses almost two-thirds), ETH
-32.8%, HYPE -26.9%. Win rate 30.6–35.7%, profit factor
0.68–0.89 on every coin. There is no coin, no sub-period, no
reading in which the shipped config works on this window: it
is a chop machine, and the chop is the trade.

This is a refresh of the Nov-14 build on the longer batch-45
window (6,111 bars vs 5,873; ten extra days to Nov 24). The
verdict is unchanged and the numbers barely moved
(Nov-14 combined: -$12,427 on 1,928 trades) — the extra ten
days added 80 trades and $102 of net, i.e. more of the same
chop. No code was changed in the refresh: the 13-test suite
passes as written, the lookahead audit found no lookahead
(see CALIBRATION.md), and the shipped KeyValue stays 1.0.

## Calibration note

Shipped the specified KeyValue=1.0. A 1.0/2.0/3.0 KeyValue
sweep re-run on this batch-45 window is in CALIBRATION.md:
2.0 flips the combined result to +$1,141 (810 trades) and
is positive on ETH and HYPE — but that is an in-sample
observation on a knob that moves the system from "flips
constantly" to "flips less often", and 3.0 is near-breakeven
combined (+$108) despite a +$3,494 HYPE read. The 1.0
config was fixed before any backtest was run; no in-sample
adoption — the shipped config stays 1.0 and the verdict
stays: loser.

## Mechanism

QuantNomad, "UT Bot Alerts" (TradingView; original idea
HPotter), Heikin Ashi OFF: xATR = ATR(10) (Wilder),
nLoss = KeyValue × xATR with KeyValue = 1.0 shipped. The
trailing stop recurses per bar (prev = the previous bar's
stop): if close and prior close are both above prev, stop =
max(prev, close − nLoss); if both below, stop = min(prev,
close + nLoss); if close is above prev, stop = close −
nLoss; otherwise stop = close + nLoss. The stop only ever
ratchets in the direction of the prevailing trend. Buy =
close crosses above the stop; sell = close crosses below.
Exit on the opposite signal. The harness 2xATR hard stop /
3xATR chandelier trail sit behind the UT stop as a safety
net for gap-through-stop moves; 60-bar max hold.

Source: QuantNomad, "UT Bot Alerts" (TradingView) —
https://proea.app/en/blog/ut-bot-alerts-settings (verified
live 2026-11-24; the article reads the original Pine v4
source line by line and confirms Key Value 1, ATR Period 10,
close source, and the ratchet recursion as implemented).

## Limitations

- Single ~8.3-month crypto window; 2,008 trades — the failure
  is overwhelming and consistent, not a sample-size artefact.
- KeyValue 1.0 is far too tight for 1h crypto volatility:
  the stop flips on noise, and every flip is a round-trip
  fee. The system as shipped is structurally unsuited to
  this timeframe.
- The calibration sweep shows a wider KeyValue helps a lot
  in-sample (2.0 → +$1,141 combined) — but adopting it would
  be in-sample selection, and 3.0 is near-breakeven combined
  (+$108), so the "right" KeyValue is not stable across the
  sweep.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped KeyValue on this window.
