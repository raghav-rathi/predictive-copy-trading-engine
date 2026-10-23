# RSI(14) Swing-Pivot Divergence

The classic momentum-divergence ruleset, mechanized with
lookahead-free confirmed swing pivots.

## Mechanism

**Pivots.** A swing HIGH at bar p is marked iff `h[p]` is the maximum
of `h[p−3 .. p+3]`; a swing LOW iff `l[p]` is the minimum of
`l[p−3 .. p+3]` (flat ties collapse to the first bar of the run).
The pivot is only *confirmed* — usable by signals — at the close of
bar p+3, so every signal on bar j uses data known at bar j's close.

**Divergence.** Compare the last two confirmed pivots, price pivot vs
RSI(14) at the same pivot bars. Fires once per pair, on the
confirmation bar of the newly confirmed (second) pivot:

| Pattern | Price | RSI(14) | Action |
|---|---|---|---|
| Regular bullish | lower low | higher low | long_entry |
| Hidden bullish | higher low | lower low | long_entry |
| Regular bearish | higher high | lower high | short_entry |
| Hidden bearish | lower high | higher high | short_entry |

Regular divergences fade the exhausted leg (reversal); hidden
divergences ride the continuing trend (the pullback holds while
momentum on the pullback weakens — textbook trend-continuation).

**Exits.** Longs exit when any bearish divergence confirms; shorts
exit when any bullish divergence confirms. (The harness executes all
signals at the next bar's open.)

**Risk.** 1.5xATR hard stop, 2xATR chandelier trail, no fixed target
(exits are divergence/signal-driven), 96-bar (~4-day) max hold, 1%
risk/trade, 3x leverage. Both directions enabled.

Parameters (fixed a priori, no optimization): RSI 14, pivot
left=right=3, ATR(14). WARMUP=80.

Usage:

```python
from strategies.rsi_divergence import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
CALIBRATION.md for the a-priori parameter note.

Sources:

- RSI divergence rules (regular + hidden, entries/exits) —
  https://www.tradingsim.com/blog/divergence
- Community RSI-divergence indicator implementations —
  https://www.tradingview.com/scripts/search/rsi%20divergence/
