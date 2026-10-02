#!/usr/bin/env python3
"""FOMO-deposit watcher (Solana leg of the predictive-copy signal).

The edge exploited by the original operator (see docs/research/) is timing:
a FOMO buy starts life as a deposit on Solana, then crosses a relay/solver
pipeline before the fill lands on Robinhood Chain. Measured deposit->fill
latency was ~0.5-1.6s, i.e. 5-16 Robinhood blocks (~100ms each) of advance
warning about *who* is about to buy -- never *what*. This watcher is the
sensor for that window: it tails Solana logs for the FOMO deposit program
and emits one newline-delimited JSON trigger per observed deposit:

    {"whale": "0x<robinhood-chain wallet>", "sol_timestamp": 1727...,
     "deposit_tx": "<solana signature>", "slot": 123456789}

The Robinhood Chain wallet address is the interesting field. The mapping
from a Solana deposit to the destination wallet lives in the FOMO app's
relay path and is NOT yet pinned down on-chain; see the TODO in
`map_deposit_to_whale`. Until that mapping is verified, this watcher runs
in log-only mode: it records every candidate deposit event so the mapping
can be reverse-engineered offline against observed fills.

Stdout is the event bus: the engine consumes NDJSON from stdin, so run as

    solana_watcher.py | engine.py --triggers -

Stdlib only. Websocket client is a minimal RFC6455 implementation, enough
for logsSubscribe notifications; no external deps to audit.

Exit codes: 0 clean shutdown (SIGINT), 2 config error, 3 transport exhausted.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import signal
import socket
import ssl
import struct
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Minimal websocket client (client->server frames masked, text frames only)
# ---------------------------------------------------------------------------


class WSClosed(Exception):
    pass


class WebSocket:
    """Just enough websocket to subscribe and read JSON text frames."""

    def __init__(self, url: str, timeout: float = 30.0):
        u = urllib.parse.urlparse(url)
        if u.scheme not in ("ws", "wss"):
            raise ValueError(f"unsupported scheme: {u.scheme}")
        self.host = u.hostname
        self.port = u.port or (443 if u.scheme == "wss" else 80)
        path = u.path or "/"
        if u.query:
            path += "?" + u.query
        raw = socket.create_connection((self.host, self.port), timeout=timeout)
        if u.scheme == "wss":
            ctx = ssl.create_default_context()
            raw = ctx.wrap_socket(raw, server_hostname=self.host)
        raw.settimeout(timeout)
        self.sock = raw
        key = base64.b64encode(secrets.token_bytes(16)).decode()
        req = (
            f"GET {path} HTTP/1.1\r\nHost: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise WSClosed("handshake EOF")
            resp += chunk
        if b" 101 " not in resp.split(b"\r\n", 1)[0]:
            raise WSClosed(f"handshake rejected: {resp[:200]!r}")
        self._buf = resp.split(b"\r\n\r\n", 1)[1]

    def _read_exact(self, n: int) -> bytes:
        while len(self._buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise WSClosed("EOF")
            self._buf += chunk
        out, self._buf = self._buf[:n], self._buf[n:]
        return out

    def send_text(self, text: str) -> None:
        payload = text.encode()
        mask = secrets.token_bytes(4)
        header = bytearray([0x81])
        n = len(payload)
        if n < 126:
            header.append(0x80 | n)
        elif n < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", n)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", n)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + mask + masked)

    def recv_text(self) -> str:
        """Return next complete text message; auto-replies to pings."""
        frags: list[bytes] = []
        while True:
            b0, b1 = self._read_exact(2)
            fin, opcode = b0 & 0x80, b0 & 0x0F
            ln = b1 & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", self._read_exact(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", self._read_exact(8))[0]
            if b1 & 0x80:
                self._read_exact(4)  # server frames are unmasked; skip if set
            payload = self._read_exact(ln) if ln else b""
            if opcode == 0x8:
                raise WSClosed("close frame")
            if opcode == 0x9:  # ping -> pong
                self._send_control(0xA, payload)
                continue
            if opcode in (0x1, 0x0):
                frags.append(payload)
                if fin:
                    return b"".join(frags).decode("utf-8", "replace")

    def _send_control(self, opcode: int, payload: bytes) -> None:
        mask = secrets.token_bytes(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes([0x80 | opcode, 0x80 | len(payload)]) + mask + masked)

    def close(self) -> None:
        try:
            self._send_control(0x8, b"")
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Watcher
# ---------------------------------------------------------------------------


def load_config(path: str | None) -> dict:
    cfg: dict = {}
    if path:
        with open(path) as f:
            cfg = json.load(f)
    # env overrides for the bits that change per environment
    cfg.setdefault("solana", {})
    if os.environ.get("SOLANA_WS_URL"):
        cfg["solana"]["ws_url"] = os.environ["SOLANA_WS_URL"]
    return cfg


def map_deposit_to_whale(logs: list[str], signature: str, cfg: dict) -> str | None:
    """Map one FOMO Solana deposit to the Robinhood Chain wallet it funds.

    TODO(verify-on-chain): the exact instruction/account layout of the FOMO
    deposit path is not yet reversed. What is known from the operator
    research: fills on Robinhood Chain are delivered by Relay
    (RelayRouterV3 -> end wallet), and the end wallets are EIP-7702 user
    accounts. Likely sources for the mapping, in order:
      1. the destination EVM address embedded in the deposit instruction
         data / an associated memo account -- parse once the program ID and
         instruction discriminator are confirmed from real deposit txs;
      2. a lookup keyed by the Solana depositor, if FOMO keeps a stable
         Solana->EVM account link per user (check against observed fills:
         candidate wallets in data/whales_seed.json).
    Until one of these is verified, returns None and the caller emits the
    raw event with whale=null for offline correlation. Guessing here would
    feed the engine phantom triggers, so this deliberately fails closed.
    """
    return None


def looks_like_deposit(logs: list[str], cfg: dict) -> bool:
    """Cheap pre-filter on log lines before paying for a tx fetch.

    TODO(verify): log substrings for the FOMO deposit program are a guess
    at the Anchor event names; confirm against a known deposit signature
    and tighten. False positives are harmless (mapped whale will be null);
    false negatives are not, so this stays permissive for now.
    """
    needles = cfg.get("solana", {}).get("log_needles", ["Deposit", "deposit"])
    text = "\n".join(logs)
    return any(n in text for n in needles)


def emit(event: dict) -> None:
    sys.stdout.write(json.dumps(event) + "\n")
    sys.stdout.flush()


def run(cfg: dict) -> int:
    sol = cfg.get("solana", {})
    ws_url = sol.get("ws_url", "wss://api.mainnet-beta.solana.com")
    program_ids = sol.get("fomo_program_ids", [])
    if not program_ids:
        print(
            "config error: solana.fomo_program_ids is empty. The FOMO "
            "deposit program ID must be verified from a real deposit tx "
            "before subscribing (see map_deposit_to_whale).",
            file=sys.stderr,
        )
        return 2

    attempt = 0
    while True:
        try:
            ws = WebSocket(ws_url)
            attempt = 0
            sub_ids: dict[int, str] = {}
            for i, pid in enumerate(program_ids):
                rid = 100 + i
                ws.send_text(json.dumps({
                    "jsonrpc": "2.0", "id": rid, "method": "logsSubscribe",
                    "params": [{"mentions": [pid]},
                               {"commitment": "confirmed"}],
                }))
                sub_ids[rid] = pid
            print(f"subscribed to {len(program_ids)} program(s) via {ws_url}",
                  file=sys.stderr)
            seen_sigs: set[str] = set()
            while True:
                msg = json.loads(ws.recv_text())
                if "id" in msg:  # subscribe acks / errors
                    if msg.get("error"):
                        print(f"subscribe error: {msg['error']}", file=sys.stderr)
                    continue
                params = msg.get("params") or {}
                value = (params.get("result") or {}).get("value") or {}
                sig = value.get("signature")
                if not sig or sig in seen_sigs:
                    continue
                seen_sigs.add(sig)
                if len(seen_sigs) > 10000:  # bound memory; dupes past this are harmless
                    seen_sigs.clear()
                logs = value.get("logs") or []
                if value.get("err") is not None:
                    continue
                if not looks_like_deposit(logs, cfg):
                    continue
                whale = map_deposit_to_whale(logs, sig, cfg)
                emit({
                    "type": "fomo_deposit",
                    "whale": whale,  # null until mapping verified (fails closed)
                    "sol_timestamp": int(time.time()),
                    "sol_time_iso": datetime.now(timezone.utc).isoformat(),
                    "deposit_tx": sig,
                    "slot": value.get("slot"),
                })
        except (WSClosed, OSError, ValueError) as e:
            attempt += 1
            backoff = min(2 ** attempt, 60)
            print(f"solana ws dropped ({e}); reconnect in {backoff}s "
                  f"(attempt {attempt})", file=sys.stderr)
            try:
                ws.close()
            except Exception:
                pass
            if attempt > 10:
                print("transport exhausted", file=sys.stderr)
                return 3
            time.sleep(backoff)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=None,
                    help="config json (default: built-ins + env)")
    args = ap.parse_args()
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    return run(load_config(args.config))


if __name__ == "__main__":
    sys.exit(main())
