# %%
import pandas as pd
import functions.acs_data_fetch as cf
import functions.acs_charts as fa
from datetime import datetime
import os
import rwend_tools.utils as ru
import streamlit as st

# Read in acs vars
acs_vars = ru.read_config('config/acs_vars.yaml')

# Set overall census api parameters
api_key = os.environ.get('census_api_key')
year = cf.get_most_recent_acs_year()

def state_level_renter_house_burden(level_selection):
    vars = acs_vars['acs_renter_housing_burden']

    if level_selection == 'State Level':
        # Set run specific census api parameters
        level = 'state:*'
        acs_type = 'acs1'

        # Run ACS Data Fetch
        df = cf.get_acs_data(api_key, vars, level, year, acs_type)

        # Get Chart
        fig, fig_df = fa.renter_housing_burden_share_map(df, level_selection)

        st.markdown('#### Share of Renters Housing Burdened by State')
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

        # Get Chart
        fig, fig_df = fa.renter_housing_burden_share_map(df, level_selection)

        st.markdown('#### Share of Renters Housing Burdened by State')
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