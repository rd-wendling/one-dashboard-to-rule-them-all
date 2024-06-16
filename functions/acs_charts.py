#%% 
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import rwend_tools.utils as t

#%% Paremeters for generate_colors 
high_color = '#ffffcc'
low_color = '#245d38'
num_colors = 10

colors = t.generate_colors(high_color, low_color, num_colors)


# Load County FIPS code dataset and handle geocoding
geojson_url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
gdf = gpd.read_file(geojson_url)
gdf['StateCounty'] = gdf['STATE'] + gdf['COUNTY']
geojson = gdf.__geo_interface__

fips_url = 'https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt'
fips_df = pd.read_csv(fips_url, sep=',', header=None, names=['State', 'StateFIPS', 'CountyFIPS', 'County', 'idk'])
fips_df['CountyFIPS'] = fips_df['CountyFIPS'].astype(str).str.zfill(3)
fips_df['StateFIPS'] = fips_df['StateFIPS'].astype(str).str.zfill(2)
fips_df['MapFIPS'] = fips_df['StateFIPS'] + fips_df['CountyFIPS']




# Map of Renter Housing Burden
def renter_housing_burden_share_map(df, level_selection, state_selection=None):
    # Calculate Share Renters Housing Burdened
    df['Share Renters Housing Burdened'] = df['B25140_011E'] / df['B25140_010E']
    
    if level_selection == 'State Level':
        df['state'] = df['state'].astype(str).str.zfill(2)
        state_fips_df = fips_df[['State', 'StateFIPS']].drop_duplicates()
        df = df.merge(state_fips_df, how='left', left_on=['state'], right_on=['StateFIPS'])

        # Calculate color scale range
        min_value = np.floor(df['Share Renters Housing Burdened'].min() * 20) / 20  
        max_value = np.ceil(df['Share Renters Housing Burdened'].max() * 20) / 20    

        # Create choropleth map using Plotly Express
        fig = px.choropleth(
            df, 
            locations='State',
            locationmode='USA-states',
            scope='usa', 
            color='Share Renters Housing Burdened',
            color_continuous_scale=colors, 
            labels={'Share Renters Housing Burdened':'Share Renters Housing Burdened'},
            hover_data={'State': True, 'Share Renters Housing Burdened': ':.2%'},  
            range_color=[min_value, max_value],
        )

        fig.update_geos(
            showcoastlines=False,
            showland=False,
            showcountries=False,
            showocean=False,
            showsubunits=True,
            subunitcolor='black',
        )

        fig.update_layout(
            coloraxis_colorbar=dict(tickformat=".0%", 
                                    len=1,
                                    yanchor='top',
                                    y=.98,
                                    x=.95,
                                    ),
            coloraxis_colorbar_title='',
            margin=dict(l=0, r=100, t=0, b=0),
        )

    if level_selection == 'County Level':
        df['state'] = df['state'].astype(str).str.zfill(2)
        df['county'] = df['county'].astype(str).str.zfill(3)
        df['MapFIPS'] = df['state'] + df['county']

        df = df.merge(fips_df, how='left', on=['MapFIPS'])

        if state_selection:
            df = df[df['State']==t.get_state_abbr(state_selection)]

        # Calculate color scale range
        min_value = np.floor(df['Share Renters Housing Burdened'].min() * 20) / 20  
        max_value = np.ceil(df['Share Renters Housing Burdened'].max() * 20) / 20    

        # Create choropleth map using Plotly Express
        fig = px.choropleth(
            df, 
            geojson=geojson, 
            locations='MapFIPS',
            featureidkey="properties.StateCounty", 
            scope='usa',
            color='Share Renters Housing Burdened',
            color_continuous_scale=colors,
            hover_data={'County': True, 'Share Renters Housing Burdened': ':.2%'}, 
        )

        if state_selection=='Alaska':
            fig.update_geos(
                center={"lat": 64, "lon": -150},
                lataxis_range=[50, 73],  
                lonaxis_range=[-180, -129]
            )

        elif state_selection:
            fig.update_geos(
                visible=False,
                fitbounds="locations",
            )

        fig.update_geos(
                showcoastlines=False,
                showland=False,
                showcountries=False,
                showocean=False,
                showsubunits=True,
                subunitcolor='black',
            )

        fig.update_layout(
            coloraxis_colorbar=dict(tickformat=".0%", 
                                    len=1,
                                    yanchor='top',
                                    y=1,
                                    x=1,
                                    ),
            coloraxis_colorbar_title='',
            margin=dict(l=0, r=100, t=15, b=0),
        )

    return fig, df



