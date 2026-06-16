import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import datetime

# Set up page styling
st.set_page_config(page_title="My Stock Tracker", layout="centered")
st.title("📈 My Personal Stock Tracker")

# --- 1. STATE INITIALIZATION ---
if 'portfolio' not in st.session_state:
    # Default sample data
    st.session_state.portfolio = [
        {"ticker": "AAPL", "shares": 10, "buy_price": 150.0},
        {"ticker": "MSFT", "shares": 5, "buy_price": 300.0}
    ]

# New state for the daily ledger
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# --- 2. SIDEBAR FORMS ---
st.sidebar.header("Manage Data")

# Form 1: Add to Portfolio
with st.sidebar.expander("💼 Add to Current Holdings", expanded=False):
    with st.form("add_stock_form"):
        ticker = st.text_input("Stock Ticker (e.g. AAPL)").upper().strip()
        shares = st.number_input("Number of Shares", min_value=0.1, step=1.0)
        buy_price = st.number_input("Average Buy Price ($)", min_value=0.1, step=1.0)
        submit_portfolio = st.form_submit_button("Add to Portfolio")
        
        if submit_portfolio and ticker:
            st.session_state.portfolio.append({"ticker": ticker, "shares": shares, "buy_price": buy_price})
            st.success(f"Added {ticker}!")

# Form 2: Log Daily Sale/Purchase
with st.sidebar.expander("📝 Log Daily Sale / Purchase", expanded=True):
    with st.form("add_transaction_form"):
        trans_date = st.date_input("Date", datetime.date.today())
        trans_type = st.selectbox("Action", ["Purchase", "Sale"])
        trans_ticker = st.text_input("Stock / Item Ticker").upper().strip()
        party_name = st.text_input("Consignee / Buyer Name")
        trans_shares = st.number_input("Quantity", min_value=0.1, step=1.0)
        trans_price = st.number_input("Price per Unit ($)", min_value=0.1, step=1.0)
        submit_transaction = st.form_submit_button("Log Transaction")

        if submit_transaction and trans_ticker and party_name:
            st.session_state.transactions.append({
                "Date": trans_date,
                "Type": trans_type,
                "Ticker/Item": trans_ticker,
                "Consignee/Buyer": party_name,
                "Quantity": trans_shares,
                "Price ($)": trans_price,
                "Total Value ($)": trans_shares * trans_price
            })
            st.success(f"Logged {trans_type} for {trans_ticker}!")

# --- 3. MAIN DASHBOARD TABS ---
tab1, tab2 = st.tabs(["📊 Portfolio Dashboard", "📝 Daily Ledger (Sales & Purchases)"])

# TAB 1: PORTFOLIO DASHBOARD
with tab1:
    if st.session_state.portfolio:
        total_value = 0.0
        total_cost = 0.0
        display_data = []

        for stock in st.session_state.portfolio:
            try:
                ticker_data = yf.Ticker(stock["ticker"])
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

        total_gain = total_value - total_cost
        total_roi = (total_gain / total_cost) * 100 if total_cost > 0 else 0

        col1, col2 = st.columns(2)
        col1.metric("Total Portfolio Value", f"${total_value:,.2f}")
        col2.metric("Total Gain / Loss", f"${total_gain:,.2f}", f"{total_roi:.2f}%")

        df = pd.DataFrame(display_data)
        st.subheader("📊 Your Holdings")
        st.dataframe(df, use_container_width=True)

        st.subheader("🍰 Portfolio Allocation")
        fig = px.pie(df, values='Current Value', names='Ticker', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("Clear Portfolio"):
            st.session_state.portfolio = []
            st.rerun()
    else:
        st.info("Your portfolio is empty. Add holdings using the sidebar menu!")

# TAB 2: DAILY TRANSACTIONS LEDGER
with tab2:
    st.subheader("Daily Sales & Purchases")
    
    if st.session_state.transactions:
        # Convert transactions list to a dataframe
        df_trans = pd.DataFrame(st.session_state.transactions)
        
        # Display the data table
        st.dataframe(df_trans, use_container_width=True)
        
        # Calculate totals for quick metrics
        total_sales = df_trans[df_trans["Type"] == "Sale"]["Total Value ($)"].sum()
        total_purchases = df_trans[df_trans["Type"] == "Purchase"]["Total Value ($)"].sum()
        
        col_a, col_b = st.columns(2)
        col_a.metric("Total Purchases Logged", f"${total_purchases:,.2f}")
        col_b.metric("Total Sales Logged", f"${total_sales:,.2f}")
        
        if st.button("Clear Daily Ledger"):
            st.session_state.transactions = []
            st.rerun()
    else:
        st.info("No transactions logged yet. Use the sidebar to record a daily sale or purchase!")
