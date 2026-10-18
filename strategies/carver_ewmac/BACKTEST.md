# EWMAC Forecast (Rob Carver) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
2026-03-14 → 2026-10-18 (5,224 bars BTC/ETH; 5,222 HYPE — cache extended
to Oct 18 during the batch run).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=300 bars (252-bar z-score window + EMA spin-up).

**Window note:** the batch brief's literal filter `[1741910400000,
1760828400000]` maps to 2025-03-14 → 2025-10-18, which is empty (the
cache starts 2026-03-14). The comment's intent ("2026-03-14 →
2026-10-18") matches the full cache, so the full cached range was used.

## Results (shipped config: EWMAC(8,32)+(16,64)+(32,128), z-scored by
252-bar rolling std and averaged, forecast = clip(10*z, ±20), long on
cross above +10 / short on cross below −10 / flat between, 2xATR stop,
120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 69 | 20.3% | +$822 | +8.2% | +0.68 | -19.6% | +$11.91 | 1.18 |
| ETH | 65 | 16.9% | +$873 | +8.7% | +0.68 | -17.6% | +$13.43 | 1.20 |
| HYPE | 80 | 27.5% | -$888 | -8.3% | -0.57 | -13.2% | -$11.10 | 0.79 |
| **Combined** | **214** | **21.5%** | **+$807** | — | — | — | +$3.77 | — |

## Verdict: mixed (leaning winner on majors, loser on HYPE)

BTC and ETH both print positive with Sharpe +0.68 and profit factor ~1.2
on a classic trend-follower profile (low-teens win rate, winners larger
than losers). HYPE loses -$888 with a 0.79 profit factor — the forecast
whipsaws on HYPE's choppier 1h structure and the ±10 band exits cut
winners before they pay for the whipsaw entries. Combined +$807 on 214
trades is a thin edge, and the coin split (works on BTC/ETH, fails on
HYPE) says "regime-dependent" rather than "robust". Fees ($1,576
combined) are material but not the story: gross edge exists on the
majors, absent on HYPE.

## Calibration note

Shipped exactly the specified parameters (three EWMAC rules, 252-bar
z-score, ±10/∓10 band, 2xATR stop, 120-bar max hold, WARMUP=300). A
single-rule (16,64) variant is reported in CALIBRATION.md — it beats the
shipped blend in-sample, but adopting it would be selecting on the same
7-month window, so the specified 3-rule blend stays.

## Mechanism

raw(fast,slow) = EMA(fast) − EMA(slow) of close for (8,32), (16,64),
(32,128); z_i = raw_i / 252-bar rolling std(raw_i); combined_z = mean of
the three; forecast = clip(10 × combined_z, −20, +20). Long entries on
forecast crossing above +10, short on crossing below −10; longs exit
when the forecast falls back below +10 (shorts mirror). 2xATR hard
stop, no trailing/target (the forecast band manages the trade), 120-bar
max hold.

Source: Rob Carver, *Systematic Trading* + EWMAC rule specs —
https://qoppac.blogspot.com/2023/01/

## Limitations

- Single 7-month crypto window; no bull-market or multi-year sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- Harness sizes fixed 1% risk per trade; Carver's real system scales
  position by forecast strength — not modeled here.
- 252-bar z-score window makes the first ~300 bars warmup-only.
