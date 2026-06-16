import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Set up page styling for mobile-friendly view
st.set_page_config(page_title="My Stock Tracker", layout="centered")
st.title("📈 My Personal Stock Tracker")

# 1. Sidebar - Add your Portfolio Holdings
st.sidebar.header("Manage Portfolio")
if 'portfolio' not in st.session_state:
    # Default sample data to show how it works
    st.session_state.portfolio = [
        {"ticker": "AAPL", "shares": 10, "buy_price": 150.0},
        {"ticker": "MSFT", "shares": 5, "buy_price": 300.0}
    ]

# Form to add new stock
with st.sidebar.form("add_stock_form"):
    ticker = st.text_input("Stock Ticker (e.g. AAPL, TSLA)").upper().strip()
    shares = st.number_input("Number of Shares", min_value=0.1, step=1.0)
    buy_price = st.number_input("Average Buy Price ($)", min_value=0.1, step=1.0)
    submit = st.form_submit_button("Add to Portfolio")
    
    if submit and ticker:
        st.session_state.portfolio.append({"ticker": ticker, "shares": shares, "buy_price": buy_price})
        st.success(f"Added {ticker}!")

# 2. Main Dashboard Logic
if st.session_state.portfolio:
    total_value = 0.0
    total_cost = 0.0
    display_data = []

    # Fetch live data for each stock in the loop
    for stock in st.session_state.portfolio:
        try:
            ticker_data = yf.Ticker(stock["ticker"])
            # Get latest closing price
            current_price = ticker_data.history(period="1d")["Close"].iloc[-1]
        except Exception:
            current_price = stock["buy_price"] # Fallback if API fails

        cost = stock["shares"] * stock["buy_price"]
        value = stock["shares"] * current_price
        gain_loss = value - cost
        roi = (gain_loss / cost) * 100 if cost > 0 else 0

        total_value += value
        total_cost += cost

        display_data.append({
            "Ticker": stock["ticker"],
            "Shares": stock["shares"],
            "Buy Price": f"${stock['buy_price']:.2f}",
            "Current Price": f"${current_price:.2f}",
            "Current Value": value,
            "Total ROI": f"{roi:.2f}%"
        })

    # Summary Display Cards
    total_gain = total_value - total_cost
    total_roi = (total_gain / total_cost) * 100 if total_cost > 0 else 0

    col1, col2 = st.columns(2)
    col1.metric("Total Portfolio Value", f"${total_value:,.2f}")
    col2.metric("Total Gain / Loss", f"${total_gain:,.2f}", f"{total_roi:.2f}%")

    # Data Table View
    df = pd.DataFrame(display_data)
    st.subheader("📊 Your Holdings")
    st.dataframe(df, use_container_width=True)

    # Visual Share Chart
    st.subheader("🍰 Portfolio Allocation")
    fig = px.pie(df, values='Current Value', names='Ticker', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    
    # Clear portfolio button
    if st.button("Clear Portfolio"):
        st.session_state.portfolio = []
        st.rerun()
else:
    st.info("Your portfolio is empty. Add stocks using the sidebar menu!")
