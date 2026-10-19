# Chande Forecast Oscillator

Chande's linear-regression forecast oscillator on Hyperliquid 1h perps.

**Idea:** fit an OLS line on the trailing 20 closes, forecast one bar
ahead, and trade the forecast error — FO = (close − forecast)/close×100
crossing its 3-bar signal line, gated on the sign of FO.

**Signals:** long on FO crossing above signal with FO>0; short on
cross below with FO<0; exit on the cross back. 2xATR stop, 40-bar max
hold, 1% risk/trade.

**Status:** backtested 2026-03-14 → 2026-10-19 on BTC/ETH/HYPE — the
worst of the batch (combined -$18,561, PF 0.57–0.66). It overtrades:
~1,000 trades/coin, one round-trip every ~5 bars, fees alone
$15,659. See BACKTEST.md for the autopsy and CALIBRATION.md for the
TSF-window sweep (window length is not the lever).
