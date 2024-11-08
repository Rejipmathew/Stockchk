import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
from datetime import datetime

# Function to fetch stock data with caching
@st.cache_data
def get_stock_data(stock_symbol, start_date, end_date):
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
    if not stock_data.empty:
        return stock_data['Adj Close']
    else:
        st.warning(f"No data found for {stock_symbol}. Please check the symbol.")
        return None

# Function to calculate simple moving averages (SMAs)
def calculate_sma(stock_data, short_window=20, long_window=200):
    short_sma = stock_data.rolling(window=short_window).mean()
    long_sma = stock_data.rolling(window=long_window).mean()
    return short_sma, long_sma

# Function to create an interactive graph with SMAs
def create_stock_graph(stock_data, short_sma, long_sma, title):
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, subplot_titles=[title])

    # Add range selector buttons
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(visible=False),
            type="date"
        )
    )

    # Add traces for stock prices and SMAs
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data.values, mode='lines', name=title), row=1, col=1)
    fig.add_trace(go.Scatter(x=short_sma.index, y=short_sma.values, mode='lines', name='20-day SMA', line=dict(color="#20fc03")), row=1, col=1)
    fig.add_trace(go.Scatter(x=long_sma.index, y=long_sma.values, mode='lines', name='200-day SMA', line=dict(color="#fc0303")), row=1, col=1)

    # Update axis labels
    fig.update_layout(title_text=title)
    fig.update_xaxes(title_text='Date', row=1, col=1)
    fig.update_yaxes(title_text='Price', row=1, col=1)

    return fig

# Main Streamlit app
def main():
    st.title("📈 Stocks Dashboard")

    # List of popular stock symbols
    default_symbols = ["AAPL", "GOOG", "MSFT", "AMZN", "TSLA", "NVDA", "META", "CRM", "JPM", "XOM"]

    # Sidebar inputs for user interaction
    st.sidebar.header("Select Stock and Date Range")
    stock_symbol = st.sidebar.selectbox("Choose a stock symbol", default_symbols)
    start_date = st.sidebar.date_input("Start Date", value=datetime.now().date().replace(year=datetime.now().year - 3))
    end_date = st.sidebar.date_input("End Date", value=datetime.now().date())

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        return

    # Display the most recent update date
    st.text(f"Last Update Date: {pd.to_datetime('today').strftime('%Y-%m-%d')}")

    # Fetch stock data
    stock_data = get_stock_data(stock_symbol, start_date, end_date)
    
    if stock_data is not None:
        # Calculate Simple Moving Averages (SMAs)
        short_sma, long_sma = calculate_sma(stock_data)

        # Display only the last year of data
        stock_data_last_year = stock_data.tail(252)
        short_sma_last_year, long_sma_last_year = short_sma.tail(252), long_sma.tail(252)
        
        # Plot the graph
        st.plotly_chart(create_stock_graph(stock_data_last_year, short_sma_last_year, long_sma_last_year, title=stock_symbol))

if __name__ == "__main__":
    main()
