# Operator whale wallets — reverse-engineering report

**Operator wallet:** `0x53a42d2d0fdd60bf8f833fb94841349095a74024` (Robinhood Chain, chain ID 4663)
**Status: BLOCKED — 0 of ~33 whale wallets identified. No on-chain data could be read from this environment (evidence below). Nothing in this file is inferred or estimated; the list simply could not be produced yet.**

## What was verified

- Chain ID confirmed once via `eth_chainId` → `0x1237` (4663) at ~03:45 UTC through the public RPC. That single call succeeded; every subsequent read (curl and Python, HTTP/2 and HTTP/1.1, up to 60s timeouts) blackholed with no response.
- The sandbox resolves `rpc.mainnet.chain.robinhood.com` to `198.18.157.248` (198.18.0.0/15, a proxy/TUN fake-IP range). TLS handshakes start; HTTP responses never arrive. General HTTPS egress does work (api.etherscan.io answered), so this is specific to the Robinhood RPC host route, not a dead sandbox.
- Blockscout (`robinhoodchain.blockscout.com/api/v2/...`) returns a Cloudflare JS challenge to direct requests and HTTP 403 to page fetches. Per policy, no bypass was attempted after the denial.

## Pipeline prepared (ready to run, in this directory)

All scripts use only the Python standard library, cache every response under `raw/`, pace requests at ~0.15s, and chunk `eth_getLogs` into 50k-block windows (the public RPC rejects ~1M-block windows).

1. `rpclib.py` — JSON-RPC client (timeouts, backoff, disk cache), operator/known token constants.
2. `scanner.py` — descends from head in 50k-block chunks collecting the operator's ERC-20 Transfer logs (in + out); stops after 60 consecutive empty chunks below the first activity found. Produces `raw/scan_{in,out}_*.json`.
3. `extract_episodes.py` — groups transfers by tx into token-in/token-out episodes (`transfer_episodes.json`); distinguishes buys (non-quote token in) from sells.
4. `block_tracer.py` — for each buy episode: fetches the block, finds the operator tx index, walks up to 12 preceding same-block txs, reads receipts, and identifies the whale as the end-wallet recipient of the same token who does not re-send it within that tx (pools/routers excluded structurally). Writes `copies.json` + `unresolved.json`.
5. `aggregate_report.py` — FIFO-matches operator buys→sells per token, attributes closed-episode PnL to the copied whale, resolves token symbols/decimals via `eth_call`, and regenerates this report with the full table.

## How to unblock (any one of these)

1. **Keyed RPC (fastest):** point the scripts at a keyed endpoint — verified URL patterns from public docs: Alchemy `https://robinhood-mainnet.g.alchemy.com/v2/<KEY>`; QuickNode, Chainstack, dRPC also support chain 4663. Set `RPC` in `rpclib.py` and run `python3 scanner.py && python3 extract_episodes.py && python3 block_tracer.py && python3 aggregate_report.py`. Needs Raghav to provide/approve an API key (signup is an external account action — not done here).
2. **Live-browser Blockscout pass:** the parent agent's live browser passed Cloudflare for x.com earlier; a browser task can read the operator's Blockscout address / token-transfers pages and episode blocks directly (manual but no key needed).
3. **Run from an unrestricted network:** the five scripts are self-contained; from any host that can reach `rpc.mainnet.chain.robinhood.com` normally, the commands in option 1 (public RPC URL) produce the full list unattended.

## Method (for whoever runs it)

A buy episode = operator tx where a non-quote token (not WETH/USDG) transfers in. The copied fill = a tx earlier in the same block (ideally the immediately preceding index; the public proof case is fill idx 12, operator idx 13 in block 67532022) whose receipt transfers the same token to an end wallet. That wallet, aggregated across episodes, is the whale list; the tweet claims 33 targets, 53 episodes, 45 green. Fixed-ticket-per-wallet should show up as uniform buy sizes per whale — a good cross-check when the data lands.

## Explicitly unverified

- The 33-wallet count, the 53 episodes, and the 45-green claim: none could be checked on-chain from here.
- The whale list itself: **not produced**. Any answer naming specific whale wallets at this point would be fabricated.


---

## RESULTS — Live-browser Blockscout pass (2026-10-02)

