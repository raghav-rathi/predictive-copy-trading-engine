# Kase Peak Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00
UTC (ms `[1773525600000, 1792328400000)`): 5,223 bars BTC/ETH,
5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=310 bars (corrected from the brief's 260 — see
CALIBRATION.md).

## Results (shipped config: KaseCD cross with PeakMax filter,
exits on the opposite KCD cross or PeakOut, 2xATR stop, 3xATR
trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1,365 | 37.7% | -$8,711 | -87.1% | -11.05 | -87.4% | -$6.38 | 0.53 |
| ETH | 1,339 | 38.9% | -$7,944 | -79.4% | -8.84 | -79.7% | -$5.93 | 0.60 |
| HYPE | 1,311 | 44.2% | -$5,819 | -58.1% | -5.04 | -60.0% | -$4.44 | 0.74 |
| **Combined** | **4,015** | **40.2%** | **-$22,474** | — | — | — | -$5.60 | — |

Every signal gate fires on every coin: long entries 642/611/607
and short entries 728/735/708 (BTC/ETH/HYPE) over the window.
PeakOut-long fires on 201/218/187 bars per coin — a real gate,
not a dead one. The mirror short PeakOut never fires, by
construction (PeakOsc ≥ 0; see README).

## Verdict: a heavy loser — the worst kind, a high-frequency one

Combined −$22,474 across 4,015 trades — the account loses 58–87%
per coin. This is not a marginal failure: Sharpe −5 to −11,
profit factors 0.53–0.74, max drawdowns −60% to −87%. The
mechanism is visible in the trade counts: KaseCD crosses zero
roughly every 4 bars, so the engine trades ~6 times a day per
coin, paying $17,791 in fees alone across the three coins
($7,144 BTC / $6,202 ETH / $4,445 HYPE). Even gross of fees the
edge is negative (win rates 38–44% with sub-1.0 profit factors),
so this is not a fee problem — the 1h KCD cross is a losing
signal here, and the frequency multiplies it.

Exit-reason breakdown (all coins): 3,421 signal exits vs 594
stops, 0 max-hold exits — positions are chopped out by the next
KCD cross within a few bars, before the trail or the hold cap can
matter. The PeakMax filter does not save the longs either:
PeakOsc exceeds PeakMax on ~10% of bars and the long PeakOut
exit fires ~200 times per coin, but the longs still lose.

Do not trade this on 1h bars. The published construction is
faithful (see CALIBRATION.md for the formula checks), which is
exactly why the result is informative: Kase's oscillator as
specified is a daily-bar tool, and transplanting its 9-bar CD
cross to hourly crypto produces whipsaw, not signal.

## Mechanism

KSDI_up(n) = ln(H/min(L,n))/σ_n, KSDI_dn(n) =
ln(L/max(H,n))/σ_n, σ_n = stddev of log returns over n;
PeakOsc = mean over n ∈ {5,…,50} of (KSDI_up − KSDI_dn);
KaseCD = PeakOsc − SMA(PeakOsc, 9); PeakMax = max(2× rolling-100
stddev of PeakOsc, 90th pct of |PeakOsc| over rolling 250).
Long on a KCD cross above 0 with PeakOsc < PeakMax, short on a
cross below 0 with PeakOsc > −PeakMax; exits on the opposite KCD
cross or PeakOut. 2xATR stop, 3xATR trail, 150-bar max hold.

Sources: https://www.kaseco.com/support/articles/PeakOuts_and_Permissions.pdf
and https://www.luxalgo.com/library/concept/kase-studies/

## Limitations

- Single 7-month crypto window, but 4,015 trades is a large
  sample for the sign — the negative result is not a small-sample
  artifact.
- PeakOsc ≥ 0 by construction makes the short-side PeakMax filter
  vacuous and the short PeakOut unreachable; the shipped short
  leg is effectively "every KCD cross-down".
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped KCD SMA on this window (see
  CALIBRATION.md).
