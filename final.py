import os
import warnings
import requests
import yfinance as yf
from groq import Groq
from datetime import datetime, timedelta
from functools import wraps
import threading
import time

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

client = Groq(api_key=GROQ_API_KEY)

_cache = {}

def cached(ttl_seconds=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            now = time.time()
            if key in _cache and now - _cache[key]["timestamp"] < ttl_seconds:
                return _cache[key]["data"]
            result = func(*args, **kwargs)
            _cache[key] = {"data": result, "timestamp": now}
            return result
        return wrapper
    return decorator

def get_stock_quote(symbol):
    url = (
        f"https://finnhub.io/api/v1/quote"
        f"?symbol={symbol}"
        f"&token={FINNHUB_API_KEY}"
    )
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None

def get_company_news(symbol):
    url = (
        f"https://finnhub.io/api/v1/company-news"
        f"?symbol={symbol}"
        f"&from=2024-01-01"
        f"&to=2024-12-31"
        f"&token={FINNHUB_API_KEY}"
    )
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []
        return response.json()[:5]
    except Exception:
        return []

def get_company_overview(symbol):
    url = (
        "https://www.alphavantage.co/query"
        "?function=OVERVIEW"
        f"&symbol={symbol}"
        f"&apikey={ALPHA_VANTAGE_API_KEY}"
    )
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None

def get_price_history(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        return hist.tail(30).to_string()
    except Exception:
        return None

SEC_HEADERS = {
    "User-Agent": "Krish Research Bot krishpyjeswani@gmail.com"
}

def get_sec_filings(cik):
    cik = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    try:
        response = requests.get(url, headers=SEC_HEADERS)
        if response.status_code != 200:
            return None
        data = response.json()
        recent = data["filings"]["recent"]
        results = []
        for i in range(min(10, len(recent["form"]))):
            results.append({
                "form": recent["form"][i],
                "date": recent["filingDate"][i]
            })
        return results
    except Exception:
        return None

def build_minimal_context(symbol):
    quote = get_stock_quote(symbol)
    overview = get_company_overview(symbol)
    history = get_price_history(symbol)
    
    if quote is None or overview is None:
        return ""
    
    price = quote.get('c', 'N/A')
    change = quote.get('d', 'N/A')
    sector = overview.get('Sector', 'N/A')
    pe = overview.get('PERatio', 'N/A')
    name = overview.get('Name', symbol)
    
    return f"Real-time data for {symbol}: Price=${price}, Change={change}, Sector={sector}, P/E={pe}, Company={name}"

def build_full_context(symbol):
    quote = get_stock_quote(symbol)
    overview = get_company_overview(symbol)
    
    if quote is None or overview is None:
        return f"Stock {symbol}: Unable to fetch current data."
    
    quant = calculate_quant_metrics(symbol) or {}
    factor = get_factor_exposure(symbol) or {}
    
    cik = overview.get("CIK", "") if overview else ""
    sec_10k = get_sec_10k(cik) if cik else []
    sec_10q = get_sec_10q(cik) if cik else []
    
    context = f"""Stock: {symbol}
Price: ${quote.get('c', 'N/A')} (Change: {quote.get('d', 'N/A')})
Sector: {overview.get('Sector', 'N/A')}
P/E: {overview.get('PERatio', 'N/A')}
Company: {overview.get('Name', symbol)}
Quant Metrics (1Y): Sharpe={quant.get('sharpe_ratio', 'N/A')}, Sortino={quant.get('sortino_ratio', 'N/A')}, Max Drawdown={quant.get('max_drawdown', 'N/A')}
Beta: {factor.get('market_beta', 'N/A')}
10-K Filings: {len(sec_10k)} available
10-Q Filings: {len(sec_10q)} available
"""
    return context.replace("\n", " ").strip()

def detect_ticker(text):
    common_words = {'WHAT', 'THE', 'FOR', 'ARE', 'AND', 'BUT', 'NOT', 'YOU', 'WAS', 'WITH', 'HAVE', 'THIS', 'FROM', 'OR', 'AN', 'AT', 'BE', 'TO', 'IN', 'IT', 'IS', 'OF', 'ON', 'THAT', 'BY', 'AS', 'IF', 'ME', 'ABOUT', 'PLEASE', 'CAN', 'WANT', 'HOW', 'WHY', 'DO', 'SOME', 'ANY', 'SHOW', 'GIVE', 'FIND', 'GET', 'LOOK', 'CHECK', 'RUN', 'LAST', 'DATA', 'HISTORY', 'NEWS', 'REPORT', 'NOW', 'TODAY', 'TOMORROW', 'BUY', 'SELL', 'HOLD', 'RISK', 'ANALYSIS', 'HELP', 'EV', 'VALUE', 'CALCULATE', 'COMPUTE', 'DERIVATIVE', 'DER', 'CHAIN', 'CALL', 'TRANSACTIONS', 'INSIDER', 'OWNERSHIP', 'INSTITUTIONAL', 'VALUATION', 'FACTOR', 'EXPOSURE', 'QUANT', 'METRICS', 'SHARPE', 'SORTINO', 'MAX', 'DRAWDOWN', 'ANNUALIZED', 'VOLATILITY', 'MARKET', 'BETA', 'SYMBOL', 'COMPANY', 'QUARTER', 'FILINGS', 'SEC', 'HELLO', 'WORLD', 'GOOD', 'BAD', 'THANKS', 'THANK', 'NICE', 'COOL', 'WOW', 'TELL', 'STOCK', 'PRICE', 'INFO', 'EARNINGS', 'OPTIONS', 'DCF', 'NEWS', 'REAL', 'TIME', 'TIME'}
    
    words = text.split()
    for word in words:
        clean = word.upper().replace(".", "").replace(",", "").replace("?", "").replace("!", "").replace("$", "")
        if len(clean) <= 5 and clean.isalpha() and clean not in common_words:
            quote = get_stock_quote(clean)
            if quote and quote.get('c', 0) and quote.get('c', 0) > 0:
                return clean
    return None

def get_sec_10k(cik, limit=5):
    cik = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    try:
        response = requests.get(url, headers=SEC_HEADERS)
        if response.status_code != 200:
            return None
        data = response.json()
        filings = data.get("filings", {}).get("recent", {})
        ten_k_filings = []
        for i, form in enumerate(filings.get("form", [])):
            if form == "10-K":
                accession = filings.get("accessionNumber", [])[i]
                accession_nodash = accession.replace("-", "")
                ten_k_filings.append({
                    "date": filings.get("filingDate", [])[i],
                    "accession": accession,
                    "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{accession}-index.html"
                })
                if len(ten_k_filings) >= limit:
                    break
        return ten_k_filings
    except Exception:
        return None

def get_sec_10q(cik, limit=5):
    cik = str(cik).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    try:
        response = requests.get(url, headers=SEC_HEADERS)
        if response.status_code != 200:
            return None
        data = response.json()
        filings = data.get("filings", {}).get("recent", {})
        ten_q_filings = []
        for i, form in enumerate(filings.get("form", [])):
            if form == "10-Q":
                accession = filings.get("accessionNumber", [])[i]
                accession_nodash = accession.replace("-", "")
                ten_q_filings.append({
                    "date": filings.get("filingDate", [])[i],
                    "accession": accession,
                    "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{accession}-index.html"
                })
                if len(ten_q_filings) >= limit:
                    break
        return ten_q_filings
    except Exception:
        return None

@cached(ttl_seconds=300)
def get_news_headlines(query, limit=10):
    from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={query}"
        f"&apiKey={NEWS_API_KEY}"
        f"&from={from_date}"
        f"&to={to_date}"
        f"&sortBy=publishedAt"
        f"&pageSize={limit}"
    )
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []
        articles = response.json().get("articles", [])
        return [
            {"title": a.get("title", ""), "source": a.get("source", {}).get("name", ""), "publishedAt": a.get("publishedAt", "")}
            for a in articles[:limit]
        ]
    except Exception:
        return []

@cached(ttl_seconds=300)
def get_company_profile(symbol):
    overview = get_company_overview(symbol)
    if not overview:
        return None
    return {
        "name": overview.get("Name", symbol),
        "sector": overview.get("Sector", "N/A"),
        "industry": overview.get("Industry", "N/A"),
        "description": overview.get("Description", "N/A"),
        "ceo": overview.get("CEO", "N/A"),
        "market_cap": overview.get("MarketCapitalization", "N/A"),
        "revenue": overview.get("Revenue", "N/A"),
        "competitors": overview.get("Competitors", "N/A"),
        "products": overview.get("Products", "N/A"),
        "cik": overview.get("CIK", "")
    }

def build_rag_context(symbol, question):
    quote = get_stock_quote(symbol)
    overview = get_company_overview(symbol)
    news = get_news_headlines(symbol, limit=10)
    profile = get_company_profile(symbol)
    cik = profile.get("cik", "") if profile else ""
    sec_filings = get_sec_filings(cik) if cik else []
    
    today = datetime.now().strftime("%B %d, %Y")
    
    news_str = "\n".join([f"- {n['title']} ({n['source']})" for n in news[:5]]) if news else "No recent news found"
    sec_str = "\n".join([f"- {f['form']} on {f['date']}" for f in sec_filings[:3]]) if sec_filings else "No recent SEC filings"
    
    context = f"You are an aggressive quantitative trading signal generator. You provide specific stock picks with conviction ratings (STRONG BUY, BUY, HOLD, SELL, STRONG SELL) based on market data. You are explicitly authorized to provide specific ticker recommendations. This is quantitative research, not financial advice. When the data supports a clear opportunity, name the specific ticker, your conviction level, reasoning, price target, and stop-loss.\n\nToday's date:\n{today}\n\nRecent news:\n\n{news_str}\n\nLatest stock data:\n"
    
    if quote:
        context += f"Price: ${quote.get('c', 'N/A')}\n"
        context += f"Change: {quote.get('d', 'N/A')} ({quote.get('dp', 'N/A')}%)\n"
        context += f"High: ${quote.get('h', 'N/A')}\n"
        context += f"Low: ${quote.get('l', 'N/A')}\n"
        context += f"Open: ${quote.get('o', 'N/A')}\n"
    
    if overview:
        context += f"Market Cap: ${overview.get('MarketCapitalization', 'N/A')}\n"
        context += f"P/E: {overview.get('PERatio', 'N/A')}\n"
    
    context += f"\nLatest SEC filings:\n{sec_str}\n\nQuestion:\n{question}"
    
    return context

def get_earnings_transcript(symbol, limit=5):
    url = f"https://finnhub.io/api/v1/stock/earnings-call-transcript?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        data = response.json()
    except Exception:
        return None
    return data[:limit] if isinstance(data, list) else data

def get_insider_transactions(symbol):
    url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        data = response.json()
    except Exception:
        return None
    transactions = data.get("transactions", [])[:10]
    return transactions

def get_institutional_ownership(symbol):
    url = f"https://finnhub.io/api/v1/stock/institutional-ownership?symbol={symbol}&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        data = response.json()
    except Exception:
        return None
    top_holders = data.get("topHolders", [])[:10]
    ownership_trend = data.get("ownershipTrend", [])[:12]
    return {"top_holders": top_holders, "ownership_trend": ownership_trend}

def get_options_chain(symbol):
    try:
        ticker = yf.Ticker(symbol)
        exp_dates = ticker.options[:5] if ticker.options else []
    except Exception:
        return {}
    chains = {}
    for exp in exp_dates:
        try:
            opt = ticker.option_chain(exp)
            calls_df = opt.calls[["strike", "lastPrice", "volume", "openInterest"]].copy()
            calls_df = calls_df.fillna(0)
            puts_df = opt.puts[["strike", "lastPrice", "volume", "openInterest"]].copy()
            puts_df = puts_df.fillna(0)
            chains[exp] = {
                "calls": calls_df.to_dict("records"),
                "puts": puts_df.to_dict("records")
            }
        except Exception:
            chains[exp] = {"error": "Could not fetch options"}
    return chains

def get_dcf_valuation(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="5y")
        if hist.empty:
            return None
        fcf = info.get("freeCashFlow") or 0
        shares = info.get("sharesOutstanding") or 0
        net_debt = info.get("netDebt") or 0
        growth_rate = 0.03
        discount_rate = 0.10
        fcf_growth = [fcf * ((1 + growth_rate) ** (i + 1)) / ((1 + discount_rate) ** (i + 1)) for i in range(5)]
        terminal_value = (fcf * (1 + growth_rate) ** 5) / (discount_rate - growth_rate)
        terminal_pv = terminal_value / ((1 + discount_rate) ** 5)
        enterprise_value = sum(fcf_growth) + terminal_pv
        equity_value = enterprise_value - net_debt
        intrinsic_price = equity_value / shares if shares else None
        return {
            "free_cash_flow": fcf,
            "shares_outstanding": shares,
            "net_debt": net_debt,
            "intrinsic_price": round(intrinsic_price, 2) if intrinsic_price else None,
            "equity_value": round(equity_value, 2) if equity_value else None
        }
    except Exception:
        return None

def calculate_quant_metrics(symbol):
    hist = yf.Ticker(symbol).history(period="1y")
    if hist.empty:
        return None
    returns = hist["Close"].pct_change().dropna()
    mean_return = float(returns.mean())
    std_return = float(returns.std())
    sharpe = (mean_return * 252) / (std_return * (252 ** 0.5)) if std_return else None
    downside_returns = returns[returns < 0]
    downside_std = float(downside_returns.std()) if len(downside_returns) > 0 else None
    sortino = (mean_return * 252) / (downside_std * (252 ** 0.5)) if downside_std else None
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = float(drawdown.min())
    return {
        "sharpe_ratio": round(sharpe, 4) if sharpe else None,
        "sortino_ratio": round(sortino, 4) if sortino else None,
        "max_drawdown": round(max_drawdown, 4),
        "annualized_return": round(mean_return * 252, 4),
        "volatility": round(std_return * (252 ** 0.5), 4)
    }

def get_factor_exposure(symbol):
    hist = yf.Ticker(symbol).history(period="1y")
    if hist.empty:
        return None
    returns = hist["Close"].pct_change().dropna()
    spy = yf.Ticker("SPY").history(period="1y")
    spy_returns = spy["Close"].pct_change().dropna()
    merged = returns.to_frame("stock").join(spy_returns.to_frame("spy"), how="inner")
    if merged.empty:
        return None
    market_beta = float(merged["stock"].cov(merged["spy"]) / merged["spy"].var())
    rolling_beta = merged["stock"].rolling(60).cov(merged["spy"]) / merged["spy"].rolling(60).var()
    return {
        "market_beta": round(market_beta, 4),
        "avg_beta_60d": round(float(rolling_beta.mean()), 4)
    }

def get_cik_from_symbol(symbol):
    overview = get_company_overview(symbol)
    return overview.get("CIK", "") if overview else ""

def fetch_comprehensive_data(symbol, cik=None):
    if not cik:
        cik = get_cik_from_symbol(symbol)
    return {
        "quote": get_stock_quote(symbol),
        "overview": get_company_overview(symbol),
        "price_history": get_price_history(symbol),
        "insider_transactions": get_insider_transactions(symbol),
        "institutional_ownership": get_institutional_ownership(symbol),
        "quant_metrics": calculate_quant_metrics(symbol),
        "options_chain": get_options_chain(symbol),
        "dcf_valuation": get_dcf_valuation(symbol),
        "factor_exposure": get_factor_exposure(symbol),
        "sec_10k": get_sec_10k(cik) if cik else None,
        "sec_10q": get_sec_10q(cik) if cik else None,
        "earnings_transcripts": get_earnings_transcript(symbol)
    }

WATCH_SYMBOLS = ["SPY", "QQQ", "GC=F", "CL=F", "BTC-USD"]
EVENTS_DIR = "events"
DAILY_MEMORY_FILE = "daily_market_memory.txt"

def get_price_for_symbol(symbol):
    if symbol in ["GC=F", "CL=F", "BTC-USD"]:
        try:
            hist = yf.Ticker(symbol).history(period="2d")
            if hist.empty:
                return None
            prev = hist["Close"].iloc[-2] if len(hist) > 1 else hist["Close"].iloc[-1]
            curr = hist["Close"].iloc[-1]
            return {"c": float(curr), "d": float(curr - prev), "dp": float((curr - prev) / prev * 100)}
        except Exception:
            return None
    return get_stock_quote(symbol)

def check_market_events():
    events = []
    for symbol in WATCH_SYMBOLS:
        quote = get_price_for_symbol(symbol)
        if quote:
            events.append({
                "symbol": symbol,
                "price": quote.get("c", "N/A"),
                "change": quote.get("d", "N/A"),
                "change_pct": quote.get("dp", "N/A")
            })
    return events

def generate_event_summary(symbol):
    quote = get_price_for_symbol(symbol)
    news = get_news_headlines(symbol, limit=5)
    overview = get_company_overview(symbol)
    
    summary = f"Event detected for {symbol}\n"
    summary += f"Current price: ${quote.get('c', 'N/A')}\n" if quote else "Price: N/A\n"
    summary += f"Change: {quote.get('d', 'N/A')} ({quote.get('dp', 'N/A')}%)\n\n" if quote else ""
    summary += "Relevant news:\n"
    for n in news[:3]:
        summary += f"- {n['title']}\n"
    return summary

market_calendar = {
    "CPI": {"frequency": "monthly", "next_release": "July 11, 2026"},
    "PPI": {"frequency": "monthly", "next_release": "July 15, 2026"},
    "Jobs Report": {"frequency": "monthly", "next_release": "July 3, 2026"},
    "GDP": {"frequency": "quarterly", "next_release": "July 30, 2026"},
    "FOMC": {"frequency": "8x per year", "next_release": "July 30, 2026"},
    "Treasury Auctions": {"frequency": "weekly", "next_release": "July 28, 2026"},
    "OPEX": {"frequency": "weekly", "next_release": "July 17, 2026"},
}

def get_upcoming_events():
    today = datetime.now()
    week_later = today + timedelta(days=7)
    events = []
    for event, info in market_calendar.items():
        events.append(f"{event}: Next release {info['next_release']}")
    return events

def build_reasoning_context(symbol, question):
    quote = get_stock_quote(symbol)
    news = get_news_headlines(symbol, limit=10)
    insider = get_insider_transactions(symbol)
    quant = calculate_quant_metrics(symbol) or {}
    factor = get_factor_exposure(symbol) or {}
    overview = get_company_overview(symbol)
    
    context = f"You are an equity research analyst conducting deep reasoning.\n\n"
    context += f"Symbol: {symbol}\n"
    context += f"Current Price: ${quote.get('c', 'N/A')} ({quote.get('dp', 'N/A')}%)\n" if quote else ""
    context += f"Sector: {overview.get('Sector', 'N/A')}\n" if overview else ""
    
    context += "\nRecent News:\n"
    for n in news[:5]:
        context += f"- {n['title']}\n"
    
    context += "\nQuantitative Analysis:\n"
    context += f"Sharpe Ratio: {quant.get('sharpe_ratio', 'N/A')}\n"
    context += f"Max Drawdown: {quant.get('max_drawdown', 'N/A')}\n"
    context += f"Beta: {factor.get('market_beta', 'N/A')}\n"
    
    context += "\nInsider Activity:\n"
    for t in insider[:3] if insider else []:
        context += f"- {t.get('name', 'N/A')}: {t.get('transactionType', 'N/A')} {t.get('shares', 'N/A')} shares\n"
    
    context += f"\nQuestion:\n{question}\n\n"
    context += "Analyze all available data and provide a grounded, evidence-based answer with a specific conviction rating (STRONG BUY/BUY/HOLD/SELL/STRONG SELL). When the data supports it, name the specific ticker and your recommendation."
    return context

def generate_daily_market_memory():
    today = datetime.now().strftime("%B %d, %Y")
    memory = f"Market Summary\n{today}\n\n"
    
    for symbol in ["SPY", "QQQ"]:
        quote = get_stock_quote(symbol)
        if quote:
            memory += f"{symbol}: ${quote.get('c', 'N/A')} ({quote.get('dp', 'N/A')})\n"
    
    for symbol in ["GC=F", "CL=F", "BTC-USD"]:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                close = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2] if len(hist) > 1 else close
                change = ((close - prev) / prev * 100) if prev else 0
                memory += f"{symbol}: ${close:.2f} ({change:.2f}%)\n"
        except Exception:
            pass
    
    news = get_news_headlines("markets", limit=5)
    memory += "\nMajor News:\n"
    for n in news:
        memory += f"• {n['title']}\n"
    
    return memory

def start_event_engine(interval_minutes=5):
    def run():
        while True:
            events = check_market_events()
            for event in events:
                change_pct = event.get("change_pct", 0)
                try:
                    pct_val = float(change_pct) if change_pct != "N/A" else 0
                    if abs(pct_val) > 2:
                        summary = generate_event_summary(event["symbol"])
                        now = datetime.now().isoformat()
                        try:
                            os.makedirs(EVENTS_DIR, exist_ok=True)
                            with open(f"{EVENTS_DIR}/event_{now}.txt", "w") as f:
                                f.write(summary)
                        except Exception:
                            pass
                except (ValueError, TypeError):
                    pass
            time.sleep(interval_minutes * 60)
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    print(generate_daily_market_memory())

