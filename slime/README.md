# Slime Family guardrails for the copy-trading engine

"The AI proposes, the server decides." — an implementation of the
[Slime Family](https://x.com/localminimaa) agent-trading architecture,
adapted to Hyperliquid perps and **paper mode only**.

## The loop

One turn of `runner.SlimeLoop.step()`:

1. **Stops first** — the watchdog sweeps open paper positions for
   stop-loss / take-profit / trailing-stop hits *before* anything else,
   and runs on its own timer even while proposers sleep.
2. **Read the market** — one `MarketSnapshot` (mids, 1h/24h change,
   funding, volume, whale flow).
3. **Quiet turn** — if the snapshot is unchanged since last turn, skip
   thinking entirely (stops were still checked in step 1).
4. **Think** — each slime (species) proposes in a strict schema:
   one `thought` string + a list of `Trade{side, coin, size_usd,
   rationale}`. A proposer can never execute; it has no path to the
   ledger.
5. **Server check** — `RiskServer` validates every trade: schema,
   coin blocklist (reuses the engine's `COIN_BLOCKLIST` from
   `paper/paper_tracker.py`), owner allowlist, max position USD, max
   open positions, engine kill-switch + daily-loss breaker (reuses
   `hyperliquid/risk.py`), per-trade price-impact cap. Rejections are
   logged with reasons, never silently dropped.
6. **Sell-back check** — the honeypot rule adapted: an immediate full
   exit into the current order book must recover ≥ 80% of entry
   notional, else the trade is refused (`sellback.py`).
7. **Preview** — margin required, estimated fees, liquidation price,
   worst-case loss, position after trade. The preview code path is
   identical for live; live stays gated (see below).
8. **Execute (paper)** — fills against the paper ledger at mid.
9. **Board** — proposal, verdict, execution, and stop events all
   posted to the append-only JSONL journal; `board.render_html()`
   builds the static public board (trades table, per-slime P&L/mood,
   thoughts feed).

## Species (strategy personalities)

| Slime      | Personality                                          |
|------------|------------------------------------------------------|
| `momentum` | rides strong 24h moves, skips extreme funding        |
| `scalper`  | fades sharp 1h spikes, small size                    |
| `sniffer`  | follows whale flow, only with the 24h trend          |
| `surfer`   | small entries when 1h and 24h trends agree           |
| `degen`    | apes the biggest 1h mover at $50k — the risk server exists to say no |

All species are heuristic so the loop runs with **no API keys**. An LLM
proposer can implement the same `Proposer` protocol.

## Paper vs live

- **Paper**: everything above runs end to end. Paper results are
  simulated and are **not** evidence of live edge.
- **Live**: refused. `SlimeLoop` raises if `live_mode=True`, and the
  engine's live executor (`hyperliquid/mirror.py`) raises
  `NotImplementedError` by design. There is no live code path to
  accidentally enable.

## Run it

```bash
# verification: proves the guardrails (all green required)
python3 slime/verify_guardrails.py

# demo loop with a stub market (paper)
python3 - <<'EOF'
import sys, time
sys.path.insert(0, '.')
from slime.runner import SlimeLoop, LoopConfig
from slime.sellback import StubBookFeed
from slime.proposer import MarketSnapshot

books = {"HYPE": {"mid": 30.0,
                  "bids": [(29.9, 1000.0)], "asks": [(30.1, 1000.0)]}}
def market():
    return MarketSnapshot(snapshot_id="demo", ts=time.time(),
                          mids={"HYPE": 30.0},
                          chg_1h={"HYPE": 5.0}, chg_24h={"HYPE": 8.0},
                          funding={"HYPE": 0.0001},
                          volume_24h={"HYPE": 5e7},
                          whale_flow={"HYPE": 5e5})
loop = SlimeLoop(LoopConfig(), StubBookFeed(books), market,
                 slime_names=["momentum", "scalper"])
loop.run(3)
loop.board.render_html("slime/board/index.html")
print("board: slime/board/index.html")
EOF
```

For live Hyperliquid books instead of stubs, use
`slime.sellback.HyperliquidBookFeed` (public API, no keys) — still
paper execution only.

## Files

- `proposer.py` — strict proposal schema + 5 heuristic species
- `risk_server.py` — server-side validator (owner rules)
- `sellback.py` — exit-liquidity check + book feeds
- `watchdog.py` — independent per-minute stops loop (reuses engine `ExitManager`)
- `preview.py` — pre-sign transaction preview
- `board.py` — JSONL journal + public-board HTML generator
- `runner.py` — the slime loop + paper ledger
- `verify_guardrails.py` — guardrail proofs (a–d), exit 0 = green
