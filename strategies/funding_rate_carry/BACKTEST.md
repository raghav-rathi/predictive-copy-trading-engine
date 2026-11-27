# Funding-Rate Carry — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-48 window ms `[1773525600000, 1795788000000)`
(2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC exclusive, last
bar 13:00 UTC): 6,184 bars BTC/ETH, 6,182 HYPE. Funding
series from the local cache (`data/funding/{BTC,ETH,HYPE}_1h.csv`,
6,206 rows each, max t 1795784400000 = Nov 27 13:00 UTC for
all three coins; HYPE was extended from Nov 21 during this
batch -- see the data note below). Every candle bar in the
window has a funding row (0 missing).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=48 bars.

## Results (shipped config: long on fund_avg_24h crossing below
-0.0000125, short on crossing above +0.0000125; exit on
normalization past half the threshold; 2xATR stop, 3xATR
trail, 168-bar max hold)

| Coin | Trades (L/S) | Win% (total) | Price $ | Funding $ | TOTAL $ | Total % | Sharpe (total) | MaxDD (total) | Expectancy (total) | PF (total) |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 8 (4/4) | 25.0% | -$282 | +$14 | -$268 | -2.7% | -1.12 | -2.8% | -$33.45 | 0.33 |
| ETH | 11 (6/5) | 27.3% | -$399 | +$9 | -$390 | -3.9% | -1.36 | -5.7% | -$35.47 | 0.38 |
| HYPE | 24 (0/24) | 33.3% | -$299 | +$26 | -$273 | -2.9% | -0.50 | -7.1% | -$11.37 | 0.76 |
| **Combined** | **43 (10/33)** | **30.2%** | **-$980** | **+$49** | **-$931** | **-3.1%** | **-1.41** | **-4.7%** | **-$21.64** | **0.57** |

Fees: BTC $75.29, ETH $56.04, HYPE $93.21 (total $224.55).
Total % is the final total-equity return (price + funding,
including the mark-to-market of any position still open at
the window end). Combined end equity $29,056.78 on $30k start.

Exit breakdown: BTC stop 6 / signal 2; ETH stop 7 / signal 4;
HYPE stop 22 / signal 2. No max-hold exits. Average hold
~18-21 hours per coin. The 2xATR stop, not the funding
normalization, decides most trades.

## Verdict: the carry is real but tiny; the price leg loses

Combined TOTAL -$931 on 43 trades (30.2% win rate, PF 0.57)
is a loser, but the split is instructive: funding PnL is
POSITIVE on every coin (+$14 / +$9 / +$26, +$49 combined)
-- the strategy does harvest funding exactly as designed,
holding against the crowded side while it pays. The problem
is scale and the price leg: ~20-hour holds at ~0.001% per
hour on ~$10-30k notional yield roughly $1 per trade in
funding, while the 2xATR stop hands back $20-35 per trade in
expectancy on price. Fading the crowded side on price does
not mean-revert within a day on 1h bars; 35 of 43 trades end
on the stop. HYPE is the least bad (PF 0.76, 24 trades, all
shorts -- it can never long at this threshold) and still
loses. Honest read: funding carry at this threshold and
hold length is a real but negligible edge swamped by
adverse price drift. Do not trade it live at this size; the
carry would need far longer holds or far larger notional to
matter, and longer holds would only give the price leg more
room to run against the fade.

## Funding accounting method

The harness runs with `use_funding=False`, so its net PnL is
price-only (gross price move minus fees/slippage). For each
closed trade, `run_backtest.py` computes funding from the
local cache: notional = entry_px x qty; rates = hourly
funding rates with t in [entry_t, exit_t); funding_usd =
`funding_pnl_usd(side, notional, rates)` (positive rate =
longs pay shorts). TOTAL per trade = harness net_pnl +
funding_usd. Combined Sharpe/MaxDD are computed on the
total: each coin's equity curve gets each trade's
funding_usd added at the trade's exit bar (cumulative from
that bar onward), then the three $10k curves are combined
the same way as the price-only runners (union of
timestamps, forward-fill, sum to a $30k curve). A position
still open at the window end contributes no funding (it has
no exit bar yet); its price MTM stays in the harness curve.
Per-coin Sharpe/MaxDD in the table are likewise computed on
each coin's total equity curve.

## Data note

The funding gate for this batch required max t =
1795784400000 (Nov 27 13:00 UTC) for all three coins. BTC
was already there; ETH had been extended by a background
retry fetch before this build started; HYPE was still stale
at 1795266000000 (Nov 21 13:00 UTC) and was extended by this
build in 1-day chunks from the Hyperliquid fundingHistory
API (7 chunks, 144 new rows, no retries needed), bringing
it to 6,206 rows with max t 1795784400000. No funding data
was fabricated: every row comes from the API, floored to
the hour-open ms, and the indicators raise on any missing
row.

Sources: Hyperliquid funding mechanics (positive rate =
longs pay shorts; see `paper/STRATEGY_RESEARCH.md` §3) and
https://swolecharts.com/hyperliquid/funding-rate

## Limitations

- Only 43 trades combined; BTC/ETH cells (8 and 11 trades)
  are thin and no per-coin read generalises.
- Funding is charged hourly on Hyperliquid; the [entry_t,
  exit_t) convention matches the harness's own funding
  window. Intrabar entry/exit timing vs the hourly funding
  timestamp is approximated at bar resolution.
- Single ~8.5-month window; next-bar-open execution vs
  idealized entry; the 168-bar max hold never binds.
- Never tune the shipped threshold on this window.
