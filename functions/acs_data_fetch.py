#%%
import requests
import pandas as pd
import datetime
import streamlit as st

def get_most_recent_acs_year():
    '''
    Tries calling ACS api until it gets a valid response to find out most recent year available

    Returns:
        - current_year: Most recent ACS year with valid response
    '''
    current_year = datetime.datetime.now().year

    while current_year >= 2000:
        base_url = f"https://api.census.gov/data/{current_year}/acs/acs1"
        response = requests.get(base_url)

        if response.status_code == 200:
            break
        else:
            current_year -= 1
    
    return current_year


@st.cache_data
def get_acs_data(api_key, variables, level, year, acs_type='acs1'):
    '''
    Fetches ACS data from Census API at given level and year for defined variables and ACS type.

    Parameters:
        - api_key: Census API Key
        - variables: A list of ACS variable codes
        - years: Years to get data 
        - acs_type: ACS type, defaults to acs1
        - filter: For "in" parameter, defaults to None

    Returns:
        - result_df: A df with all data from the ACS
    '''

    base_url = f"https://api.census.gov/data/{year}/acs/{acs_type}"

    params = {
        "get": ",".join(variables),
        "for": level,
        "key": api_key,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0]) 
            df = df.apply(pd.to_numeric, errors='ignore')
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

