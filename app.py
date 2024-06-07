#%%
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import functions.acs_charts as fa
import base64
from functions.tools import read_config
import time

#%% Custom Color Pallete
color_palette = ['#c3002f', '#001970', '#245d38', '#6d3a5d', '#ffd100', '#7a853b', '#35647e']

#%% Defining some defaults for our filters to start at
location_selection = 'Colorado'
year_range = [2015, 2016]

#%% Read in ACS 1 Data
acs1_yoy_df = pd.read_parquet('data/acs1/acs1_data_yoy.parquet')
acs1_yoy_df['Value'] = pd.to_numeric(acs1_yoy_df['Value']) # Convert 'Value' column to numeric type
acs1_max_year = acs1_yoy_df['Year'].max()
acs1_min_year = acs1_yoy_df['Year'].min()

acs1_recent_df = pd.read_parquet('data/acs1/acs1_data_recent.parquet')
acs1_recent_df['Value'] = pd.to_numeric(acs1_recent_df['Value']) # Convert 'Value' column to numeric type

#%% Read in ACS 5 Data
acs5_recent_co_df = pd.read_parquet('data/acs5/acs5_data_recent_co.parquet')
acs5_recent_co_df['Value'] = pd.to_numeric(acs5_recent_co_df['Value']) 
acs5_max_year = acs5_recent_co_df['Year'].max()

#%% Create View Dropdown List
dropdown_views = ['State Level Summary', 'County Level Summary']

#%% Create County Level Map Metric List
county_map_metric = ['Vacancy Rate', 'Share of Renters Housing Burdened', 'Share of Owners Housing Burdened', 
                     'Median Contract Rent', 'Homeownership Rate', 'Housing Units per Capita']

#%% Create Location Dropdown List 
dropdown_locations = acs1_yoy_df['NAME'].unique().tolist()

#%% Create Inc Demographic cut Dropdown List
inc_demo_list = ['Age of Householder', 'Sex', 'Race of Householder', 'Ethnicity of Householder', 'Tenure']

#%% Streamlit Setup
st.set_page_config(layout="wide")

# Read in Style.css
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Define the path to Logo image
image_path = "assets/stock_colorado_logo.jpg"

# Read the image file as bytes
with open(image_path, "rb") as img_file:
    img_bytes = img_file.read()

# Encode the image bytes as base64
img_base64 = base64.b64encode(img_bytes).decode()

# Display the title with the image on the right
st.markdown(
    f"""
    <div class="title-container">
        <div class="title">Colorado Housing Statistics</div>
        <div class="image-container">
            <img src="data:image/png;base64,{img_base64}" alt="Image" class="logo-img" style="height: 100%; width: auto; border: 1px solid white;">
        </div>
    </div>
    <br><br><br>
    """,
    unsafe_allow_html=True
)

# Add Sidebar Filters
view_selection = st.sidebar.selectbox("#### View Selection", dropdown_views, index=dropdown_views.index("State Level Summary"))

if view_selection == 'State Level Summary':
    st.sidebar.markdown('')
    year_range = st.sidebar.slider('#### Select Year Range', min_value=int(acs1_yoy_df['Year'].min()), max_value=int(acs1_yoy_df['Year'].max()), value=(int(acs1_yoy_df['Year'].min()), int(acs1_yoy_df['Year'].max())))
    st.sidebar.markdown('<br><br><br>', unsafe_allow_html=True)
    st.sidebar.write(f'**Data Source:** U.S. Census Bureau. American Community Survey 1-Year Data ({acs1_min_year} - {acs1_max_year})')
elif view_selection == 'County Level Summary':
    st.sidebar.markdown('')
    county_map_metric_selection = st.sidebar.selectbox("#### Metric Shown on Map", county_map_metric, index=county_map_metric.index("Vacancy Rate"))
    st.sidebar.markdown('<br><br><br>', unsafe_allow_html=True)
    st.sidebar.write(f'**Data Source:** U.S. Census Bureau. American Community Survey 5-Year Data ({acs5_max_year})')


#%% Filter df from year range slider
acs1_yoy_df = acs1_yoy_df[(acs1_yoy_df['Year'] >= year_range[0]) & (acs1_yoy_df['Year'] <= year_range[1])]

