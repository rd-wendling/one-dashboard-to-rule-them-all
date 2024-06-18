# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import re


# Function to fetch ZIP codes csv
@st.cache_data()
def read_zipcodes(path):
    df = pd.read_csv(path)
    df['zip'] = df['zip'].astype(str).str.zfill(5)
    df = df[['zip', 'lat', 'lng', 'state_name', 'county_name']]
    return df


# Function to get the meter measurement of each peak on the mountain forecast website which we need to make the forecast request
@st.cache_data()
def get_forecast_meters():
    '''
    This function loops through each leter of the alphabet to get the list of mountains on the mountain forecast website under
    each letter. This function returns a list of dictionaries that contain the Peak Name and Height in Meters as listed on the
    mountain forecast website. We need this because the forecast URLs include both of these so it's information we need later
    to scrape the forecast data for each peak.
    '''
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
@st.cache_data(ttl='6h')
def get_mountain_forecast(peak, meter_height):
    '''
    This function obtains the conditions report at the peak of the mountain input.

    Parameters:
        - peak: Peak name with - for spaces, i.e. Pikes Peak would be Pikes-Peak
        - meter_height: Meter height for the peak, must be exactly as show on mountain-forecast website since we pass it 
                        directly to the URL

    Returns:
        - A list a dictionaries with Peak Name, DOW, Time of Day, and Condition
    '''
    try:
        url = f'https://www.mountain-forecast.com/peaks/{peak}/forecasts/{meter_height}'
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            dow_names = []
            for dow_element in soup.find_all('div', class_='forecast-table-days__name'):
                dow_name = dow_element.get_text()
                dow_names.append(dow_name)

            time_of_day_data = []
            for time_of_day_element in soup.find_all('div', class_=re.compile(r'.*forecast-table__container.*forecast-table__time.*')):  # Regular expression to match class names containing 'forecast-table__container' and 'forecast-table__time' with wildcards
                time_of_day = time_of_day_element.get_text()
                time_of_day_data.append({'Time of Day': time_of_day})

            conditions_data = []
            for conditions_element in soup.find_all('span', class_='forecast-table__phrase forecast-table__phrase--en'):
                conditions = conditions_element.get_text()
                conditions_data.append({'Conditions': conditions})

            # Issues with these sections but wanted to keep the code to revisit later
            # wind_speed_data = []
            # for wind_elements in soup.find_all('div', class_='wind-icon'):
            #     wind_element = wind_elements.find_next('text')
            #     wind_speed = wind_element.get_text()
            #     wind_speed_data.append({'Wind Speed': wind_element})

            # rain_data = []
            # for rain_elements in soup.find_all('div', class_='rain-amount forecast-table__container forecast-table__container--rain'):
            #     rain_element = rain_elements.find_next('span')
            #     rain = rain_element.get_text().replace('—', '0.0')
            #     rain_data.append({'Precip.': rain})
                
            # DOW only obtained once but everything else has 3 values per DOW due to Time of Day, so must fix that so get equal lens
            tripled_dow_names = [{'Day': day} for day in dow_names for _ in range(3)]

            # Same sort of things here just need peak name list of equal len to the rest
            peak_list = [peak.replace('-', ' ')]
            peak_list = [{'Peak': peak} for peak in peak_list for _ in range(len(tripled_dow_names))]

            # Combine each list of data in one
            combined_list = []
            for d1, d2, d3, d4 in zip(peak_list, tripled_dow_names, time_of_day_data, conditions_data):
                combined_dict = {**d1, **d2, **d3, **d4}
                combined_list.append(combined_dict)

            return combined_list

    except Exception as e:
        print(f'Failed to fetch url for {peak}, error: {e}')

# Function to get a list of all 14ers by scraping Wikipedia
@st.cache_data(ttl='1d')
def get_14ers():
    '''
    This function obtains the list of 14ers in Colorado from Wikipedia.
    '''
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