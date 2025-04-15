import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, date
from newsapi import NewsApiClient
from django.conf import settings
import logging # Added for logging errors

# Configure logging
logger = logging.getLogger(__name__)

# Define the target stock tickers
TARGET_STOCKS = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'GOOGL']

def get_historical_stock_data(tickers, years=3):
    """Fetches historical stock data for given tickers for the specified number of years.

    Args:
        tickers (list): A list of stock ticker symbols.
        years (int): Number of years of historical data to fetch.

    Returns:
        pandas.DataFrame: A DataFrame containing the historical data (Adj Close),
                          or None if fetching fails.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)

    try:
        # Fetch the full dataset first
        full_data = yf.download(tickers, start=start_date, end=end_date)

        # Check if download was successful and data is available
        if full_data.empty:
            logger.warning(f"No data downloaded for {tickers} between {start_date} and {end_date}")
            return None

        # Select 'Adj Close', handle single vs multiple tickers
        if isinstance(full_data.columns, pd.MultiIndex):
            data = full_data['Adj Close']
            # Drop tickers with all NaN Adj Close (might happen if ticker is invalid for the period)
            data = data.dropna(axis=1, how='all')
        elif 'Adj Close' in full_data.columns:
             # Handle single ticker case (DataFrame with single-level columns)
             data = full_data[['Adj Close']]
             data.columns = [tickers[0]] # Name the column correctly
        else:
            logger.error(f"'Adj Close' column not found in downloaded data for {tickers}. Available: {full_data.columns}")
            return None

        if data.empty:
             logger.warning(f"'Adj Close' data is empty after selection for {tickers}")
             return None

        # Ensure data is sorted by date
        data = data.sort_index()

        # Handle potential missing data (e.g., fill forward, then backward)
        data = data.ffill().bfill()

        return data

    except Exception as e:
        print(f"Error fetching historical data for {tickers}: {e}")
        return None

def get_historical_stock_data_by_date(tickers, start_date, end_date):
    """Fetches historical stock data for given tickers between specified dates.

    Args:
        tickers (list): A list of stock ticker symbols.
        start_date (datetime.date or str): Start date (YYYY-MM-DD or date object).
        end_date (datetime.date or str): End date (YYYY-MM-DD or date object).

    Returns:
        pandas.DataFrame: A DataFrame containing the historical data (Adj Close),
                          or None if fetching fails.
    """
    try:
        # Ensure dates are in the correct string format if needed by yfinance
        start_str = start_date.isoformat() if isinstance(start_date, date) else start_date
        end_str = end_date.isoformat() if isinstance(end_date, date) else end_date

        # Fetch the full dataset first
        full_data = yf.download(tickers, start=start_str, end=end_str)

        # Check if download was successful and data is available
        if full_data.empty:
            logger.warning(f"No data downloaded for {tickers} between {start_str} and {end_str}")
            return None

        # Select 'Adj Close', handle single vs multiple tickers
        if isinstance(full_data.columns, pd.MultiIndex):
            # Make sure 'Adj Close' exists at the top level
            if 'Adj Close' not in full_data.columns.levels[0]:
                 logger.error(f"'Adj Close' not found in MultiIndex columns for {tickers}. Available: {full_data.columns.levels[0]}")
                 return None
            data = full_data['Adj Close']
            # Drop tickers with all NaN Adj Close
            data = data.dropna(axis=1, how='all')
        elif 'Adj Close' in full_data.columns:
             data = full_data[['Adj Close']]
             # Ensure column name matches ticker if single ticker requested
             if len(tickers) == 1:
                 data.columns = tickers
        else:
            logger.error(f"'Adj Close' column not found in downloaded data for {tickers}. Available: {full_data.columns}")
            return None

        if data.empty:
             logger.warning(f"'Adj Close' data is empty after selection for {tickers}")
             return None

        # Ensure data is sorted by date
        data = data.sort_index()

        # Handle potential missing data
        data = data.ffill().bfill()

        return data

    except Exception as e:
        logger.error(f"Error fetching historical data for {tickers}: {e}", exc_info=True)
        return None

def get_news_headlines(tickers, days_lookback=30):
    """Fetches news headlines for given tickers for the specified lookback period.

    Args:
        tickers (list): A list of stock ticker symbols (or relevant keywords).
        days_lookback (int): Number of past days to fetch news for.

    Returns:
        list: A list of dictionaries, where each dictionary represents an article
              with keys like 'publishedAt', 'title', 'description', 'source', 'url'.
              Returns an empty list if fetching fails or no API key is found.
    """
    if not settings.NEWS_API_KEY:
        logger.error("NewsAPI key not found in settings.")
        return []

    newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)
    all_articles = []
    to_date = datetime.now().date()
    from_date = to_date - timedelta(days=days_lookback)

    # NewsAPI recommends using keywords for stocks
    query = " OR ".join(tickers)

    try:
        # Fetch news using the /everything endpoint
        # Note: Free tier might limit lookback range (e.g., 1 month) and requests
        # For broader search, consider source filtering or /top-headlines
        page = 1
        total_results = 1 # Placeholder to start loop
        fetched_results = 0

        while fetched_results < total_results and fetched_results < 500: # Limit total fetches
            response = newsapi.get_everything(
                q=query,
                from_param=from_date.isoformat(),
                to=to_date.isoformat(),
                language='en',
                sort_by='publishedAt', # Or 'relevancy', 'popularity'
                page_size=100, # Max page size
                page=page
            )

            if response['status'] == 'ok':
                articles = response.get('articles', [])
                total_results = response.get('totalResults', 0)
                all_articles.extend(articles)
                fetched_results += len(articles)

                # Break if no more articles or if total results limit reached
                if not articles or fetched_results >= total_results:
                    break
                page += 1
            else:
                logger.error(f"NewsAPI error: {response.get('message')}")
                break # Stop fetching on error

        # Basic cleaning/structuring
        cleaned_articles = [
            {
                'publishedAt': article.get('publishedAt'),
                'title': article.get('title'),
                'description': article.get('description'),
                'source': article.get('source', {}).get('name'),
                'url': article.get('url')
            } for article in all_articles
        ]
        return cleaned_articles

    except Exception as e:
        logger.error(f"Error fetching news headlines for {tickers}: {e}", exc_info=True)
        return []

def get_news_headlines_by_date(tickers, end_date, days_lookback=28):
    """Fetches news headlines for given tickers up to end_date with a lookback.

    Args:
        tickers (list): A list of stock ticker symbols (or relevant keywords).
        end_date (datetime.date or str): The latest date for news.
        days_lookback (int): Number of past days from end_date to fetch news for.
                           (Limited by NewsAPI plan, typically ~30 days for free tier).

    Returns:
        list: A list of dictionaries representing articles.
              Returns an empty list if fetching fails or no API key.
    """
    if not settings.NEWS_API_KEY:
        logger.error("NewsAPI key not found in settings.")
        return []

    newsapi = NewsApiClient(api_key=settings.NEWS_API_KEY)
    all_articles = []

    try:
        # Ensure end_date is a date object
        if isinstance(end_date, str):
            to_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            to_date_obj = end_date

        from_date_obj = to_date_obj - timedelta(days=days_lookback)

        query = " OR ".join(tickers)

        # Fetch news page by page
        page = 1
        total_results = 1
        fetched_results = 0
        max_fetch = 500 # Limit API calls

        while fetched_results < total_results and fetched_results < max_fetch:
            response = newsapi.get_everything(
                q=query,
                from_param=from_date_obj.isoformat(),
                to=to_date_obj.isoformat(),
                language='en',
                sort_by='publishedAt',
                page_size=100,
                page=page
            )

            if response['status'] == 'ok':
                articles = response.get('articles', [])
                total_results = response.get('totalResults', 0)
                all_articles.extend(articles)
                fetched_results += len(articles)
                if not articles or fetched_results >= total_results:
                    break
                page += 1
            else:
                # Log the specific error from NewsAPI
                api_error_code = response.get('code')
                api_error_message = response.get('message')
                logger.error(f"NewsAPI error (Code: {api_error_code}): {api_error_message}")
                # Specific handling for date range issue
                if api_error_code == 'parameterInvalid' and 'too far in the past' in api_error_message:
                     logger.warning(f"NewsAPI lookback limit likely exceeded. Requested {days_lookback} days back from {to_date_obj}.")
                break # Stop fetching on error

        cleaned_articles = [
            {
                'publishedAt': article.get('publishedAt'),
                'title': article.get('title'),
                'description': article.get('description'),
                'source': article.get('source', {}).get('name'),
                'url': article.get('url')
            } for article in all_articles
        ]
        return cleaned_articles

    except Exception as e:
        # Catch potential strptime errors or other issues
        logger.error(f"Error fetching/processing news headlines for {tickers}: {e}", exc_info=True)
        return []

# --- NewsAPI functions will go here later ---

# --- Alpha Vantage functions will go here later ---

# --- Twitter/Reddit/RSS scraping functions will go here later ---
