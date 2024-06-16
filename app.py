#%%
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import functions.acs_charts as fa
import functions.acs_streamlit as ast
import functions.acs_data_fetch as cf
import functions.stocks_streamlit as ss
import us
import time

# Get a list of all US states
us_states = [state.name for state in us.states.STATES]

# Get Most Recently Available ACS Year
year = cf.get_most_recent_acs_year()
year_max = year
year_min = year - 10

#%% Streamlit Setup
st.set_page_config(layout="wide")

# Read in Style.css
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Add Sidebar Filters
dropdown_views = ['Housing Statistics', 'Stock Market']
view_selection = st.sidebar.selectbox("#### View Selection", dropdown_views)



if view_selection == 'Housing Statistics':

    # Display the page title
    st.markdown(
        f"""
        <div class="title-container">
            <div class="title">{view_selection}</div>
        </div>
        """, unsafe_allow_html=True
    )

    # Section 1 
    st.markdown('#### Cumulative Change in Housing Costs and Incomes')
    st.write('')

    col1, col2 = st.columns([1, 2])
    with col1:
        state_selection = st.selectbox("**Select Geographic Level**", ['US National Average'] + us_states)

    with col2:
        year_range1 = st.slider('**Select Year Range**', min_value=year_min, max_value=year_max, value=(year_min, year_max), key='slider_key_1')

    ast.yoy_cum_change_line_charts(state_selection, year_range1)


    # Section 2
    st.write('')
    st.markdown('#### Share of Renters Housing Burdened Map')
    st.write('')

    # State vs. County Selection
    level_list = ['State Level', 'County Level']
    level_selection = st.selectbox("**Geographic Level Selection**", level_list)

    ast.renter_house_burden(level_selection, us_states)

    # Section 3
    st.write('')
    st.markdown(f'#### National Average vs. Select State -- Year over Year')
    st.write('')
    state_selection = st.selectbox("**Select State**", us_states, index=us_states.index('Colorado'))

    ast.yoy_comp_line_charts(state_selection)

    # Final Section
    st.write('')
    ast.housing_terms()


if view_selection == 'Stock Market':
    ss.stock_ticker(6)

    st.sidebar.write('')
    if st.sidebar.button('Refresh Page'):
        st.session_state.clear()

    ss.market_time_series()
