"""Upstream TOPICS taxonomy, copied verbatim from h100envy/gem-search automation.py.

Kept so the vendored jev.py reference detector stays importable without the
upstream launch/wallet machinery. See PROVENANCE.md.
"""
TOPICS = {
    'agents': r'\b(agent[s]?|agentic|llm|language model|artificial intelligence|агент\w*|нейросет\w*|искусственн\w+ интеллект\w*)\b',
    'robotics': r'\b(robot[s]?|robotics|humanoid|drone[s]?|робот\w*|дрон\w*)\b',
    'privacy': r'\b(privacy|encryption|zero.knowledge|cryptography|приватност\w*|шифрован\w*|криптограф\w*)\b',
    'devtools': r'\b(compiler|debugger|developer tool|database|open.source|компилятор\w*|отладчик\w*|открыт\w+ код\w*)\b',
    'science': r'\b(fusion|quantum|telescope|spacecraft|satellite|квантов\w*|телескоп\w*|спутник\w*)\b',
}
