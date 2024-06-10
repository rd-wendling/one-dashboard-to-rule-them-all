#%%
from ftplib import FTP
import os
import pandas as pd
from zipfile import ZipFile
from scipy.stats import norm
import numpy as np

#%%
def download_pums_data(state, year, acs_type):
    '''
    Grabs ACS PUMS data from the Census FTP Server for a given state, year, and acs type. 

    Parameters:
        - state: State to get PUMS data for
        - year: Year to get PUMS data for
        - acs_type: ACS version to get PUMS data for such as ACS1, ACS5, etc.

    Returns:
        - combined_df: A df from all the PUMS files that were downloaded from the server, which are also now stored locally
    '''
    # Connect to the Census FTP server
    ftp = FTP('ftp2.census.gov')
    ftp.login()

    # Define the directory structure on the FTP server
    directory = f'/programs-surveys/acs/data/pums/{year}/{acs_type}/'

    # Change directory to the desired location
    ftp.cwd(directory)

    # List files in the directory
    files = ftp.nlst()

    # Filter files to get the ones for the specified state
    state_files = [file for file in files if state.lower() in file.lower()]

    # Create a directory to store downloaded files
    new_dir = f'../data/pums_{acs_type}/PUMS_{year}_{state}_{acs_type}'
    os.makedirs(new_dir, exist_ok=True)

    # Download files
    for file in state_files:
        file_path = f'{new_dir}/{file}'
        with open(file_path, 'wb') as f:
            ftp.retrbinary(f'RETR {file}', f.write)

    # Close FTP connection
    ftp.quit()

    # Extract CSV file from ZIP archive and read into a DataFrame
    dfs = []
    for file in state_files:
        if file.endswith('.zip'):
            zip_path = f'{new_dir}/{file}'
            with ZipFile(zip_path, 'r') as zip_ref:
                csv_files = [name for name in zip_ref.namelist() if name.endswith('.csv')]
                if csv_files:
                    csv_file = csv_files[0]
                    with zip_ref.open(csv_file) as f:
                        df = pd.read_csv(f, low_memory=False)
                        dfs.append(df)
                else:
                    print(f"No CSV file found in {zip_path}")

    combined_df = pd.concat(dfs, ignore_index=True)

    return combined_df




# %%
def est_moe_sdr(df, data_level, confidence_level=0.90):
    '''
    Calculates an estimate and uses the successive difference replicate (SDR) method
    to aproximate standard errors and obtain a MOE from ACS PUMS data set.

    Parameters:
        - df: A df containing PUMS data
        - data_level: Either Household or Person, PUMS data dictionary will tell you which is correct for each variable
        - confidence_level: Confidence level for MOE, defaults to 90% to align with Census estimates

    Returns:
        - X: Generated estimate
        - margin_of_error: MOE for X at given confidence level
    '''

    if data_level == 'Household':
        weight = 'WGTP'
    elif data_level == 'Person':
        weight = 'PWGTP'

    # Specify the replicate weight columns
    replicate_weight_cols = [f'{weight}{i}' for i in range(1, 81)]  

    # Calculate the full sample estimate (X)
    X = df[weight].sum()

    # Calculate the sum of squared deviations for all replicate weights
    sum_of_squared_deviations = 0
    for col in replicate_weight_cols:
        x_r = df[col].sum()
        result = (x_r - X) ** 2
        sum_of_squared_deviations += result

    # Calculate the standard error (SE(X))
    standard_error = np.sqrt(sum_of_squared_deviations * (4 / 80))

    # Calculate the z-score corresponding to the confidence level
    z_score = norm.ppf((1 + confidence_level) / 2)

    # Calculate the margin of error (MOE)
    margin_of_error = z_score * standard_error

    return X, margin_of_error





#%% Example usage
state = 'CO' 
year = 2022   
acs_type = '1-Year'  

df = download_pums_data(state, year, acs_type)

# %%
