# Volatility Quality Index — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: Stridsman VQI, frozen convention
e=(close change)/true range, S=sum(e, 10), VQI=WMA(S, 14); trade
the 10-bar VQI change, gated on |change| >= 0.5x its 50-bar median;
1.5xATR stop, 2R target, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 1,243 | 37.5% | -$8,865 | -88.6% | -5.73 | -90.3% | -$7.13 | 0.72 | $8,752 |
| ETH | 1,278 | 39.2% | -$7,143 | -71.5% | -3.04 | -83.1% | -$5.59 | 0.85 | $10,526 |
| HYPE | 1,221 | 41.2% | -$4,277 | -42.6% | -1.39 | -59.1% | -$3.50 | 0.91 | $7,019 |
| **Combined** | **3,742** | **39.3%** | **-$20,285** | — | — | — | **-$5.42** | — | **$26,297** |

Signal gates fire on nearly every bar (long entries 2,154/2,178/2,182,
short entries 2,206/2,184/2,166 for BTC/ETH/HYPE — ~73% of all bars
carry an entry signal). The 10-bar VQI change flips sign almost
every bar, so the strategy is effectively always in a trade:
1,221–1,278 trades per coin in 8 months, ~5 trades a day. Fees
alone ($26,297 combined) exceed the net loss; expectancy is
-$3.50 to -$7.13 per trade. BTC loses 89% of the account
(MaxDD -90.3%).

## Verdict: the most expensive loser — a fee-bleed machine

Combined -$20,285 across 3,742 trades. VQI's 10-bar change is far
too noisy at 1h resolution to be a direction signal: it says
volatility was directional over the last 10 bars, which on hourly
crypto is true and false again within a day. The gate
(0.5x median) barely filters — |change| clears half its median
about three-quarters of the time — so the strategy trades
constantly and pays $26,297 in fees to lose $20,285 net. Nothing
about the sign of the VQI change predicts the next 48 bars.

## Calibration note

Shipped gate=0.5x. A gate 0.0 – 0.5 – 1.0 sweep is in
CALIBRATION.md: gate=1.0 is least bad (combined -$15,571 on 2,670
trades) and gate=0.0 is worst (-$23,804 on 4,799 trades), but no
setting is green on any coin. The shipped gate=0.5x was fixed a
priori — adopted before the sweep, not because of it.

## Mechanism

FROZEN CONVENTION (documented exactly in `indicators.py` and
CALIBRATION.md): per-bar efficiency e_t = (close_t − close_{t−1}) /
true_range_t; S_t = sum of e over the trailing 10 bars;
VQI_t = WMA(S, 14). Long when VQI_t > VQI_{t−10} and the gate
clears; short on the mirror. Exit when the 10-bar VQI change flips
sign or the 20-bar EMA of close crosses against the position.
1.5xATR stop, 2R target, 48-bar max hold.

Source: Alpha Volatility Quality (Stridsman VQI, Coder Wolves) —
https://in.tradingview.com/script/asS85p1B-Alpha-Trading-Alpha-Volatility-Quality-Coder-Wolves/

## Limitations

- Single 8-month crypto window; 3,742 trades, all three legs deeply
  negative, so the sign is not a small-sample accident.
- BTC leg loses 89% of the account; fees ($26,297) exceed the net
  loss — the strategy would be a loser even at zero fees on BTC/ETH.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped gate on this window (see CALIBRATION.md).
