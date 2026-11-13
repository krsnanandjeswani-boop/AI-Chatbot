import unittest
from unittest.mock import Mock, patch

import requests

import news_provider
from news_provider import format_news_context, search_google_news


SAMPLE_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>NVIDIA reports new CEO transition</title>
      <link>https://news.google.com/rss/articles/example?oc=5</link>
      <pubDate>Thu, 12 Nov 2026 13:56:53 GMT</pubDate>
      <source url="https://nvidianews.nvidia.com">NVIDIA Newsroom</source>
    </item>
  </channel>
</rss>
"""


class GoogleNewsProviderTests(unittest.TestCase):
    def setUp(self):
        with news_provider._news_cache_lock:
            news_provider._news_cache.clear()

    def test_parses_headlines_and_sends_encoded_search_parameters(self):
        response = Mock(content=SAMPLE_FEED)
        response.raise_for_status.return_value = None

        with patch("news_provider.requests.get", return_value=response) as get:
            result = search_google_news("Jensen Huang")

        self.assertIsNone(result.error)
        self.assertEqual(len(result.articles), 1)
        self.assertEqual(result.articles[0].publisher, "NVIDIA Newsroom")
        self.assertEqual(result.articles[0].published_at, "Thu, 12 Nov 2026 13:56:53 GMT")
        self.assertEqual(result.articles[0].url, "https://news.google.com/rss/articles/example?oc=5")
        self.assertEqual(
            get.call_args.kwargs["params"]["q"],
            f"Jensen Huang when:{news_provider.RECENT_NEWS_DAYS}d",
        )
        self.assertEqual(get.call_args.kwargs["timeout"], 8)

    def test_discards_old_articles_for_current_news_queries(self):
        old_feed = SAMPLE_FEED.replace(b"2026", b"2024")
        response = Mock(content=old_feed)
        response.raise_for_status.return_value = None

        with patch("news_provider.requests.get", return_value=response):
            result = search_google_news("Jensen Huang current news")

        self.assertEqual(result.articles, ())
        self.assertIn("last 30 days", format_news_context(result))

    def test_historical_queries_do_not_apply_current_news_window(self):
        response = Mock(content=SAMPLE_FEED)
        response.raise_for_status.return_value = None

        with patch("news_provider.requests.get", return_value=response) as get:
            result = search_google_news("Jensen Huang in 2024")

        self.assertFalse(result.recent_only)
        self.assertEqual(get.call_args.kwargs["params"]["q"], "Jensen Huang in 2024")

    def test_caches_successful_searches(self):
        response = Mock(content=SAMPLE_FEED)
        response.raise_for_status.return_value = None

        with patch("news_provider.requests.get", return_value=response) as get:
            first = search_google_news("Jensen Huang")
            second = search_google_news("  jensen   huang ")

        self.assertEqual(first.articles, second.articles)
        get.assert_called_once()

    def test_reports_http_errors_without_claiming_no_news(self):
        response = Mock(content=b"", status_code=429)
        response.raise_for_status.side_effect = requests.HTTPError(response=response)

        with patch("news_provider.requests.get", return_value=response):
            result = search_google_news("Nvidia")

        self.assertIn("HTTP 429", result.error)
        self.assertIn("search failed", format_news_context(result).lower())

    def test_context_marks_headlines_as_unverified_leads(self):
        response = Mock(content=SAMPLE_FEED)
        response.raise_for_status.return_value = None

        with patch("news_provider.requests.get", return_value=response):
            result = search_google_news("Jensen Huang")

        context = format_news_context(result)
        self.assertIn("not independently verified", context)
        self.assertIn("allegations", context)
        self.assertIn(result.articles[0].url, context)


if __name__ == "__main__":
    unittest.main()
