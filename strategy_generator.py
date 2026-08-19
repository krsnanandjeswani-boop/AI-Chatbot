import json
from groq import Groq
import os

DEFAULT_UNIVERSE = ["SPY", "QQQ", "IWM", "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM", "XOM"]

_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=_GROQ_API_KEY)


def generate_strategy(symbols=None, question="Design a trading strategy"):
    """Generate a trading strategy.

    symbols: None           -> the LLM intelligently picks a universe (single stock OR
                               a broader basket / sector rotation / broad market strategy)
             str or list    -> strategy applied to the given symbol(s)
    """
    if symbols is None:
        symbol_arg = (
            "You are free to choose the universe. Decide intelligently: design a single-stock "
            "strategy OR a broader basket / sector-rotation / broad-market strategy when that is "
            "the smarter approach. If you choose a basket, pick 3-8 liquid symbols that fit your thesis."
        )
    elif isinstance(symbols, list):
        symbol_arg = f"Apply to this universe: {', '.join(symbols)}"
    else:
        symbol_arg = f"Apply to this single symbol: {symbols}"

    prompt = f"""You are a quantitative research analyst. Generate a trading strategy in JSON format.

{question}
{symbol_arg}

IMPORTANT: You are NOT limited to one stock. Broader portfolio/basket strategies (sector rotation,
momentum basket, ETF timing, broad market regime filter, pairs, etc.) are encouraged when they make
more sense than a single ticker.

Output ONLY valid JSON with this structure:
{{
    "name": "Strategy Name",
    "type": "single_stock | basket | broad_market | sector_rotation | pairs",
    "universe": ["SYM1", "SYM2"],
    "entry": ["condition1", "condition2"],
    "exit": ["condition1", "condition2"],
    "position_size": 0.05,
    "max_positions": 20,
    "risk_management": {{
        "stop_loss": 0.05,
        "take_profit": 0.15,
        "trailing_stop": 0.08,
        "notes": "plain english risk rules"
    }},
    "rationale": "2-3 sentences explaining the edge and why it is robust across the universe"
}}

Constraints:
- entry/exit conditions may ONLY use these patterns (integer parameters):
  SMA(n1) > SMA(n2),  SMA(n1) < SMA(n2),  Close > SMA(n),  Close < SMA(n),
  EMA(n1) > EMA(n2),  RSI > x,  RSI < x,  RSI(n) > x,  RSI(n) < x,
  MACD > MACD_signal,  MACD < MACD_signal,
  Close > BB_upper,  Close < BB_lower,
  Volume > Volume_SMA(n)
- Focus on: momentum, mean reversion, trend following, volatility breakout, sector rotation,
  or similar quantifiable factors.
- Be specific about parameters (e.g., "SMA(20) > SMA(50)" not "moving average crossover").
- Include a market-regime filter (RSI/trend/vol) in entry conditions if it improves robustness.

JSON:"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
    except Exception:
        return _default_strategy(symbols)

    try:
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1] if "```" in content else content
            if content.startswith("json"):
                content = content[4:]
        strategy = json.loads(content.strip())
        return _normalize_strategy(strategy, symbols)
    except Exception:
        return _default_strategy(symbols)


def _normalize_strategy(strategy, symbols):
    universe = strategy.get("universe")
    if isinstance(universe, str):
        universe = [universe]
    if not universe:
        if isinstance(symbols, list):
            universe = symbols
        elif isinstance(symbols, str):
            universe = [symbols]
        else:
            universe = DEFAULT_UNIVERSE[:5]
    strategy["universe"] = [str(s).upper() for s in universe]

    strategy.setdefault("name", "Default Strategy")
    strategy.setdefault("entry", [])
    strategy.setdefault("exit", [])
    strategy.setdefault("position_size", 0.05)
    strategy.setdefault("max_positions", 20)
    strategy.setdefault("risk_management", {})
    strategy.setdefault("rationale", "")
    strategy.setdefault("type", "single_stock" if len(strategy["universe"]) == 1 else "basket")

    # Drop conditions the backtester cannot evaluate
    from backtester import SUPPORTED_CONDITION_PATTERNS
    strategy["entry"] = [c for c in strategy["entry"] if _condition_supported(c, SUPPORTED_CONDITION_PATTERNS)]
    strategy["exit"] = [c for c in strategy["exit"] if _condition_supported(c, SUPPORTED_CONDITION_PATTERNS)]

    return strategy


def _condition_supported(cond, patterns):
    import re
    c = str(cond).upper().replace(" ", "")
    for pat in patterns:
        if re.match(pat, c):
            return True
    return False


def _default_strategy(symbols):
    universe = symbols if isinstance(symbols, list) else ([symbols] if isinstance(symbols, str) else DEFAULT_UNIVERSE[:5])
    universe = [s.upper() for s in universe]
    return {
        "name": "Default SMA Crossover",
        "type": "basket" if len(universe) > 1 else "single_stock",
        "universe": universe,
        "entry": ["SMA(20) > SMA(50)", "RSI > 55"],
        "exit": ["SMA(20) < SMA(50)"],
        "position_size": 0.05,
        "max_positions": 20,
        "risk_management": {"stop_loss": 0.08, "take_profit": 0.20},
        "rationale": "Default fallback: trend-following SMA crossover with RSI momentum confirmation."
    }


def critique_strategy(strategy, metrics):
    prompt = f"""You are a quantitative researcher analyzing a strategy's backtest results.

Strategy: {json.dumps(strategy, indent=2)}

Backtest Metrics:
{json.dumps(metrics, indent=2)}

Suggest 3 concrete improvements to increase Sharpe ratio and reduce drawdown. Be specific about
parameter changes or rule additions. If the strategy targets a single symbol, consider whether
broadening it to a basket would improve robustness.

Response:"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception:
        return "Unable to generate critique at this time. The Groq API may be unavailable or the API key may be invalid."

