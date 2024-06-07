#%% 
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import numpy as np
import geopandas as gpd
import functions.tools as t

# Paremeters for generate_colors 
high_color = '#ffffcc'
low_color = '#245d38'
num_colors = 10

colors = t.generate_colors(high_color, low_color, num_colors)

# Load County FIPS code dataset and handle geocoding
geojson_url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
gdf = gpd.read_file(geojson_url)
colorado_gdf = gdf[gdf['STATE'] == '08']
colorado_gdf['StateCounty'] = colorado_gdf['STATE'] + colorado_gdf['COUNTY']
colorado_geojson = colorado_gdf.__geo_interface__

fips_url = 'https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt'
fips_df = pd.read_csv(fips_url, sep=',', header=None, names=['State', 'StateFIPS', 'CountyFIPS', 'County', 'idk'])
fips_df = fips_df[fips_df['State'] == 'CO'][['County', 'CountyFIPS']]

fips_df['StateFIPS'] = '08'
fips_df['CountyFIPS'] = fips_df['CountyFIPS'].astype(str).str.zfill(3)
fips_df['MapFIPS'] = fips_df['StateFIPS'] + fips_df['CountyFIPS']




# Function for Line Charts YoY Cumulative Change (State Level)
def line_chart_yoy_cum_change(df, color_palette):
    vars = ["B19013_001E", "B25058_001E", "B25077_001E"]
    df = df[(df['Variable'].isin(vars)) & (df['NAME']=='Colorado')]
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
                    labels={'Chart Var': col_name, 'Year': 'Year'},
                    color_discrete_sequence=color_palette)

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


# Function for Line Charts YoY (State Level)
def line_chart_yoy(df, location_selection, color_palette, label, y_format, variable=None, rate_flag=None, numerator=None, denominator=None):
    vars = [variable, numerator, denominator]
    vars = list(filter(lambda x: x is not None, vars))
    locs = [location_selection, 'Colorado']
    df = df[df['Variable'].isin(vars) & df['NAME'].isin(locs)].reset_index(drop=True)
    df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index(drop=False)

    if rate_flag == 1:
        df['Chart Var'] = df[numerator] / df[denominator]
    else:
        df['Chart Var'] = df[variable]

    df = df[['NAME', 'Year', 'Chart Var']]
    fig = px.line(df, x=df.Year, y=df['Chart Var'], color='NAME',
                    labels={'Chart Var': label, 'Year': 'Year'},
                    color_discrete_sequence=color_palette)

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
    y_range = [y_min - (0.15 * (y_max - y_min)), y_max + (0.15 * (y_max - y_min))]  

    # Set y-axis range
    fig.update_yaxes(range=y_range)

    # Update layout to adjust margin
    fig.update_layout(yaxis_title=None, xaxis_title=None, margin=dict(t=15, b=0, l=0),
                      legend=dict(
                        orientation='h',
                        y=1.05,
                        x=0
                        )
    )
    
    return fig



