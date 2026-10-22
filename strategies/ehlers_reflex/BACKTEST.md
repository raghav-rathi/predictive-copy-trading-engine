# Reflex Zero-Lag — Backtest

**Data:** local cache CSVs (`data/candles/{BTC,ETH,HYPE}_1h.csv`,
columns t,o,h,l,c,v; t in ms), sliced to the batch window
2026-03-14 00:00 UTC → 2026-10-21 23:59:59 UTC
(ms constants `[START_MS=1773446400000, END_MS=1792627199000)`;
actual data starts 2026-03-14 22:00 UTC for BTC/ETH):
5,301 bars BTC/ETH, 5,299 HYPE. No API calls; fully offline.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=100 bars.

## Results (shipped config: Reflex(20), long on a zero cross up, short
on a zero cross down, exits on the opposite cross, 2xATR stop,
2.5xATR chandelier trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 198 | 31.3% | -$2,290 | -22.1% | -1.73 | -24.3% | -$11.57 | 0.73 |
| ETH | 208 | 33.2% | +$859 | +9.4% | +0.74 | -16.5% | +$4.13 | 1.10 |
| HYPE | 201 | 37.8% | +$449 | +5.1% | +0.47 | -12.2% | +$2.23 | 1.05 |
| **Combined** | **607** | **34.1%** | **-$982** | — | — | — | -$1.62 | 0.96 |

## Verdict: an honest loser — BTC bleeds it out and fees eat the rest

Combined -$982 across 607 trades (PF 0.96, expectancy -$1.62).
The Reflex zero-cross fires fast — that is the advertised property —
but on 1h crypto it fires *too* fast: 607 round trips in 7 months
with a 34.1% win rate means most crosses are whipsaw, not turns. The
ledger, coin by coin:

- **BTC is the bleed** (-$2,290, PF 0.73, Sharpe -1.73, MaxDD
  -24.3% — the deepest hole of the three). BTC's 1h chop flips
  Reflex across zero repeatedly; every flip is a full trade with
  fees, and the legs rarely extend past the 2xATR stop.
- **ETH is borderline noise** (+$859, PF 1.10, expectancy +$4.13).
  Green on paper, but fees ($1,940) are 2.3x the net — one fewer
  winning trade and the sign flips.
- **HYPE is borderline noise too** (+$449, PF 1.05, expectancy
  +$2.23, fees $1,114 = 2.5x net). No HYPE carry story here, unlike
  the TRIX batch — Reflex's fast crosses do not sit in HYPE's trend
  legs any better than they sit in BTC's chop.
- Fees total $5,107 across the three coins: the strategy is a
  fee-transfer machine. The win rate (31–38%) is structurally too
  low for the 2.5xATR-trail payoff shape on these coins.

There is no coin doing the work and nothing to rescue by selection:
every length in the CALIBRATION.md sweep is negative combined.

## Calibration note

Shipped the specified length=20, fixed **a priori** — adopted before
any backtest ran. The 10/20/40 sweep (CALIBRATION.md) shows 20 as the
least-bad in-sample setting (combined -$982 vs -$5,542 at len=10 and
-$1,392 at len=40), but that ranking does not change the shipped
config and leaning toward any other length *because* of the ranking
would be in-sample selection. The honest read: the length moves the
whipsaw frequency, not the conclusion — this variant is not a
three-coin strategy on this window.

## Mechanism

Reflex(20): SuperSmoother(20) of close (Ehlers 2-pole,
`a1=exp(-1.414·π/20)`, `b1=2·a1·cos(1.414·180°/20)`,
`filt[i]=c1·(x[i]+x[i-1])/2 + c2·filt[i-1] + c3·filt[i-2]`),
`Slope=(filt−filt.shift(20))/20`,
`Sum=Σ_{k=1..20}((filt+k·Slope)−filt.shift(k))`,
`MS=0.04·Sum²+0.96·MS.shift(1)`, `Reflex=Sum/√MS`. Long on a cross
above zero, short on a cross below zero; exits on the opposite
cross. 2xATR hard stop, 2.5xATR chandelier trail, 150-bar max hold.

Source: Reflex (John Ehlers, TASC Feb 2020) —
https://forex-station.com/download/file.php?id=3357914&sid=f0c366b7fa15f05758951129dc3ccff7

## Limitations

- Single 7-month crypto window; 607 trades across 3 coins is a thin
  sample, and the combined ledger is negative.
- ETH and HYPE legs are near-noise (fees 2.3x/2.5x net); BTC leg is
  a real loser.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- The zero-cross fires on Reflex's own normalized scale — the
  threshold is fixed at zero with no chop filter, which is likely
  the main structural weakness.
- Never tune the shipped length on this window (see CALIBRATION.md).
