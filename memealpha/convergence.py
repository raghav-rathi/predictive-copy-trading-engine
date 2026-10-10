"""Step 5-6: holdings scan and convergence signal.

Step 5: for each surviving wallet, collect what it bought and still holds
inside the recent window.

Step 6: the convergence rule — one wallet buying something is luck, three
wallets buying the same token at once is signal. This module finds every
token held/bought by at least ``min_wallets`` tracked wallets.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Convergence:
    """One token with multi-wallet overlap."""

    token: str
    wallets: list[str] = field(default_factory=list)
    symbol: str = ""
    coverage: float = 0.0  # share of the tracked wallet set (filled by finder)

    @property
    def wallet_count(self) -> int:
        return len(self.wallets)


def find_convergence(
    holdings_by_wallet: dict[str, set[str]],
    min_wallets: int = 3,
    symbols: dict[str, str] | None = None,
) -> list[Convergence]:
    """Return tokens held by >= ``min_wallets`` tracked wallets.

    ``holdings_by_wallet`` maps wallet address -> set of token identifiers
    (mint address or symbol; be consistent). Results are sorted by wallet
    count descending, then token identifier for determinism.
    """
    symbols = symbols or {}
    token_to_wallets: dict[str, list[str]] = {}
    for wallet, tokens in holdings_by_wallet.items():
        for token in tokens:
            token_to_wallets.setdefault(token, []).append(wallet)

    out: list[Convergence] = []
    n_wallets = len(holdings_by_wallet)
    for token, wallets in token_to_wallets.items():
        if len(wallets) >= min_wallets:
            out.append(
                Convergence(
                    token=token,
                    wallets=sorted(wallets),
                    symbol=symbols.get(token, ""),
                    coverage=len(wallets) / n_wallets if n_wallets else 0.0,
                )
            )
    out.sort(key=lambda c: (-c.wallet_count, c.token))
    return out


def convergence_coverage(conv: Convergence) -> float:
    """Share of tracked wallets behind a convergence (0..1)."""
    return float(conv.coverage)