# Acs1 Renters Housing Burdened
def housing_burdened_chart(df, own_rent_selection, color_palette):
    if own_rent_selection == 'Renters':
        vars = ['B25106_025E', 'B25106_028E', 'B25106_029E', 'B25106_032E',
                'B25106_033E', 'B25106_036E', 'B25106_037E', 'B25106_040E',
                'B25106_041E', 'B25106_044E']

        # Filter the DataFrame
        df = df[df['Variable'].isin(vars) & (df['NAME'] == 'Colorado')].reset_index(drop=True)

        # Group by 'Year' and calculate housing burden ratios
        df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
        df['< 20k'] = df['B25106_028E'] / df['B25106_025E']
        df['20k - 34k'] = df['B25106_032E'] / df['B25106_029E']
        df['35k - 49k'] = df['B25106_036E'] / df['B25106_033E']
        df['50k - 74k'] = df['B25106_040E'] / df['B25106_037E']
        df['>= 75k'] = df['B25106_044E'] / df['B25106_041E']

    elif own_rent_selection == 'Owners':
        vars = ['B25106_003E', 'B25106_006E', 'B25106_007E', 'B25106_010E', 'B25106_011E', 'B25106_014E',
                'B25106_015E', 'B25106_018E', 'B25106_019E', 'B25106_022E',]

        # Filter the DataFrame
        df = df[df['Variable'].isin(vars) & (df['NAME'] == 'Colorado')].reset_index(drop=True)

        # Group by 'Year' and calculate housing burden ratios
        df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
        df['< 20k'] = df['B25106_006E'] / df['B25106_003E']
        df['20k - 34k'] = df['B25106_010E'] / df['B25106_007E']
        df['35k - 49k'] = df['B25106_014E'] / df['B25106_011E']
        df['50k - 74k'] = df['B25106_018E'] / df['B25106_015E']
        df['>= 75k'] = df['B25106_022E'] / df['B25106_019E']

    cols_to_keep = ['NAME', 'Year', '< 20k', '20k - 34k', '35k - 49k', '50k - 74k', '>= 75k']
    df = df.loc[:, cols_to_keep].drop_duplicates()

    # Create a list of income brackets
    income_brackets = cols_to_keep[2:]

    # Define unique colors for each income bracket
    colors_custom = color_palette

    # Create the figure
    fig = go.Figure()

    # Add traces for each income bracket
    for i, income_bracket in enumerate(income_brackets):
        fig.add_trace(go.Scatter(x=df['Year'],
                                y=df[income_bracket],
                                mode='lines+markers',
                                name=income_bracket,
                                line=dict(color=colors_custom[i]),
                                showlegend=True))

    # Format axes
    fig.update_yaxes(tickformat=".0%", range=(0, 1.1))

    # Add markers with no fill
    fig.update_traces(mode='markers+lines', marker=dict(color='white', line=dict(width=1.5)))

    # Update layout to adjust margin
    fig.update_layout(title='',
                      xaxis_title='',margin=dict(t=35, l=0),
                      legend=dict(
                        orientation='h',
                        y=1.075,
                        x=0
                        ))

    return fig


# Income by Demographic selection
def inc_by_demo(df, inc_metric_selection, color_palette, county=None):
    if county:
        location = county
    else:
        location = 'Colorado'

    if inc_metric_selection == 'Age of Householder':
        title = 'Median Household Income'
        vars = ["B19049_001E", "B19049_002E", "B19049_003E", "B19049_004E", "B19049_005E"]
        rename_dict = {
                        'B19049_001E': 'Overall', 
                        'B19049_002E': 'Under 25',
                        'B19049_003E': '25 to 44',
                        'B19049_004E': '45 to 64',
                        'B19049_005E': '65+',
                        }
        
    elif inc_metric_selection == 'Race of Householder':
        title = 'Median Household Income'
        vars = ["B19013A_001E", "B19013B_001E", "B19013C_001E", "B19013D_001E", "B19013E_001E", "B19013F_001E", "B19013G_001E"]
        rename_dict = {
                        'B19013A_001E': 'White Alone', 
                        'B19013B_001E': 'Black or African American Alone',
                        'B19013C_001E': 'American Indian and Alaska Native Alone',
                        'B19013D_001E': 'Asian Alone',
                        'B19013E_001E': 'Native Hawaiian and Other Pacific Islander Alone',
                        'B19013F_001E': 'Some Other Race Alone',
                        'B19013G_001E': 'Two or More Races',
                        }
        
    elif inc_metric_selection == 'Ethnicity of Householder':
        title = 'Median Household Income'
        vars = ["B19013H_001E", "B19013I_001E"]
        rename_dict = {
                        'B19013H_001E': 'White Alone, Not Hispanic or Latino', 
                        'B19013I_001E': 'Hispanic or Latino',
                        }
        
    elif inc_metric_selection == 'Sex':
        title = 'Median Personal Earnings'
        vars = ["B20002_002E", "B20002_003E"]
        rename_dict = {
                        'B20002_002E': 'Male', 
                        'B20002_003E': 'Female',
                        }
        
    elif inc_metric_selection == 'Tenure':
        title = 'Median Household Income'
        vars = ["B25119_002E", "B25119_003E"]
        rename_dict = {
                        'B25119_002E': 'Homeowner', 
                        'B25119_003E': 'Renter',
                        }
        
    df = df[(df['Variable'].isin(vars)) & (df['NAME']==location)]
    df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
    df = df.rename(columns=rename_dict)

    # Create a list of age brackets
    brackets = df.columns[2:].to_list()

    # Create the figure
    fig = go.Figure()

    # Add traces for each income bracket
    i = 0
    for bracket in brackets:
        fig.add_trace(go.Bar(x=[bracket],
                             y=df[bracket],
                             name=bracket,
                             marker=dict(color=color_palette[brackets.index(bracket)]),
                             text=df[bracket],  # Data labels
                             textposition='auto',
                             texttemplate="$%{y:,.0f}"))  # Automatically position data labels

        i += 1

    # Format axes
    y_max = df[brackets].max().max() * 1.2
    fig.update_yaxes(tickformat="$,.0f", range=(0, y_max), title=title,)

    # Update layout to adjust margin
    fig.update_layout(margin=dict(t=0, l=0),
                      showlegend=False,
                      barmode='group',
                      )

    return fig


