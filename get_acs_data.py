# %%
import pandas as pd
from datetime import datetime
import functions.census_fetch as cf
from functions.tools import read_config
from datetime import datetime
import os

#%% Helper function
def census_run_helper(api_key, variables_to_fetch, geographic_level, years_to_fetch, acs_type='acs1', filter=None):
    # Initialize an empty DataFrame to store the combined results
    combined_results = pd.DataFrame()

    # Split the variables list into chunks of 10
    variable_chunks = [variables_to_fetch[i:i+10] for i in range(0, len(variables_to_fetch), 10)]

    # Fetch data and metadata for each chunk of variables
    for chunk in variable_chunks:
        # Add 'NAME' to the current chunk of variables
        chunk = chunk + ['NAME']

        # Fetch data and metadata which contains definitions of the variable codes
        acs1_result_data, acs1_variable_metadata = cf.get_acs_data(api_key, chunk, geographic_level, years_to_fetch, acs_type, filter)

        # Melt the DataFrame
        melted_acs1_result_data = pd.melt(acs1_result_data, id_vars=['NAME', 'Year'], var_name='Variable', value_name='Value')
        melted_acs1_result_data = pd.merge(melted_acs1_result_data, acs1_variable_metadata, how='left', left_on=['Variable', 'Year'], right_on=['variable_name', 'year'])
        melted_acs1_result_data = melted_acs1_result_data[['NAME', 'Year', 'Variable', 'label', 'concept', 'Value']]

        # Concatenate the current chunk's results with the combined results
        combined_results = pd.concat([combined_results, melted_acs1_result_data])

    return combined_results



# Read in user inputs config file
user_inputs = read_config('user_inputs/acs_inputs.yaml')

#%% Fetch ACS 1-Year Data
# Get all years starting from user defined start year up to the current year
current_year = datetime.now().year
years_to_fetch = list(range(user_inputs['acs_start_year'], current_year + 1))
years_to_fetch.remove(2020)

# Set census api parameters
api_key = os.environ.get('census_api_key')



#%% YoY ACS 1
# Path to file we'll write data we obtain to
out_file_path = 'data/acs1/acs1_data_yoy.parquet'
variables_to_fetch = user_inputs['variables_to_fetch']

# State Level
geographic_level = "state:*"
state_acs1_df = census_run_helper(api_key, variables_to_fetch, geographic_level, years_to_fetch)

# US National Level
geographic_level = "us:1"
us_acs1_df = census_run_helper(api_key, variables_to_fetch, geographic_level, years_to_fetch)

# Get both levels into one df
acs1_df = pd.concat([state_acs1_df, us_acs1_df], ignore_index=True)

# Write data out, for now into the actual repo (not typically how we'd do it, but this is a special case)
acs1_df.to_parquet(out_file_path, compression='snappy')




#%% Most recent ACS 1 Year only
# Path to file we'll write data we obtain to
out_file_path = 'data/acs1/acs1_data_recent.parquet'
variables_to_fetch = user_inputs['variables_to_fetch'] + user_inputs['variables_to_fetch_recent']

acs1_df_yoy = pd.read_parquet('data/acs1/acs1_data_yoy.parquet')
year = [acs1_df_yoy['Year'].max()]

#%% State Level
geographic_level = "state:*"
state_acs1_df = census_run_helper(api_key, variables_to_fetch, geographic_level, year)

# US National Level
geographic_level = "us:1"
us_acs1_df = census_run_helper(api_key, variables_to_fetch, geographic_level, year)

# Get both levels into one df
acs1_df = pd.concat([state_acs1_df, us_acs1_df], ignore_index=True)

# Write data out, for now into the actual repo (not typically how we'd do it, but this is a special case)
acs1_df.to_parquet(out_file_path, compression='snappy')






#%% Most recent ACS 5 Year, CO only
# Path to file we'll write data we obtain to
out_file_path = 'data/acs5/acs5_data_recent_co.parquet'
variables_to_fetch = user_inputs['variables_to_fetch_recent'] + user_inputs['variables_to_fetch']

acs1_df_yoy = pd.read_parquet('data/acs1/acs1_data_yoy.parquet')
year = [acs1_df_yoy['Year'].max()]

# County Level
geographic_level = "county:*"
county_acs5_df = census_run_helper(api_key, variables_to_fetch, geographic_level, year, acs_type='acs5', filter='state:08')

# State Level
geographic_level = "state:08"
state_acs5_df = census_run_helper(api_key, variables_to_fetch, geographic_level, year, acs_type='acs5')

# Get both levels into one df
acs5_df = pd.concat([county_acs5_df, state_acs5_df], ignore_index=True)

# Write data out, for now into the actual repo (not typically how we'd do it, but this is a special case)
acs5_df.to_parquet(out_file_path, compression='snappy')

