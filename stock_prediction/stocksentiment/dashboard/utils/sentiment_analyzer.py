from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Initialize VADER analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment_vader(text):
    """Analyzes the sentiment of a single text using VADER.

    Args:
        text (str): The text to analyze.

    Returns:
        dict: A dictionary containing VADER scores (neg, neu, pos, compound).
              Returns None if input is not a string or analysis fails.
    """
    if not isinstance(text, str):
        return None # Or return default neutral scores
    try:
        vs = analyzer.polarity_scores(text)
        return vs
    except Exception as e:
        logger.error(f"Error analyzing sentiment for text: '{text[:50]}...': {e}", exc_info=True)
        return None

def analyze_headlines_sentiment(articles):
    """Analyzes sentiment for a list of news articles (dictionaries).

    Adds 'sentiment' (VADER compound score) and 'sentiment_label' (Positive/Negative/Neutral)
    to each article dictionary.

    Args:
        articles (list): A list of article dictionaries (expecting 'title' and 'description').

    Returns:
        list: The list of articles with added sentiment information.
              Returns an empty list if input is invalid.
    """
    if not isinstance(articles, list):
        logger.error("Invalid input: articles must be a list.")
        return []

    analyzed_articles = []
    for article in articles:
        if not isinstance(article, dict):
            logger.warning("Skipping non-dictionary item in articles list.")
            continue

        # Combine title and description for better context, handle missing values
        title = article.get('title', '') or ''
        description = article.get('description', '') or ''
        text_to_analyze = f"{title}. {description}".strip()

        if not text_to_analyze or text_to_analyze == '.':
            article['sentiment'] = 0.0 # Default to neutral if no text
            article['sentiment_label'] = 'Neutral'
            analyzed_articles.append(article)
            continue

        sentiment_scores = analyze_sentiment_vader(text_to_analyze)

        if sentiment_scores:
            compound_score = sentiment_scores['compound']
            article['sentiment'] = compound_score
            # Simple labeling based on compound score thresholds
            if compound_score >= 0.05:
                article['sentiment_label'] = 'Positive'
            elif compound_score <= -0.05:
                article['sentiment_label'] = 'Negative'
            else:
                article['sentiment_label'] = 'Neutral'
        else:
            # Handle cases where sentiment analysis failed
            article['sentiment'] = 0.0
            article['sentiment_label'] = 'Neutral' # Or 'Error'

        analyzed_articles.append(article)

    return analyzed_articles

def aggregate_sentiment_over_time(analyzed_articles, freq='D'):
    """Aggregates sentiment scores from articles over time.

    Args:
        analyzed_articles (list): List of articles with 'publishedAt' and 'sentiment' keys.
        freq (str): Pandas frequency string for resampling (e.g., 'D' for daily, 'W' for weekly).

    Returns:
        pandas.Series: A time series with the average daily sentiment score,
                       or an empty Series if processing fails.
    """
    if not analyzed_articles:
        return pd.Series(dtype=float)

    try:
        df = pd.DataFrame(analyzed_articles)
        # Convert 'publishedAt' to datetime objects, coercing errors
        df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')
        # Drop rows where conversion failed
        df = df.dropna(subset=['publishedAt', 'sentiment'])
        df = df.set_index('publishedAt')

        # Resample and calculate mean sentiment
        daily_sentiment = df['sentiment'].resample(freq).mean()

        # Fill missing days with 0 (neutral)
        daily_sentiment = daily_sentiment.fillna(0)

        return daily_sentiment
    except Exception as e:
        logger.error(f"Error aggregating sentiment over time: {e}", exc_info=True)
        return pd.Series(dtype=float)
