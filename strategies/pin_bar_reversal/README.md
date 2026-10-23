# Pin Bar Reversal

**Mechanism:** a pin bar (Pinocchio bar) is a single candle whose long
rejection tail dominates the bar — the market probed far in one
direction and was rejected back, closing near the opposite extreme.
The textbook shape (Martin Pring's price-action canon):

- **Bullish pin:** `lower_wick >= 2/3 × range`, `body <= 1/3 × range`,
  `upper_wick <= 0.2 × range`, AND the low is a 5-bar swing low.
- **Bearish pin:** the mirror image at a 5-bar swing high.

The 5-bar swing location filter is the Pring rule: a long tail in
the middle of nowhere is noise; it only counts as rejection at a
local extreme.

**Trade logic:** the pin IS the entry — long on a bullish pin,
short on a bearish pin. Exits are the opposite rejection (a bearish
pin ends a long), plus a 1xATR stop just beyond the rejection tail,
the textbook 2R take-profit (2xATR), and a 48-bar max hold. Both
sides, no trail — these are mean-reversion swings, not trend legs.

**Why it should work (in theory):** a pin at a swing extreme prints
the footprint of aggressive absorption — sellers shoved price down,
buyers took the other side and closed the bar up. Textbook
price-action says the tail marks where the large orders sat, and
price tends to retrace from there.

**Sources:**
- https://halleytech.substack.com/p/reversal-candlestick-patterns
- https://quantstrategy.io/blog/what-is-pin-bar-pin-bar-reversal-trading-strategies/
