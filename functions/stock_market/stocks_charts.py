#%%
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import streamlit as st


#%%
def candle_stick_chart(df):

    formatted_dates = df['t'].dt.strftime('%Y-%m-%d')

    # Create candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=formatted_dates,
                                        open=df['o'],
                                        high=df['h'],
                                        low=df['l'],
                                        close=df['c'],
                                        )
                            ])
    # Calculate y-axis range
    y_min = df['l'].min()  
    y_max = df['h'].max()  
    y_range = [y_min - (0.2 * (y_max - y_min)), y_max + (0.2 * (y_max - y_min))]  
    
    fig.update_layout(xaxis_rangeslider_visible=False,
                      margin=dict(t=25, b=0, l=0, r=0),
                      )
    
    fig.update_yaxes(tickformat='$,.0f',
                     range=y_range)
    
    # Add hover labels to candlestick trace
    fig.update_traces(hoverinfo='text',
                      hovertext=df[['t', 'o', 'h', 'l', 'c']].apply(lambda row: f"<b>Date</b>: {row['t'].strftime('%Y-%m-%d')}<br>"
                                                                                f"<b>Open</b>: ${row['o']:.2f}<br>"
                                                                                f"<b>High</b>: ${row['h']:.2f}<br>"
                                                                                f"<b>Low</b>: ${row['l']:.2f}<br>"
                                                                                f"<b>Close</b>: ${row['c']:.2f}",
                                                                                axis=1))

    
    return fig

#%%
def time_series_chart(df, title):
    # Create a Plotly figure for the time series plot
    fig = go.Figure()

    # Add a line trace for the time series data
    fig.add_trace(go.Line(
        x=df['t'], 
        y=df['c'], 
        hovertemplate=(
            'Date: %{x|%Y-%m-%d}<br>' + 
            'Close Price: $%{y:,.2f}<br>' + 
            '<extra></extra>' 
        )
    ))

    # Update the layout of the chart
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        title={'text':title,
               'x':0,
               'y':1,
               'xanchor': 'left',
               'yanchor': 'top'
               },
        xaxis_tickformat='%Y-%m-%d',  # Date format for x-axis ticks (optional)
        showlegend=False,
        margin=dict(t=25, b=0, l=0, r=0),
    )

    fig.update_yaxes(tickformat='$,.0f')

    return fig