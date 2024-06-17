#%%
import streamlit as st
import random
import functions.stock_market.stocks_data_fetch as sdf
import functions.stock_market.stocks_charts as sc
import os
import finnhub
import pandas as pd
from datetime import datetime, timedelta
from streamlit_extras.stylable_container import stylable_container

# Get the date variables we'll need
current_date = datetime.now()
two_years_ago = (current_date - timedelta(days=2*365))
one_years_ago = (current_date - timedelta(days=365))
one_years_ago_plus_one_day = (current_date - timedelta(days=364))

# Get API Keys
polygon_api_key = st.secrets["polygon_stock_api_key"]
finnhub_api_key = st.secrets["finnhub_api_key"]
finnhub_client = finnhub.Client(api_key=finnhub_api_key)

# Function to get list of all US Stock symbols
st.cache_data(ttl='1d')
def us_stock_symbols():
    symbols = finnhub_client.stock_symbols('US')
    symbol_df = pd.DataFrame(symbols)
    return symbol_df
symbol_df = us_stock_symbols()

# Function to format data for stock ticker
def stock_ticker_labels(df):
    '''
    Takes a df in the format we get back from fetch_stock_quote and returns metrics in proper string format
    for displaying.

    Parameters:
        - df: The df fetch_stock_quote() returns

    Returns:
        - cp: Current price as dollars
        - delta: Price change from now to previous close in dollars with correct sign (+/-)
        - cp_num: Current price numeric (not formatted string)
    '''
    cp_num = df['current_price']
    cp = f"${df['current_price']:.2f}"

    if df['change_from_prev_close'] < 0:
        delta = df['change_from_prev_close'] * -1
        delta = f"-${delta:.2f}"
    else:
        delta = f"${df['change_from_prev_close']}"

    return cp, delta, cp_num

# Generates the stock tickers
@st.cache_data(ttl='30s')
def stock_ticker(n):
    '''
    Takes a number n and displays that many stock tickers side by side

    Parameters:
        - n: The number of columns/stock tickers to create
    '''
    # All Stock Symbols of S&P500 Stocks
    sp500_symbols = sdf.get_sp500_symbols()

    # Pick 10 at random
    fetch_symbols = random.sample(sp500_symbols, n)
    data = [sdf.fetch_stock_quote(finnhub_client, symbol['symbol']) for symbol in fetch_symbols]

    # Create n columns
    cols = st.columns(n)

    # Loop through columns and fetch_stock_quote() returns to create tickers
    for i, stock in enumerate(data):
        if stock:
            with cols[i % n]:
                for item in fetch_symbols:
                    if item['symbol']==stock['symbol']:
                        stock_name = item['name']
                        break

                label = f"{stock['symbol']}, ({stock_name})"

                cp, delta, cp_num = stock_ticker_labels(stock)
                with stylable_container(
                    key='stock-tickers',
                    css_styles="""
                    [data-testid="stMetric"]{
                        background: #151515;
                        color: white;
                        border-radius: 5pt;
                        padding: 5pt;
                        margin: 0pt
                    }
                    [data-testid="stMetric"] [data-testid="stMetricLabel"]{
                    color: white;
                    }
                    """,
                ):
                    st.metric(label=label, value=cp, delta=delta)
                


# Create the Market Index Time Series section
def market_time_series():
    st.write('')
    st.markdown(f'#### Market Index Hisotry')

    # Create filters side by side using columns
    col1, col2 = st.columns([1, 2])
    with col1:
        # Create radio buttons horizontally
        market = st.radio("", ["Dow Jones Industrial Average", "S&P 500"])
    with col2:
        # Create Year Slider
        year_range = st.slider('', min_value=two_years_ago, max_value=current_date, value=(two_years_ago, current_date), key='slider_markets')
        start_date = year_range[0].strftime('%Y-%m-%d')
        end_date = year_range[1].strftime('%Y-%m-%d')

    # Get the right chart based on radio selection
    st.write('')
    if market == "Dow Jones Industrial Average":
        symbol = 'DIA'
        df = sdf.get_time_series(symbol, polygon_api_key, start_date, end_date)
        fig = sc.time_series_chart(df, title='SPDR Dow Jones Industrial Average ETF (DIA)')
        st.plotly_chart(fig, use_container_width=True)
    elif market == "S&P 500":
        symbol = 'VOO'
        df = sdf.get_time_series(symbol, polygon_api_key, start_date, end_date)
        fig = sc.time_series_chart(df, title='Vanguard S&P 500 ETF (VOO)')
        st.plotly_chart(fig, use_container_width=True)
    st.write('')


