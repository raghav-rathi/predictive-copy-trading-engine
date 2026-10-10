"""Step 7: the 9-point scoring rubric.

Each candidate token is graded on nine binary criteria (1 point each).
Anything scoring below 9 is rejected — in this port the bar is a perfect
card, exactly as the method describes it. The threshold is configurable
via ``PASS_THRESHOLD`` for experimentation, but the default is 9.

Criterion weights are all 1.0 by design: the rubric is a checklist, not a
weighted model. Each criterion documents what "passing" means and what
feature key it reads.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Feature keys expected in the ``features`` dict passed to score_token().
CRITERIA: tuple[tuple[str, str, str], ...] = (
    (
        "early_buyer_hold",
        "Early-buyer provenance",
        "At least one tracked early-buyer wallet still holds the token.",
    ),
    (
        "wallet_convergence",
        "Wallet convergence",
        "Bought/held by >= 3 tracked wallets at once (the 3-wallet rule).",
    ),
    (
        "recent_activity",
        "Recent wallet activity",
        "The converging wallets traded within the last 30 days.",
    ),
    (
        "human_flow",
        "Human-like flow",
        "No converging wallet shows a bot timing signature.",
    ),
    (
        "liquidity_ok",
        "Liquidity floor",
        "Pool liquidity above the configured minimum (else uncopyable).",
    ),
    (
        "holder_distribution_ok",
        "Holder distribution",
        "Top-10 holders own less than the concentration cap.",
    ),
    (
        "contract_safe",
        "Contract safety",
        "No honeypot flags; mint/freeze authority renounced or locked.",
    ),
    (
        "buy_pressure_ok",
        "Buy pressure",
        "More buys than sells over the last 24h (buyers in control).",
    ),
    (
        "volume_alive",
        "Volume alive",
        "24h volume above the dust floor (not a dead chart).",
    ),
)

PASS_THRESHOLD = 9


@dataclass
class Score:
    token: str
    total: int
    breakdown: dict[str, int] = field(default_factory=dict)
    passes: bool = False

    def missing(self) -> list[str]:
        """Criterion keys that failed."""
        return [key for key, pts in self.breakdown.items() if not pts]


def score_token(
    token: str,
    features: dict[str, bool],
    threshold: int = PASS_THRESHOLD,
) -> Score:
    """Grade a candidate token against the 9-point rubric.

    ``features`` maps each criterion key in CRITERIA to True/False.
    Missing keys count as failures — no silent passes.
    """
    breakdown = {key: 1 if features.get(key) is True else 0 for key, _, _ in CRITERIA}
    total = sum(breakdown.values())
    return Score(token=token, total=total, breakdown=breakdown, passes=total >= threshold)


def rubric_table() -> str:
    """Human-readable rubric for docs/notes."""
    lines = ["# | Criterion | What passes", "-- | --------- | -----------"]
    for i, (_, name, desc) in enumerate(CRITERIA, 1):
        lines.append(f"{i} | {name} | {desc}")
    lines.append(f"\nPass bar: {PASS_THRESHOLD}/9. Below that: rejected.")
    return "\n".join(lines)
