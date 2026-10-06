# Predictive Copy Trading Engine

A minimal-latency, self-scoring copy/fade engine for Robinhood Chain.

A copy-trading system for **Robinhood Chain** (Arbitrum Orbit L2, chain
ID 4663) that learns from the public operator who pioneered same-block
copy trading there — including the lesson his own data teaches: *the
mechanism is sound; naive target-copying loses.*

**Status: research + scaffold. Paper-trade first. Not live, not
financial advice.**

## What it is

@outputlayer's "Predictive Copy Trading on Robinhood Chain" showed how
to land a copy-buy in the *same block* as a FOMO whale's fill: watch
the Solana leg of the FOMO app (deposit → relay → solver → fill) for
0.5–1.6 s of advance warning about **who** is about to buy, then let a
detector contract figure out **what** at execution time, by diffing the
whale's candidate-token balances and reverting cheaply (~31k gas) when
nothing grew.

We reverse-engineered the operator running that system at scale
(25 target wallets, 53 same-block episodes, all sourced on-chain —
see `docs/research/`), profiled the top targets' actual profitability,
and found:

- The top 7 "whales" are **one bot fleet** behind a single funder EOA
  (`0xf70da97812CB96acDF810712Aa562db8dfA3dbEF`) — no diversification.
- The fleet's priced realized PnL is **≈ −5,095.82 USDG**. Its most
  copied wallet (9×) runs a 9.1% win rate and −5,099.50 USDG; another
  "top" wallet is a $10-ticket, 26-second flipper.
- The operator's public claim (+$21.3k, 45/53 green) is **not
  supported** by his own targets' closed records.

So this project builds the mechanism but replaces the copied list with
a **self-scoring copy/fade engine**: every candidate wallet is
continuously scored on its own realized PnL, win rate, hold times and
ticket sizes; proven-and-copyable wallets get copied, proven losers get
faded (never followed), and everything else is ignored. Exits are
independent of the whales (mirror-sell plus hard stop-loss, take-profit
and max-hold), and **live trading is gated behind a positive paper
track record**. The full reasoning lives in
[`docs/STRATEGY.md`](docs/STRATEGY.md).

## Architecture

| Layer | Component | Role |
|---|---|---|
| 1. Signal | `watcher/solana_watcher.py` | Tails the FOMO Solana deposit flow; emits `{whale, sol_timestamp, deposit_tx}` triggers 5–16 blocks before the fill |
| 1. Signal | `watcher/chain_feed.py` | Robinhood sequencer feed client; measures the real trigger→fill window |
| 2. Scoring | `scorer/wallet_scorer.py` | FIFO buy→sell pairing from Blockscout transfers → win rate, realized PnL, median hold/ticket → COPY / FADE / PASS into `data/targets.json` |
| 3. Execution | `contracts/src/CopyDetector.sol` | Balance-diff detector: snapshot candidates, buy whichever grew, cheap revert on a miss; per-call spend cap + slippage guard |
| 4. Exits | `engine/engine.py` | Mirror-sell, stop-loss, take-profit, max-hold; first trigger wins |
| 5. Gate | `engine/engine.py` | Paper by default; live requires an explicit flag **and** a positive paper record (default: ≥30 closed trades, PnL ≥ 0) |
| 6. Venue 2 | `hyperliquid/` | The same strategy on Hyperliquid perps: WS `userFills` signal (ms), realized-PnL scoring, proportional mirror + Kelly cap, paper-first — see `hyperliquid/README.md` |

## Repo layout

```
contracts/            Foundry project: CopyDetector + unit tests
docs/STRATEGY.md      Strategy design, findings, risks, roadmap
docs/research/        The reverse-engineering reports this is built on
watcher/              Solana deposit watcher + sequencer feed client
scorer/               Wallet profitability scorer (Blockscout API v2)
engine/               Paper-first copy/fade engine (+ examples/)
data/whales_seed.json The operator's 25 targets with our research verdicts
config.example.json   All thresholds, caps, exit params; live_trading: false
hyperliquid/          Hyperliquid perps copy engine: WS signal, scoring,
                      proportional mirror + Kelly cap, exits, reconcile,
                      paper-first runner (see hyperliquid/README.md)
funding/              Delta-neutral funding farm: short perp + long spot on
                      highest 7d-avg-funding coins, paper-only second book
                      (see funding/README.md)
docs/research/copy-engine-research.md  Open-source copy-bot research +
                      Hyperliquid mechanics that the hyperliquid/ module
                      is built on
```

## Quickstart (offline, paper only)

```bash
cp config.example.json config.json   # then edit; keep live_trading: false

# smoke-test the engine against the sample event stream
python3 engine/engine.py --config config.example.json \
  --events engine/examples/events.sample.ndjson \
  --targets engine/examples/targets.sample.json
# -> opens/closes hypothetical trades, writes data/paper_trades.csv

# score the seed wallets (needs network access to Blockscout)
python3 scorer/wallet_scorer.py --config config.json \
  --seed data/whales_seed.json --out data/targets.json

# unit tests for the detector
cd contracts && forge test
```

## What's real vs. TODO

Real: the research (episode-level attribution + FIFO wallet profiles),
the scorer, the paper engine with its exit manager and live gate, the
detector contract logic and unit tests.
TODO-verify before any deployment, deliberately not guessed: the FOMO
Solana program ID and deposit→wallet mapping (the watcher fails closed
until then), the Robinhood Chain router/PoolManager wiring in the
detector, and the sequencer feed message schema. Each is marked
`TODO-verify-on-chain` where it lives.

## Roadmap

1. Verify the Solana deposit layout + deposit→wallet mapping; un-null
   the watcher.
2. Verify swap wiring on-chain; fork-test the detector.
3. Continuous scorer runs + candidate discovery beyond the seed set.
4. Paper-run end-to-end; review gate metrics weekly, in public.
5. Only after a positive paper record: a capped, single-wallet live
   pilot behind the same exit rules.

## Disclaimer

Research code, published to show the work. Not financial advice.
Robinhood Chain memecoin flow is launchpad-driven and rugs are common;
strategies here can lose money fast, which is precisely why the paper
gate exists.
