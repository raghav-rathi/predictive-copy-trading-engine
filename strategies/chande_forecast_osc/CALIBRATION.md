# Chande Forecast Oscillator — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-19, same costs/sizing). One parameter varied
against the shipped config: the TSF regression window (shipped 20 →
10 / 40). Signal SMA 3, sign gate, 2xATR stop, 40-bar max hold
unchanged.

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| TSF 20 (shipped) | BTC | 922 | 29.9% | -$7,109 | -9.08 | 0.57 |
| TSF 20 (shipped) | ETH | 891 | 32.7% | -$5,511 | -5.58 | 0.66 |
| TSF 20 (shipped) | HYPE | 1,019 | 34.8% | -$5,941 | -7.36 | 0.62 |
| TSF 10 | BTC | 958 | 30.6% | -$7,137 | -8.90 | 0.55 |
| TSF 10 | ETH | 966 | 31.2% | -$6,710 | -7.88 | 0.58 |
| TSF 10 | HYPE | 1,091 | 37.8% | -$5,490 | -6.55 | 0.66 |
| TSF 40 | BTC | 956 | 28.6% | -$7,099 | -8.72 | 0.55 |
| TSF 40 | ETH | 880 | 28.7% | -$6,369 | -6.72 | 0.60 |
| TSF 40 | HYPE | 962 | 34.3% | -$5,098 | -5.73 | 0.67 |

## One-line verdict

- **TSF 10 / TSF 40:** nothing changes the story — every variant loses
  $5k–$7k per coin with ~900–1,100 trades. A longer regression window
  (40) trims the HYPE loss slightly (-$5,098) but the trade count and
  the churn profile are essentially identical.
- **The parameter is not the problem.** The churn comes from the
  signal layer (a 3-bar SMA of FO crossed both ways), not the forecast
  window: any TSF length still produces an oscillator that whipsaws
  across its own fast signal line. Fixing this would need a slower
  signal, a volatility filter, or a minimum-hold rule — all of which
  are different strategies, not calibrations.
- **Shipped decision:** keep TSF 20 as specified. The sweep exists to
  document that the window length is not the lever.
