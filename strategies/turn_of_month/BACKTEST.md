# Turn of the Month — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 8 | 25.0% | -284.65 | -0.99 | -5.2% | -35.58 | 0.30 |
| ETH | 8 | 50.0% | -241.37 | -0.94 | -4.6% | -30.17 | 0.28 |
| HYPE | 8 | 25.0% | -266.85 | -0.88 | -3.0% | -33.36 | 0.49 |
| **Combined** | **24** | **33.3%** | **-792.87** | **-1.12** | **-4.3%** | **-33.04** | **0.37** |

Fees: total $175.25.
Exits: BTC {'stop': 8}; ETH {'stop': 8}; HYPE {'stop': 8}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29,207.13.

## Verdict: LOSER — -$792.87 on 24 trades, combined Sharpe -1.12, MaxDD -4.3%, PF 0.37.

The trade count is exactly as designed (8 month-ends per coin:
Mar 31 through Oct 31), and all three coins lose with the same
shape — expectancy about -$30 to -$36 per trade. The striking
fact is the exit split: all 24 trades end on the harness
2xATR stop / 2.5xATR trail, and the calendar exit (day-3
23:00 bar) never fires once. Over a ~4-day hold in 1h crypto,
a 2.5xATR chandelier trail from the peak is hit before the
calendar window closes on every single turn. The equity-index
turn-of-month effect, as implemented here with the
batch-standard risk layer, does not survive crypto
volatility. Fees ($175.25) are a minor part of the loss; the
losses are stop-outs. With 24 trades the sample is small, but
there is no coin and no month in which the calendar leg pays.
No parameter was tuned; the window was not widened.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Only 24 trades — the verdict is "loses here with this risk
  layer", not a claim about the equity-index effect itself.
- The result is conditional on the 2xATR stop / 2.5xATR trail:
  the calendar exit never gets a chance to execute.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
