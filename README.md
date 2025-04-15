# StockSentiment Web Application

## Overview

StockSentiment is a Django-based web application designed to analyze stock market sentiment and predict potential price movements. It integrates data from various sources, including financial APIs (Yahoo Finance, Alpha Vantage), news APIs (NewsAPI), and social media platforms (Twitter, Reddit), to provide users with comprehensive insights.

The application aims to offer three main analysis modes:

1.  **Historic Analysis:** Analyze past stock performance alongside historical news sentiment and basic machine learning predictions over a user-defined period.
2.  **Live Prediction:** Fetch real-time stock data, aggregate live sentiment from multiple sources (Twitter, Reddit, Google News), and use an LLM (via OpenRouter) to generate near real-time predictions with explanations.
3.  **Correlation Analysis:** Explore the statistical correlation between historical sentiment trends and stock price movements for selected stocks.

## Features & Progress

### Core Setup
*   **Project Structure:** Django project `stocksentiment` with a `dashboard` app.
*   **Environment:** Uses `venv` for virtual environment management and `.env` for API key storage (`python-dotenv`).
*   **Dependencies:** Managed via `requirements.txt`. Key libraries include Django, yfinance, newsapi-python, vaderSentiment, scikit-learn, pandas, plotly, Bootstrap 5 (via CDN).
*   **Basic UI:** Responsive navigation bar and page structure using Bootstrap 5. Placeholder pages for all main features (`index`, `historic`, `live`, `correlation`).
*   **Utility Modules:** Separate modules created for `data_fetchers`, `sentiment_analyzer`, `ml_model`, `correlation_analyzer`, and `llm_integration` within the `dashboard` app.

### Historic Analysis (Partially Implemented)
*   **Data Fetching:**
    *   Fetches historical stock price data (Adjusted Close) for selected tickers (AAPL, TSLA, AMZN, MSFT, GOOGL) within a user-specified date range using `yfinance`.
    *   Fetches relevant news headlines for the selected tickers from `NewsAPI` for the last ~28 days of the selected date range (due to API limitations).
*   **Sentiment Analysis:**
    *   Analyzes the sentiment of fetched news headlines using VADER (`vaderSentiment`).
    *   Aggregates sentiment scores (compound score) on a daily basis.
*   **Visualization:**
    *   Displays an interactive historical price chart using `Plotly`.
    *   Displays an interactive timeline of aggregated daily news sentiment using `Plotly`.
    *   Lists recent news headlines with their sentiment scores and links to the source.
*   **User Interface:**
    *   Allows users to select multiple stocks (up to 5).
    *   Allows users to select a start and end date for the analysis.
    *   Displays results dynamically based on user input.
    *   Handles basic input validation and displays errors.
*   **To-Do:**
    *   Implement the machine learning prediction component (e.g., RandomForest) using features derived from price and sentiment data.
    *   Display ML predictions on the page.

### Live Prediction (Not Started)
*   **Planned Features:**
    *   Fetch real-time data (Alpha Vantage).
    *   Scrape live sentiment (snscrape for Twitter, PRAW for Reddit, feedparser for Google News).
    *   Aggregate live sentiment.
    *   Integrate with OpenRouter API (Mistral model specified) for LLM-based prediction and explanation.
    *   Display live charts and LLM output.
    *   Show Alpha Vantage API usage/limits.

### Correlation Analysis (Not Started)
*   **Planned Features:**
    *   Calculate correlation (Pearson/Spearman) between historical price changes and aggregated sentiment scores over 3 years.
    *   Display correlation scores.
    *   Visualize price vs. sentiment with overlays using Plotly.

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd stock_prediction
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create `.env` file:**
    *   Copy the `.env.example` file (if it exists) or create a new file named `.env` in the project root (`stock_prediction/`).
    *   Add your API keys to the `.env` file:
        ```dotenv
        NEWS_API_KEY=<your_newsapi_key>
        ALPHA_VANTAGE_API_KEY=<your_alpha_vantage_key>
        REDDIT_CLIENT_ID=<your_reddit_client_id>
        REDDIT_CLIENT_SECRET=<your_reddit_client_secret>
        REDDIT_USER_AGENT="StockSentimentApp by u/<your_reddit_username>" # Customize user agent
        OPENROUTER_API_KEY=<your_openrouter_key>
        ```
    *   **(Important):** Obtain keys from the respective services (NewsAPI, Alpha Vantage, Reddit Developer Portal, OpenRouter).
5.  **Navigate to the Django project directory:**
    ```bash
    cd stocksentiment
    ```
6.  **Run database migrations (optional for initial setup with SQLite):**
    ```bash
    python manage.py migrate
    ```
7.  **Run the Django development server:**
    ```bash
    python manage.py runserver
    ```
8.  Open your web browser and navigate to `http://127.0.0.1:8000/`.

## Technology Stack

*   **Backend:** Python, Django
*   **Frontend:** HTML, CSS, Bootstrap 5, JavaScript (minimal currently)
*   **Data Handling:** Pandas, NumPy
*   **Financial Data:** yfinance, Alpha Vantage (planned)
*   **News Data:** NewsAPI
*   **Sentiment Analysis:** VADER (vaderSentiment), LLM (OpenRouter - planned)
*   **Social Media Scraping:** snscrape (Twitter - planned), PRAW (Reddit - planned), feedparser (RSS - planned)
*   **Machine Learning:** Scikit-learn (planned)
*   **Plotting:** Plotly
*   **Environment:** python-dotenv


![image](https://github.com/user-attachments/assets/242d93fc-2d5b-4623-ae85-375bb5b63ea2)

![image](https://github.com/user-attachments/assets/05c6b7ae-a282-4f8e-bdd0-fa9d015fb011)

![image](https://github.com/user-attachments/assets/d7f10675-3f3c-4439-b0a5-5900f933e01d)


![image](https://github.com/user-attachments/assets/271ccb2b-9630-48ce-8818-bbb32b12b731)

![image](https://github.com/user-attachments/assets/5cf540d6-4151-4a6f-8c16-034e9719d145)

![image](https://github.com/user-attachments/assets/1af29c3f-e999-4ccd-9c2e-daf2088ed3cd)





