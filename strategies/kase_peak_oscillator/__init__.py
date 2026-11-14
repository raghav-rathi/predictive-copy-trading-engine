"""Kase Peak Oscillator engine: registration + re-exports."""

from strategies.kase_peak_oscillator import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="Kase Peak Oscillator",
        slug="kase_peak_oscillator",
        description=(
            "Kase Peak Oscillator (Cynthia Kase, 'Trading with the Odds', "
            "1996). KSDI_up(n) = ln(H/min(L,n))/sigma_n, KSDI_dn(n) = "
            "ln(L/max(H,n))/sigma_n, sigma_n = stddev of log returns over "
            "n; PeakOsc = mean over n in {5,...,50} of (KSDI_up - "
            "KSDI_dn); KaseCD = PeakOsc - SMA(PeakOsc, 9); PeakMax = "
            "max(2x rolling-100 stddev of PeakOsc, 90th pct of |PeakOsc| "
            "over rolling 250). Long when KaseCD crosses above 0 while "
            "PeakOsc < PeakMax, short on a cross below 0 while PeakOsc > "
            "-PeakMax; exits on the opposite KCD cross or PeakOut; 2xATR "
            "stop, 3xATR trail, 150-bar max hold."
        ),
        source_name="Kase Peak Oscillator (Cynthia Kase)",
        source_url="https://www.kaseco.com/support/articles/PeakOuts_and_Permissions.pdf",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
