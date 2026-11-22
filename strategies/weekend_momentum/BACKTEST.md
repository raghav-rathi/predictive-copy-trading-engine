# Weekend Crypto Momentum — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms).
**Window:** 2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC
(BTC/ETH 6,040 bars, HYPE 6,038 bars) — 35–36 weekend sessions.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=192 bars.

## Results (shipped config: 168h momentum, weekend session only,
one entry per weekend, Monday-00:00 exit, 2xATR stop, 2xATR trail,
72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 35 | 42.9% | +$454 | +4.5% | +0.88 | -5.9% | +$12.97 | 1.32 |
| ETH | 35 | 40.0% | +$389 | +3.9% | +0.73 | -7.1% | +$11.12 | 1.27 |
| HYPE | 35 | 42.9% | +$367 | +3.7% | +0.71 | -5.4% | +$10.48 | 1.30 |
| **Combined** | **105** | **41.9%** | **+$1,210** | — | — | — | +$11.53 | — |

Fees: BTC $336, ETH $264, HYPE $152 (total $752).

## Verdict: modestly positive, thin sample, contested anomaly

All three coins agree (+$367 to +$454, Sharpe +0.71 to +0.88,
profit factor 1.27–1.32), which is a better sign than a single
coin carrying the result — but 35 trades per coin is still a thin
sample, and the win rate is only ~42%: the edge, if it exists, is
a few larger weekend winners outweighing more frequent small
losses, not a high hit rate. Combined +$1,210 on $10k over 8
months is ~+12% with only ~14% time in market (weekends only),
which is the right shape for the paper's claim — and exactly the
shape that could also be a lucky 35-weekend draw in a contested
anomaly. Other 2026 studies find weekday return differences are
within noise and only weekend volatility is robust; this result
does not settle that dispute. Read it as suggestive, not as
confirmation.

## A design finding worth keeping: re-entry churn kills it

During development the signals were stateless (an entry signal on
every qualifying weekend bar, so a mid-weekend stop-out re-entered
on the next bar). That variant ran 786 trades and lost **−$16,076
combined (−55% per coin, Sharpe ≈ −4.5)** — the 2xATR stop fired
repeatedly inside choppy weekends and each re-entry paid fresh
fees for another stop-out. The shipped one-entry-per-weekend state
machine is not a tweak to make the numbers look good; it is the
paper's trade (a single weekend hold), and the stateless variant
is a different, strictly worse trade. The comparison is recorded
here so nobody "simplifies" the signals back to stateless.

## Mechanism

168h momentum (close vs close 168 bars ago); long when > 0,
short when < 0, entries only on Fri 00:00 – Sun 23:59 UTC bars,
one entry per weekend; forced exit on the Monday 00:00 UTC bar
(executed at the Monday 01:00 open). 2xATR stop, 2xATR trail,
72-bar max hold. All params fixed a priori; no optimization.

Source: Advances in Consumer Research, "The Weekend Effect in
Crypto Momentum"
(https://acr-journal.com/article/the-weekend-effect-in-crypto-momentum-does-momentum-change-when-markets-never-sleep--1514/).

## Limitations

- 35 trades per coin: no per-coin statistic here is significant;
  the cross-coin agreement is encouraging but not proof.
- Single 8-month crypto window (a mostly down-trending market);
  funding unmodeled; exit executes one hour later than the
  paper's Sunday 23:59 close (Monday 01:00 open).
- The 2xATR stop / 2xATR trail are house risk overlays, not in
  the source paper; they cut some weekend holds short.
- Never tune the shipped parameters on this window.
