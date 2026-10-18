# Silver Bullet Killzones (ICT) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 → 2026-10-18 (5,224 bars BTC/ETH; 5,222 HYPE).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 0.75xATR stop (FVG-extreme
proxy), 3x leverage cap, $10k start. WARMUP=220 bars.

**Timezone assumption:** t is ms UTC; NY = UTC−4h (EDT) is used for every
bar. Verified safe for this window: 2026 US daylight time ran Mar 8 →
Nov 1, so the entire 2026-03-14 → 2026-10-18 window is EDT — no DST
transition inside the backtest.

**Window note:** the batch brief's literal filter `[1741910400000,
1760828400000]` maps to 2025-03-14 → 2025-10-18, which is empty (the
cache starts 2026-03-14). The comment's intent ("2026-03-14 →
2026-10-18") matches the full cache, so the full cached range was used.

## Results (shipped config: NY killzones 03–04/10–11/14–15, 4h EMA(50)
bias, entries on retrace into a same-NY-day unmitigated FVG with a
micro market-structure shift, 0.75xATR stop / 1.5xATR target as
FVG-extreme and 2R proxies, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 7 | 42.9% | +$40 | +0.4% | +0.18 | -3.2% | +$5.78 | 1.08 |
| ETH | 3 | 0.0% | -$369 | -3.7% | -2.19 | -3.7% | -$123.00 | 0.00 |
| HYPE | 3 | 33.3% | -$50 | -0.5% | -0.18 | -3.0% | -$16.76 | 0.78 |
| **Combined** | **13** | **30.8%** | **-$379** | — | — | — | -$29.15 | — |

## Verdict: LOSER (on a sample too small to grade)

Net -$379 on 13 combined trades across 7 months. The four-way
conjunction (killzone + 4h-EMA bias + same-day FVG touch + micro MSS)
fires only ~2 times per coin per quarter on 1h bars, so there is no
statistical basis for an edge claim in either direction — BTC's +$40 on
7 trades and ETH's -$369 on 3 trades are both noise. What the test does
show honestly: the setup as specified barely trades on 1h crypto, and
the trades it takes don't pay. The protocol was designed for intraday
tape-reading on low timeframes; compressed onto 1h bars, the
"displacement → FVG → retrace" sequence rarely resolves inside one
killzone hour.

## Calibration note

Shipped exactly the specified parameters (three killzones, 4h EMA(50)
bias, same-day FVG, 0.75/1.5xATR risk, 24-bar max hold, WARMUP=220). A
10:00–11:00-only killzone variant is reported in CALIBRATION.md — it
trades even less and does worse.

## Mechanism

NY hour = (t/3.6M − 4) mod 24; killzones at NY hours 3, 10, 14. HTF
bias: 1h closes → 4h closes → EMA(50), aligned to each 1h bar via the
latest 4h bar fully closed by that bar's close (merge_asof, no
lookahead); bullish when the 4h EMA is rising. Bullish FVG at bar i:
low[i] > high[i−2]; tracked per NY day, mitigated on first overlap;
entries require touching an unmitigated gap printed earlier the same NY
day. MSS: close above/below the last fully-confirmed 3-bar micro swing
high/low. The opposite setup reverses the position.

Source: Michael Huddleston (ICT), 2022 mentorship —
https://chartwhisperer.ca/blog/ict-silver-bullet-killzones-trading-guide

## Limitations

- 13 combined trades: no edge can be established or rejected.
- Signal on killzone bar i executes at bar i+1's open — the hour AFTER
  the killzone, not inside it (harness execution convention).
- 1h bars compress the protocol's intended low-timeframe tape; 15m/5m
  bars were not tested.
- Funding unmodelled; FVG stop/target are ATR proxies, not the true
  FVG extreme / measured 2R.
