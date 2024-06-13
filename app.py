#%%
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import functions.acs_charts as fa
import functions.acs_streamlit as ast


#%% Streamlit Setup
st.set_page_config(layout="wide")

# Read in Style.css
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Add Sidebar Filters
dropdown_views = ['Housing Statistics']
view_selection = st.sidebar.selectbox("#### View Selection", dropdown_views)

# Display the page title
st.markdown(
    f"""
    <div class="title-container">
        <div class="title">{view_selection}</div>
    </div>
    """, unsafe_allow_html=True
)

if view_selection == 'Housing Statistics':
    # State vs. County Selection
    level_list = ['State Level', 'County Level']
    level_selection = st.sidebar.selectbox("#### Geographic Level Selection", level_list)

    ast.state_level_renter_house_burden(level_selection)