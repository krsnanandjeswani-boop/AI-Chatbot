from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import re
from threading import Lock
from time import time
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import requests


GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search"
NEWS_CACHE_TTL_SECONDS = 300
MAX_NEWS_QUERY_LENGTH = 240
MAX_NEWS_RESULTS = 10
RECENT_NEWS_DAYS = 30


@dataclass(frozen=True)
class NewsArticle:
    title: str
    publisher: str
    published_at: str
    url: str


@dataclass(frozen=True)
class NewsSearchResult:
    articles: tuple[NewsArticle, ...] = ()
    error: str | None = None
    recent_only: bool = True


_news_cache: dict[str, tuple[float, tuple[NewsArticle, ...]]] = {}
_news_cache_lock = Lock()


def _is_historical_query(query: str) -> bool:
    current_year = datetime.now(timezone.utc).year
    return any(
        int(year) < current_year
        for year in re.findall(r"\b(?:19|20)\d{2}\b", query)
    )


def _parse_published_at(value: str):
    if not value:
        return None
    try:
        published_at = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    return published_at.astimezone(timezone.utc)


def search_google_news(query: str, limit: int = 8) -> NewsSearchResult:
    normalized_query = " ".join(query.split())[:MAX_NEWS_QUERY_LENGTH]
    if not normalized_query:
        return NewsSearchResult()

    result_limit = max(1, min(int(limit), MAX_NEWS_RESULTS))
    recent_only = not _is_historical_query(normalized_query)
    cache_key = f"{normalized_query.casefold()}|{recent_only}"
    now = time()

    with _news_cache_lock:
        cached_result = _news_cache.get(cache_key)
        if cached_result and now - cached_result[0] < NEWS_CACHE_TTL_SECONDS:
            return NewsSearchResult(
                articles=cached_result[1][:result_limit],
                recent_only=recent_only,
            )

    try:
        response = requests.get(
            GOOGLE_NEWS_RSS_URL,
            params={
                "q": (
                    f"{normalized_query} when:{RECENT_NEWS_DAYS}d"
                    if recent_only
                    else normalized_query
                ),
                "hl": "en-US",
                "gl": "US",
                "ceid": "US:en",
            },
            headers={"User-Agent": "QuantbotResearch/1.0"},
            timeout=8,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        return NewsSearchResult(
            error=f"Google News RSS returned HTTP {status}.",
            recent_only=recent_only,
        )
    except requests.RequestException as exc:
        return NewsSearchResult(
            error=f"Google News RSS is unavailable ({type(exc).__name__}).",
            recent_only=recent_only,
        )

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError:
        return NewsSearchResult(
            error="Google News RSS returned invalid XML.",
            recent_only=recent_only,
        )

    articles = []
    current_time = datetime.now(timezone.utc)
    recent_cutoff = current_time - timedelta(days=RECENT_NEWS_DAYS)
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        published_at = (item.findtext("pubDate") or "").strip()
        parsed_url = urlparse(url)
        if (
            not title
            or parsed_url.scheme != "https"
            or parsed_url.hostname != "news.google.com"
        ):
            continue
        published_datetime = _parse_published_at(published_at)
        if recent_only and (
            published_datetime is None
            or published_datetime < recent_cutoff
            or published_datetime > current_time + timedelta(days=1)
        ):
            continue

        source = item.find("source")
        publisher = (source.text if source is not None and source.text else "").strip()
        articles.append(
            NewsArticle(
                title=title,
                publisher=publisher or "Publisher not listed",
                published_at=published_at,
                url=url,
            )
        )
        if len(articles) == result_limit:
            break

    article_tuple = tuple(articles)
    with _news_cache_lock:
        _news_cache[cache_key] = (time(), article_tuple)

    return NewsSearchResult(articles=article_tuple, recent_only=recent_only)


def format_news_context(result: NewsSearchResult) -> str:
    if result.error:
        return (
            "CURRENT NEWS SEARCH FAILED: "
            f"{result.error} No current news results are available; do not claim "
            "that the news search found no coverage."
        )
    if not result.articles:
        if result.recent_only:
            return (
                f"CURRENT NEWS SEARCH: No dated headlines from the last "
                f"{RECENT_NEWS_DAYS} days matched this query. Do not present older "
                "headlines or model memory as current news; say current sourcing "
                "found no recent results."
            )
        return (
            "HISTORICAL NEWS SEARCH: No matching headlines were returned. This "
            "does not establish that no relevant news exists."
        )

    lines = [
        ("CURRENT" if result.recent_only else "HISTORICAL")
        + " HEADLINE SEARCH "
        f"(Google News RSS; searched {datetime.now().astimezone().isoformat(timespec='minutes')}; "
        + (
            f"only articles published within the last {RECENT_NEWS_DAYS} days; "
            if result.recent_only
            else "no recency filter; "
        )
        + "headline metadata only):",
        "These results are discovery leads, not independently verified article text. "
        "Do not infer article details from a headline. Treat allegations of "
        "wrongdoing, espionage, or personal conduct as allegations unless confirmed "
        "by primary documentation or multiple independent, reputable reports. "
        "Distinguish confirmed facts from reported claims and cite relevant results "
        "with their supplied links and publication dates.",
    ]
    for article in result.articles:
        lines.append(
            f"- {article.title} | Publisher: {article.publisher} | "
            f"Published: {article.published_at or 'date not listed'} | "
            f"Link: {article.url}"
        )
    return "\n".join(lines)
