"""Live-order entry point. Raises NotImplementedError BY DESIGN.

This repo has no live trading - the same stance as the hyperliquid/ and
slime/ modules (paper mode only). The six-bot desk emits alerts (gate.py);
fills are simulated by the paper backtest. If you are looking for where
orders would go: here, and it refuses.
"""


def place_order(*args, **kwargs):
    raise NotImplementedError(
        "live trading is disabled by design - this desk is paper mode only; "
        "alerts are emitted by gate.py and fills simulated in backtest.py"
    )
