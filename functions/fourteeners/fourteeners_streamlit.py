#%%
import pandas as pd
import functions.fourteeners.fourteeners_data_fetch as fd
import streamlit as st
import functions.tools as t
from geopy.distance import geodesic

# Function to style a df and return it as html, not using it due to issues with streamlit handling styled dfs in st.dataframe 
# so had to do something simpler. Keeping incase that changes. 
def style_df(df):
    styles = {
        'header': 'background-color: #245d38; color: white; font-weight: bold; text-align: center;',
        'even_row': 'background-color: #d0d2d3; color: black;',
        'odd_row': 'background-color: white; color: black;',
        'numeric_columns': 'text-align: right;',
        'text_columns': 'text-align: right;',
    }
    styled_df = df.style \
        .applymap(lambda x: styles['numeric_columns'] if pd.api.types.is_numeric_dtype(x) else styles['text_columns']) \
        .set_table_styles([{
            'selector': 'thead th',
            'props': styles['header']
        }, {
            'selector': 'tr:nth-child(even)',
            'props': styles['even_row']
        }, {
            'selector': 'tr:nth-child(odd)',
            'props': styles['odd_row']
        }, {
            'selector': '.row_heading', 
            'props': 'display: none;'
        },
        {
            'selector': '.blank.level0', 
            'props': 'display: none;'
        }]) \
        .format(precision=2, thousands=',') \
    
    return styled_df.to_html()


# Function to get distance between two geo-cordinates 
def calculate_distance(start_lat, start_lon, end_lat, end_lon, units):
    '''
    This function obtains the distance between two geo-cordinates (lat/long points)

    Parameters:
        - start_lat: Latitude of point A
        - start_lon: Longitude of point A
        - end_lat: Latitude of point B
        - end_lon: Longitude of point B
        - units: Unit of returned distance, can be Miles or Kilometers

    Returns:
        - Distance in selected units as float
    '''
    start_point = (start_lat, start_lon)
    end_point = (end_lat, end_lon)
    distance_km = geodesic(start_point, end_point).kilometers
    distance_miles = distance_km * 0.621371

    if units == 'Miles':
        return round(distance_miles, 2)
    elif units == 'Kilometers':
        return round(distance_miles.round, 2)



# Function to add header
def fourteeners_heading():
    # Add title
    t.write_around_markdown('#### Colorado 14ers by Distance Away', 0, 1)
    st.write("""A fourteener (14er) is a mountain peak with an elevation of at least 14,000 feet. Colorado is home to 53 such peaks.
                Below is a list of all 53 fourteeners in Colorado, sorted by distance away from the zipcode entered, along with condition
                reports for the summit of each peak for both the AM and PM over the next few days. This is something I use to plan which 
                fourteeners to hike and when.""")
    st.write("""Clear conditions are highlighted in green, rainy/snowy conditions in yellow, and stormy in red. This table is scrollable and can be
                sorted by any column if sorting by distance away is not the prefered order.""")


