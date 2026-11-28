# Balance Line Pullback (Bill Williams) — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive;
cache ends 2026-11-27 14:00 UTC, last bar 13:00 UTC):
6,185 bars BTC/ETH, 6,183 HYPE. Funding not modeled
(fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: pullback touch of the Balance
Line (jaw) within 5 bars + turn with the mouth open; exit
on a close back through the jaw, lips crossing teeth, or
the opposite entry; 2xATR stop, 3xATR trail, 96-bar max
hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 410 | 22.7% | -$5,271.09 | -52.5% | -3.45 | -58.7% | -$12.86 | 0.61 | $3,063.13 |
| ETH | 446 | 22.2% | -$3,919.80 | -39.3% | -2.16 | -50.4% | -$8.79 | 0.73 | $2,822.21 |
| HYPE | 398 | 27.4% | -$2,239.82 | -22.4% | -1.17 | -28.3% | -$5.63 | 0.84 | $1,780.48 |
| **Combined** | **1,254** | **24.0%** | **-$11,430.71** | **-38.1%** | **-2.99** | **-44.3%** | **-$9.12** | **0.72** | **$7,665.82** |

Exit-reason breakdown: BTC signal 212 / stop 198 / max_hold 0;
ETH signal 244 / stop 202 / max_hold 0; HYPE signal 243 /
stop 155 / max_hold 0. Net % is the final-equity return
($30k combined -> $18,585.61); Net $ is the sum of
closed-trade PnL.

## Verdict: the Balance Line is a magnet for whipsaws, not a springboard

Combined -$11,430.71 on 1,254 trades (win rate 24.0%, PF
0.72) is a decisive loser. The setup fires constantly --
the jaw is a slow SMMA(13) that price crosses and touches
all the time on 1h bars, so "pullback to the balance line"
is a routine event, not a rare one -- and the turn that
follows is usually a 1-bar poke: 699 of 1,254 trades die
on the signal exit (close back through the jaw or the
mouth closing) and 555 more hit the 2xATR stop. The mouth
gate does not save it: the jaw-only variant (see
CALIBRATION.md) is even worse (-$16,565), but the gated
version still loses on every coin. It is not a fee story:
gross PnL before the $7,665.82 of fees is still
-$3,764.89. The 96-bar max hold never binds (0 trades):
every trade resolves through the signal exit or the stop
first. Honest read: on 1h crypto the Balance Line does
not act as a level the trend resumes from -- it acts as a
line price chops through, and buying the touch buys the
chop.

## Mechanism

Indicators in indicators.py: median = (h+l)/2; jaw/teeth/
lips are SMMA(median, 13/8/5) seeded with the simple
average of the first n prices (UNSHIFTED -- the book's
8/5/3-bar forward displacement is a plotting convention
and would be lookahead); atr14 is Wilder ATR(14); a touch
is a bar low (longs) or high (shorts) inside jaw +/-
0.5*ATR, with a 5-bar rolling "recent touch" window.
signals.py enters long when a recent touch, close > jaw,
close > prior close, and mouth open up all hold on the
first bar of such a run (mirror for shorts), enters
neither if both would fire on one bar (impossible in
practice), and exits a long on a close crossing below the
jaw or the lips crossing below the teeth, or on the
opposite entry. The house 2xATR stop / 3xATR trail sit
behind the signal exit, with a 96-bar max hold.

Sources: Bill Williams, "Trading Chaos" / "New Trading
Dimensions" -- Balance Line trades --
https://www.forexfactory.com/thread/26044-profitunity-chaos-trading-system-by-bill-williams?page=83

## Limitations

- 1,254 trades is plenty of sample: the loss is not a
  small-sample artefact, it is the strategy.
- Single ~8.5-month crypto window, all three coins in the
  same regime for much of it; funding unmodeled;
  next-bar-open execution vs idealized entry.
- The 5-bar touch window and 0.5xATR tolerance are the
  strategy's own readings of the book's qualitative rule;
  the book does not fix them.
- Never tune the shipped touch tolerance or mouth gate on
  this window.