# Share Renters vs. Homeowners
def tenure_split_chart(df, location_selection, color_palette):
    tenure_vars = ['B25003_001E', 'B25003_002E', 'B25003_003E']

    # Filter the DataFrame for tenure variables and location
    tenure_df = df[df['Variable'].isin(tenure_vars) & (df['NAME'] == 'Colorado')].reset_index(drop=True)

    # Calculate Share Renting and Share Owning
    tenure_df = tenure_df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
    tenure_df['Share Renting'] = tenure_df['B25003_003E'] / tenure_df['B25003_001E']
    tenure_df['Share Owning'] = tenure_df['B25003_002E'] / tenure_df['B25003_001E']

    # Select required columns and drop duplicates
    tenure_df = tenure_df[['NAME', 'Year', 'Share Renting', 'Share Owning']].drop_duplicates()

    # Create stacked bar chart
    fig = go.Figure()

    # Add trace for Share Renting
    fig.add_trace(go.Bar(
        x=tenure_df['Year'],
        y=tenure_df['Share Renting'],
        name='Share Renting',
        marker_color=color_palette[0],
        text=tenure_df['Share Renting'].apply(lambda x: f"{x:.1%}"),  
        textposition='auto',
    ))

    # Add trace for Share Owning
    fig.add_trace(go.Bar(
        x=tenure_df['Year'],
        y=tenure_df['Share Owning'],
        name='Share Owning',
        marker_color=color_palette[1],
        text=tenure_df['Share Owning'].apply(lambda x: f"{x:.1%}"), 
        textposition='auto',
    ))

    # Update layout for stacked bars
    fig.update_layout(
        barmode='stack',
        xaxis=dict(
            title='',
            tickmode='array',
            tickvals=list(range(tenure_df['Year'].min(), tenure_df['Year'].max() + 1)),  
        ),
        yaxis=dict(
            title='',
            tickformat='.0%'
        ),
        legend_title=''
    )

    # Rotate year labels
    fig.update_xaxes(tickangle=-90)

    # Update layout to adjust margin
    fig.update_layout(yaxis_title=None, xaxis_title=None, margin=dict(t=30, l=0),
                      legend=dict(
                        orientation='h',
                        y=1.06,
                        x=-.025,
                        )
    )

    return fig



