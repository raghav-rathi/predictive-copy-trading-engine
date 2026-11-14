# Heikin Ashi Delta Momentum — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC
(ms `[1773525600000, 1792328400000)`): 5,223 bars BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.
**Signal counts (per coin, full window):** BTC 679 long / 679 short
entries; ETH 700 / 700; HYPE 647 / 646 — every gate fires on every coin.

## Results (shipped config: HA delta zero-cross entries, exit on the
reverse cross, 2xATR stop, 3xATR trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1343 | 23.8% | -$9,072 | -90.8% | -11.48 | -90.9% | -$6.76 | 0.50 |
| ETH | 1386 | 24.7% | -$8,140 | -81.4% | -7.70 | -81.4% | -$5.87 | 0.63 |
| HYPE | 1280 | 30.5% | -$6,981 | -69.9% | -5.97 | -70.6% | -$5.45 | 0.65 |
| **Combined** | **4009** | **26.3%** | **-$24,193** | — | — | — | -$6.03 | — |

## Verdict: a clear loser on all three coins

Combined -$24,193 across 4,009 trades — the worst single-strategy
dollar loss in this batch's builder set so far, and there is no coin
to hide behind: BTC -90.8%, ETH -81.4%, HYPE -69.9% of the $10k start.
The mechanism is the failure, not the parameters:

- The HA delta flips sign roughly every 8 bars on 1h crypto (679
  crosses per side on BTC), so the strategy is almost always in a
  position and almost always entering late: the smoothing that makes
  Heikin Ashi charts readable is the same smoothing that makes the
  zero-cross lag the turn by several bars.
- Win rates of 23.8–30.5% with profit factors of 0.50–0.65 mean the
  average loss is roughly twice the average win — the 2xATR stop is
  hit far more often than the 3xATR trail ever pays.
- Fees alone ($15,130 combined) exceed half the total loss; at ~1,340
  trades per coin in 7 months the strategy is a fee machine first and
  a momentum strategy second.

Ship as documented, paper-only. Do not trade this on 1h crypto
without a trend filter and a much slower trigger — and any such change
is a new strategy, not a tweak to this one.

## Mechanism

HA_close=(o+h+l+c)/4, HA_open=(prev HA_open+prev HA_close)/2 seeded
with the first bar's open, delta=HA_close−HA_open. Long when delta
crosses from negative to positive (or turns positive after ≥3
negative bars) with HA_close>HA_open; short on the mirror image.
Exit when delta crosses back through zero. 2xATR hard stop, 3xATR
chandelier trail, 150-bar max hold.

Source: Heikin Ashi trading strategy —
https://www.babypips.com/learn/forex/how-to-trade-heikin-ashi?locale=ja

## Limitations

- Heikin Ashi smoothing lag: entries and exits both arrive after the
  turn; HA prices are not real prices.
- No trend filter — the zero-cross fires in chop as readily as in
  trends; 4,009 trades in 7 months is overtrading by any standard.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped rule on this window (see CALIBRATION.md).
