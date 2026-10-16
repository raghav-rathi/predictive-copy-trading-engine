# Time-Series Momentum (Liu-Tsyvinski) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 → 2026-10-09 (~5,000 bars each; API caps history at 5,000
candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(`use_funding=False`; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 3xATR stop, 3x leverage cap,
$10k start per coin, 672-bar max hold, warmup 750 bars.

## Results (shipped config, no tuning)

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 3 | 0.0% | -$241.35 (-2.41%) | -2.79 | -2.51% | -$80.45 | 0.00 |
| ETH | 1 | 100% | +$14.69 (+0.15%) | 0.22 | -1.02% | +$14.69 | inf |
| HYPE | 1 | 100% | +$15.57 (+0.16%) | 1.10 | -0.03% | +$15.57 | inf |
| **Combined** | **5** | **40.0%** | **-$211.09 (-0.70% on $30k)** | — | — | -$42.22 | — |

Trade log: BTC short 76,711 → 76,868 (May 26, signal exit, -$24.84);
BTC long 77,144 → stopped at 76,110 (May 26, -$107.88);
BTC short 63,585 → stopped at 64,281 (Aug 11, -$108.64);
ETH long 1,881.3 → 1,887.6 (Aug 11, signal exit, +$14.69);
HYPE long 42.89 → 43.19 (May 17, signal exit, +$15.57).
Total fees $36.91; two of three BTC trades died on the 3xATR stop.

## Verdict: LOSER on the observed window (and under-sampled)

Five trades in ~208 days across three coins is not a strategy backtest, it
is five anecdotes — but the anecdotes are all the data this specification
produces, and they are negative: BTC 0-for-3 with two stop-outs, combined
-$211. The ETH/HYPE wins are single signal-exits of +$15 each, i.e. noise.
No spin: as literally specified, this does not clear the bar and should not
see capital. The interesting finding is *why* it is so quiet (see below);
any revival of this idea needs a looser trigger (single-horizon cross, or
a lower joint threshold) before re-testing.

## Calibration note

The headline mechanism question is answered by the entry counts: over
~5,000 bars per coin, the joint same-bar cross of the 1-week and 4-week
vol-scaled returns fired exactly 5 times (BTC 3, ETH 1, HYPE 1), clustering
at violent regime flips (May 17, May 26, Aug 11). The vol-scaled ratios
carry inherent noise with sd ~sqrt(168)≈13 under iid returns, so each ratio
individually spends most of its time far outside the ±0.5 band; demanding
*both* to cross the band on the *same* bar makes the trigger extraordinarily
rare, and when it fires it is at maximum disagreement between the horizons
— exactly the moment the 3xATR stop is most likely to get run over, as the
two BTC stop-outs show. On the warmup question: r672 looks like it needs
1344 bars (672 shift + 672 vol window), but the rolling vol uses
min_periods=672 on non-NaN values, so the first valid r672 (and r672_s one
bar later) lands at bar ~673 — inside the 750-bar warmup, no dead zone, no
special handling needed. Loosening the trigger is the obvious next
experiment: cross on either horizon alone, or require the cross within a
3–5 bar window instead of the same bar, would multiply the sample ~10x and
give the hysteresis exits something to actually do (long_exit/short_exit
fired 800–2,000 times per coin, almost always while flat).

## Mechanism

Volatility-scaled past returns at 1-week (168 bars) and 4-week (672 bars)
on 1h candles, per Liu & Tsyvinski (2021) and Liu, Tsyvinski & Wu (2022):
long when both ratios cross above +0.5 on the same bar, short when both
cross below -0.5; hysteresis exits when both ratios decay past ±0.3;
3xATR hard stop, no trailing, 672-bar (4-week) max hold, 1% risk/trade,
3x leverage cap. Ratios are computed through bar i, shifted one bar for the
no-lookahead convention, signals fire on bar i, execute at bar i+1 open.
Source: https://github.com/bigcan/sharpen

## Limitations

- Five trades: no statistical content; verdict is "negative on what exists,"
  not "proven worthless."
- Single 7-month window (Mar–Oct 2026), choppy-to-bearish crypto regime;
  momentum strategies live or die by regime and this window had one big
  breakdown (BTC 82.5k → 80k in October, inside the sample).
- Funding unmodeled; shorts held through the sample would have earned it.
- Next-bar-open execution; real momentum ignition bars gap, slippage is
  understated on exactly the bars this strategy trades.
- The ±0.5/±0.3 thresholds are the task's trigger design, not the paper's
  (the paper sorts on the ratios cross-sectionally; it never proposes a
  binary same-bar dual-horizon trigger).
