# %% Import Dependencies
import pandas as pd
import functions.housing_statistics.acs_data_fetch as cf
import functions.housing_statistics.acs_charts as fa
from datetime import datetime
import os
import rwend_tools.utils as ru
import streamlit as st
import us
import concurrent.futures

# Read in acs vars
acs_vars = ru.read_config('config/acs_vars.yaml')

# Define parameters for api requests
api_key = st.secrets['census_api_key']
year = cf.get_most_recent_acs_year()

# Function to get State FIPS Code from name
def get_fips_by_state(state_name):
    '''
    Returns a US State's FIPS code given a state name.

    Parameters:
        - state_name: Name of state to get FIPS code for

    Returns:
        - FIPS code for state_name
    '''
    state_obj = us.states.lookup(state_name)
    if state_obj:
        return state_obj.fips
    else:
        return None

# Function to display Share of Renter's Housing Burdened Section
def renter_house_burden(level_selection, us_states):
    '''
    Generates the streamlit elements for the Share of Renter's Housing Burdened Section
    of the dashboard.

    Parameters:
        - level_selection: 'State' or 'County', determines the level to generate the map and table at.
        - us_states: List of all US States
    '''
    vars = acs_vars['acs_renter_housing_burden']

    # Creates the Streamlit elements given a State Level user selection
    if level_selection == 'State Level':

        # Run ACS Data Fetch
        level = 'state:*'
        acs_type = 'acs1'
        df = cf.get_acs_data(api_key, vars, level, year, acs_type)

        # Get Chart Fig and Table df
        fig, fig_df = fa.renter_housing_burden_share_map(df, level_selection)

        # Create two columns to show map and table side by side
        col1, col2 = st.columns([2, 1])

        # Map into col1
        with col1:
            st.plotly_chart(fig, use_container_width=True)

        # Df into col2 as a table 
        with col2:
            fig_df = fig_df[['State', 'Share Renters Housing Burdened']].sort_values(by='Share Renters Housing Burdened', ascending=False)
            st.write('')
            st.dataframe(
                fig_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Share Renters Housing Burdened": st.column_config.ProgressColumn(
                        "Share of Renters Housing Burdened",
                        min_value=0,
                        max_value=1,
                    )
                }
            )

    # Creates the Streamlit elements given a County Level user selection
    if level_selection == 'County Level':
        # Run ACS Data Fetch
        level = 'county:*'
        acs_type = 'acs5'
        df = cf.get_acs_data(api_key, vars, level, year, acs_type)

        # Display an optional State Filter to view the County Level data on a state-by-state basis
        state_selection = st.selectbox("**Optional State Filter**", us_states, index=None)

        # Get chart based on if a state was indeed selected
        if state_selection:
            fig, fig_df = fa.renter_housing_burden_share_map(df, level_selection, state_selection)
        else:
            fig, fig_df = fa.renter_housing_burden_share_map(df, level_selection)

        # Create two columns to show map and table side by side
        col1, col2 = st.columns([2, 1])

         # Map into col1
        with col1:
            st.plotly_chart(fig, use_container_width=True)

        # Df into col2 as a table 
        with col2:
            fig_df = fig_df[['State', 'County', 'Share Renters Housing Burdened']].sort_values(by='Share Renters Housing Burdened', ascending=False)
            st.write('')
            st.dataframe(
                fig_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Share Renters Housing Burdened": st.column_config.ProgressColumn(
                        "Share of Renters Housing Burdened",
                        min_value=0,
                        max_value=1,
                    )
                }
            )

