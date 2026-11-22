# Negative-Funding Fade — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) plus hourly funding from
the local cache (`data/funding/{COIN}_1h.csv`, 6,062 contiguous
rows per coin, fetched via `fetch_funding.py` from Hyperliquid
`fundingHistory`; turn-negative events in-window: BTC 276, ETH
271, HYPE 314).
**Window:** 2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC
(BTC/ETH 6,040 bars, HYPE 6,038 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. **Funding
PnL is NOT modeled** (the pinned driver runs with
`use_funding=False`) — see Limitations.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long only. WARMUP=24 bars.

## Results (shipped config: long on funding turning negative,
8-bar hold, 2xATR stop, no trail/target)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 177 | 42.4% | -$1,181 | -10.5% | -0.85 | -20.0% | -$6.67 | 0.83 |
| ETH | 174 | 46.6% | -$1,460 | -14.6% | -1.52 | -20.3% | -$8.39 | 0.78 |
| HYPE | 197 | 49.2% | +$1,763 | +17.6% | +1.43 | -7.9% | +$8.95 | 1.22 |
| **Combined** | **548** | **46.2%** | **-$878** | — | — | — | -$1.60 | — |

Fees: BTC $1,740, ETH $1,367, HYPE $1,106 (total $4,214).

## Verdict: loser on price action; the funding leg is untested

Combined net is −$878 on 548 trades — a genuine loser on the
price leg, not a thin-sample artifact. The sample is large (548
trades) and the loss is consistent on the two majors (BTC −$1,181,
ETH −$1,460, both with Sharpe < −0.8 and ~−20% max drawdown).
HYPE is the lone winner (+$1,763, Sharpe +1.43), but one coin
out of three does not rescue the thesis, and HYPE's own 2026
funding regime (negative only 10% of hours vs ~18–20% for BTC/ETH)
means its turns are a different, rarer event.

Stated plainly: buying the turn-negative bar and holding 8 hours
lost money on BTC and ETH in this window. The most likely
mechanics: (a) negative funding often marks a market already
falling hard, so the "crowded short" fade buys into momentum
against it for 8 hours; (b) the round-trip cost (0.11% of
notional in fee + slippage) is large against an 8-hour price move
— fees alone ($4,214) are ~5x the combined net loss, so even a
flat price leg loses.

## Mechanism

Long on the first bar funding turns negative (after a bar >= 0),
exit after an 8-bar hold; 2xATR stop, 8-bar max hold, long only.
All params fixed a priori; no optimization.

Source: Jlabs Digital, "Dissecting Funding Rate model"
(https://typefully.com/jlabsdigital/dissecting-funding-rate-model-BGOoArs).

## Limitations

- **Funding income is not modeled.** The thesis has two legs —
  price mean-reversion AND receiving funding payments while long
  during negative funding — and this backtest measures only the
  price leg. The funding leg is small (8h × |rate| × notional;
  typical |rate| ~1–5e-5/hr gives ~0.01–0.04% of notional, vs
  0.11% round-trip fees), so it cannot plausibly flip the combined
  −$878 into a win, but the honest statement is that the full
  Jlabs return (which includes funding received) is not what was
  tested here.
- The source's +227.67% / Sharpe 0.84 is since 2020 across (per
  Jlabs) a broader set of conditions; this test is one 8-month
  window, three coins, 1h bars, next-bar-open execution.
- The 2xATR stop is a risk overlay, not in the source; it cuts
  some 8h holds short. The 7-day Janorium variant was not tested.
- Never tune the shipped parameters on this window.
