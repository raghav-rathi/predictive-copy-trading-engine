# Fibonacci Cluster — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00
UTC (ms `[1773525600000, 1792328400000)`; HYPE data starts
2026-03-15 00:00 UTC): 5,223 bars BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=120 bars.

**Structure found:** zigzag pivots — BTC 198, ETH 308, HYPE 651.
Bars with at least one cluster — BTC 4,475/5,223 (86%), ETH
4,598/5,223 (88%), HYPE 4,722/5,221 (90%). Clusters form readily at
the shipped 0.5x ATR width; no relaxation to 0.75 ATR was needed.

## Results (shipped config: 5-bar fractal pivots, min 2% swing,
38.2%/50%/61.8% of last 3 swings, cluster = ≥ 2 levels from
different swings within 0.5x ATR(14), bounce entry on a 0.25x ATR
touch, exit on opposite-cluster touch, 2xATR stop, 3xATR trail,
200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 283 | 30.0% | -$4,346 | -43.4% | -4.04 | -46.0% | -$15.36 | 0.55 |
| ETH | 341 | 30.8% | -$3,054 | -30.5% | -2.20 | -31.2% | -$8.96 | 0.73 |
| HYPE | 337 | 32.0% | -$2,309 | -22.9% | -1.54 | -30.0% | -$6.85 | 0.81 |
| **Combined** | **961** | **31.0%** | **-$9,709** | — | — | — | **-$10.10** | — |

Entry signals fired on every coin (long/short): BTC 299/377,
ETH 459/423, HYPE 427/473.

## Verdict: a loser on all three coins, and the worst batch leg by dollars

Combined -$9,709 across 961 trades, 31.0% win rate, expectancy
-$10.10 a trade. Every coin is deeply negative, and BTC's -46.0%
max drawdown is the worst single-coin drawdown in the batch so far.
The mechanism fails in the way the caveats warned about:

- **Clusters are everywhere, so the edge is nowhere.** With 9
  levels per bar and clusters on ~88% of bars, the "confluence"
  filter barely filters — the nearest cluster sits close to the
  close most of the time, so ordinary noise triggers the touch and
  the system trades ~1.5 times a day per coin.
- **The bounce does not hold.** Exits split roughly evenly between
  stops and opposite-cluster touches (BTC 145 stop / 138 signal,
  ETH 147 / 194, HYPE 148 / 189) — about half the bounces fail
  outright into the 2xATR stop, and the ones that "work" mostly
  exit at the next cluster for a small gain that does not cover
  the stop-outs. Win rate ~31% with PF 0.55–0.81 says the average
  loss is much larger than the average win.
- **Fees compound the damage:** $6,048 total, 62% of the net loss
  — 961 trades at 0.055% per side round-trip is a heavy tax on a
  system whose edge is a coin flip at a nearby line.

## Mechanism

ZigZag swings from 5-bar fractal pivots (2-bar confirmation, min
2% swing); 38.2%/50%/61.8% retracements of the last 3 completed
swings; a cluster is ≥ 2 levels from different swings within 0.5x
ATR(14). Long on a low touching a support cluster and closing back
above it; short on a high touching a resistance cluster and closing
back below it. Exit on touch of the opposite cluster. 2xATR hard
stop, 3xATR chandelier trail, 200-bar max hold.

Source: Fibonacci confluence / clusters —
https://www.fxfoundations.com/learn/technical-analysis/fibonacci

## Limitations

- Single 7-month crypto window; 961 trades is a large sample for a
  loser, which makes the negative verdict more reliable, not less.
- Fibonacci confluence is a weak filter when levels are dense —
  the cluster test needs a genuinely independent second factor
  (prior support/resistance, volume node) to mean anything.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped cluster width on this window (see
  CALIBRATION.md — the 0.75x setting looks less bad in-sample and
  was deliberately not adopted).
