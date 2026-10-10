"""End-to-end orchestration of the 7-step wallet-discovery pipeline.

Steps:
  1. Seed: a meme coin that was hot in a previous cycle (caller-provided).
  2. Discovery: earliest 20 buyer wallets (GMGN for Solana / GMGN chains,
     Etherscan for EVM).
  3. Activity filter: keep wallets trading in the last 30 days.
  4. Bot filter: drop second-spaced (bot-signature) wallets.
  5. Holdings scan: what survivors bought and still hold in the last 30d.
  6. Convergence: tokens held by 3+ tracked wallets.
  7. Scoring: 9-point rubric; reject below 9.

Network access is injected via small callables so the pipeline itself is
pure and unit-testable. There is no execution/trading code here — the
output is a scored watchlist, nothing more.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from .convergence import Convergence, find_convergence
from .discovery import (
    EarlyBuyer,
    EtherscanClient,
    GmgnClient,
    discover_early_buyers,
)
from .filters import filter_active, filter_bots
from .scoring import Score, score_token


@dataclass
class PipelineResult:
    seed_token: str
    chain: str
    early_buyers: list[EarlyBuyer] = field(default_factory=list)
    active_wallets: list[str] = field(default_factory=list)
    dropped_inactive: list[str] = field(default_factory=list)
    bot_wallets: list[str] = field(default_factory=list)
    human_wallets: list[str] = field(default_factory=list)
    convergences: list[Convergence] = field(default_factory=list)
    scores: list[Score] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def watchlist(self) -> list[Score]:
        """Candidates that cleared the 9-point bar."""
        return [s for s in self.scores if s.passes]


def run_pipeline(
    seed_token: str,
    chain: str = "sol",
    n_early: int = 20,
    activity_days: int = 30,
    min_convergence: int = 3,
    # Injected data providers (defaults hit the live read-only clients).
    fetch_early_buyers: Callable[[], list[EarlyBuyer]] | None = None,
    fetch_last_trade: Callable[[list[str]], dict[str, float]] | None = None,
    fetch_trade_counts: Callable[[list[str]], dict[str, int]] | None = None,
    fetch_trade_times: Callable[[list[str]], dict[str, list[float]]] | None = None,
    fetch_holdings: Callable[[list[str]], dict[str, set[str]]] | None = None,
    fetch_features: Callable[[str], dict[str, bool]] | None = None,
    gmgn: GmgnClient | None = None,
    etherscan: EtherscanClient | None = None,
    now: float | None = None,
) -> PipelineResult:
    """Run the full discovery pipeline for one seed token."""
    now = now if now is not None else time.time()
    res = PipelineResult(seed_token=seed_token, chain=chain)
    client = gmgn or GmgnClient(chain=chain)

    # Step 2: discovery.
    if fetch_early_buyers is not None:
        buyers = fetch_early_buyers()
    else:
        buyers = discover_early_buyers(
            seed_token, chain=chain, n=n_early, gmgn=client, etherscan=etherscan
        )
    res.early_buyers = buyers
    if not buyers:
        res.notes.append("no early buyers discovered (API blocked or no data)")
        return res
    wallets = [b.address for b in buyers]

    # Step 3: activity filter.
    if fetch_last_trade is not None:
        last_trade = fetch_last_trade(wallets)
        counts = fetch_trade_counts(wallets) if fetch_trade_counts else {}
    else:
        last_trade, counts = {}, {}
        for w in wallets:
            trades = client.wallet_recent_trades(w, limit=50)
            ts = [
                float(t.get("time") or t.get("timestamp") or 0)
                for t in trades
                if t.get("time") or t.get("timestamp")
            ]
            # normalize ms -> s
            ts = [t / 1000.0 if t > 1e12 else t for t in ts]
            last_trade[w] = max(ts) if ts else 0.0
            counts[w] = len(ts)
    kept, dropped = filter_active(last_trade, counts, days=activity_days, now=now)
    res.active_wallets = [v.address for v in kept]
    res.dropped_inactive = [v.address for v in dropped]
    if not res.active_wallets:
        res.notes.append("no wallets active in window; pipeline stops here")
        return res

    # Step 4: bot filter.
    if fetch_trade_times is not None:
        trade_times = fetch_trade_times(res.active_wallets)
    else:
        trade_times = {}
        for w in res.active_wallets:
            trades = client.wallet_recent_trades(w, limit=50)
            ts = [
                float(t.get("time") or t.get("timestamp") or 0) for t in trades
            ]
            trade_times[w] = [t / 1000.0 if t > 1e12 else t for t in ts if t]
    humans, bots = filter_bots(trade_times)
    res.human_wallets = [v.address for v in humans]
    res.bot_wallets = [v.address for v in bots]
    if not res.human_wallets:
        res.notes.append("all active wallets flagged as bots; pipeline stops here")
        return res

    # Step 5: holdings scan.
    if fetch_holdings is not None:
        holdings = fetch_holdings(res.human_wallets)
    else:
        holdings = {}
        for w in res.human_wallets:
            tokens = client.wallet_tokens(w)
            holdings[w] = {
                str(t.get("address") or t.get("mint") or t.get("symbol") or "")
                for t in tokens
            } - {""}

    # Step 6: convergence.
    res.convergences = find_convergence(holdings, min_wallets=min_convergence)
    if not res.convergences:
        res.notes.append(
            f"no token held by >={min_convergence} wallets; no candidates"
        )
        return res

    # Step 7: scoring.
    for conv in res.convergences:
        feats = fetch_features(conv.token) if fetch_features else {}
        # Steps 2-6 already prove three of the nine criteria.
        feats = {
            "early_buyer_hold": True,
            "wallet_convergence": True,
            "recent_activity": True,
            "human_flow": True,
            **feats,
        }
        res.scores.append(score_token(conv.token, feats))

    res.notes.append(
        f"{len(res.watchlist)} of {len(res.scores)} candidates cleared the bar"
    )
    return res
