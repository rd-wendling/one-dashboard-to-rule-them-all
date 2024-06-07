# colorado-housing-dashboard
Welcome to my Colorado Housing Dashboard project! This project is a web-based dashboard application built with [Streamlit](https://streamlit.io/), using data from the U.S. Census Bureau's American Community Survey (ACS) 1-year and 5-year estimates, which provide detailed population, income, and housing information.

## Table of Contents
- [Features](#features)
- [Screenshots](#screenshots)
- [Local Installation](#local-installation)

## Features
- **Interactive Visualizations**: Explore and compare data through maps, graphs, and other visual tools.
- **Real-time Data**: This dashboard is fed by the Census Bureau's APIs enabling accurate up tp date access to housing data.
- **User-friendly Interface**: Easy-to-use interface with intuitive controls and ADA compliant visualizations.
- **Open Access**: The code and dashboard are publicly avilable, and all charts and tables can be exported by any user.

## Screenshots

Below is a preview of the kinds of visualizations you will find in this dashbaord:

**1. Share of Renters Housing Burdened by State**
   ![Screenshot1](assets/screenshots/state_by_state_renter_housing_burden.png)
   <br><br>
**2. Colorado Select Housing Metrics Summary**
   ![Screenshot1](assets/screenshots/colorado_summary.png)
   <br><br>
**3. Vacancy Rates by County**
   ![Screenshot1](assets/screenshots/county_level_vac_rate.png)

## Local Installation
To run this dashboard locally, follow these steps:

1. **Clone the Repository**
    ```sh
    git clone https://github.com/Ryanwendling17/colorado-housing-dashboard.git
    cd colorado-housing-dashboard
    ```

2. **Install Dependencies**
    <br>Make sure you have Python installed (this was created using 3.11). Then, install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the Application**
    ```sh
    streamlit run app.py
    ```

Once the application is running, open your web browser and navigate to `http://localhost:8501` to view the dashboard.

### Command Line Options
- `--server.port`: Specify the port to run the application (default is 8501).
- `--server.headless`: Run the server in headless mode (useful for deployment).

