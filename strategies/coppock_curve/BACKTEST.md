# Coppock Curve — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:00 UTC
(ms `[1773446400000, 1792589754418)`; END computed at run time,
on-disk cache `data/candles/*_1h.csv` through 13:00 UTC; the direct
API route was flapping, so the fetch used the cached bars rather
than a live re-pull — no bars fabricated): 5,296 bars BTC/ETH, 5,294
HYPE (HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: Coppock = WMA(ROC(14)+ROC(11), 10) linear
weights, long on a cross above zero, short on a cross below zero,
exits on the opposite cross, 2xATR stop, 3xATR trail, 200-bar max
hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 263 | 30.0% | -$2,314 | -22.2% | -1.41 | -31.6% | -$8.80 | 0.80 |
| ETH | 276 | 31.2% | -$1,311 | -13.1% | -0.70 | -24.3% | -$4.75 | 0.90 |
| HYPE | 240 | 36.7% | +$3,089 | +30.9% | +1.70 | -11.3% | +$12.87 | 1.21 |
| **Combined** | **779** | **32.6%** | **-$535** | — | — | — | -$0.69 | — |

## Verdict: net loser — green only on HYPE, red everywhere else

Combined -$535 on 779 trades, expectancy -$0.69/trade. The strategy
is a loser in this window, and the structure of the loss is blunt:

- **BTC is the worst leg** (-$2,314, Sharpe -1.41, profit factor
  0.80, MaxDD **-31.6%**): the zero-cross fires late on BTC's fast
  1h reversals, so entries buy breakdowns and sell breakdown-bounces;
  fees ($2,761) exceed the net loss.
- **ETH is negative but closer to noise** (-$1,311, PF 0.90,
  expectancy -$4.75): same late-cross problem, softer drawdown
  (-24.3%).
- **HYPE is the only green leg** (+$3,089, Sharpe +1.70, PF 1.21,
  DD -11.3%): HYPE's trending regimes reward the slow zero-cross;
  but one coin out of three does not make an edge — it is the
  regime, not the indicator, doing the work here.
- 779 trades is a reasonable sample, which makes the red sign harder
  to wave away: this is not a thin-sample artifact, it is the
  oscillator mis-firing on range/reversal structure two coins out of
  three.

## Calibration note

Shipped the canonical WMA length=10. A 7/10/15 WMA-length sweep is in
CALIBRATION.md: no setting is positive on BTC or ETH (all six
coin-reads negative); HYPE peaks at 7 (+$3,684) and fades as the
length grows. The sweep does not rescue the strategy — it only
reshuffles which HYPE leg is greenest. Shipped 10 was fixed a priori
(no in-sample adoption).

## Mechanism

E.S.C. Coppock (Barron's, 1962): Coppock = WMA(ROC(14)+ROC(11), 10)
with linear weights (newest bar heaviest), where ROC(n) = 100 *
(close / close.shift(n) - 1). Long when the curve crosses above the
zero line (momentum turning from negative to positive), short when it
crosses below; exits on the opposite cross. 2xATR hard stop, 3xATR
chandelier trail, 200-bar max hold.

Source: Coppock Curve (E.S.C. Coppock, 1962) —
https://en.wikipedia.org/wiki/Coppock_curve

## Limitations

- Coppock was designed for MONTHLY index closes (the 14/11 lookbacks
  are the 11-to-14-month "mourning period"); on 1h crypto it is a
  fast momentum oscillator, not a bottom-detector — and on BTC/ETH it
  loses. The canonical params were kept anyway for comparability;
  the regime mismatch is real and shows in the numbers.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- HYPE leg's +$3,089 is the only green — treat it as
  coin-regime luck, not a portable edge, until out-of-sample.
- Never tune the shipped WMA length on this window (see
  CALIBRATION.md).
