# Ichimoku MACD

Ichimoku cloud + Tenkan/Kijun cross, confirmed by MACD histogram
sign: only take the cross when price is on the cloud's side and
MACD momentum agrees.

## Rules

- **Ichimoku (Tenkan 9, Kijun 26, Senkou B 52, displacement 26):**
  Tenkan = 9-bar (high+low)/2, Kijun = 26-bar (high+low)/2,
  Senkou A = (Tenkan+Kijun)/2 displaced 26 bars forward,
  Senkou B = 52-bar (high+low)/2 displaced 26 bars forward.
  The cloud used is the spans **as plotted at bar i** (displaced
  values, computed from data ending at bar i-26 — fully causal).
  The Chikou span is NOT used: it reads 26 bars into the future.
- **MACD(12, 26, 9):** standard EMA MACD; the histogram
  (line − signal) is the confirmation.
- **Long entry:** close above the cloud (above BOTH Senkou A and
  Senkou B) AND Tenkan crosses above Kijun AND MACD histogram > 0.
- **Short entry:** close below the cloud (below both spans) AND
  Tenkan crosses below Kijun AND MACD histogram < 0.
- **Long exit:** Tenkan crosses below Kijun OR the close is no
  longer above the cloud (close <= the higher span — it has
  entered the cloud or fallen below it).
- **Short exit:** Tenkan crosses above Kijun OR the close is no
  longer below the cloud (close >= the lower span).
- The harness risk layer's 2xATR stop / 2.5xATR trail also
  applies. Max hold 120 bars.
- Warmup 120 bars.

All computation is causal, so signals on bar i use only data
through bar i's close.

## Source

- Ichimoku Kinko Hyo (Goichi Hosoda); MACD (Gerald Appel):
  https://www.investopedia.com/terms/i/ichimoku-cloud.asp

Paper only, no live execution.
