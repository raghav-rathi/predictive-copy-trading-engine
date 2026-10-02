# Strategy: a self-scoring copy/fade engine for Robinhood Chain

Status: research + scaffold. Paper-trade first. Nothing in this repo trades
live, and live mode is hard-gated (see "The paper-trade gate").

## 1. The opportunity we started from

In September 2026, @outputlayer published "Predictive Copy Trading on
Robinhood Chain", describing a same-block copy mechanism, and reported an
operator running it at scale: wallet
`0x53a42d2d0fdd60bf8f833fb94841349095a74024`, ~33 FOMO whale target
wallets, fixed ticket per wallet, 53 episodes / 45 green, +$21.3k realized,
≈ $6k/day. We set out to build the same class of system. Then we
reverse-engineered the operator before writing any trading code
(`docs/research/`), and the findings changed the design.

## 2. The mechanism (as published, and as it really works)

Robinhood Chain is an Arbitrum Orbit L2 (chain ID 4663, ~100 ms blocks,
single sequencer). FOMO app buys flow:

```
FOMO frontend -> Solana deposit -> relay -> solver -> fill on Robinhood Chain
```

The Solana leg settles 0.5–1.6 s before the Robinhood Chain fill — at
~100 ms blocks, that is 5–16 blocks of advance warning about **who** is
about to buy, but not **what**. The published trick: don't predict the
token, test for it on-chain. A detector contract snapshots the candidate
balances of the target wallet, is called repeatedly across the window,
and at execution time buys whichever candidate token's balance grew;
if none grew, the call reverts for ~31k gas (~cents). Pre-signed calls
are streamed a few per block so one lands in the fill's own block,
immediately behind it.

Our on-chain review of 58 operator episodes (53 attributable) supports
the same-block core claim — the operator's buys do land in the fill's
block, earlier evidence: fill index 12 / copy index 13 in block 67532022
in the original write-up; ZKSTR 9→10 in block 77900398 in ours. Two
published details did **not** survive contact with the chain:

- **Strict N+1 adjacency is not the general pattern.** In TANK (block
  77880520) the fill was at index 5 and the copy at 21, with a reverted
  operator attempt at index 2 in the same block. The robust pattern is
  "same block, after the fill by log order", not "exactly one behind".
- **"Fixed ticket per whale" is not visible in the operator's legs.**
  Observed payment legs run $2.00–$3,000.00 USDG plus WETH legs, routed
  multi-hop (WETH→stock-token→target). Ticket sizing per target remains
  unproven either way.

Design consequence: the detector should treat "landed anywhere after the
fill in the same block" as success, and the burst schedule should be a
few calls per block across the whole window, not a single snipe.

## 3. What reverse-engineering the operator taught us

Full evidence: `docs/research/operator-whale-wallets.md` (episode-level
attribution) and `docs/research/whale-profiles.md` (FIFO profitability
profiling of the top 7 targets, Blockscout data to block 77,996,388).

1. **We found 25 distinct target wallets across 53 same-block episodes**,
   not 33. The gap is plausibly unexamined older history (our pagination
   stopped at block 76,052,367), 4 unassigned + 1 ambiguous episodes, and
   an excluded small-ticket method class — but 33 remains unverified.

