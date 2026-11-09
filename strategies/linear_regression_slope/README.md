# Linear Regression Slope

OLS regression of close on bar index over the last 20 bars: slope = Σ(x − x̄)(y − ȳ) / Σ(x − x̄)² with x = 0..19, R² = slope²·Sxx / SStot (the fraction of the window's price variance the fitted line explains). The slope is normalized by price (slope / close) so it is comparable across coins priced orders of magnitude apart. R² is pure fit quality — direction comes from the slope's sign.

## Rules

- Long: the LinReg(20) slope turns positive (slope > 0 with the previous bar's slope ≤ 0) AND R² ≥ 0.5. Exit on the slope turning negative (slope < 0) or R² falling below 0.3.
- Short: mirror — the slope turns negative AND R² ≥ 0.5. Exit on the slope turning positive or R² < 0.3.
- All windows end at bar i, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- LuxAlgo — R-squared Trend Fit (R² as the squared correlation of price against bar index; direction from the slope): https://www.luxalgo.com/library/concept/r-squared-trend-fit/
- Blockspot — What is the linear regression trend slope? (slope = direction and rate of change; R² = whether to believe it): https://blockspot.io/what-is-the-linear-regression-trend-slope/
- Technical Analysis Pro — Linear Regression Channel (R² bands; slope sign = bias): https://www.technical-analysis-pro.com/indicators-linear-regression-channel/

Paper only, no live execution.
