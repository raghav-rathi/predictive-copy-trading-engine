# DPO Zero-Line Cross — Backtest

**Data:** Hyperliquid 1h cache, BTC + ETH + HYPE, sliced to the batch
window 2026-03-14 00:00 UTC → 2026-10-21 23:59:59 UTC (ms
`[1773446400000, 1792627199000)`; actual data covers 2026-03-14 22:00
UTC → 2026-10-21 13:00 UTC): 5,296 bars BTC/ETH, 5,294 HYPE (HYPE
starts 2026-03-15 00:00 UTC). Exact duplicate bars deduped on `t`.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: DPO(20) with 11-bar displacement,
SMA(50) trend filter, long on zero-cross-up in uptrend / short on
zero-cross-down in downtrend, exits on the opposite zero-cross, 2xATR
stop, 2.5xATR trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 243 | 23.5% | -$3,229 | -32.3% | -2.79 | -33.0% | -$13.29 | 0.63 |
| ETH | 271 | 25.5% | -$1,343 | -13.4% | -0.98 | -31.6% | -$4.96 | 0.87 |
| HYPE | 243 | 23.5% | -$166 | -1.7% | -0.02 | -18.9% | -$0.68 | 0.98 |
| **Combined** | **757** | **24.2%** | **-$4,738** | — | — | — | -$6.26 | 0.83 |

## Verdict: a clean loser — the cycle turn is not a tradeable edge here

Combined -$4,738 across 757 trades, PF 0.83, win rate 24.2%. Every
coin loses; there is no HYPE-shaped rescue this time.

- **BTC is the worst leg** (-$3,229, Sharpe -2.79, PF 0.63, MaxDD
  -33.0%). 243 trades at -$13.29 expectancy — zero-crosses on BTC's
  1h are just chop turned into positions: the displaced DPO lags the
  turn, the trend filter arrives after the leg has already run, and
  fees ($2,415) finish the job.
- **ETH is a slow bleed** (-$1,343, PF 0.87, Sharpe -0.98,
  MaxDD -31.6%). 271 trades — the most of any leg — at -$4.96
  expectancy; fees ($2,488) are almost 2x the net loss.
- **HYPE is a coin flip** (-$166, PF 0.98, Sharpe -0.02,
  expectancy -$0.68). The only leg near breakeven — 243 trades of
  noise. Notably the coin that carried batch 12's winners pays
  nothing for a cycle-turn strategy.
- No combination of settings saves it (see CALIBRATION.md): n=10 is
  worse everywhere (-$7,766 combined), n=30 is the least-bad
  (-$3,300, HYPE +$1,238) but still red combined — and the shipped
  n=20 was fixed before the first run, so the n=30 HYPE green stays
  an observation, not a config change.

The mechanism's flaw is visible: DPO's 11-bar displacement means the
zero-cross confirms the turn *after* price has already moved through
the lagged mean, and the SMA(50) trend filter then admits the trade
only when the leg is half over. Entries are structurally late, so
the strategy buys cycle tops and sells cycle bottoms often enough to
hold a 24% win rate, and the 2xATR stop turns those into steady
small losers.

## Mechanism

DPO(20) = close − SMA(close, 20).shift(11); trend filter SMA(close,
50). Long on a DPO zero-cross-up while close > SMA(50); short on a
zero-cross-down while close < SMA(50). Exits are the opposite
zero-cross regardless of trend — a cross the other way means the
cycle itself turned. 2xATR hard stop, 2.5xATR chandelier trail,
150-bar max hold.

Sources: DPO (Ehlers/Investopedia convention) —
https://capital.com/en-eu/learn/technical-analysis/detrended-price-oscillator ;
DPO trading rules (trend filter) —
https://www.incrediblecharts.com/indicators/detrended_price_oscillator.php

## Limitations

- Single 7-month crypto window; 757 trades of one regime.
- All three legs red — worst combined result of batches 10–12's
  honest-loser streak, and no coin salvages it.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped length on this window (see CALIBRATION.md).
