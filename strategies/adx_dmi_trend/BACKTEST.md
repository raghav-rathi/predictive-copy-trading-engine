# Wilder ADX/DMI Trend System — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC/ETH 6,064 bars, HYPE 6,062 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=40 bars.

## Results (shipped config: ADX(14) > 25 gate, DI cross entry;
exit on opposite DI cross or ADX < 20; 2xATR harness backstop;
168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 90 | 25.6% | +$1,609 | +16.1% | +1.14 | -16.4% | +$17.88 | 1.40 |
| ETH | 87 | 27.6% | -$1,073 | -10.7% | -1.03 | -19.6% | -$12.33 | 0.72 |
| HYPE | 101 | 19.8% | -$1,896 | -19.0% | -2.50 | -19.0% | -$18.77 | 0.51 |
| **Combined** | **278** | **24.1%** | **-$1,360** | — | — | — | **-$4.89** | — |

Fees: BTC $970, ETH $726, HYPE $458 (total $2,154).

## Verdict: loser overall — the BTC win does not save it

Combined −$1,360 across 278 trades (24.1% win rate, −$4.89
expectancy). The headline split is the story: BTC +$1,609 with
Sharpe +1.14 and profit factor 1.40, ETH −$1,073, HYPE −$1,896
with Sharpe −2.50 and profit factor 0.51. Two of three coins
lose, and the combined total is negative.

- The BTC win is not a validated edge. It is one coin out of
  three over one 8-month window, with a 25.6% win rate — the
  profit comes from a minority of large winners, exactly the
  profile that flips sign when one or two trades go the other
  way. Nothing in the ETH/HYPE results corroborates it.
- Fees ($2,154) exceed the combined loss ($1,360): gross PnL
  before fees is ≈ +$794. The system is roughly break-even
  before costs and a loser after them — the honest description
  is "no edge after fees", not "broken mechanism". The DI cross
  does catch some real 1h trends (hence the gross-positive
  result), but not enough to pay Hyperliquid taker fees at 1%
  risk sizing.
- The ADX gate did its job as specified: 278 trades in eight
  months (~1 per coin per week) versus the Keltner combo's
  1,084 in the same window — the system sat out the chop, as
  Wilder intended. The trades it did take were still only
  ~24% winners.
- The 168-bar max hold never binds (0 max-hold exits) and the
  2xATR stop fires ~25% of the time; most exits are the
  opposite DI cross or ADX falling below 20, as designed.

Stated plainly: do not trade this as a standalone system. The
BTC print is a single-coin artifact; the combined evidence is a
small loser driven by costs, and the mechanism shows no robust
cross-coin edge on 1h crypto.

## Mechanism

LONG when +DI crosses above -DI while ADX(14) > 25; exit on the
opposite cross or ADX < 20; short mirror. All params fixed a
priori; no optimization.

Source: J. Welles Wilder, *New Concepts in Technical Trading
Systems* (1978) —
https://en.wikipedia.org/wiki/Average_directional_movement_index.

## Limitations

- Single 8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 278 trades is a moderate sample: the combined −$1,360 is
  meaningful as "no edge after fees" but the per-coin split
  (BTC + / ETH, HYPE −) is within what chance produces across
  three correlated coins — do not quote the BTC +$1,609 as an
  edge.
- Never tune the shipped parameters on this window — least of
  all the 25/20 ADX thresholds, which directly control how many
  trades fire.
