"""gemsearch — crypto-adapted port of the GemSearch JEV narrative detector.

Provenance: core detection logic is ported from h100envy/gem-search (MIT),
see vendor/PROVENANCE.md. This package adapts the spider/JEV pipeline to
crypto social chatter: narrative clustering + $ticker extraction + the same
four-seat local verification structure (lookout / maker / skeptic / runner).

Paper/research only. A shortlist is a research lead, not a trading signal.
"""

__version__ = "0.1.0"
__upstream__ = "https://github.com/h100envy/gem-search"