2. **The top 7 targets are one bot fleet, not seven whales.** Every
   Relay-routed buy for wallets 1, 2, 3, 4, 5 and 7 was funded by the
   same EOA, `0xf70da97812CB96acDF810712Aa562db8dfA3dbEF`, via
   RelayRouter. They trade in lockstep (wallet 7's XRAY buy landed 15 s
   before wallet 2's; wallet 6, the only non-Relay wallet, bought IRIS
   and ZIP exactly one block after wallet 5's buys). Copying the list
   buys one strategy seven times, with zero diversification.

3. **The fleet loses money.** Priced realized PnL across the profiled
   wallets ≈ **−5,095.82 USDG** over 34 priced episodes. The operator's
   public claim (+$21.3k, 45/53 green) is not supported by the targets'
   own closed records — the operator may still be fine (their exits are
   not the whales' exits), but "copy these entries, hold like they do"
   is a losing strategy on the whales' own books.

4. **Per-wallet verdicts** (details and per-token outcomes in the profile
   report):
   - Wallet 1 `0x8A71…6599b` (9 copies): 9.1% win rate, −5,099.50 USDG,
     all 9 copied tokens net red. The most-copied target is the worst.
     **FADE candidate.**
   - Wallet 2 `0x23ad…b7BD8` (9 copies): ≈ +664.65 USDG, 4/5 priced
     green — the only net-positive record, with copyable tickets
     (~$0.5–1.9k) and ~20 min median hold. Most capital still sits in
     open positions, so the verdict is provisional. **WATCH.**
   - Wallet 4 `0x453f…89875` (3 copies): +162.41 USDG on 3 priced closes
     (2/3 green), but its only genuinely-attributed copied token,
     DOTSPAD, closed −24.4%; 12 of 15 closes unpriced. **WATCH.**
   - Wallet 5 `0xbDcE…A9520` (3 copies): 0/5 green, −822.73 USDG on the
     fully-priced set. **FADE candidate.**
   - Wallet 6 `0x4189…beAD4` (2 copies): its two copied tokens are the
     operator's best outcomes anywhere (ZKSTR +43.6%, SCORE +7.9%) —
     but it trades $13.50–$27 fixed tickets with 1 s–3 min holds. The
     edge is in the structure, and the structure is uncopyable: a
     copier's slippage exceeds the ticket. **PASS.**
   - Wallet 3 `0x0B64…89327` (7 copies): ~$10 tickets, ~26 s median
     hold, +12.33 USDG total — fee dust. **PASS.**
   - Wallet 7 `0xf4d8…5eA5ba6` (2 copies): zero closable positions in
     coverage; net-distributing older inventory while being copied.
     **PASS/AVOID.**
   - Operator attributions for wallets 3↔4 look swapped (DRAGON/bankme
     appear in wallet 4's history; ERRAND/HARMONIC in wallet 3's) — a
     reminder that even the operator's targeting layer has bugs, and
     one more reason not to inherit anyone's list blindly.

**Conclusion: the mechanism is sound; naive target-copying loses.** The
only defensible version of this trade is to score targets yourself,
continuously, and let the scores — not a copied list — decide what gets
mirrored, what gets faded, and what gets ignored.

## 4. Our design: the self-scoring copy/fade engine

Five layers. Signal and execution are the operator's; scoring, exits and
the paper gate are ours.

### 4.1 Signal layer — Solana watcher (`watcher/solana_watcher.py`)
Tails Solana logs for the FOMO deposit flow and emits NDJSON triggers
`{whale, sol_timestamp, deposit_tx}`: who is about to receive a fill, and
when the 5–16 block window opens. The Robinhood Chain sequencer feed
(`watcher/chain_feed.py`) tracks block cadence and measures the actual
trigger→fill latency distribution, because the published 0.5–1.6 s window
is a measurement from one week in September, not a constant of nature.
The Solana-deposit→Robinhood-wallet mapping is **TODO-verify** and fails
closed (triggers carry `whale: null` until it is pinned down).

### 4.2 Scoring layer (`scorer/wallet_scorer.py`)
Continuously re-scores every candidate wallet from Blockscout API v2
token transfers (the RPC route is unreliable from some networks; the
explorer API is the data source that worked). Per wallet, FIFO
buy→sell pairing over swap legs yields: closed positions, win rate,
realized PnL in observed quote legs (USDG/WETH reported separately,
never silently converted), median hold, typical ticket, open inventory.
Classification, thresholds all in `config.example.json`:

- **COPY** — enough closed positions, win rate and realized PnL above
  thresholds, *and* a copyable structure: median hold and ticket inside
  configured bounds (a 26-second, $10 flipper fails this even if green).
- **FADE** — proven loser: enough closed positions with win rate and PnL
  below thresholds. We never buy what they buy. Optionally (config,
  default off) their fresh buys act as exit/avoid signals on anything we
  hold, and are logged as paper short candidates for research only.
- **PASS** — everything else: uncopyable structure, insufficient data,
  or no edge either way. The engine does nothing with PASS wallets.

Current classifications from our research are seeded in
`data/whales_seed.json` (fade: wallets 1, 5; watch: 2, 4; pass: 3, 6, 7
and the 18 single-episode wallets, which are unrated, not endorsed).
The scorer overwrites these with live-computed classes as data accrues.

### 4.3 Execution layer (`contracts/`)
`CopyDetector.sol`: owner-managed registry mapping each COPY wallet to
its candidate token set. `snapshot(whale)` records candidate balances;
`attemptCopy(whale)` diffs live balances against the snapshot and, on
growth, swaps into the grown token under a per-call spend cap and
slippage bound; on no growth it reverts `NoGrowthDetected` — the cheap
miss that makes streaming calls across the window economical. Only
COPY-classified wallets are registered, and registration is driven by
the scorer's output, never by hand-copied lists. Router/PoolManager
addresses for Robinhood Chain are **TODO-verify-on-chain** in the code
and deliberately not fabricated.

### 4.4 Exit layer (`engine/engine.py`)
Entries are the easy half; the profiled fleet's losses are mostly an
exit problem (wallet 1 holds a median ~51 min into names that bleed
−30…−90%). Rules, all configurable, first trigger wins:
1. **Mirror exit** — the copied whale sells the token: we sell.
2. **Hard stop-loss** — position down `stop_loss_pct` from entry.
3. **Take-profit** — position up `take_profit_pct` from entry.
4. **Max hold** — `max_hold_seconds` elapsed regardless of PnL. A copier
   is never left bagholding a proven-loser fleet's position overnight.
5. **Fade override** — a FADE-classified wallet buys a token we hold:
   log it; with config enabled, exit. (Default: log only.)

### 4.5 The paper-trade gate (headline feature)
The engine defaults to paper mode: it consumes the same triggers, opens
hypothetical positions at trigger-window prices, runs the same exit
manager, and logs every entry/exit/PnL to `data/paper_trades.csv`. Live
execution requires **both**:
- `live_trading: true` set explicitly in config (the engine refuses to
  start live on a missing/ambiguous flag), **and**
- a positive paper track record over a configurable minimum sample
  (e.g. ≥ 30 closed paper trades with positive aggregate PnL), checked
  at startup from the CSV.

Given what the fleet data showed — the loudest public claim in this
space does not match its own targets' books — no capital should touch
this mechanism before it has proven itself on paper, in public commits.

## 5. Risks and open questions

- **FOMO-flow dependency.** The entire signal is one app's relay
  plumbing. If FOMO changes its deposit path, solver, or latency
  profile, the 5–16 block window can vanish overnight. The feed client
  measures the window continuously so decay is visible, not silent.
- **Rug risk.** Robinhood Chain memecoin flow is launchpad-driven
  (Pons/Noxa.fun/hood.fun class venues), and an $18.4M extraction ring
  has already been reported on this chain. COPY classification must
  stay earned and current; yesterday's green wallet can be tomorrow's
  exit liquidity — ours or theirs.
- **Edge decay from publication.** The operator's list is now public
  (including in this repo). Published targets attract competing copiers
  and can be gamed by the targets themselves. Our scorer re-derives
  targets continuously precisely so the list is a measurement, not a
  heirloom.
- **Unverified plumbing.** The Solana→EVM wallet mapping, the exact
  candidate-token set per whale (the detector needs to know what to
  snapshot; per-whale token history from the scorer is the current
  answer), the Robinhood Chain router/PoolManager wiring, and the feed
  schema are all marked TODO-verify in code. None are guessed.
- **The operator's own PnL.** We verified the whales' books, not the
  operator's exits. Whether the operator actually netted +$21.3k by
  exiting better than his targets is an open empirical question; the
  paper engine's job is to answer it for our exits, not to assume it.
- **Costs.** Misses are cheap (~31k gas), but burst streaming across
  every window for every COPY wallet adds up; gas accounting belongs in
  the paper log from day one so the gate evaluates net, not gross.

## 6. Roadmap

1. Verify the Solana deposit instruction layout and the deposit→wallet
   mapping against observed fills; un-null the watcher.
2. Verify Robinhood Chain swap wiring on-chain (Universal Router /
   PoolManager addresses, USDG/WETH pools); fork-test the detector.
3. Run the scorer over the full 25-wallet seed set + continuous
   candidate discovery; publish `data/targets.json` snapshots.
4. Paper-run the engine end-to-end; review the gate metrics weekly.
5. Only after a positive paper record: a capped, single-wallet live
   pilot — behind the same exit rules, with the gate left in place.

*Research code. Not financial advice. Memecoins on a young L2 can go to
zero between two 100 ms blocks; size accordingly, or better, stay on
paper until the data says otherwise.*
