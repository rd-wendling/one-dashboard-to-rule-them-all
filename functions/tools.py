#%%
import os
import glob
import yaml
import zipfile
from datetime import datetime
import numpy as np
import us

#%%
def read_config(input_path = 'config/config.yaml'):
    '''
    Reads a yaml file and converts it to a dict.

    Parameters:
        - input_path: Path to the input yaml file

    Returns:
        - yaml_data: A dictionary of the yaml contents
    '''
    read = open(input_path, 'r')
    data = read.read()
    yaml_data = yaml.safe_load(data)
    return yaml_data

#%%
def find_most_recent_zip(downloads_path):
    '''
    Given a folder path will return the most recent zipped file in it, this was designed to help get CHAS data from HUD. The chrome automation downloads the zipped file, 
    then this finds the most recent downloaded zipped file on the system so we can run this even if file names change.

    Parameters:
        - downloads_path: Path to the folder to seach in, typically downloads folder

    Returns:
        - most_recent_zip: Path to the most recently modified zipped file
    '''
    # Get all zip files in the downloads directory
    zip_files = glob.glob(os.path.join(downloads_path, '*.zip'))
    
    # Return None if no zip files are found
    if not zip_files:
        return None
    
    # Find the most recently modified zip file
    most_recent_zip = max(zip_files, key=os.path.getmtime)
    return most_recent_zip

#%%
def extract_zip(zip_path, extract_to):
    '''
    Given a path to a zipped file/folder this extracts contents from the zip to a specified extract location

    Parameters:
        - zip_path: path to a zipped file/folder
        - extract_to: path to a folder the extracted contents will go
    '''
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    
#%%
def generate_colors(high_color, low_color, num_colors):
    '''
    Given two colors, this will generate a color pallete spectrum between those given colors. The number of discrete colors on the spectrum is a user input.

    Parameters:
        - high_color: Top end of color spectrum, must be hex code
        - low_color: Low end of color spectrum, must be hex code
        - num_colors: Number of discrete colors to be defined in the returned color pallete

    Returns:
        - colors: A list of hex codes even spaced between the high and low end defined colors
    '''
    colors = [high_color]
    for i in range(1, num_colors - 1):
        r = int(np.interp(i, [0, num_colors - 1], [int(high_color[1:3], 16), int(low_color[1:3], 16)]))
        g = int(np.interp(i, [0, num_colors - 1], [int(high_color[3:5], 16), int(low_color[3:5], 16)]))
        b = int(np.interp(i, [0, num_colors - 1], [int(high_color[5:], 16), int(low_color[5:], 16)]))
        colors.append('#{:02x}{:02x}{:02x}'.format(r, g, b))
    colors.append(low_color)
    return colors


#%%
def get_state_abbr(state_name):
    '''
    Given a full state name, the two letter state abbrevation is returned.

    Parameters:
        - state_name: Full name of state, ex. Colorado

    Returns:
        - state.abbr: Two letter state abbrevation, ex. CO
    '''
    state = us.states.lookup(state_name)
    if state is not None:
        return state.abbr
    else: 
        return 'Unknown'  