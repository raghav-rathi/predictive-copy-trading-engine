# Inside Bar Breakout

Trade the expansion out of volatility contraction — the
contraction-then-expansion sequence at the heart of price-action
trading.

## Mechanism

1. **Inside bar (contraction):** strict definition — the bar's
   *whole* range (wicks included) sits inside the prior (mother)
   bar's range:
   `inside = (h < h.shift(1)) & (l > l.shift(1))`. A wick poking
   out by a tick disqualifies the bar. The inside bar signals
   indecision and compressed volatility.
2. **Mother levels:** on an inside bar the setup arms with
   `mother_high = prior-bar high`, `mother_low = prior-bar low`.
   The levels stay armed for up to **5 bars** — after 5 bars with
   no breakout the setup expires (stale compression is not a
   setup). A newer inside bar inside the window resets the levels
   (fresh setup).
3. **Breakout (expansion):**
   - **Long** when the close crosses *above* the armed mother high.
   - **Short** when the close crosses *below* the armed mother low.
   - Crosses are evaluated against the forward-filled armed levels,
     so a signal on bar j uses only data through bar j's close
     (the harness executes at the next bar's open).
   - **Tie-break:** if both crosses fired on the same bar (only
     possible when a newer inside bar re-armed and jumped the
     levels), take the mother bar's direction — bull mother
     prefers long, bear mother prefers short.
4. **Exits:** the opposite breakout signal exits the position
   (`long_exit = short_entry`, `short_exit = long_entry`), on top
   of the risk layer: 1.5xATR hard stop (canon: opposite side of
   the mother bar; 1.5xATR is the harness's parametrized stand-in),
   **2R target** (the classic inside-bar 2:1 minimum), no trailing
   stop, 48-bar (~2-day) max hold. Both directions, 1% risk/trade,
   3x leverage cap.

Parameters: strict inside definition, 5-bar expiry, ATR(14),
stop 1.5xATR, target 2R, max hold 48. WARMUP=40. All fixed a
priori — no optimization (see CALIBRATION.md).

Usage:

```python
from strategies.inside_bar_breakout import indicators, signals, risk

sig = signals.add_signals(indicators.add_indicators(df))
```

See BACKTEST.md for the Hyperliquid 1h (BTC/ETH/HYPE) results and
the honest verdict.

Sources:

- Inside bar candlestick pattern, mechanics and breakout playbook —
  https://www.rebelsfunding.com/what-is-the-inside-bar-candlestick-pattern/
- Inside bar price-action strategy notes —
  http://forexmt4indicators.com/inside-bar-pattern-price-action-strategy/
