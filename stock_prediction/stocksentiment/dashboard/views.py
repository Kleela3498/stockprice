from django.shortcuts import render
from django.http import HttpRequest # For type hinting
from .utils import data_fetchers, sentiment_analyzer # Import our utils
import plotly.graph_objects as go
import plotly.offline as opy
import pandas as pd
import logging
from datetime import datetime, timedelta, date # Added date

logger = logging.getLogger(__name__)

def index(request: HttpRequest):
    return render(request, 'dashboard/index.html')

def historic(request: HttpRequest):
    # Default date range (e.g., last 3 years)
    default_end_date = date.today()
    default_start_date = default_end_date - timedelta(days=3*365)

    context = {
        'stocks': data_fetchers.TARGET_STOCKS,
        'selected_stocks': [],
        'start_date': default_start_date, # Add default dates to context
        'end_date': default_end_date,
        'price_chart_html': None,
        'sentiment_chart_html': None,
        'news_articles': [],
        'error': None
    }

    if request.method == 'POST':
        selected_tickers = request.POST.getlist('stocks')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        # Validate and convert dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if start_date >= end_date:
                 raise ValueError("Start date must be before end date.")
            # Update context with user-selected dates
            context['start_date'] = start_date
            context['end_date'] = end_date
        except (ValueError, TypeError) as e:
            context['error'] = f"Invalid date format or range: {e}"
            context['selected_stocks'] = selected_tickers # Keep selected stocks
            return render(request, 'dashboard/historic.html', context)

        context['selected_stocks'] = selected_tickers

        if not selected_tickers:
            context['error'] = "Please select at least one stock."
            return render(request, 'dashboard/historic.html', context)

        if len(selected_tickers) > 5:
             context['error'] = "Please select a maximum of 5 stocks."
             context['selected_stocks'] = [] # Reset selection
             return render(request, 'dashboard/historic.html', context)

        # Calculate days difference for news lookback, capped at ~30 for NewsAPI
        news_lookback_days = min((end_date - start_date).days, 28)
        if news_lookback_days <= 0:
            news_lookback_days = 1 # Ensure at least 1 day for news

        try:
            # 1. Fetch Stock Data (using selected dates)
            logger.info(f"Fetching historical stock data for: {selected_tickers} from {start_date} to {end_date}")
            stock_data = data_fetchers.get_historical_stock_data_by_date(selected_tickers, start_date, end_date)

            # 2. Fetch News (using dates, limited by lookback)
            logger.info(f"Fetching news headlines for: {selected_tickers} up to {end_date} (lookback {news_lookback_days} days)")
            news_articles = data_fetchers.get_news_headlines_by_date(selected_tickers, end_date, news_lookback_days)

            # 3. Analyze Sentiment
            logger.info(f"Analyzing sentiment for {len(news_articles)} articles.")
            analyzed_articles = sentiment_analyzer.analyze_headlines_sentiment(news_articles)
            context['news_articles'] = analyzed_articles[:20] # Display top 20 recent articles

            # 4. Aggregate Sentiment
            logger.info("Aggregating sentiment over time.")
            daily_sentiment = sentiment_analyzer.aggregate_sentiment_over_time(analyzed_articles, freq='D')

            # 5. Generate Plots
            if stock_data is not None and not stock_data.empty:
                logger.info("Generating price chart.")
                price_fig = go.Figure()
                for ticker in stock_data.columns:
                    price_fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data[ticker], mode='lines', name=ticker))
                price_fig.update_layout(
                    title=f'Historical Adjusted Close Prices ({start_date} to {end_date})',
                    xaxis_title='Date', yaxis_title='Price (USD)', legend_title='Tickers'
                )
                context['price_chart_html'] = opy.plot(price_fig, auto_open=False, output_type='div')
            else:
                 logger.warning("No stock data available to generate price chart.")
                 context['error'] = (context.get('error') or "") + "Could not fetch stock price data. "

            if not daily_sentiment.empty:
                # Filter sentiment data to match selected date range
                filtered_sentiment = daily_sentiment[start_date:end_date]
                if not filtered_sentiment.empty:
                    logger.info("Generating sentiment chart.")
                    sentiment_fig = go.Figure()
                    sentiment_fig.add_trace(go.Scatter(x=filtered_sentiment.index, y=filtered_sentiment.values, mode='lines+markers', name='Avg Daily Sentiment'))
                    if len(filtered_sentiment) >= 7:
                        rolling_avg = filtered_sentiment.rolling(window=7).mean()
                        sentiment_fig.add_trace(go.Scatter(x=rolling_avg.index, y=rolling_avg.values, mode='lines', name='7-Day Rolling Avg'))
                    sentiment_fig.update_layout(title='Average Daily News Sentiment (VADER Compound Score)', xaxis_title='Date', yaxis_title='Avg. Sentiment Score')
                    context['sentiment_chart_html'] = opy.plot(sentiment_fig, auto_open=False, output_type='div')
                else:
                    logger.warning("No sentiment data available within the selected date range.")
            else:
                logger.warning("No sentiment data available to generate sentiment chart.")
                # Keep the existing error message if sentiment processing failed earlier
                if "Could not process sentiment data" not in (context.get('error') or ""):
                    context['error'] = (context.get('error') or "") + "Could not process sentiment data for the selected range. "

            # TODO: Add ML Prediction step here later

        except Exception as e:
            logger.error(f"Error processing historic data: {e}", exc_info=True)
            context['error'] = "An unexpected error occurred while processing the data."

    return render(request, 'dashboard/historic.html', context)

def live(request: HttpRequest):
    return render(request, 'dashboard/live.html')

def correlation_view(request: HttpRequest):
    # Logic for correlation analysis will go here
    context = {}
    return render(request, 'dashboard/correlation.html', context)
