#%%
import pandas as pd
import functions.fourteeners.fourteeners_data_fetch as fd
import streamlit as st
from geopy.distance import geodesic





def calculate_distance(start_lat, start_lon, end_lat, end_lon, units):
    start_point = (start_lat, start_lon)
    end_point = (end_lat, end_lon)
    distance_km = geodesic(start_point, end_point).kilometers
    distance_miles = distance_km * 0.621371

    if units == 'Miles':
        return round(distance_miles, 2)
    elif units == 'Kilometers':
        return round(distance_miles.round, 2)



#%%
def fourteeners():
    # Get zipcode data
    all_zipcodes = fd.read_zipcodes('data/us_zipcodes/uszips.csv')

    # Create dropdown for user location
    zipcode_selection = st.selectbox("**Enter Zipcode**", all_zipcodes['zip'].to_list(), index=None)

    # Filter zipcode data based on selection
    if not zipcode_selection:
        zipcode_selection = '80501' # hardcoded default
    all_zipcodes = all_zipcodes[all_zipcodes['zip']==zipcode_selection].reset_index(drop=True)
    
    user_lat = all_zipcodes['lat'][0]
    user_long = all_zipcodes['lng'][0]

    # Get the 14er data from wikipedia
    data = fd.get_14ers()
    df = pd.DataFrame(data)

    # Get clean up that data
    df['rank'] = df['rank'].astype(int)
    df['name'] = df['name'].str.split('[').str[0].str.strip()                                      # all text left of [
    df['elevation'] = df['elevation'].str.split('m').str[1]                             # all text right of m
    df['elevation'] = df['elevation'].str.replace(r'[^\d.]', '', regex=True).astype(int)    # remove non-numeric chars
    df['location'] = df['location'].str.split('/').str[1] 
    df['lat'] = df['location'].str.split('°N').str[0].str.replace(r'[^\d.]', '', regex=True).astype(float)
    df['long'] = df['location'].str.split('°N').str[1].str.replace(r'[^\d.]', '', regex=True).astype(float) * -1
    df['distance_from_user_miles'] = df.apply(lambda row: calculate_distance(user_lat, user_long, row['lat'], row['long'], 'Miles'), axis=1)
   
    # Get the mountain forecast meter height for each peak
    data = fd.get_forecast_meters()
    mf_df = pd.DataFrame(data)
    mf_df['MF Height'] = mf_df['MF Height'].str.replace(r'[^\d.]', '', regex=True)

    # Get mountain forecast meter height into main df
    df = df.merge(mf_df, how='inner', left_on=['name'], right_on=['MF Peak'])
    df['peak_forecast_name'] = df['name'].str.replace(' ', '-')

    # Get mountain weather forecast
    data = []
    for idx, row in df.iterrows():
        meter_height = row['MF Height']
        peak = row['peak_forecast_name']
        result = fd.get_mountain_forecast(peak, meter_height)
        

    df.rename(columns={'name':'Peak',
                       'elevation': 'Elevation (ft.)',
                       'rank': 'Elevation Rank',
                       'range': 'Range',
                       'distance_from_user_miles': f'Miles from {zipcode_selection}'
                       }, inplace=True)
    df = df[['Peak', 'Elevation (ft.)', 'Elevation Rank', 'Range', f'Miles from {zipcode_selection}']]
    df.sort_values(by=f'Miles from {zipcode_selection}', inplace=True)
    st.dataframe(df, hide_index=True, use_container_width=True)