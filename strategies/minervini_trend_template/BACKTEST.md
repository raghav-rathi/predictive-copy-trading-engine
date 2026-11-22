# Minervini Trend Template — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC
(BTC/ETH 6,040 bars, HYPE 6,038 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 6xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=960 bars.

## Results (shipped config: full 8-condition SEPA gate, 20-bar
breakout entry, 50-SMA violation exit, 6xATR stop ≈ 7.5%,
8xATR trail, 720-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 17 | 29.4% | -$112 | -1.1% | -0.38 | -2.9% | -$6.60 | 0.70 |
| ETH | 21 | 23.8% | +$435 | +4.4% | +1.13 | -3.1% | +$20.73 | 1.86 |
| HYPE | 25 | 12.0% | -$264 | -2.6% | -1.18 | -4.8% | -$10.55 | 0.55 |
| **Combined** | **63** | **20.6%** | **+$60** | — | — | — | **+$0.94** | — |

Fees: BTC $55, ETH $52, HYPE $39 (total $146).

## Verdict: breakeven — the gate fires, the edge does not show

Combined net is +$60 on 63 trades: a rounding error, not a
result. The per-coin split says everything about how thin this
is — ETH is +$435 while HYPE is −$264 on near-identical trade
counts, and the win rates (12–29%) are trend-following-low
across the board: the gate's few winners have to carry many
small losers, and on this window they only just do.

- The ETH leg (+$435, PF 1.86) looks like the template working
  until you count the trades: 21, with 5 wins. Five wins is
  noise with a favourable sign.
- The HYPE leg (12.0% win rate, PF 0.55 on 25 trades) looks like
  a failure, but it is the same story in reverse: 3 wins out of
  25, and one more winner flips the sign.
- The BTC leg (−$112 on 17 trades) is dead flat.

Structural observations worth keeping: the gate is selective
enough to fire only ~1 trade per coin per 12 days, which is the
SEPA idea working as intended — but the 52-week conditions are
running on an 8-month window (see CALIBRATION.md), so the gate
is weaker than the original, and the 1h compression means the
"1-month rising 200 SMA" is a much weaker trend statement than
Minervini's daily version. A real verdict would need a longer
window (ideally a full 52 weeks so conditions 7/8 mean what
they say) or a deliberately looser gate validated out-of-sample
— not parameter tuning on this window.

## Mechanism

Full 8-condition gate (price above SMA150/200, SMA150 above
SMA200, SMA200 rising over 720 bars, SMA50 above both, price
above SMA50, ≥25% above trailing low, within 25% of trailing
high, RSI(14) > 55); entry on a close above the trailing 20-bar
high; exit on a close below SMA50 or an opposite breakout;
6xATR stop (≈7.5% target), 8xATR trail, 720-bar max hold. Short
mirror is builder-added. All params fixed a priori; no
optimization.

Source: MQL5, "Automating Classic Market Methods (Part 4): Mark
Minervini's Trend Template" (http://mql5.com/en/articles/22790).

## Limitations

- 63 trades total, per-coin samples 17–25: no per-coin
  statistic here is significant; do not quote the ETH leg as an
  edge or the HYPE leg as a failure.
- The 52-week high/low conditions use the expanding trailing
  high/low over the window to date, not a true 52-week window.
- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
