import yfinance as yf
from datetime import datetime


class DataIngestionLayer:
    def __init__(self):
        pass

    def scrape_news(self, ticker):
        """
        2026 Stable Yahoo Method: Uses the Search API.
        No BeautifulSoup or Selenium required.
        """
        news_list = []
        try:
            print(f"[*] Querying Yahoo Finance API for {ticker} news...")

            # Use the Search module to find news related to the ticker
            search = yf.Search(ticker, max_results=8)
            raw_news = search.news

            if not raw_news:
                print(f"[!] Yahoo returned no news for {ticker}.")
                return []

            for item in raw_news:
                # Yahoo's API uses these specific keys
                title = item.get("title")
                link = item.get("link")

                # Convert the 'providerPublishTime' to readable format
                pub_time = item.get("providerPublishTime", 0)
                ts = (
                    datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M")
                    if pub_time
                    else "N/A"
                )

                if title and link:
                    news_list.append(
                        {
                            "ticker": ticker,
                            "headline": title,
                            "url": link,
                            "timestamp": ts,
                        }
                    )

            print(f"[OK] Retrieved {len(news_list)} headlines.")

        except Exception as e:
            print(f"[!] Yahoo API Error: {e}")

        return news_list