# Function for Comp Line Charts YoY 
def comp_line_chart_yoy(df, location_selection, label, y_format, variable=None, rate_flag=None, numerator=None, denominator=None):
    vars = [variable, numerator, denominator]
    vars = list(filter(lambda x: x is not None, vars))
    locs = [location_selection, 'US National Average']
    df = df[df['Variable'].isin(vars) & df['NAME'].isin(locs)].reset_index(drop=True)
    df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index(drop=False)

    if rate_flag == 1:
        df['Chart Var'] = df[numerator] / df[denominator]
    else:
        df['Chart Var'] = df[variable]

    df = df[['NAME', 'Year', 'Chart Var']]
    fig = px.line(df, x=df.Year, y=df['Chart Var'], color='NAME',
                    labels={'Chart Var': label, 'Year': 'Year'},)

    # Format axis
    fig.update_yaxes(tickformat=y_format)
    fig.update_xaxes(tickformat="d")

    # Set legend position and rename
    fig.update_layout(legend=dict(title=""))

    # Add markers with no fill
    fig.update_traces(mode='markers+lines', marker=dict(color='white', line=dict(width=1.5)))

    # Calculate y-axis range
    y_min = df['Chart Var'].min()  
    y_max = df['Chart Var'].max()  
    y_range = [y_min - (0.05 * y_min), y_max + (0.05 * y_max)]  

    # Set y-axis range
    #fig.update_yaxes(range=y_range)

    # Update layout to adjust margin
    fig.update_layout(yaxis_title=None, xaxis_title=None, margin=dict(t=15, b=0, l=0),
                      legend=dict(
                        orientation='h',
                        y=1.05,
                        x=0
                        )
    )
    
    return fig



# Function for Line Charts YoY Cumulative Change 
def line_chart_yoy_cum_change(df, vars):

    df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
    df = df.rename(columns={
                            'B19013_001E': 'Median Household Income', 
                            'B25058_001E': 'Median Contract Rent',
                            'B25077_001E': 'Median Home Value',
                            })
    min_year = df['Year'].min()

    def cumulative_change(column):
        return (column - column.iloc[0]) / column.iloc[0]

    cumulative_changes = df.groupby('NAME').transform(cumulative_change)
    cumulative_changes.drop(columns='Year', inplace=True)

    # Concatenate the cumulative changes with the original DataFrame
    df = pd.concat([df['Year'], cumulative_changes], axis=1)
    col_name = f'Cumulative Change since {min_year}'
    df = df.melt(id_vars='Year', var_name='Metric', value_name=col_name)

    fig = px.line(df, x=df.Year, y=df[col_name], color='Metric',
                    labels={'Chart Var': col_name, 'Year': 'Year'},)

    # Format axes
    fig.update_yaxes(tickformat='.0%')
    fig.update_xaxes(tickformat="d")

    # Set legend position and rename
    fig.update_layout(legend=dict(title=""))

    # Add markers with no fill
    fig.update_traces(mode='markers+lines', marker=dict(color='white', line=dict(width=1.5)))

    # Calculate y-axis range
    y_min = df[col_name].min()  
    y_max = df[col_name].max()  
    y_range = [y_min - (0.025 * (y_max - y_min)), y_max + (0.15 * (y_max - y_min))]  

    # Set y-axis range
    fig.update_yaxes(range=y_range)

    # Update layout to adjust margin
    fig.update_layout(yaxis_title=None, xaxis_title=None, margin=dict(t=15, b=50, l=0),
                      legend=dict(
                        orientation='h',
                        y=1.12,
                        x=0
                        )
    )
    
    return fig