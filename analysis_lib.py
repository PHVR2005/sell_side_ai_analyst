import yfinance as yf
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import sys

# Ensure VADER lexicon is downloaded (Streamlit compatible)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # This print will show in the terminal when Streamlit starts
    print("Downloading VADER sentiment lexicon...")
    nltk.download('vader_lexicon')

def get_fundamental_data(ticker):
    """Fetches fundamental data for a given ticker."""
    info = ticker.info
    income_stmt = ticker.financials
    
    latest_revenue = None
    if not income_stmt.empty and 'Total Revenue' in income_stmt.index:
        latest_revenue = income_stmt.loc['Total Revenue'].iloc[0]

    return {
        "pe_ratio": info.get('trailingPE'),
        "pb_ratio": info.get('priceToBook'),
        "beta": info.get('beta'),
        "market_cap": info.get('marketCap'),
        "latest_revenue": latest_revenue,
        "company_name": info.get('longName')
    }

def get_market_sentiment(ticker):
    """Fetches news and calculates average sentiment."""
    news = ticker.news
    if not news:
        return 0.0

    analyzer = SentimentIntensityAnalyzer()
    total_sentiment = sum(analyzer.polarity_scores(article['title'])['compound'] for article in news)
    return total_sentiment / len(news)

def generate_recommendation(fundamentals, sentiment):
    """Generates Buy/Sell/Hold recommendation based on rules."""
    score = 0
    rules_triggered = []

    # Sentiment rule
    if sentiment > 0.15:
        score += 40; rules_triggered.append(f"Strong positive sentiment ({sentiment:.2f})")
    elif sentiment < -0.15:
        score -= 40; rules_triggered.append(f"Strong negative sentiment ({sentiment:.2f})")
    else:
        rules_triggered.append(f"Neutral sentiment ({sentiment:.2f})")
    
    # P/E rule
    pe = fundamentals.get('pe_ratio')
    if pe:
        if 0 < pe < 15:
            score += 30; rules_triggered.append(f"Undervalued (Low P/E: {pe:.2f})")
        elif pe > 35:
            score -= 30; rules_triggered.append(f"Overvalued (High P/E: {pe:.2f})")
    else:
        rules_triggered.append("P/E ratio not available")
            
    # P/B rule
    pb = fundamentals.get('pb_ratio')
    if pb:
        if 0 < pb < 1.5:
            score += 15; rules_triggered.append(f"Good value (Low P/B: {pb:.2f})")
        elif pb > 3.0:
            score -= 10; rules_triggered.append(f"Expensive (High P/B: {pb:.2f})")
    else:
        rules_triggered.append("P/B ratio not available")

    # Final "Call"
    if score > 35:
        recommendation = "BUY"
    elif score < -25:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"
        
    return recommendation, score, rules_triggered

def run_analysis_for_app(ticker_symbol):
    """
    New function to run the full analysis and return a
    structured dictionary for the Streamlit app.
    """
    try:
        stock_ticker = yf.Ticker(ticker_symbol)
        
        # 1. Get Fundamentals
        fundamentals = get_fundamental_data(stock_ticker)
        
        # 2. Get Sentiment
        avg_sentiment = get_market_sentiment(stock_ticker)
        
        # 3. Generate Recommendation
        recommendation, score, rules = generate_recommendation(fundamentals, avg_sentiment)
        
        # 4. Return everything in a dictionary
        return {
            "status": "success",
            "ticker": ticker_symbol,
            "company_name": fundamentals.get('company_name'),
            "recommendation": recommendation,
            "score": score,
            "fundamentals": fundamentals,
            "sentiment": avg_sentiment,
            "rules": rules
        }
            
    except Exception as e:
        print(f"Error analyzing {ticker_symbol}: {e}")
        return {
            "status": "error",
            "message": str(e),
            "ticker": ticker_symbol
        }
