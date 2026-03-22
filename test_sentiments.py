from scrapper import DataIngestionLayer
from analyzer import SentimentAnalyzer


def run_sentiment_check(ticker):
    # 1. Initialize Modules
    print(f"[*] Initializing Scraper and FinBERT Model...")
    ingestor = DataIngestionLayer()
    # Note: On CPU, this next line takes 2-5 seconds to load the model
    analyzer = SentimentAnalyzer()

    print(f"\n{'=' * 40}")
    print(f"FETCHING NEWS FOR: {ticker}")
    print(f"{'=' * 40}")

    # 2. Module A: Scrape News
    news_items = ingestor.scrape_news(ticker)

    if not news_items or "error" in news_items[0]:
        print("[!] No news headlines found for this ticker.")
        return

    # 3. Module B: Process Sentiment
    # We extract just the headlines from the list of dictionaries
    headlines = [item["headline"] for item in news_items]

    print(f"[*] Analyzing {len(headlines)} headlines...")
    scored_results = analyzer.analyze_headlines(headlines)

    # 4. Display Combined Results
    print(f"\n--- SENTIMENT ANALYSIS REPORT ---")

    total_score = 0
    for i, res in enumerate(scored_results):
        sentiment = res["sentiment"].upper()
        conf = res["confidence"] * 100
        headline = res["headline"]

        print(f"[{sentiment}] ({conf:.1f}%) - {headline}")
        total_score += res["score_value"]

    # Calculate Average Vibe
    avg_vibe = total_score / len(scored_results)
    vibe_label = (
        "BULLISH" if avg_vibe > 0.2 else "BEARISH" if avg_vibe < -0.2 else "NEUTRAL"
    )

    print(f"\nOVERALL MARKET VIBE: {vibe_label} ({avg_vibe:.2f})")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    target = input("Enter Ticker (e.g., TSLA): ").upper()
    run_sentiment_check(target)
