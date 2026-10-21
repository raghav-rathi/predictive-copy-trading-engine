# Know Sure Thing — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:00 UTC
(ms `[1773446400000, 1792589754418)`; END computed at run time,
on-disk cache `data/candles/*_1h.csv` through 13:00 UTC; the direct
API route was flapping, so the fetch used the cached bars rather
than a live re-pull — no bars fabricated): 5,296 bars BTC/ETH, 5,294
HYPE (HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: KST = 1\*SMA(ROC10,10)+2\*SMA(ROC15,10)
+3\*SMA(ROC20,10)+4\*SMA(ROC30,15), 9-bar signal line; long on a
cross-up while KST<0, short on a cross-down while KST>0; exits on the
opposite cross, 2xATR stop, 3xATR trail, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 202 | 32.7% | -$2,287 | -22.0% | -1.72 | -28.5% | -$11.32 | 0.76 |
| ETH | 206 | 34.0% | -$1,846 | -18.5% | -1.34 | -25.7% | -$8.96 | 0.82 |
| HYPE | 198 | 41.4% | +$5,582 | +56.4% | +2.89 | -11.1% | +$28.19 | 1.45 |
| **Combined** | **606** | **36.0%** | **+$1,449** | — | — | — | +$2.39 | — |

## Verdict: net positive combined, but carried by a single leg —
loser on BTC and ETH

Combined +$1,449 looks green until you open it: every dollar of it
(and more) comes from HYPE (+$5,582). The other two coins are firm
losers, and the loss structure is worse than Coppock's:

- **BTC is the worst leg** (-$2,287, Sharpe **-1.72**, PF 0.76,
  expectancy -$11.32/trade, MaxDD -28.5%): the sign-gate keeps
  entries early but BTC's 1h reversals still fade every KST turn;
  fees ($2,133) are nearly the whole story of the loss.
- **ETH loses cleanly too** (-$1,846, Sharpe -1.34, PF 0.82): the
  KST cross is no better than the raw Coppock cross here.
- **HYPE is the standout of the batch** (+$5,582, Sharpe +2.89, PF
  1.45, 41.4% win, expectancy +$28.19/trade, DD only -11.1%): the
  smoothed multi-timeframe momentum genuinely caught HYPE's
  trending regimes. But one coin out of three, in one 7-month
  window, is regime luck until proven otherwise — the same
  indicator loses on the two largest coins.
- 606 trades is a decent sample: the red sign on BTC/ETH is not a
  thin-sample artifact.

## Calibration note

Shipped the standard signal=9. A 6/9/14 signal-length sweep is in
CALIBRATION.md: the longer 14 smooths the cross and improves
BTC/ETH (still red) while nearly matching 9 on HYPE; 6 is the
worst everywhere. The 9 was fixed a priori (Pring's standard) —
no in-sample adoption, even though 14 is the in-sample combined
winner (+$3,374).

## Mechanism

Martin Pring's Know Sure Thing: KST = 1\*SMA(ROC(10),10) +
2\*SMA(ROC(15),10) + 3\*SMA(ROC(20),10) + 4\*SMA(ROC(30),15), where
ROC(n) = 100 \* (close/close.shift(n) - 1); the longest timeframe
carries the largest weight, so KST turns later but smoother than a
single ROC. Signal line = SMA(KST, 9). Long when KST crosses above
its signal **while KST is still below zero** (early-turn entry, not
a late extension); short on a cross-down while KST is still above
zero. Exits on the opposite cross (ungated). 2xATR hard stop, 3xATR
chandelier trail, 200-bar max hold.

Source: Know Sure Thing (Martin Pring) —
https://www.ebc.com/forex/know-sure-thing-indicator-explained-formula-and-strategies

## Limitations

- Two of three coins lose; the green combined number is a HYPE-only
  phenomenon. Do not read this as a working strategy — it is a
  working HYPE leg attached to two losers.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The sign-gate (long only while KST<0) suppresses late-chase
  entries but also skips the cleanest trend legs — the
  rally-then-crash case only crosses down after KST is already
  negative, so the gate skips the short entirely.
- Never tune the shipped signal length on this window (see
  CALIBRATION.md).