#%% Create some of the Acs1 Charts
tenure_split = fa.tenure_split_chart(acs1_yoy_df, location_selection, color_palette)
state_map, rent_housing_burden_comp_df = fa.renter_housing_burden_share_state_map(acs1_recent_df)
unit_dist_by_struc_type_chart = fa.structure_type_split_chart(acs1_yoy_df, location_selection)
cumulative_change = fa.line_chart_yoy_cum_change(acs1_yoy_df, color_palette)


#%% Streamlit App Layout
# Tab 1, Statewide Summary
if view_selection == 'State Level Summary':
    # Top Section with State by State Map and df
    st.markdown('#### Share of Renters Housing Burdened by State')
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(state_map, use_container_width=True)
    with col2:
        st.write("")
        rent_housing_burden_comp_df_clean = rent_housing_burden_comp_df[['NAME', 'Share Renters Housing Burdened']].sort_values(by='Share Renters Housing Burdened', ascending=False)
        rent_housing_burden_comp_df_clean['Share Renters Housing Burdened'] = (rent_housing_burden_comp_df_clean['Share Renters Housing Burdened'] * 100).round(2).astype(str) + '%'
        st.dataframe(rent_housing_burden_comp_df_clean,
                        column_order=('NAME', 'Share Renters Housing Burdened'),
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                        "NAME": st.column_config.TextColumn(
                            "States",
                        ),
                        "Share Renters Housing Burdened": st.column_config.ProgressColumn(
                            "Share of Renters Housing Burdened",
                            min_value=0,
                            max_value=1,
                            )}
                        )
    st.write('')
    st.write('')
    st.write('')

    # Next section with 3 charts side by side
    st.markdown('#### Colorado at a Glance')
    st.write('')
    st.write('')
    
    # Next section with 2 charts side by side
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f'##### Income by Demographic Selection')
        inc_metric_selection = st.selectbox("", inc_demo_list, index=inc_demo_list.index("Age of Householder"))
        inc_by_demo = fa.inc_by_demo(acs1_recent_df, inc_metric_selection, color_palette)
        st.plotly_chart(inc_by_demo, use_container_width=True)
    with col2:
        st.markdown(f'##### Share Housing Burdened per Income Bracket by Tenure Selection')
        rent_own_selection = st.selectbox("", ['Renters', 'Owners'], index=['Renters', 'Owners'].index('Renters'))
        housing_burden_inc = fa.housing_burdened_chart(acs1_yoy_df, rent_own_selection, color_palette)
        st.plotly_chart(housing_burden_inc, use_container_width=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown(f'##### Share Owning vs. Renting')
        st.plotly_chart(tenure_split, use_container_width=True)
    with col2:
        st.markdown(f'##### Housing Cost Change vs. Income')
        st.plotly_chart(cumulative_change, use_container_width=True)
    with col3:
        st.markdown(f'##### Housing Units Distribution by Structure Type')
        st.plotly_chart(unit_dist_by_struc_type_chart, use_container_width=True)

    # Bottom section of YoY Line Charts
    st.markdown(f'#### Colorado vs. Comparison -- Year over Year')
    st.write('')
    location_selection = st.selectbox("**Select Comparison**", dropdown_locations, index=dropdown_locations.index("United States"))

    # YoY Line Charts Setup
    line_chart_setup = read_config('user_inputs/yoy_line_chart_setup.yaml')
    metric_list = [metric['name'] for metric in line_chart_setup['metrics']]

    col1, col2= st.columns([1, 1])
    with col1:
        metric_selection_left = st.selectbox("**Metric Shown on Left Chart**", metric_list, index=metric_list.index("Housing Units per Capita"))
        filtered_metrics_left = [metric for metric in line_chart_setup['metrics'] if metric['name'] == metric_selection_left]
        metric_left = filtered_metrics_left[0]       
        left_fig = fa.line_chart_yoy(acs1_yoy_df, location_selection, color_palette, metric_left['details']['label'], y_format=metric_left['details']['y_format'], variable=metric_left['details']['variable'] , rate_flag=metric_left['details']['rate_flag'], numerator=metric_left['details']['numerator'], denominator=metric_left['details']['denominator'])
        st.write('')
        st.markdown(f'###### {metric_selection_left}')
        st.plotly_chart(left_fig, use_container_width=True)
    with col2:
        metric_selection_right = st.selectbox("**Metric Shown on Right Chart**", metric_list, index=metric_list.index("Contract Rent to Income Ratio"))
        filtered_metrics_right = [metric for metric in line_chart_setup['metrics'] if metric['name'] == metric_selection_right]
        metric_right = filtered_metrics_right[0]       
        right_fig = fa.line_chart_yoy(acs1_yoy_df, location_selection, color_palette, metric_right['details']['label'], y_format=metric_right['details']['y_format'], variable=metric_right['details']['variable'] , rate_flag=metric_right['details']['rate_flag'], numerator=metric_right['details']['numerator'], denominator=metric_right['details']['denominator'])
        st.write('')
        st.markdown(f'###### {metric_selection_right}')
        st.plotly_chart(right_fig, use_container_width=True)

    # Data note
    st.markdown('<br><br>', unsafe_allow_html=True)
    st.write(f'''**Data Note:** This tab utilizes American Community Survey (ACS) 1-Year Data in order to present time-series charts at the State level. Any visualization on this tab 
             not showing a time-series trend is using data only from the most recent ACS 1-Year dataset ({acs1_max_year}).''')



# Tab 2, County Level Summary
elif view_selection == 'County Level Summary':
    st.markdown(f'#### {county_map_metric_selection} by County')
    fig, df, max_rent = fa.county_level_map(acs5_recent_co_df, county_map_metric_selection)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write("")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.write("")
        # Clean up df to display in dashboard
        df = df[['County', county_map_metric_selection]].sort_values(by=county_map_metric_selection, ascending=False)
        if max_rent:
            max = max_rent
            if county_map_metric_selection == 'Median Contract Rent':
                format = "$%.0f"
            else:
                format = "%.3f"
        else:
            max = 1
            format = None

        st.dataframe(df,
                        column_order=('County', county_map_metric_selection),
                        hide_index=True,
                        use_container_width=True,
                        column_config={"County": st.column_config.TextColumn("County",),
                                    county_map_metric_selection: st.column_config.ProgressColumn(county_map_metric_selection, min_value=0, max_value=max, format=format)}
                    )

    # County Selection Section
    county_selection_list = acs5_recent_co_df['NAME'].unique().tolist()
    county_selection_list.remove('Colorado')
    st.markdown('<br>', unsafe_allow_html=True)
    st.write('')

    st.markdown(f'#### County Selection')
    county_selection = st.selectbox('', county_selection_list)

    # Create line charts with county selection as filter
    county_rent_housing_burdened_by_income_chart = fa.county_rent_housing_burdened_by_income(acs5_recent_co_df, county_selection, color_palette)
    county_structure_type_split_chart = fa.structure_type_split_chart(acs5_recent_co_df, county_selection, 'acs5')

    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("")
        st.markdown(f'##### Housing Units Distribution by Structure Type')
        st.plotly_chart(county_structure_type_split_chart, use_container_width=True)

        st.markdown(f'##### Income by Demographic Selection')
        inc_metric_selection = st.selectbox("", inc_demo_list, index=inc_demo_list.index("Age of Householder"))
        inc_by_demo = fa.inc_by_demo(acs5_recent_co_df, inc_metric_selection, color_palette, county_selection)
        st.plotly_chart(inc_by_demo, use_container_width=True)

    with col2:
        st.write("")
        st.markdown(f'##### Renter Housing Burden Rate per Income Bracket')
        st.plotly_chart(county_rent_housing_burdened_by_income_chart, use_container_width=True)
        
        st.markdown(f'##### {county_selection} vs. State Averages')
        st.write("")
        df = fa.county_vs_state_df(acs5_recent_co_df, county_selection)
        height = len(df) * 38
        st.dataframe(df, hide_index=True, use_container_width=True, height=height,)


    # Data note about ACS5
    st.markdown('<br><br>', unsafe_allow_html=True)
    st.write(f'''**Data Note:** This tab utilizes American Community Survey (ACS) 5-Year Data in order to present metrics at the County level. While the primary reporting year for this data is 
                2022, it includes data collected over the preceding four years. Variations may arise between metrics such as Median Contract Rent for Colorado Statewide on this tab and the Statewide 
                Summary tab for {acs5_max_year}, which uses ACS 1-Year Data. We recommend prioritizing metrics derived from ACS 1-Year Data when both options 
                are available.''')


