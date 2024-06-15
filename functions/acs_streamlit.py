# %%
import pandas as pd
import functions.acs_data_fetch as cf
import functions.acs_charts as fa
from datetime import datetime
import os
import rwend_tools.utils as ru
import streamlit as st
import us

def get_fips_by_state(state_name):
    state_obj = us.states.lookup(state_name)
    if state_obj:
        return state_obj.fips
    else:
        return None

# Read in acs vars
acs_vars = ru.read_config('config/acs_vars.yaml')

# Set overall census api parameters
api_key = os.environ.get('census_api_key')
year = cf.get_most_recent_acs_year()


def renter_house_burden(level_selection, us_states):
    vars = acs_vars['acs_renter_housing_burden']

    if level_selection == 'State Level':
        # Set run specific census api parameters
        level = 'state:*'
        acs_type = 'acs1'

        # Run ACS Data Fetch
        df = cf.get_acs_data(api_key, vars, level, year, acs_type)

        # Get Chart
        fig, fig_df = fa.renter_housing_burden_share_map(df, level_selection)

        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig, use_container_width=True)
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

    if level_selection == 'County Level':
        # Set run specific census api parameters
        level = 'county:*'
        acs_type = 'acs5'

        # Run ACS Data Fetch
        df = cf.get_acs_data(api_key, vars, level, year, acs_type)

        state_selection = st.selectbox("**Optional State Filter**", us_states, index=None)

        # Get Chart
        if state_selection:
            fig, fig_df = fa.renter_housing_burden_share_map(df, level_selection, state_selection)
        else:
            fig, fig_df = fa.renter_housing_burden_share_map(df, level_selection)

        # Structure Chart and Df Display
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig, use_container_width=True)
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


def yoy_comp_line_charts(state_selection):
    year_max = year
    year_min = year - 10
    year_range2 = st.slider('**Select Year Range**', min_value=year_min, max_value=year_max, value=(year_min, year_max), key='slider_key_2')

    # YoY Line Charts Setup
    line_chart_setup = ru.read_config('config/yoy_comp_line_chart_setup.yaml')
    metric_list = [metric['name'] for metric in line_chart_setup['metrics']]

    col1, col2= st.columns([1, 1])
    with col1:
        metric_selection_left = st.selectbox("**Metric Shown on Left Chart**", metric_list, index=metric_list.index("Housing Units per Capita"))
        filtered_metrics_left = [metric for metric in line_chart_setup['metrics'] if metric['name'] == metric_selection_left]
        metric_left = filtered_metrics_left[0]       

    with col2:
        metric_selection_right = st.selectbox("**Metric Shown on Right Chart**", metric_list, index=metric_list.index("Contract Rent to Income Ratio"))
        filtered_metrics_right = [metric for metric in line_chart_setup['metrics'] if metric['name'] == metric_selection_right]
        metric_right = filtered_metrics_right[0]       

    # Run ACS Data Fetch
    left_vars = [metric_left['details']['variable'], metric_left['details']['numerator'], metric_left['details']['denominator']]
    right_vars = [metric_right['details']['variable'], metric_right['details']['numerator'], metric_right['details']['denominator']]
    
    var_list = left_vars + right_vars
    var_list = [item for item in var_list if item != 'None']
    
    df = pd.DataFrame()
    for loop_year in range(year_range2[0], year_range2[1]):
        df1 = cf.get_acs_data(api_key, var_list, f'state:{get_fips_by_state(state_selection)}', loop_year)
        df2 = cf.get_acs_data(api_key, var_list, 'us:1', loop_year)

        df3 = pd.concat([df1, df2], ignore_index=True)
        df3['Year'] = loop_year
        df = pd.concat([df, df3])

    df.reset_index(inplace=True)

    df['NAME'] = None
    for row in df.index:
        if pd.notna(df['state'][row]):
            df['NAME'][row] = state_selection
        elif df['us'][row] == 1:
            df['NAME'][row] = 'US National Average'

    df = pd.melt(df, id_vars=['NAME', 'Year'], var_name='Variable', value_name='Value')

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




def yoy_cum_change_line_charts(state_selection, year_range1):
    var_list = acs_vars['acs_cum_change_chart']

    df = pd.DataFrame()
    for loop_year in range(year_range1[0], year_range1[1]):
        if state_selection == 'US National Average':
            stagedf = cf.get_acs_data(api_key, var_list, 'us:1', loop_year)
            stagedf.rename(columns={'us': 'NAME'}, inplace=True)
        else:
            stagedf = cf.get_acs_data(api_key, var_list, f'state:{get_fips_by_state(state_selection)}', loop_year)
            stagedf.rename(columns={'state': 'NAME'}, inplace=True)

        stagedf['Year'] = loop_year
        df = pd.concat([df, stagedf])

    df.reset_index(inplace=True, drop=True)
    df = pd.melt(df, id_vars=['NAME', 'Year'], var_name='Variable', value_name='Value')

    fig = fa.line_chart_yoy_cum_change(df, var_list)

    st.markdown(f'###### Cumulative Change in Housing Costs and Incomes since {year_range1[0]}, {state_selection}')
    st.plotly_chart(fig, use_container_width=True)



def housing_terms():
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
     
