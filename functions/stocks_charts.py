#%%
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import streamlit as st

#%%
def time_series_chart(df):
    # Create a Plotly figure for the time series plot
    fig = go.Figure()

    st.dataframe(df)
    # Add a line trace for the time series data using the DataFrame index
    fig.add_trace(go.Line(x=df.index, y=df['4. close']))

    # Update the layout of the chart
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickformat='%Y-%m-%d',  # Date format for x-axis ticks (optional)
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0)
    )

    return fig