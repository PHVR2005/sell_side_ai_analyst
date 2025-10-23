import streamlit as st
import analysis_lib as al  # Import our new library
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Sell-Side AI Analyst",
    page_icon="📈",
    layout="wide"
)

# --- Hardcoded NIFTY 50 Stocks ---
# (Dictionary for user-friendly names and correct tickers)
NIFTY_50_STOCKS = {
    "Select a Stock": "",
    "Adani Ports": "ADANIPORTS.NS",
    "Apollo Hospitals": "APOLLOHOSP.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Axis Bank": "AXISBANK.NS",
    "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Bajaj Finserv": "BAJAJFINSV.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "BPCL": "BPCL.NS",
    "Britannia": "BRITANNIA.NS",
    "Cipla": "CIPLA.NS",
    "Coal India": "COALINDIA.NS",
    "Divi's Labs": "DIVISLAB.NS",
    "Dr. Reddy's": "DRREDDY.NS",
    "Eicher Motors": "EICHERMOT.NS",
    "Grasim": "GRASIM.NS",
    "HCL Tech": "HCLTECH.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "HDFC Life": "HDFCLIFE.NS",
    "Hero MotoCorp": "HEROMOTOCO.NS",
    "Hindalco": "HINDALCO.NS",
    "HUL": "HINDUNILVR.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "Infosys": "INFY.NS",
    "ITC": "ITC.NS",
    "JSW Steel": "JSWSTEEL.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "L&T": "LT.NS",
    "LTIMindtree": "LTIM.NS",
    "M&M": "M&M.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Nestlé India": "NESTLEIND.NS",
    "NTPC": "NTPC.NS",
    "ONGC": "ONGC.NS",
    "Power Grid": "POWERGRID.NS",
    "Reliance": "RELIANCE.NS",
    "SBI": "SBIN.NS",
    "SBI Life": "SBILIFE.NS",
   "Sun Pharma": "SUNPHARMA.NS",
    "Tata Consumer": "TATACONSUM.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Tata Steel": "TATASTEEL.NS",
    "TCS": "TCS.NS",
    "Tech Mahindra": "TECHM.NS",
    "Titan": "TITAN.NS",
    "UltraTech Cement": "ULTRACEMCO.NS",
    "UPL": "UPL.NS",
    "Wipro": "WIPRO.NS"
}

# --- Sidebar for User Input ---
st.sidebar.header("Stock Selection")
st.sidebar.markdown("Choose from the NIFTY 50 list or enter a custom ticker.")

selected_stock_name = st.sidebar.selectbox(
    "Select from NIFTY 50:",
    options=NIFTY_50_STOCKS.keys()
)

custom_ticker = st.sidebar.text_input(
    "Or enter custom ticker (e.g., IRFC.NS):"
)

# Determine which ticker to analyze
if custom_ticker:
    ticker_to_analyze = custom_ticker.upper()
else:
    ticker_to_analyze = NIFTY_50_STOCKS[selected_stock_name]

# --- Main Page Display ---
st.title("📈 Sell-Side AI Analyst")
st.markdown("An automated tool to generate a Buy/Sell/Hold recommendation based on fundamentals and market sentiment.")

if st.sidebar.button("Run Analysis"):
    if not ticker_to_analyze:
        st.warning("Please select a stock or enter a custom ticker.")
    else:
        with st.spinner(f"Analyzing {ticker_to_analyze}... This may take a moment."):
            report = al.run_analysis_for_app(ticker_to_analyze)
        
        if report["status"] == "success":
            st.header(f"Report for: {report.get('company_name', report['ticker'])}")
            
            # --- Key Recommendation ---
            st.markdown("---")
            rec = report['recommendation']
            score = report['score']
            
            if rec == "BUY":
                st.metric("Final Recommendation", f"🟩 {rec}", f"Score: {score}")
            elif rec == "SELL":
                st.metric("Final Recommendation", f"🟥 {rec}", f"Score: {score}")
            else:
                st.metric("Final Recommendation", f"🟨 {rec}", f"Score: {score}")
            st.markdown("---")

            # --- Layout for Metrics ---
            col1, col2 = st.columns(2)
            
            # Column 1: Fundamental Metrics
            with col1:
                st.subheader("Key Metrics (Fundamentals)")
                f = report['fundamentals']
                st.metric("P/E Ratio", f"{f.get('pe_ratio'):.2f}" if f.get('pe_ratio') else "N/A")
                st.metric("P/B Ratio", f"{f.get('pb_ratio'):.2f}" if f.get('pb_ratio') else "N/A")
                st.metric("Beta (Risk)", f"{f.get('beta'):.2f}" if f.get('beta') else "N/A")
                st.metric("Market Cap", f"{f.get('market_cap'):,}" if f.get('market_cap') else "N/A")
            
            # Column 2: Sentiment & Drivers
            with col2:
                st.subheader("Analysis & Drivers")
                sentiment = report['sentiment']
                sentiment_emoji = "😐"
                if sentiment > 0.15: sentiment_emoji = "😊"
                if sentiment < -0.15: sentiment_emoji = "😟"
                
                st.metric("Market Sentiment", f"{sentiment_emoji} {sentiment:.4f}")
                
                st.markdown("**Recommendation Drivers:**")
                for rule in report['rules']:
                    st.markdown(f"- {rule}")
        
        elif report["status"] == "error":
            st.error(f"Error analyzing {report['ticker']}: {report['message']}")
            st.warning("Please ensure the ticker is correct (e.g., 'RELIANCE.NS' for Indian stocks) and you have an internet connection.")

else:
    st.info("Select a stock from the left and click 'Run Analysis'.")
