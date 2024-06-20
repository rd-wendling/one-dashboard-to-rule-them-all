#%% Import Dependencies
import streamlit as st
import functions.weather.weather_data_fetch as fw
import functions.weather.weather_streamlit as fs
import functions.fourteeners.fourteeners_data_fetch as fd
from datetime import datetime
import base64

# Get Weather Data API Key
weather_api_key = st.secrets["weather_api_key"]

def weather_main():
    # Get zipcode data
    all_zipcodes = fd.read_zipcodes('data/us_zipcodes/uszips.csv')

    # Create dropdown for user location
    location = st.selectbox("**Enter Zipcode**", all_zipcodes['zip'].to_list(), index=None, placeholder="Defaulting to 80501")

    # Filter zipcode data based on selection
    if not location:
        location = '80501' # hardcoded default

    # Add title
    st.write(f"#### Weather Outlook for {location}")

    # Fetch Current Weather data for user's location
    weather_df, condition_df, aqi_df = fw.current_weather_get(weather_api_key, location)

    # Fetch Astronomy data
    date = datetime.now().strftime('%Y-%m-%d')
    astro_df = fw.astronomy_get(weather_api_key, location, date)

    # Fetch 7-Day Forecast
    forecast_df = fw.forecast_weather_get(weather_api_key, location, 7)

    # Get astro df variables set
    moon_phase = astro_df[astro_df['index']=='moon_phase']['astro'].reset_index(drop=True)
    sunrise = astro_df[astro_df['index']=='sunrise']['astro'].reset_index(drop=True)
    sunset = astro_df[astro_df['index']=='sunset']['astro'].reset_index(drop=True)
    moonrise = astro_df[astro_df['index']=='moonrise']['astro'].reset_index(drop=True)
    moonset = astro_df[astro_df['index']=='moonset']['astro'].reset_index(drop=True)
    moon_illum = astro_df[astro_df['index']=='moon_illumination']['astro'].reset_index(drop=True)

    # Grab path to the moon icon we need
    img_path = fw.get_moon_icon_path(moon_phase[0])

    # Read the image file as bytes
    with open(img_path, "rb") as img_file:
        img_bytes = img_file.read()

    # Encode the image bytes as base64
    img_base64 = base64.b64encode(img_bytes).decode()

    # Grab the condition icon img path
    condition_img_path = f"https:{condition_df['icon'][0]}"

    # Loop ober the forecast df to get the HTML we need for each forecast column
    html_list = []
    for i in range(0, 7):
        html = f"""<div id="forecast-col">
                        <p style='padding-top: 0px;'><b>{forecast_df.columns[i]}</b></p>
                        <div style='padding: 0px; margin-top:-15px;'>
                            <img src='https:{forecast_df.iloc[-2, i]}'>
                        </div>
                        <p style='padding-top: 0px;'>{forecast_df.iloc[1, i]} °F</p>
                        <p style='padding-top: 0px;'>{forecast_df.iloc[3, i]} °F</p>
                        <p style='padding-top: 0px;'>{forecast_df.iloc[-7, i]}%</p>
                        <p style='padding-top: 0px;'>{forecast_df.iloc[6, i]} mph</p>
                    </div>
                """
        html_list.append(html)


    # Build the entire weather page with custom HTML, helps given all the formatting we're doing to have more
    # specific control
    st.html(
        f"""
            <div id="weather-page-parent">
                <div id="outlook-astro-parent" style="display: flex; justify-content: center;">
                    <div id="todays-outlook-container">
                        <h2 id="weather-h2">Today's Outlook</h2>
                        <p style='padding-top: 5px; margin-top:5px;'>Current Conditions</p>
                        <div style='display: flex; justify-content: center; padding: 0px; margin-top:-10pt;'">
                            <img src='{condition_img_path}'>
                        </div>
                        <p style='padding: 0px; margin-bottom:15px; margin-top:-5pt;'><b>{condition_df['text'][0]}</b></p>
                        <div style='display: flex; justify-content: space-between;'>
                            <div id="outlook-astro-container-col1">
                                <p style='padding: 0px; text-align:left'>
                                    <b>Temperature:</b> {weather_df['temp_f'][0]} °F <br>
                                    <b>Humidity:</b> {weather_df['humidity'][0]}% <br>
                                    <b>Wind Speed:</b> {weather_df['wind_mph'][0]} mph
                                </p>
                            </div>
                            <div id="outlook-astro-container-col2" style='position: relative;'>
                                <p style='padding: 0px; text-align:left; position:absolute; right:0; top:0''>
                                    <b>Feels Like:</b> {weather_df['feelslike_f'][0]} °F <br>
                                    <b>Visibility:</b> {weather_df['vis_miles'][0]} miles <br>
                                    <b>Wind Gusts:</b> {weather_df['gust_mph'][0]} mph
                                </p>
                            </div>
                        </div>
                    </div>
                    <div id="astro-container">
                        <h2 id="weather-h2">Astronomy</h2>
                        <p style='padding-top: 5px; margin-top:5px;'>{moon_phase[0]}</p>
                        <div style='display: flex; justify-content: center; padding: 0px; margin-top:-4px;'">
                            <img src="data:image/png;base64,{img_base64}" style="width: 38px;">
                        </div>
                        <p style='padding-top: 10px;'><b>Moon Illumination:</b> {moon_illum[0]}%</p>
                        <div style='display: flex; justify-content: space-between;'>
                            <div id="outlook-astro-container-col1">
                                <p style='padding: 0px; text-align:left'>
                                    <b>Sun Rise:</b> {sunrise[0]}<br>
                                    <b>Sun Set:</b> {sunset[0]}
                                </p>
                            </div>
                            <div id="outlook-astro-container-col2">
                                <p style='padding: 0px; text-align:left; position:absolute; right:0; top:0''>
                                    <b>Moon Rise:</b> {moonrise[0]}<br>
                                    <b>Moon Set:</b> {moonset[0]}
                                </p>
                            </div>
                        </div>
                    </div>
                 </div>
                <div id="seven-day-parent">
                    <h2 id="weather-h2" style="padding-bottom: 10px;">7-Day Forecast</h2>
                    <div style="display: flex; justify-content: space-between;">
                        <div id="metric-col">
                            <p style='text-align: left; padding-top: 91px;'><b>High</b></p>
                            <p style='text-align: left; padding-top: 0px;'><b>Low</b></p>
                            <p style='text-align: left; padding-top: 0px;'><b>Chance of Rain</b></p>
                            <p style='text-align: left; padding-top: 0px;'><b>Max Wind Speed</b></p>
                        </div>
                        {"".join(html_list)}
                    </div>
                </div>
            </div>
    """)


    


    