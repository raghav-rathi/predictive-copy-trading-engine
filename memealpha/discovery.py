"""Step 1-2: seed selection and earliest-buyer discovery.

Two read-only discovery paths:

* Solana: the public (undocumented) gmgn.ai API, hit directly at gmgn.ai.
  No referral links, no API key. Endpoints are best-effort and may change;
  every method degrades to an empty list and records ``last_error`` instead
  of raising on transport failures.
* EVM: Etherscan's public ``tokentx`` API for a token contract. This path
  needs an Etherscan API key for reliable use; without one it returns an
  explicit "unavailable" result rather than guessing.

``discover_early_buyers`` is the entry point both paths feed into: given a
token address it returns the earliest distinct buyer wallets, excluding
known program/router addresses.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field


GMGN_BASE = "https://gmgn.ai"
ETHERSCAN_BASE = "https://api.etherscan.io/api"

_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# Well-known on-chain program/router addresses that are never "buyers".
# Kept short on purpose: callers should extend per chain.
PROGRAM_BLOCKLIST = frozenset(
    {
        # Solana DEX routers / programs (base58)
        "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",  # Jupiter v6
        "JUP4Fb2cqiRUcaTHdrPC8h2MVXAz6zM9tWJqA2SEYY",  # Jupiter v4
        "675kPX9MHTjS2zt1bmTLUexhuz8YJ4WJ8kH5wL1V",    # Raydium v4 (example)
    }
)


@dataclass
class EarlyBuyer:
    """One distinct early buyer of the seed token."""

    address: str
    first_buy_ts: float
    first_buy_usd: float = 0.0
    tx_signature: str = ""


@dataclass
class FetchResult:
    ok: bool
    payload: object = None
    error: str = ""


def _get_json(url: str, timeout: float = 20.0) -> FetchResult:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return FetchResult(ok=True, payload=json.loads(resp.read().decode()))
    except Exception as exc:  # noqa: BLE001 - best-effort public API
        return FetchResult(ok=False, error=f"{type(exc).__name__}: {exc}"[:300])


class GmgnClient:
    """Read-only client for gmgn.ai's public token/wallet endpoints.

    Chain slug follows gmgn.ai's own convention: ``sol``, ``eth``, ``bsc``,
    ``base``, ``arb``, ``blast``, ``tron`` ...
    """

    def __init__(self, chain: str = "sol", timeout: float = 20.0) -> None:
        self.chain = chain
        self.timeout = timeout
        self.last_error: str = ""

    def _get(self, path: str, params: dict | None = None) -> FetchResult:
        url = f"{GMGN_BASE}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        res = _get_json(url, timeout=self.timeout)
        if not res.ok:
            self.last_error = res.error
        return res

    def token_traders(self, mint: str, limit: int = 100) -> list[dict]:
        """Top traders of a token (GMGN "Top Traders" tab data)."""
        res = self._get(
            f"/api/v1/token_traders/{self.chain}/{mint}",
            {"limit": limit},
        )
        if not res.ok:
            return []
        data = res.payload if isinstance(res.payload, dict) else {}
        return data.get("data", {}).get("rank", []) or []

    def token_holders(self, mint: str, limit: int = 100) -> list[dict]:
        res = self._get(
            f"/api/v1/token_holders/{self.chain}/{mint}",
            {"limit": limit},
        )
        if not res.ok:
            return []
        data = res.payload if isinstance(res.payload, dict) else {}
        return data.get("data", {}).get("holders", []) or []

    def wallet_tokens(self, wallet: str) -> list[dict]:
        """Tokens currently held by a wallet (for the holdings scan)."""
        res = self._get(f"/api/v1/address_tokens/{self.chain}/{wallet}")
        if not res.ok:
            return []
        data = res.payload if isinstance(res.payload, dict) else {}
        return data.get("data", {}).get("tokens", []) or []

    def wallet_recent_trades(self, wallet: str, limit: int = 50) -> list[dict]:
        """Recent trades of a wallet (for the 30-day activity filter)."""
        res = self._get(
            f"/api/v1/address_trades/{self.chain}/{wallet}",
            {"limit": limit},
        )
        if not res.ok:
            return []
        data = res.payload if isinstance(res.payload, dict) else {}
        return data.get("data", {}).get("history", []) or []


class EtherscanClient:
    """Read-only Etherscan client for the EVM earliest-buyer path."""

    def __init__(self, api_key: str = "", timeout: float = 20.0) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.last_error: str = ""

    def token_transfers(
        self, contract: str, start_block: int = 0, end_block: int = 99999999
    ) -> list[dict]:
        """All ERC-20 transfers of a contract, oldest first."""
        if not self.api_key:
            self.last_error = "no Etherscan API key configured"
            return []
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": contract,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
            "apikey": self.api_key,
        }
        url = ETHERSCAN_BASE + "?" + urllib.parse.urlencode(params)
        res = _get_json(url, timeout=self.timeout)
        if not res.ok:
            self.last_error = res.error
            return []
        data = res.payload if isinstance(res.payload, dict) else {}
        if data.get("status") != "1":
            self.last_error = str(data.get("message", "etherscan error"))[:200]
            return []
        return data.get("result", []) or []


def _norm_ts(value: object) -> float:
    """Normalize GMGN/Etherscan timestamps (s, ms or us; str or int) to seconds."""
    try:
        ts = float(value)
    except (TypeError, ValueError):
        return 0.0
    if ts > 1e14:  # microseconds (~16 digits for current dates)
        ts /= 1e6
    elif ts > 1e11:  # milliseconds (~13 digits for current dates)
        ts /= 1e3
    return ts


def earliest_buyers_from_traders(
    traders: list[dict], n: int = 20, now: float | None = None
) -> list[EarlyBuyer]:
    """Pick the n earliest distinct buyer wallets from GMGN trader rows.

    GMGN trader rows carry the wallet's first-buy info; rows that resolve
    to a program/router address are skipped.
    """
    now = now or time.time()
    seen: dict[str, EarlyBuyer] = {}
    for row in traders:
        addr = str(row.get("address") or row.get("maker") or "")
        if not addr or addr in PROGRAM_BLOCKLIST:
            continue
        first_ts = _norm_ts(
            row.get("first_buy_time") or row.get("first_trade_time") or 0
        )
        if first_ts <= 0 or first_ts > now:
            continue
        if addr not in seen:
            usd = 0.0
            try:
                usd = float(row.get("first_buy_usd") or row.get("buy_usd") or 0)
            except (TypeError, ValueError):
                usd = 0.0
            seen[addr] = EarlyBuyer(
                address=addr,
                first_buy_ts=first_ts,
                first_buy_usd=usd,
                tx_signature=str(row.get("first_tx") or ""),
            )
    ordered = sorted(seen.values(), key=lambda b: b.first_buy_ts)
    return ordered[:n]


def earliest_buyers_from_transfers(
    transfers: list[dict], n: int = 20, contract: str = ""
) -> list[EarlyBuyer]:
    """Pick the n earliest distinct buyers from Etherscan tokentx rows.

    Transfers are expected oldest-first (``sort=asc``). Mint/burn legs
    (from the zero address) are skipped.
    """
    seen: dict[str, EarlyBuyer] = {}
    zero = "0x0000000000000000000000000000000000000000"
    for tx in transfers:
        to_addr = str(tx.get("to", ""))
        from_addr = str(tx.get("from", ""))
        if not to_addr or to_addr.lower() == zero:
            continue
        if from_addr.lower() == zero:
            continue  # mint, not a buy
        if to_addr in seen or to_addr in PROGRAM_BLOCKLIST:
            continue
        ts = _norm_ts(tx.get("timeStamp"))
        if ts <= 0:
            continue
        seen[to_addr] = EarlyBuyer(
            address=to_addr,
            first_buy_ts=ts,
            tx_signature=str(tx.get("hash", "")),
        )
        if len(seen) >= n:
            break
    return list(seen.values())[:n]


def discover_early_buyers(
    token_address: str,
    chain: str = "sol",
    n: int = 20,
    gmgn: GmgnClient | None = None,
    etherscan: EtherscanClient | None = None,
) -> list[EarlyBuyer]:
    """Discovery entry point: earliest ``n`` buyer wallets of a token.

    Solana (and other GMGN-supported chains) go through GMGN; pure-EVM
    contracts can use the Etherscan path when a key is configured.
    """
    if chain == "eth" and etherscan is not None:
        transfers = etherscan.token_transfers(token_address)
        if transfers:
            return earliest_buyers_from_transfers(transfers, n=n)
    client = gmgn or GmgnClient(chain=chain)
    traders = client.token_traders(token_address, limit=max(n * 5, 100))
    return earliest_buyers_from_traders(traders, n=n)
