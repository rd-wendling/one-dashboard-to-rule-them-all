# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# Function to get time series data on a give stock over a given timeframe from polygon api
@st.cache_data
def get_time_series(symbol, api_key, start_date, end_date):
    '''
    Takes a stock symbol, polygon api key, start date and end date, returns a df with daily 
    stock data on given stock over defined timeframe.

    Parameters:
        - symbol: Stock symbol (i.e. APPL)
        - api_key: Polygon api key
        - start_date
        - end_date

    Returns:
        - Pandas df with daily stock data
    '''
    base_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/day/{start_date}/{end_date}"
    params = {
        "sort": "asc",
        "adjusted": "true",
        "apikey": api_key,
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            df = pd.DataFrame(data['results'])
            df['t'] = pd.to_datetime(df['t'], unit='ms')
            return df
        except Exception as e:
            print(f"Error: {e}")
            return pd.DataFrame()
    else:
        print(f"Error fetching data: {response.status_code}")
        try:
            error_message = response.json()['message']
            print(f"Error message: {error_message}")
        except Exception as e:
            print(f"Error processing JSON for error message: {e}")
        return pd.DataFrame()


# Function to get current stock quote of selected stock using finnhub
def fetch_stock_quote(finnhub_client, symbol):
    '''
    Takes a finnhub_client and stock symbol. Initialize the finnhub_client and pass it to the function. Returns
    current stock quote.

    Parameters:
        - finnhub_client
        - symbol: Stock symbol (i.e. APPL)

    Returns:
        - Stock quote dictionary 
    '''
    try:
        quote = finnhub_client.quote(symbol)
        quote = {
            'symbol': symbol,
            'current_price': quote['c'],
            'change_from_prev_close': quote['d'],
            'daily_high': quote['h'],
            'daily_low': quote['l'],
        }
        return quote
    except Exception as e:
        print(f'Error fetching stock quote. Error: {e}')
        return None


# Function to a list of all S&P 500 Stocks by scraping Wikipedia
@st.cache_data(ttl='1d')
def get_sp500_symbols():
    # Grab Wikipedia article with all the S&P 500 stocks
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing the S&P 500 symbols
        table = soup.find('table', {'id': 'constituents'})

        # Extract symbols from the table
        symbols = []
        for row in table.find_all('tr')[1:]:  
            symbol = row.find_all('td')[0].text.strip()  
            name = row.find_all('td')[1].text.strip() 
            data = {'symbol': symbol, 'name': name} 
            symbols.append(data)

        return symbols
    else:
        print(f"Error fetching data: {response.status_code}")
        try:
            error_message = response.json()['message']
            print(f"Error message: {error_message}")
        except Exception as e:
            print(f"Error processing JSON for error message: {e}")
        return None
