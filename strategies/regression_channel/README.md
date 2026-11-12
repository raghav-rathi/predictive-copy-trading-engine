# Linear Regression Channel

A linear regression channel mean-reversion system. The OLS regression
line over the last 100 bars is the "fair value" trend; the bands are
the line plus/minus 2.0 standard deviations of the residuals over the
same 100 bars. Price stretched to a band is overextended; the trade
is taken when price crosses back inside the band, betting on the
reversion to the midline, and exited at the midline itself.

## Rules

- **Long entry:** close crosses back above the lower band (coming up
  from below/at the band).
- **Short entry:** close crosses back below the upper band.
- **Long exit:** close crosses back above the regression midline.
- **Short exit:** close crosses back below the regression midline.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
  Max hold 120 bars.

All computation is causal, so signals on bar i use only data through
bar i's close.

## Source

- Linear Regression Channel (Technical Analysis Pro): https://www.technical-analysis-pro.com/indicators-linear-regression-channel/

Paper only, no live execution.