# State Level Map of Renter Housing Burden
def renter_housing_burden_share_state_map(df):
    rent_housing_burden_comp_vars = ['B25140_010E', 'B25140_011E']
    rent_housing_burden_comp_df = df[df['Variable'].isin(rent_housing_burden_comp_vars)].reset_index(drop=True)

    # Calculate Share Renting and Share Owning
    rent_housing_burden_comp_df = rent_housing_burden_comp_df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
    rent_housing_burden_comp_df['Share Renters Housing Burdened'] = rent_housing_burden_comp_df['B25140_011E'] / rent_housing_burden_comp_df['B25140_010E']

    # Select required columns and drop duplicates
    rent_housing_burden_comp_df['State'] = df['NAME'].apply(t.get_state_abbr)
    rent_housing_burden_comp_df = rent_housing_burden_comp_df[['State', 'NAME', 'Share Renters Housing Burdened']].drop_duplicates()

    # Calculate color scale range
    min_value = np.floor(rent_housing_burden_comp_df['Share Renters Housing Burdened'].min() * 20) / 20  
    max_value = np.ceil(rent_housing_burden_comp_df['Share Renters Housing Burdened'].max() * 20) / 20    

    # Create choropleth map using Plotly Express
    fig = px.choropleth(
        rent_housing_burden_comp_df, 
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

    return fig, rent_housing_burden_comp_df



# Distribution of Structure Types
def structure_type_split_chart(df, location_selection, acs_type='acs1'):
    color_palette = ['#00000', '#245d38', '#6d3a5d', '#c3002f', '#001970' , '#ffd100'] # hardcoded here so I can control order

    # Define the dwelling type variables of interest
    dwelling_type_vars = ['B25024_001E', 'B25024_002E', 'B25024_003E', 'B25024_004E','B25024_005E', 'B25024_006E',
                          'B25024_007E', 'B25024_008E', 'B25024_009E', 'B25024_010E', 'B25024_011E']

    # Filter the DataFrame for dwelling type variables and location
    if acs_type == 'acs1':
        dwelling_type_df = df[df['Variable'].isin(dwelling_type_vars) & (df['NAME'] == 'Colorado')].reset_index(drop=True)
    elif acs_type == 'acs5':
        dwelling_type_df = df[df['Variable'].isin(dwelling_type_vars) & (df['NAME'] == location_selection)].reset_index(drop=True)

    # Get the most recent year in the DataFrame
    most_recent_year = dwelling_type_df['Year'].max()

    # Filter DataFrame for the most recent year
    dwelling_type_df = dwelling_type_df[dwelling_type_df['Year'] == most_recent_year]

    # Calculate Share Renting and Share Owning
    dwelling_type_df = dwelling_type_df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
    dwelling_type_df['Single Family'] = (dwelling_type_df['B25024_002E'] + dwelling_type_df['B25024_003E']) / dwelling_type_df['B25024_001E']
    dwelling_type_df['Small Multifamily'] = (dwelling_type_df['B25024_004E'] + dwelling_type_df['B25024_005E'])/ dwelling_type_df['B25024_001E']
    dwelling_type_df['Medium Multifamily'] = (dwelling_type_df['B25024_006E'] + dwelling_type_df['B25024_007E']) / dwelling_type_df['B25024_001E']
    dwelling_type_df['Large Multifamily'] = (dwelling_type_df['B25024_008E'] + dwelling_type_df['B25024_009E']) / dwelling_type_df['B25024_001E']
    dwelling_type_df['Mobile Home'] = dwelling_type_df['B25024_010E'] / dwelling_type_df['B25024_001E']
    dwelling_type_df['Boat, RV, Van, etc.'] = dwelling_type_df['B25024_011E'] / dwelling_type_df['B25024_001E']

    # Select required columns and drop duplicates
    dwelling_type_df = dwelling_type_df[['NAME', 'Single Family', 'Small Multifamily', 'Medium Multifamily',
                                         'Large Multifamily', 'Mobile Home', 'Boat, RV, Van, etc.']].drop_duplicates()

    # Create stacked bar chart
    fig = go.Figure()

    # Add traces for each dwelling type
    fig.add_trace(go.Pie(
        labels=dwelling_type_df.columns,
        values=dwelling_type_df.iloc[0],  
        marker_colors=color_palette,
        hole=0.4,  
        hovertemplate='%{label}: %{percent:.1%}',  
    ))

    # Update layout
    fig.update_layout(
        legend=dict(title='', 
                    yanchor='top',
                    y = 1.20,
                    orientation='h',  
                    ),
        margin=dict(t=68, b=50),
    )

    return fig



# County level maps given metric selection
def county_level_map(df, county_map_metric_selection):
    if county_map_metric_selection == 'Share of Renters Housing Burdened':
        format = ':,.2%'
        tick_format = '.0%'
        vars = ['B25140_010E', 'B25140_011E']
        df = df[df['Variable'].isin(vars)].reset_index(drop=True)
        df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
        df[county_map_metric_selection] = df['B25140_011E'] / df['B25140_010E']
        max_rent = None

    elif county_map_metric_selection == 'Median Contract Rent':
        format = ':$,.0f'
        tick_format = '$,.0f'
        vars = ['B25058_001E']
        df = df[df['Variable'].isin(vars)].reset_index(drop=True)
        df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
        df[county_map_metric_selection] = df['B25058_001E'] 
        max_rent = df[county_map_metric_selection].max()

    elif county_map_metric_selection == 'Share of Owners Housing Burdened':
        format = ':,.2%'
        tick_format = '.0%'
        vars = ['B25140_002E', 'B25140_003E']
        df = df[df['Variable'].isin(vars)].reset_index(drop=True)
        df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
        df[county_map_metric_selection] = df['B25140_003E'] / df['B25140_002E']
        max_rent = None

    elif county_map_metric_selection == 'Homeownership Rate':
        format = ':,.2%'
        tick_format = '.0%'
        vars = ['B25003_001E', 'B25003_002E']
        df = df[df['Variable'].isin(vars)].reset_index(drop=True)
        df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
        df[county_map_metric_selection] = df['B25003_002E'] / df['B25003_001E']
        max_rent = None

    elif county_map_metric_selection == 'Vacancy Rate':
        format = ':,.2%'
        tick_format = '.0%'
        vars = ['B25002_001E', 'B25002_003E']
        df = df[df['Variable'].isin(vars)].reset_index(drop=True)
        df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
        df[county_map_metric_selection] = df['B25002_003E'] / df['B25002_001E']
        max_rent = None

    elif county_map_metric_selection == 'Housing Units per Capita':
        format = ':,.2'
        tick_format = '.2'
        vars = ['B25001_001E', 'B01003_001E']
        df = df[df['Variable'].isin(vars)].reset_index(drop=True)
        df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
        df[county_map_metric_selection] = df['B25001_001E'] / df['B01003_001E']
        max_rent = df[county_map_metric_selection].max()

    # Extract county names without ", Colorado"
    df['County'] = df['NAME'].str.split(',').str[0]
    df = df.merge(fips_df, on='County', how='left')

    # Create county choropleth map using Plotly Express
    fig = px.choropleth_mapbox(
        df, 
        geojson=colorado_geojson, 
        locations='MapFIPS',
        featureidkey="properties.StateCounty", 
        mapbox_style='carto-positron',
        zoom=5.9,
        center={'lat': 39.015, 'lon': -105.55},
        color=county_map_metric_selection,
        color_continuous_scale=colors,
        hover_data={'County': True, county_map_metric_selection: format}, 
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
        coloraxis_colorbar=dict(tickformat=tick_format, 
                                len=1,
                                yanchor='top',
                                y=1,
                                ),
        coloraxis_colorbar_title='',
        margin=dict(l=0, r=150, t=0, b=0),
    )

    return fig, df, max_rent




#%% ACS5 Housing Burden by Income Bracket By County
def county_rent_housing_burdened_by_income(df, county_selection, color_palette):
    rent_housing_burden_vars = ['B25106_025E', 'B25106_028E', 'B25106_029E', 'B25106_032E',
                                'B25106_033E', 'B25106_036E', 'B25106_037E', 'B25106_040E',
                                'B25106_041E', 'B25106_044E']
    rent_housing_burden_df = df[df['Variable'].isin(rent_housing_burden_vars) & (df['NAME'] == county_selection)].reset_index(drop=True)

    # Group by 'Year' and calculate housing burden ratios
    rent_housing_burden_df = rent_housing_burden_df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
    rent_housing_burden_df['< 20k'] = rent_housing_burden_df['B25106_028E'] / rent_housing_burden_df['B25106_025E']
    rent_housing_burden_df['20k - 34k'] = rent_housing_burden_df['B25106_032E'] / rent_housing_burden_df['B25106_029E']
    rent_housing_burden_df['35k - 49k'] = rent_housing_burden_df['B25106_036E'] / rent_housing_burden_df['B25106_033E']
    rent_housing_burden_df['50k - 74k'] = rent_housing_burden_df['B25106_040E'] / rent_housing_burden_df['B25106_037E']
    rent_housing_burden_df['>= 75k'] = rent_housing_burden_df['B25106_044E'] / rent_housing_burden_df['B25106_041E']
    cols_to_keep = ['NAME', '< 20k', '20k - 34k', '35k - 49k', '50k - 74k', '>= 75k']
    rent_housing_burden_df = rent_housing_burden_df.loc[:, cols_to_keep].drop_duplicates()

    # Create a list of income brackets
    income_brackets = cols_to_keep[1:]

    # Create the figure
    fig = go.Figure()

    # Add traces for each income bracket
    for income_bracket in income_brackets:
        fig.add_trace(go.Bar(x=[income_bracket],
                             y=rent_housing_burden_df[income_bracket],
                             name=income_bracket,
                             marker=dict(color=color_palette[income_brackets.index(income_bracket)])))

    # Format axes
    fig.update_yaxes(tickformat=".0%", range=(0, 1.1))

    # Update layout to adjust margin
    fig.update_layout(margin=dict(t=0, l=0),
                      showlegend=False,
                      barmode='group'
                      )

    return fig



#%% Generates the county vs state exportable table
def county_vs_state_df(df, county_selection):
    df = df[df['NAME'].isin([county_selection, 'Colorado'])].reset_index(drop=True)
    df = df.pivot_table(index=['NAME', 'Year'], values='Value', columns='Variable').reset_index()
    df2 = pd.DataFrame()

    df2['County'] = df['NAME']
    df2['Population'] = df['B01003_001E'].apply(lambda x: '{:,.0f}'.format(x) if pd.notnull(x) else None)
    df2['Housing Units'] = df['B25001_001E'].apply(lambda x: '{:,.0f}'.format(x) if pd.notnull(x) else None)
    df2['Housing Units per Capita'] = (df['B25001_001E'] / df['B01003_001E']).apply(lambda x: '{:,.3f}'.format(x) if pd.notnull(x) else None)
    df2['Vacancy Rate'] = (df['B25002_003E'] / df['B25002_001E']).apply(lambda x: '{:.2%}'.format(x) if pd.notnull(x) else None)
    df2['Median Household Income'] = df['B19013_001E'].apply(lambda x: '${:,.0f}'.format(x) if pd.notnull(x) else None)
    df2['Median Household Income -- Renters'] = df['B25119_003E'].apply(lambda x: '${:,.0f}'.format(x) if pd.notnull(x) else None)
    df2['Median Contract Rent'] = df['B25058_001E'].apply(lambda x: '${:,.0f}'.format(x) if pd.notnull(x) else None)
    df2['Share of Renters Housing Burdened'] = (df['B25140_011E'] / df['B25140_010E']).apply(lambda x: '{:.2%}'.format(x) if pd.notnull(x) else None)
    df2['Median Household Income -- Owners'] = df['B25119_002E'].apply(lambda x: '${:,.0f}'.format(x) if pd.notnull(x) else None)
    df2['Median Home Value'] = df['B25077_001E'].apply(lambda x: '${:,.0f}'.format(x) if pd.notnull(x) else None)
    df2['Share of Owners Housing Burdened'] = (df['B25140_003E'] / df['B25140_002E']).apply(lambda x: '{:.2%}'.format(x) if pd.notnull(x) else None)
    df2['Homeownership Rate'] = (df['B25003_002E'] / df['B25003_001E']).apply(lambda x: '{:.2%}'.format(x) if pd.notnull(x) else None)

    df2 = pd.melt(df2, id_vars=['County'], value_vars=df2.columns[1:], var_name='Metric', value_name='Value')
    
    # Preserve the original order of metrics
    original_order = ['Population', 'Housing Units', 'Housing Units per Capita', 'Vacancy Rate',
                    'Median Household Income', 'Median Household Income -- Renters',
                    'Median Contract Rent', 'Share of Renters Housing Burdened',
                    'Median Household Income -- Owners', 'Median Home Value', 'Share of Owners Housing Burdened', 
                    'Homeownership Rate']
    df2['Metric'] = pd.Categorical(df2['Metric'], categories=original_order, ordered=True)

    df2 = df2.pivot(index='Metric', columns='County', values='Value').reset_index()
    df2.rename(columns={'Colorado': 'Colorado Overall'}, inplace=True)
    df2 = df2[['Metric', county_selection, 'Colorado Overall']]

    return df2