Recovered via Blockscout API v2 in the live browser after scripted access was Cloudflare-blocked. Read-only; no state changes.

**Operator:** `0x53a42d2d0fdd60bf8f833fb94841349095a74024` — a contract called by rotating EOAs; buy episodes identified by ERC-20 receipts at the operator address (methods 0x00000007 / 0x00000009).

**Coverage:** 58 clear buy episodes found (53 on transfer pages 1–8 + 5 older-phase on pages 9–10; pagination stopped at page 10, block 76052367 — older history below that not exhaustively enumerated). 53 episodes assigned to a whale under the strict same-block rule (end wallet received the same token in the same block, earlier by log order; pool/router/solver/hook legs excluded). 4 examined with no same-block preceding end recipient (AVM 77731535, U 77575335, VRAX 77460183, Suited 76608264). 1 ambiguous (TIDE 76782614) excluded from all counts. A separate method-0x00000005 small-ticket class (17 episodes) excluded as not copy-buys.

### Whale wallets — 25 distinct (53 assigned episodes)

| # | Whale wallet | Episodes | Tokens (block) |
|---|---|---|---|
| 1 | `0x8A71697cc8a6E820C0bc12B29C1b329C3ab6599b` | 9 | STEER (77610718), DOTARENA (77401526), ROBOT (77202838), DOTTIE (77177351), ZIP (77134967), ZUPITER (76811111), GITPAD (76806706), STONKCALL (76674237), SIGIL (76480777) |
| 2 | `0x23ad4067aF541ee28c7f5c69Eff348139Beb7BD8` | 9 | TANK (77880520), XRAY (77867661), WAVE (77446016), DOTTIE (77369560), PONSHI (77258828), TIDE (76919121), MTA (76543240), DOTS (76092924), VLADBOT (76052367) |
| 3 | `0x0B64C0469Be9502A45c79840e180842463189327` | 7 | DRAGON (77485236), bankme (77432283), VRAX (76490804), Suited (76490311), ZKHUB (76396359), Watermelinu (76395323), VRAX (76391362) |
| 4 | `0x453f238A896538cA9560004500Af1392C7889875` | 3 | ERRAND (77094457), HARMONIC (76637260), DOTSPAD (76475193) |
| 5 | `0xbDcE13a1caDEa23a61013Fbfb470c7eEF4bA9520` | 3 | ZIP (77482752), IRIS (76563238), VRAX (76064840) |
| 6 | `0x4189BF4fA87Df00DfFe5dEe85339747F615beAD4` | 2 | ZKSTR (77900398), SCORE (77592914) |
| 7 | `0xf4d8eFcfEA218cE76BfDE064a2Be406345eA5ba6` | 2 | XRAY (77867512), PARLEY (77330249) |
| 8 | `0x0fF344fFa232c31c2731b15121d482A4d79Bc4fa` | 1 (candidate) | OTIS (77876765) |
| 9 | `0x410795f6CC4013DF6aF5E2C05C6A6bFd5C0F0260` | 1 | CLUB (77857841) |
| 10 | `0x20aC05aafC1b5786d7dB843eA98680708f190dce` | 1 | PUNKS (77851688) |
| 11 | `0xA3c7bA27455617Aa74752407e75f43172268Ce89` | 1 (candidate) | revenue (77796405) |
| 12 | `0x516520189516Ba25C20E633289e7fd79EdaFD73c` | 1 | U (77764069) |
| 13 | `0xe87548Bb6bCB664102300353A1751Aa188C36081` | 1 (candidate, low conf.) | MARLIN (77744657) |
| 14 | `0x4f61815D66aC5dD30F8FEF0d642e3946650F8213` | 1 | BALLAST (77692897) |
| 15 | `0xD223225CcAC5E89d75bC373786e5c71EDCbb41f8` | 1 | TRENCHES (77664907) |
| 16 | `0x54e04dF6A6f6FEb56E13937E2eaF3371E5717f3c` | 1 (candidate) | CASINO (77621156) |
| 17 | `0x194DB29F5bEBacF3201aBc9dbDda452116A3FF23` | 1 | ZIP (77299279) |
| 18 | `0xF7c0D9aEe226B632a25b1C096d8c285eD20d55b1` | 1 | FARTDOG (76943815) |
| 19 | `0xD73D6b8B9E875569C0F03c572A3806E619BCBEc2` | 1 | MVA (76657951) |
| 20 | `0xDCE001e4eC11AB58650c51AE9658accbe0F49c48` | 1 | LIGER (76633160) |
| 21 | `0x696d1265C8Fc4F14797aBEBFAe3C43EBFA9D8e28` | 1 | DOTS (76539919) |
| 22 | `0xf3756b61Cc04A16114A6bCa9f1AB6C28273D3174` | 1 (candidate, low conf.) | HI (76338326) |
| 23 | `0xd874259110C6E086F1d2feE474b73e69b8F5DAB0` | 1 | BOTBOOK (76134180) |
| 24 | `0xa984149dA86Ad9Cc8D67a47e3d7B57aDB1415502` | 1 | VRAX (76092757) |
| 25 | `0x03bA951f72e59899Ac8Dab30cB5624dbE5D52Bb8` | 1 | VRAX (76059954) |

