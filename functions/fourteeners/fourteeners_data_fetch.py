# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st


# Function to fetch ZIP codes using the Zippopotam.us API
@st.cache_data()
def read_zipcodes(path):
    df = pd.read_csv(path)
    df['zip'] = df['zip'].astype(str).str.zfill(5)
    df = df[['zip', 'lat', 'lng', 'state_name', 'county_name']]
    return df

# Function to get the meter measurement of each peak on the mountain forecast website which we need to make the forecast request
@st.cache_data()
def get_forecast_meters():
    char_range = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    data = []
    for char in char_range:
        url = f'https://www.mountain-forecast.com/countries/United-States/locations/{char}'
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            ul_tag = soup.find('ul', class_='b-list-table')
        
            if ul_tag:
                for li_tag in ul_tag.find_all('li'):
                    parts = li_tag.find_all('span')
                    peak = parts[0].get_text().strip() 
                    height = parts[1].get_text()
                    data.append({'MF Peak': peak, 'MF Height': height})

        else:
            print(f"Error fetching data: {response.status_code}")
    
    return data

# Function to get the meter measurement of each peak on the mountain forecast website which we need to make the forecast request
@st.cache_data()
def get_mountain_forecast(peak, meter_height):
    try:
        url = f'https://https://www.mountain-forecast.com/peaks/{peak}/forecasts/{meter_height}'
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f'Failed to fetch url for {peak}, error: {e}')

# Function to get a list of all 14ers by scraping Wikipedia
@st.cache_data(ttl='1d')
def get_14ers():
    url = 'https://en.wikipedia.org/wiki/List_of_Colorado_fourteeners'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing the S&P 500 symbols
        table = soup.find('table', {'class': 'wikitable sortable'})

        # Extract symbols from the table
        data = []
        for row in table.find_all('tr')[1:]:  
            rank = row.find_all('td')[0].text.strip()  
            name = row.find_all('td')[1].text.strip()
            range = row.find_all('td')[2].text.strip() 
            elevation = row.find_all('td')[3].text.strip() 
            location = row.find_all('td')[6].text.strip()  
            data_dict = {'rank': rank, 'name': name, 'range': range, 'elevation': elevation, 'location': location} 
            data.append(data_dict)

        return data
    else:
        print(f"Error fetching data: {response.status_code}")
        try:
            error_message = response.json()['message']
            print(f"Error message: {error_message}")
        except Exception as e:
            print(f"Error processing JSON for error message: {e}")
        return None