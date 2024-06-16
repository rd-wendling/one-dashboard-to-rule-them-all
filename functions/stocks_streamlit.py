#%%
import streamlit as st
import random
import functions.stocks_data_fetch as sdf
import functions.stocks_charts as sc
import os
import finnhub
import pandas as pd


alphavantage_api_key = os.environ.get('stocks_api_key')
finnhub_api_key = os.environ.get('finnhub_api_key')
finnhub_client = finnhub.Client(api_key=finnhub_api_key)


#%%
def stock_ticker(n):
    # All Stock Symbols of S&P500 Stocks
    sp500_symbols = sdf.get_sp500_symbols()

    # Pick 10 at random
    fetch_symbols = random.sample(sp500_symbols, n)
    data = [sdf.fetch_stock_quote(finnhub_client, symbol['symbol']) for symbol in fetch_symbols]

    # Create 10 columns
    cols = st.columns(n)

    for i, stock in enumerate(data):
        with cols[i % n]:
            for item in fetch_symbols:
                if item['symbol']==stock['symbol']:
                    stock_name = item['name']
                    break

            label = f"{stock['symbol']}, ({stock_name})"

            cp = f"${stock['current_price']:.2f}"

            if stock['change_from_prev_close'] < 0:
                delta = stock['change_from_prev_close'] * -1
                delta = f"-${delta:.2f}"
            else:
                delta = f"${stock['change_from_prev_close']}"
            st.metric(label=label, value=cp, delta=delta)


def market_time_series():
    st.write('')
    st.markdown(f'#### Market Index Hisotry')

    # Create radio buttons horizontally
    market = st.radio("", ["Dow Jones Industrial Average", "S&P 500"])
        
    if market == "Dow Jones Industrial Average":
        symbol = 'DIA'
        df = sdf.get_time_series(symbol, alphavantage_api_key, 'compact').T
        fig = sc.time_series_chart(df)

        st.markdown(f'###### SPDR Dow Jones Industrial Average ETF (DIA)')
        st.plotly_chart(fig, use_container_width=True)

    elif market == "S&P 500":
        symbol = 'VOO'
        df = sdf.get_time_series(symbol, alphavantage_api_key, 'compact').T
        fig = sc.time_series_chart(df)

        st.markdown(f'###### Vanguard S&P 500 ETF (VOO)')
        st.plotly_chart(fig, use_container_width=True)
            