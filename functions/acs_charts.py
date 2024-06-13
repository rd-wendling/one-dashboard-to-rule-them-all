#%% 
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import numpy as np
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




# State Level Map of Renter Housing Burden
def renter_housing_burden_share_map(df, level_selection):
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

        # Calculate color scale range
        min_value = np.floor(df['Share Renters Housing Burdened'].min() * 20) / 20  
        max_value = np.ceil(df['Share Renters Housing Burdened'].max() * 20) / 20    

        # Create choropleth map using Plotly Express
        fig = px.choropleth_mapbox(
            df, 
            geojson=geojson, 
            locations='MapFIPS',
            featureidkey="properties.StateCounty", 
            mapbox_style='carto-positron',
            zoom=3.225,
            center={'lat': 37.6, 'lon': -95.7129}, #center of usa
            color='Share Renters Housing Burdened',
            color_continuous_scale=colors,
            hover_data={'County': True, 'Share Renters Housing Burdened': ':.2%'}, 
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