Most whale wallets are EIP-7702 delegated user accounts (Simple7702Account) — real FOMO app users, not infrastructure.

### Evidence samples
- Exact N→N+1 (positions via tx API): ZKSTR block 77900398 — whale fill tx `0xed59c564fe6ea7375864a5186772b373669c9bfc0d924f19e49623c4e1208e7c` at position 9 (PoolManager → `0x4189BF4fA87Df00DfFe5dEe85339747F615beAD4`) → operator buy tx `0x92268821d8ef0cfb8e4f4f6694a7fc4fdcab2f19e044f1537f5f99885baec286` at position 10.
- Log-order pair: BOTBOOK block 76134180 — Relay fill tx `0x675e3a90b9c88c21ead60623c441dafbeff42dd5b5b81edd11dd54f6c3759e6d` (log 58 → `0xd874259110C6E086F1d2feE474b73e69b8F5DAB0`) → operator buy tx `0x32f7d96ee5f055730588a58af3fc919ca0e07c76c3b999c90ec8cd45e494ff35` (log 87).
- Log-order pair: VRAX block 76092757 — Relay fill tx `0x9db31f017f2f670c7b21d2a4244be6511e855598c0cfa061090c30aa89a639a2` (log 93 → `0xa984149dA86Ad9Cc8D67a47e3d7B57aDB1415502`; operator paid USDG $1,876.73) → operator buy tx `0xef81fbd751034b7f8d05effb8df7e7acccefb3d65b8300f557d6e4bace256222` (log 104).
- Counterexample to strict adjacency: TANK block 77880520 — fill tx `0x1de38ec53d2013e4b9f9f67b021d643569cf1fd6f855622a1dbdcf0b11d1f465` at position 5 (RelayRouterV3 → `0x23ad4067aF541ee28c7f5c69Eff348139Beb7BD8`) → operator buy tx `0xa5ed9ae86ca1f0fd56c43180b677daf431763b8de5b8a091aadc50f7d0cc3a8b` at position 21. The block also contained a reverted operator attempt at position 2.

### Claims NOT verified / deviations from the tweet
- "~33 whales": 25 distinct strict-rule whales. The rest may hide among the 4 unassigned + 1 ambiguous episodes, the excluded method-0x00000005 class, or history below block 76052367.
- "53 closing episodes / 45 green": 58 clear buys found; the pages 1–8 count (53) matches the claimed 53 numerically, but 5 additional older buys exist. Green/red (P&L) never checked.
- "Fixed ticket per whale": NOT verified. Visible payment legs vary widely (USDG $2.00–$3,000.00; WETH ≈0.4479 / ≈0.5604), and funding is multi-hop (WETH→ORBIO/NVDA/SPCX/HOOD→target), so single legs are not full tickets.
- Strict N+1 adjacency: verified exactly once (ZKSTR 9→10); contradicted by TANK (5→21). General pattern = same block, fill earlier by log order, often with unrelated txs in between.
- Recurring deviation: in OTIS, CLUB, U, MARLIN, AVM, CASINO, U#2, VRAX#1, Suited#1, CLANKCAT, HI episodes, a Relay/FOMO fill to a recurring wallet landed 1–3 blocks BEFORE the operator buy — not counted under the strict rule.
- Operator ticket size per episode was not systematically extracted.
