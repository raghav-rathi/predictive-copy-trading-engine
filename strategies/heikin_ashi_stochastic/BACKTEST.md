# Heikin Ashi + Stochastic — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-45 window ms `[1773525600000, 1795525200000)`
(2026-03-14 22:00 UTC → 2026-11-24 14:00 UTC exclusive, last
bar 13:00 UTC): 6,111 bars BTC/ETH, 6,109 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=60 bars.

## Results (shipped config: HA bullish + ha_close > EMA(50) of
ha_close + %K cross above %D while %K < 30 for LONG, mirror
for SHORT; exit on the opposite %K/%D cross; 2xATR stop,
3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 15 | 13.3% | -$234 | -2.34% | -1.40 | -3.67% | -$15.63 | 0.44 |
| ETH | 19 | 21.1% | -$151 | -1.51% | -0.86 | -2.72% | -$7.96 | 0.64 |
| HYPE | 13 | 23.1% | -$122 | -1.22% | -0.78 | -1.74% | -$9.36 | 0.58 |
| **Combined** | **47** | **19.1%** | **-$507** | — | — | — | -$10.80 | — |

Fees: BTC $159, ETH $186, HYPE $60 (total $405). Sides:
BTC 8 long / 7 short; ETH 4 long / 15 short; HYPE 8 long /
5 short (20 long / 27 short combined). Every entry closed
by window end — no position was still open at the last bar.
Net % is the final-equity return; Net $ is the sum of
closed-trade PnL.

## Verdict: a small loser on a tiny sample — the gates strangle it

Combined -$507 on 47 trades with a 19.1% win rate and a
-$10.80 expectancy. The dollar loss is small (the account
is down 1–2% per coin) but the shape is bad: win rate
13–23% and profit factor 0.44–0.64 on every coin, with the
worst expectancy on BTC (-$15.63/trade). Nothing here wins
anywhere.

- **The sample is too small to condemn the mechanism
  strongly, but the direction is clear.** 47 trades in
  ~8.3 months across three coins is ~1 trade per coin per
  5.5 days. The long gate (HA bullish + above EMA(50) +
  %K < 30 at the cross) is nearly shut by construction — see
  README/CALIBRATION — so the system mostly trades shorts
  (27 of 47) and catches few bounces. A system that fires
  this rarely needs a much longer window before any verdict
  beyond "loses a little, trades rarely" is justified.
- **Fees are not the story here** ($405 vs -$507 net) — the
  gross edge before fees is only about -$102 over 47 trades.
  The losses are the trades themselves: a 19% win rate with
  2xATR stops and exits on the opposite cross means most
  positions are stopped or crossed out before the HA trend
  pays.
- **Per-coin split:** BTC is the worst (-$234, PF 0.44, 2
  wins in 15 trades); ETH and HYPE lose less in dollars but
  no better in shape (PF 0.64 / 0.58). No coin offers a
  reading worth chasing.

Stated plainly: as specified, Heikin Ashi + Stochastic on 1h
crypto is a rare, short-biased, small loser. Do not quote it
as a near-miss — 47 trades is not enough to say the edge is
almost there, and the win rate says the entries are not
catching turns.

## Mechanism

Heikin Ashi candles computed recursively (ha_close =
(o+h+l+c)/4, ha_open = (prev ha_open + prev ha_close)/2,
seeded ha_open[0] = o[0]); ha_ema50 = EMA(50) of ha_close.
Stochastic(14,3): %K = 100 × (c − lowest low 14) /
(highest high 14 − lowest low 14), %D = SMA(3) of %K
(fast form — see CALIBRATION.md). LONG on HA bullish +
ha_close > ha_ema50 + %K cross above %D while %K < 30;
SHORT on the mirror; exit on the opposite cross. 2xATR
stop, 3xATR trail, 60-bar max hold. All params fixed a
priori; no optimization.

Source: Heikin Ashi (Munehisa Homma) + Stochastic Oscillator
(George Lane)
(https://school.stockcharts.com/doku.php?id=chart_analysis:heikin_ashi).

## Limitations

- Single ~8.3-month crypto window; only 47 trades — the
  verdict is directionally negative, not statistically
  strong.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window — least of
  all the 30/70 stochastic thresholds or the EMA(50) length,
  which directly control how many (few) trades fire.