# Creates the Selected Stock Summary Section
def selected_stock_summary(symbol_df=symbol_df):
    st.write('')
    st.markdown(f'#### Selected Stock Overview')
    
    # Create the stock selection box with symbol and name
    symbol_df['searchText'] = symbol_df['displaySymbol'] + ' (' + symbol_df['description'] +')'
    stock_selection = st.selectbox("", symbol_df['searchText'], index=None, placeholder="Enter a stock symbol (defaults to MSFT)")
    st.write('')
    
    # Set default stock if none selected yet
    if stock_selection:
        pass
    else:
        stock_selection = "MSFT (MICROSOFT CORP)"

    # Filter down df to selected stock 
    symbol_selection = symbol_df[symbol_df['searchText']==stock_selection]['displaySymbol']
    symbol_selection.reset_index(drop=True, inplace=True)

    # Get Ticker data for the Stock
    stock = sdf.fetch_stock_quote(finnhub_client, symbol_selection)
    cp, delta, cp_num = stock_ticker_labels(stock)

    # Get 52 Week High and Low, and YoY Change
    df = sdf.get_time_series(symbol_selection[0], polygon_api_key, one_years_ago.strftime('%Y-%m-%d'), current_date.strftime('%Y-%m-%d'))
    
    # Create the four metric columns and populate with relevant data
    cols = st.columns(4)
    # Normal ticker
    with cols[0]:
        st.metric(label=stock_selection, value=cp, delta=delta)
    # Price Change Year over Year
    with cols[3]:
        close_last_year = df[df['t']==df['t'].min()]['c']
        yoy_change = cp_num - close_last_year
        yoy_percent_change = yoy_change / close_last_year 
        value = f"${yoy_change[0]:.2f}"

        # Similar to stock_ticker_labels() but different since main value can be negative to not using that function to format here
        if yoy_change[0] < 0:
            value = yoy_change[0] * -1
            value = f"-${value:.2f}"
        else:
            value = f"${yoy_change[0]:.2f}"
        if yoy_percent_change[0] < 0:
            delta_percent = yoy_percent_change[0] * -1
            delta_percent = f"-{delta_percent*100:.2f}%"
        else:
            delta_percent = f"{yoy_percent_change[0]*100:.2f}%"

        # Display metrics
        st.metric(label='Price Change YoY', value=value, delta=delta_percent)
    # 52 Week Low
    with cols[1]:
        year_min = df['l'].min()
        value = f"${year_min:.2f}"
        st.metric(label='52 Week Low', value=value)
    # 52 Week High
    with cols[2]:
        year_max = df['h'].max()
        value = f"${year_max:.2f}"
        st.metric(label='52 Week Max', value=value)
    
    # Candlestick Chart
    st.write('')
    st.markdown(f'##### Candlestick Chart, {symbol_selection[0]}')

    cols = st.columns([1, 98, 1])
    with cols[1]:
        # Create Year Slider
        year_range = st.slider('', min_value=two_years_ago, max_value=current_date, value=(datetime(2024, 3, 1), datetime(2024, 6, 1)), key='slider_stock')
        start_date = year_range[0].strftime('%Y-%m-%d')
        end_date = year_range[1].strftime('%Y-%m-%d')

    df = sdf.get_time_series(symbol_selection[0], polygon_api_key, start_date, end_date)
    fig = sc.candle_stick_chart(df)
    st.plotly_chart(fig, use_container_width=True)


