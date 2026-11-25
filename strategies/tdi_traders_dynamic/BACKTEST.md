# Traders Dynamic Index — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: RSI(13), price line SMA(2),
signal line SMA(7), base line SMA(34), bands ±1.6185σ, long
on price crossing above signal with price above base and
base above 50, short on the mirror, exit on the opposite
cross, 2xATR stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 246 | 27.2% | -$3,133 | -31.0% | -3.43 | -33.6% | -$12.74 | 0.56 |
| ETH | 241 | 26.1% | -$2,572 | -25.7% | -2.35 | -26.6% | -$10.67 | 0.65 |
| HYPE | 220 | 32.7% | -$1,617 | -15.6% | -1.88 | -20.1% | -$7.35 | 0.73 |
| **Combined** | **707** | **28.6%** | **-$7,322** | — | **-3.73** | **-25.4%** | **-$10.36** | **0.64** |

Fees: BTC $2,248, ETH $1,785, HYPE $997 (total $5,030).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL. Combined start $30,000,
end $22,765. Exits: BTC 196 signal / 50 stop; ETH 185 / 56;
HYPE 189 / 31.

## Verdict: a loser on every coin — the base-line filter does not save the cross

Combined -$7,322 on 707 trades, win rate 26.1–32.7%,
profit factor 0.56–0.73 on every coin, expectancy
-$7.35 to -$12.74 per trade. The TDI is a momentum panel
built for trending forex days; on 1h crypto the RSI(13)
price line whipsaws across its 7-bar signal line, and the
base-line filter (price above base, base above 50) mostly
just delays entries until the move is already half over —
the crosses that clear the filter are the ones chasing.
BTC is worst (-31.0%, Sharpe -3.43, MaxDD -33.6%); HYPE
is least-bad (-15.6%, PF 0.73) and still firmly negative.
There is no coin, no sub-period, no reading in which the
shipped config works on this window.

## Calibration note

Shipped the specified RSI(13). A 10/13/21 RSI-period sweep
on this batch-46 window is in CALIBRATION.md: 10 gives
-$7,629 combined (759 trades), 21 gives -$7,645 (701
trades). The knob is flat — all three values lose ~$7.3–7.6k
— which only confirms the verdict: the failure is the
cross-plus-filter logic, not the RSI length. No in-sample
adoption; the shipped config stays 13.

## Mechanism

RSI(13) (Wilder). Price line = SMA(RSI, 2); signal line =
SMA(RSI, 7); market base line = SMA(RSI, 34); volatility
bands = base ± 1.6185 × std(RSI, 34) (computed and stored;
not used by the shipped signals). Long = price line crosses
above signal line AND price line > base line AND base line >
50; short = price line crosses below signal line AND price
line < base line AND base line < 50. Exit on the opposite
price/signal cross, with no base-line condition. The harness
2xATR hard stop / 3xATR chandelier trail sit behind the
cross as a safety net for gap-through moves; 60-bar max hold.

Source: Dean Malone, Traders Dynamic Index (TDI) —
https://www.quantum-algo.com/blog/guides/traders-dynamic-index-tdi/
(verified URL, given in the batch-46 brief; the guide
confirms RSI 13, the 2/7/34 line lengths, the 1.6185
volatility-band multiplier, and the 50-level base-line
filter).

## Limitations

- Single ~8.4-month crypto window; 707 trades — the failure
  is consistent across all three coins, not a sample-size
  artefact.
- The base-line filter is slow (SMA(34) of RSI): after any
  sharp pullback the price line must climb back above a
  still-elevated base before a long can fire, so entries
  systematically chase.
- The calibration sweep shows the RSI period cannot rescue
  it (10/13/21 all lose $7.3k+), so the "right" RSI length
  is not identifiable from this window — and would not
  matter if it were.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped RSI period on this window.