# Function to display YoY Comparison Charts Section
def yoy_comp_line_charts(state_selection, us_states, year=year):
    '''
    Generates the streamlit elements for the National Average vs. Select State -- Year over Year Section
    of the dashboard.

    Parameters:
        - state_selection: User's selection of a state to compare YoY to US National Average of given metric
    '''
    # Cols here displays the year slider within the section, without this it spills over a bit horizontally 
    cols = st.columns([1, 2])
    with cols[0]:
         ## State Selection
        state_selection = st.selectbox("**Select State**", us_states, index=us_states.index('Colorado'))
    with cols[1]:
        # Create a year filter as a slider covering the most recent ACS year to 10 years before that
        year_max = year
        year_min = year - 10
        year_range2 = st.slider('**Select Year Range**', min_value=year_min, max_value=year_max, value=(year_min, year_max), key='slider_key_2')

    # Read in our setup yaml and get a list of metrics from it for our metric selection dropdowns
    line_chart_setup = ru.read_config('config/yoy_comp_line_chart_setup.yaml')
    metric_list = [metric['name'] for metric in line_chart_setup['metrics']]

    # Create two columns to show each selected metric's chart side by side
    col1, col2= st.columns([1, 1])

    # Both columns contain a metric selection filter and will then get the metric selected as a str to pass to api request
    with col1:
        metric_selection_left = st.selectbox("**Metric Shown on Left Chart**", metric_list, index=metric_list.index("Housing Units per Capita"))
        filtered_metrics_left = [metric for metric in line_chart_setup['metrics'] if metric['name'] == metric_selection_left]
        metric_left = filtered_metrics_left[0]       
    with col2:
        metric_selection_right = st.selectbox("**Metric Shown on Right Chart**", metric_list, index=metric_list.index("Contract Rent to Income Ratio"))
        filtered_metrics_right = [metric for metric in line_chart_setup['metrics'] if metric['name'] == metric_selection_right]
        metric_right = filtered_metrics_right[0]       

    # Run ACS Data Fetch needed for both charts
    ## Grabbing the three possible metrics from the setup yaml filtered list
    left_vars = [metric_left['details']['variable'], metric_left['details']['numerator'], metric_left['details']['denominator']]
    right_vars = [metric_right['details']['variable'], metric_right['details']['numerator'], metric_right['details']['denominator']]
    
    ## Combine them into a master list and remove any strings=='None'
    var_list = left_vars + right_vars
    var_list = [item for item in var_list if item != 'None']
    
    ## Loop over each year in the year slider and fetch variables we need for the charts at both the state and national level,
    ##  combining into one master df
    dfs = []
    state_fips = get_fips_by_state(state_selection)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks for each year and region
        futures = []
        for region in [f'state:{state_fips}', 'us:1']:
            for year in range(year_range2[0], year_range2[1] + 1):
                future = executor.submit(cf.get_acs_data, api_key, var_list, region, year)
                futures.append((future, region, year))
        for future, region, year in futures:
            try:
                result = future.result()
                if not result.empty:
                    result['Year'] = year
                    result['NAME'] = state_selection if region.startswith('state') else 'US National Average'
                    try:
                        result = result.drop(columns=['state'])
                    except:
                        result = result.drop(columns=['us'])
                    dfs.append(result)
            except Exception as e:
                print(f"An error occurred: {e}")

    df = pd.concat(dfs, ignore_index=True)
    df.reset_index(drop=True, inplace=True)
    

    # Melt the df so it works for our plots
    df = pd.melt(df, id_vars=['NAME', 'Year'], var_name='Variable', value_name='Value')

    # Get the chart the user selected for each column and display it
    with col1:
        left_fig = fa.comp_line_chart_yoy(df, state_selection, metric_left['details']['label'], y_format=metric_left['details']['y_format'], variable=metric_left['details']['variable'] , rate_flag=metric_left['details']['rate_flag'], numerator=metric_left['details']['numerator'], denominator=metric_left['details']['denominator'])
        st.write('')
        st.markdown(f'###### {metric_selection_left}')
        st.plotly_chart(left_fig, use_container_width=True)
    with col2:    
        right_fig = fa.comp_line_chart_yoy(df, state_selection, metric_right['details']['label'], y_format=metric_right['details']['y_format'], variable=metric_right['details']['variable'] , rate_flag=metric_right['details']['rate_flag'], numerator=metric_right['details']['numerator'], denominator=metric_right['details']['denominator'])
        st.write('')
        st.markdown(f'###### {metric_selection_right}')
        st.plotly_chart(right_fig, use_container_width=True)

# Function to display YoY Cumulative Change Section
def yoy_cum_change_line_charts(geolevel, year_range1):
    '''
    Generates the streamlit elements for the National Average vs. Select State -- Year over Year Section
    of the dashboard.

    Parameters:
        - geolevel: User's selection of a geographic level to view metrics for
        - year_range1: User's selection of years to view change over, min year selected here becomes the base year
    '''
    var_list = acs_vars['acs_cum_change_chart']

    # Run ACS Data Fetch 
    ## Loop over each year in the year slider and fetch variables we need for the charts at either the state or national level
    dfs = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks for each year and region (state or US)
        futures = []
        for loop_year in range(year_range1[0], year_range1[1] + 1):
            region = 'us:1' if geolevel == 'US National Average' else f'state:{get_fips_by_state(geolevel)}'
            future = executor.submit(cf.get_acs_data, api_key, var_list, region, loop_year)
            futures.append((future, loop_year))

        for future, loop_year in futures:
            try:
                stagedf = future.result()
                if not stagedf.empty:
                    stagedf['Year'] = loop_year
                    stagedf.rename(columns={'us': 'NAME', 'state': 'NAME'}, inplace=True)
                    dfs.append(stagedf)
            except Exception as e:
                print(f"An error occurred: {e}")

    df = pd.concat(dfs, ignore_index=True)
    df.reset_index(drop=True, inplace=True)

    # Melt the df so it works for our plot
    df = pd.melt(df, id_vars=['NAME', 'Year'], var_name='Variable', value_name='Value')

    # Get the plot fig and display it
    fig = fa.line_chart_yoy_cum_change(df, var_list)
    st.markdown(f'###### Cumulative Change in Housing Costs and Incomes since {year_range1[0]}, {geolevel}')
    st.plotly_chart(fig, use_container_width=True)

# Function to display housing terms and data citiations
def housing_terms():
    st.write('')
    st.write('')
    st.write('#### Terms and Data Citations')
    st.write('')
    st.write('**Housing Burdened:** A household is said to be housing burdened when it spends more than 30% of its income on housing costs.')
    st.write('**Contract Rent:** The monthly rental cost specified in a lease agreement, excluding other rental costs like utilities.')
    st.markdown('''**Data Sources:** <br>
                    <li> U.S. Census Bureau. American Community Survey 5-Year Data: Source for all county level housing data.
                    <li> U.S. Census Bureau. American Community Survey 1-Year Data: Source for state and national level housing data.
             ''', unsafe_allow_html=True
    )
     
