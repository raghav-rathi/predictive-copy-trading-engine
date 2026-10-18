# 3/10 Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-18
(~5,224 bars each; the disk cache covers exactly this window).
Note: the coordinator's example epoch constants (1741910400000–1760828400000)
decode to 2025 dates — a year off — so the correct 2026 bounds
(1773525600000–1792328400000) were used instead, matching the stated window.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: SMA(3)-SMA(10) of (h+l)/2 vs SMA(16) trigger,
long on cross-up with osc>0, short on cross-down with osc<0, exit on
cross back, 1.5xATR stop, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 325 | 30.2% | -$5,592 | -55.9% | -4.72 | -55.9% | -$17.21 | 0.55 |
| ETH | 328 | 29.6% | -$1,337 | -13.4% | -0.47 | -32.2% | -$4.08 | 0.91 |
| HYPE | 300 | 36.0% | -$1,942 | -20.1% | -1.34 | -28.5% | -$6.47 | 0.85 |
| **Combined** | **953** | **31.9%** | **-$8,872** | — | — | — | -$9.31 | — |

## Verdict: LOSER

Negative on all three coins, -$8,872 combined over 953 trades. The
trend filter (osc>0 / osc<0) does not save it: the 16-bar trigger lags,
so most crosses fire as momentum is already exhausted, and the
cross-back exit cuts winners at the first pullback while the 1.5xATR
stop takes the full loss on the failures — win rate ~30–36%, profit
factor 0.55–0.91. The gross book is underwater on every coin, so the
failure is the edge, not the costs (fees are a drag but PF<1 gross is
the verdict). Raschke's 3/10 was built for equity-index swing trading
on daily bars with discretionary context; as a mechanical 1h crypto
signal it loses.

## Calibration note

Shipped exactly the specified parameters (3/10/SMA16, trend filter,
cross-back exits, 1.5xATR stop, 48-bar max hold, WARMUP=60). A
one-variant sweep (faster SMA(8) trigger) is reported in
CALIBRATION.md — it does not rescue the strategy (BTC still -$5,445,
ETH worse at -$3,563; HYPE improves to -$483 but stays negative).

## Mechanism

median = (h+l)/2; osc = SMA(3)-SMA(10); signal = SMA(16) of osc. Long
when osc crosses above signal AND osc > 0; short when osc crosses below
signal AND osc < 0. Exit when osc crosses back through the signal line.

Source: Linda Raschke & Larry Connors, *Street Smarts* (1995) —
implementation reference — https://www.tradingview.com/scripts/lindaraschke/

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- Only 1h bars tested; daily bars untested.
