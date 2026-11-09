# Gann Square of Nine

W. D. Gann's Square of Nine: numbers spiral outward from 1, and a 45-degree step around the spiral adds 0.25 to the square root of price, so the level at angle θ from a price p is (√p ± θ/180)². A full 360° turn adds 2.0 to the square root. This strategy builds the 45° ladder from the prior close: with s = √p and base = ⌊s·4⌋/4 (the quarter-root grid line at or below s), the levels are L_j = (base + 0.25·j)², j = 0..8. The level immediately above the prior close is L_1 and the level at or below it is L_0.

## Rules

- Long: the close crosses above the nearest level above the prior close (L_1) AND that level sits within 0.5% of the prior close. Exit on a close back below the entry level, or on reaching the next level up (L_2 at the entry bar).
- Short: mirror — the close crosses below the nearest level below the prior close (L_0) with that level within 0.5% of the prior close. Exit on a close back above the entry level, or on reaching the next level down.
- The entry level / target are entry-bar state (tracked causally in `signals.py`); entries only fire while flat. ATR stop / trail from the risk layer also applies.
- Note the 0.5% filter binds very differently by coin: the ladder spacing in percent terms is ≈ 0.5/√p, so on BTC (~$80k, √p ≈ 283) levels sit ~0.18% apart and the filter almost always passes, while on HYPE (~$20, √p ≈ 4.5) levels sit ~11% apart and the filter passes only when the prior close happens to sit within 0.5% below a level. HYPE therefore trades far less often.

## Source

- Investopedia — Gann Indicators Explained: https://www.investopedia.com/articles/trading/08/gann-indicator.asp
- PatternsWizard — Gann Square of Nine (formula + worked example): https://patternswizard.com/gann-square-of-nine/
- TradingView — Gann indicators and strategies (Square of Nine Pine scripts, Level = (√Base ± n × 0.25)²): https://www.tradingview.com/scripts/gann/page-3/?script_access=all
- Forexop — Gann Square of 9 Calculator: https://forexop.com/gann-square-of-9-calculator/

Paper only, no live execution.
