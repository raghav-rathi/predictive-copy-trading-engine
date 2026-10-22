# DEMA Trend Cross — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 13:00 UTC
(ms `[1773446400000, 1792627199000)`; actual data starts 2026-03-14
22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,301 bars
BTC/ETH, 5,299 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=140 bars.

## Results (shipped config: DEMA(21)/DEMA(55) cross, long on cross-up,
short on cross-down, exits on the opposite cross, 2xATR stop,
2.5xATR trail, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 169 | 36.7% | -$1,102 | -11.0% | -0.70 | -26.5% | -$6.52 | 0.85 |
| ETH | 164 | 33.5% | +$544 | +5.4% | +0.51 | -15.1% | +$3.32 | 1.06 |
| HYPE | 181 | 35.4% | -$74 | -0.7% | +0.05 | -21.9% | -$0.41 | 0.99 |
| **Combined** | **514** | **35.2%** | **-$632** | — | — | — | -$1.23 | — |

## Verdict: a loser — DEMA crosses whipsaw on 1h crypto

Combined -$632 across 514 trades, and there is no silver leg to hide
behind: BTC loses -$1,102 (PF 0.85, MaxDD -26.5% — the deepest hole of
the three), HYPE is dead flat (-$74, PF 0.99, Sharpe +0.05), and ETH's
+$544 is borderline noise (PF 1.06, expectancy +$3.32, and $1,461 in
fees — nearly 3x the net). The 1h cross fires too early on choppy
legs: DEMA's lag reduction, which is the mechanism's selling point,
also makes it react to moves that do not persist, and the 2xATR stop
then absorbs each false start. Win rates in the low-to-mid 30s with a
1% risk size cannot carry the trade count.

Treat this as a negative result: Mulloy's DEMA cross, at (21,55) with
these risk settings, does not beat costs on 1h BTC/ETH/HYPE over this
7-month window. The (21,55) pair was shipped a priori and stays the
registry config regardless of the sweep — see CALIBRATION.md.

## Calibration note

Shipped the specified fast/slow=(21,55). A (10,30)/(21,55)/(34,89)
sweep is in CALIBRATION.md: all three settings lose combined
(-$2,494 / -$632 / -$2,670 respectively). The (21,55) pair was fixed
a priori — adopted before the sweep, not because of it — so its
least-bad ranking is an in-sample observation, not a justification.

## Mechanism

DEMA: EMA1 = EMA(close, n), EMA2 = EMA(EMA1, n),
DEMA = 2×EMA1 − EMA2. Long when DEMA(21) crosses above DEMA(55);
short on the cross below. Exits are the opposite cross — a cross back
means the trend read failed. 2xATR hard stop, 2.5xATR chandelier
trail, 200-bar max hold.

Source: DEMA (Patrick Mulloy, TASC Jan 1994) —
https://forex-station.com/download/file.php?id=3525533&sid=69c919d7260e3323d4ab1f31c1bb8753

## Limitations

- Single 7-month crypto window; 514 trades is a thin sample.
- ETH leg is near-noise (fees ~3x net); HYPE leg is flat; BTC leg is negative.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped pair on this window (see CALIBRATION.md).