# Function to fetch and display data table
def fourteeners_table():
    # Get zipcode data
    all_zipcodes = fd.read_zipcodes('data/us_zipcodes/uszips.csv')

    # Create dropdown for user location
    zipcode_selection = st.selectbox("**Enter Zipcode**", all_zipcodes['zip'].to_list(), index=None, placeholder="Defaulting to 80501")

    # Filter zipcode data based on selection
    if not zipcode_selection:
        zipcode_selection = '80501' # hardcoded default
    all_zipcodes = all_zipcodes[all_zipcodes['zip']==zipcode_selection].reset_index(drop=True)
    
    # Record lat and long of the zipcode input for distance calc later
    user_lat = all_zipcodes['lat'][0]
    user_long = all_zipcodes['lng'][0]

    # Get the 14er data from wikipedia
    data = fd.get_14ers()
    df = pd.DataFrame(data)

    # Get clean up that wikipedia data
    df['rank'] = df['rank'].astype(int)
    df['name'] = df['name'].str.split('[').str[0].str.strip()                                       # all text left of [
    df['elevation'] = df['elevation'].str.split('m').str[1]                                         # all text right of m
    df['elevation'] = df['elevation'].str.replace(r'[^\d.]', '', regex=True).astype(int)            # remove non-numeric chars
    df['location'] = df['location'].str.split('/').str[1] 
    df['lat'] = df['location'].str.split('°N').str[0].str.replace(r'[^\d.]', '', regex=True).astype(float)
    df['long'] = df['location'].str.split('°N').str[1].str.replace(r'[^\d.]', '', regex=True).astype(float) * -1
    df['distance_from_user_miles'] = df.apply(lambda row: calculate_distance(user_lat, user_long, row['lat'], row['long'], 'Miles'), axis=1) # Distance calculation
   
    # Get the mountain-forecast.com meter height for each peak
    data = fd.get_forecast_meters()
    mf_df = pd.DataFrame(data)
    mf_df['MF Height'] = mf_df['MF Height'].str.replace(r'[^\d.]', '', regex=True)

    # Merge mountain-forecast meter height into main df
    df = df.merge(mf_df, how='inner', left_on=['name'], right_on=['MF Peak'])
    df['peak_forecast_name'] = df['name'].str.replace(' ', '-')

    # Get mountain weather forecast for each peak in the df
    forecast_df = pd.DataFrame()
    for idx, row in df.iterrows():
        meter_height = row['MF Height']
        peak = row['peak_forecast_name']
        data = fd.get_mountain_forecast(peak, meter_height)
        forecast_df = pd.concat([forecast_df, pd.DataFrame(data)])

    # Clean up the returned forecast df
    padding_len = len(str(forecast_df.index.max()))
    forecast_df['OrderHelper'] = forecast_df.index.astype(str).str.zfill(padding_len)
    forecast_df = forecast_df[forecast_df['OrderHelper'].astype(int) < 18]
    forecast_df = forecast_df[forecast_df['Time of Day'] != 'night']
    forecast_df['Day'] = forecast_df['OrderHelper'] + '.' + forecast_df['Day']
    forecast_df['Day and Time'] = forecast_df['Day'] + ', ' + forecast_df['Time of Day']
    forecast_df['Conditions'] = forecast_df['Conditions'].str.title()

    pivot_df = forecast_df.pivot_table(index='Peak', columns='Day and Time', values='Conditions', aggfunc='first').reset_index()
    pivot_df.reset_index(drop=True, inplace=True)
    pivot_df = pivot_df.reindex(sorted(pivot_df.columns), axis=1)
    pivot_df.columns = [col[padding_len+1:] if col != 'Peak' else col for col in pivot_df.columns]
    pivot_cols = [col for col in pivot_df.columns if col != 'Peak']

    # Merge forecast data into main df
    df = df.merge(pivot_df, how='left', left_on='name', right_on='Peak')
    df = df.drop('Peak', axis=1)

    # Rename main df cols for display
    df.rename(columns={'name':'Peak',
                       'elevation': 'Elevation (ft.)',
                       'rank': 'Elevation Rank',
                       'range': 'Range',
                       'distance_from_user_miles': f'Miles from {zipcode_selection}'
                       }, inplace=True)
    
    # Keep only relevant cols and sort df by distance to user
    df = df[['Peak', 'Elevation (ft.)', 'Elevation Rank', 'Range', f'Miles from {zipcode_selection}'] + pivot_cols]
    df.sort_values(by=f'Miles from {zipcode_selection}', inplace=True)

    # Function to apply conditional styling
    def highlight_cells(value):
        if isinstance(value, str): 
            if "Mountain" in value:
                pass
            elif value == 'Clear':
                return 'background-color: #C6EFCE;'
            elif "Rain" in value:
                return 'background-color: #FFEB9C;'
            elif "Snow" in value:
                return 'background-color: #FFEB9C;'
            elif "storm" in value:
                return 'background-color: #FFC7CE;'
        else:
            return ''
        
    # Apply our styling rules
    df_styled = df.style.applymap(highlight_cells)

    # Format entire cols
    df_styled.format({'Elevation (ft.)': '{:,.0f}',
                      f'Miles from {zipcode_selection}': '{:,.2f}'})

    # Display the df
    st.dataframe(df_styled, hide_index=True, use_container_width=True, height=580)
