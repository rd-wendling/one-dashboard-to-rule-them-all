#%%
import requests
import pandas as pd
import streamlit as st

#%%
@st.cache_data
def astronomy_get(api_key, location, date):
    base_url = f"http://api.weatherapi.com/v1/astronomy.json"

    params = {
        "key": api_key,
        "q": location,
        "dt": date,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            data = data['astronomy']

            df = pd.DataFrame(data)  
            df.reset_index(drop=False, inplace=True)

            return df
        except Exception as e:
            print(f"Error processing JSON")
            return pd.DataFrame()
    else:
        print(f"Error fetching data: {response.status_code}")


#%%
def current_weather_get(api_key, location):
    base_url = f"http://api.weatherapi.com/v1/current.json"

    params = {
        "key": api_key,
        "q": location,
        "aqi": "yes",
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            data = data['current']

            keys_to_remove = ['condition', 'air_quality']
            filtered_data = {key: value for key, value in data.items() if key not in keys_to_remove}
            df_current = pd.DataFrame(filtered_data, index=[0])  

            condition_data = data['condition']
            df_condition = pd.DataFrame(condition_data, index=[0])  

            air_quality_data = data['air_quality']
            df_aqi = pd.DataFrame(air_quality_data, index=[0])  
            return df_current, df_condition, df_aqi
        
        except Exception as e:
            print(f"Error processing JSON")
            empty_df = pd.DataFrame()
            return empty_df, empty_df, empty_df
    else:
        print(f"Error fetching data: {response.status_code}")


#%%
def forecast_weather_get(api_key, location, days_out):
    base_url = f"http://api.weatherapi.com/v1/forecast.json"

    params = {
        "key": api_key,
        "q": location,
        "days": days_out,
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            data = data['forecast']['forecastday']

            df = pd.DataFrame(data)
            df = pd.concat([df[['date']], df['day'].apply(pd.Series)], axis=1)
            df = pd.concat([df, df['condition'].apply(pd.Series)], axis=1)

            df.drop(columns=['condition'], inplace=True)
            df.set_index('date', inplace=True)
            transposed_df = df.T

            return transposed_df
        
        except Exception as e:
            print(f"Error processing JSON")
            empty_df = pd.DataFrame()
            return empty_df
    else:
        print(f"Error fetching data: {response.status_code}")




#%%
@st.cache_data
def get_moon_icon_path(moon_phase):
    moon_phase = moon_phase.lower().replace(' ', '_')
    img_path = f'assets/moon_icons/{moon_phase}.png'
    return img_path