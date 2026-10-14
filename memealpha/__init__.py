"""Meme-alpha wallet discovery.

A research port of the "meme alpha wallet discovery" method published by
@crbpite8 on X (Oct 9, 2026,
https://x.com/crbpite8/status/2108668827412341014).

The idea in one paragraph: seed on a meme coin that was hot in a previous
cycle, find its earliest buyers, keep only the wallets still trading, throw
out bots, look at what those wallets bought and still hold recently, and
treat tokens held by 3+ of them as signal. A 9-point rubric gates what is
worth watching.

Everything here is read-only discovery and scoring. There is no trading
execution wiring anywhere in this package. Research use only.
"""

from .discovery import GmgnClient, EtherscanClient, EarlyBuyer, discover_early_buyers
from .filters import filter_active, bot_verdict, filter_bots, trade_intervals
from .convergence import find_convergence, Convergence
from .scoring import score_token, Score, CRITERIA, PASS_THRESHOLD
from .pipeline import run_pipeline, PipelineResult

__all__ = [
    "GmgnClient",
    "EtherscanClient",
    "EarlyBuyer",
    "discover_early_buyers",
    "filter_active",
    "bot_verdict",
    "filter_bots",
    "trade_intervals",
    "find_convergence",
    "Convergence",
    "score_token",
    "Score",
    "CRITERIA",
    "PASS_THRESHOLD",
    "run_pipeline",
    "PipelineResult",
]
