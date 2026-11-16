# Bayesian Changepoint — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=50 bars.

## Results (shipped config: BOCD, Gaussian likelihood, constant
hazard 1/100, P(change) > 0.5, trade the post-change mean sign,
1.5xATR stop, 72-bar max hold, no target)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 21 | 19.0% | -$847 | -8.5% | -1.10 | -10.6% | -$40.34 | 0.42 | $253 |
| ETH | 29 | 13.8% | -$665 | -6.7% | -0.86 | -9.8% | -$22.94 | 0.67 | $257 |
| HYPE | 5 | 60.0% | +$1,109 | +11.1% | +1.45 | -6.3% | +$221.80 | 5.05 | $38 |
| **Combined** | **55** | **20.0%** | **-$403** | — | — | — | **-$7.34** | — | **$548** |

The detector fires rarely (long entries 10/14/5, short entries
11/15/0 for BTC/ETH/HYPE) — 5–29 trades per coin in 8 months.
HYPE's +$1,109 comes from just 5 trades (3 wins, profit factor
5.05): a tiny sample, not evidence the detector works on HYPE.
BTC and ETH win rates are 19% and 14%: when a changepoint fires,
the post-change mean sign is usually noise — exactly the
volatility-shift caveat. A volatility jump resets the run, the
post-change mean is estimated from a handful of bars, and the trade
is entered on that sign.

## Verdict: small loser — the detector fires, the direction doesn't pay

Combined -$403 across 55 trades, expectancy -$7.34/trade. The loss
is small only because the strategy barely trades. The HYPE leg
(+$1,109, Sharpe +1.45) is 5 trades and should not be read as a
winner; BTC (-$847, win rate 19%) and ETH (-$665, win rate 14%)
show the rule loses where it has any sample at all. Runtime is
fine: the capped run-length recursion (RMAX=200) runs all three
coins in ~2 seconds.

## Calibration note

Shipped hazard=0.01. A hazard 0.005 – 0.01 – 0.02 sweep is in
CALIBRATION.md: combined -$469 / -$403 / -$612 — the hazard moves
the trade count (48 → 55 → 66) and almost nothing else. The shipped
hazard=0.01 was fixed a priori — adopted before the sweep, not
because of it.

## Mechanism

Adams & MacKay Bayesian online changepoint detection: posterior
run-length over log-returns, Gaussian likelihood with a
Normal-Inverse-Gamma conjugate prior, constant hazard 1/100, run
length capped at 200. Long on a detected changepoint
(P(change) > 0.5) with a positive post-change mean return; short on
the mirror. Exit on the next changepoint or a post-change mean sign
flip. 1.5xATR stop, 72-bar max hold, no target.

Source: Bayesian Online Changepoint Detection (Adams & MacKay 2007) —
https://arxiv.org/pdf/0710.3742

## Limitations

- Single 8-month crypto window; 55 trades total is a thin sample
  and the HYPE leg is 5 trades — no leg has enough data to claim
  anything, and the two legs with data are both losers.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped hazard on this window (see CALIBRATION.md).
