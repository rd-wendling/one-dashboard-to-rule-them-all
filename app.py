#%% Import Dependencies
import streamlit as st
st.set_page_config(layout="wide")
import functions.housing_statistics.acs_streamlit as ast
import functions.housing_statistics.acs_data_fetch as cf
import functions.stock_market.stocks_streamlit as ss
import functions.news.news_streamlit as ns
import functions.tools as tl
import functions.fourteeners.fourteeners_streamlit as fs
import functions.weather.weather_streamlit as ws
import us

# Function to get a list of all US states
st.cache_data(ttl='1d')
def us_states_list():
    us_states = [state.name for state in us.states.STATES]
    return us_states
us_states = us_states_list()

# Get Most Recently Available ACS Year
year_max = cf.get_most_recent_acs_year()
year_min = year_max - 10

# Read in Style.css
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Add Sidebar Filters
dropdown_views = ['Weather', 'Stock Market', 'News and Research', 'Housing Statistics', 'Colorado 14ers']
view_selection = st.sidebar.selectbox("#### View Selection", dropdown_views)
st.sidebar.write('')


# Create Housing Statistics Page
if view_selection == 'Housing Statistics':
    # Display the page title
    st.markdown(
        f"""
        <div class="title-container">
            <div class="title">{view_selection}</div>
        </div>
        """, unsafe_allow_html=True
    )

    # Section 1: Cumulative Change in Housing Costs and Incomes
    ## Section title
    tl.write_around_markdown('#### Cumulative Change in Housing Costs and Incomes', 0, 1)

    ## Create two columns to display filters side by side
    col1, col2 = st.columns([1, 2])
    with col1:
        state_selection = st.selectbox("**Select Geographic Level**", ['US National Average'] + us_states)
    with col2:
        year_range1 = st.slider('**Select Year Range**', min_value=year_min, max_value=year_max, value=(year_min, year_max), key='slider_key_1')

    ## Display the Cumulative Change in Housing Costs and Incomes chart based on filter selections
    ast.yoy_cum_change_line_charts(state_selection, year_range1)


    # Section 2: Share of Renters Housing Burdened
    ## Section title
    tl.write_around_markdown('#### Share of Renters Housing Burdened Map', 1, 1)

    ## State vs. County Selection
    level_list = ['State Level', 'County Level']
    level_selection = st.selectbox("**Geographic Level Selection**", level_list)

    ## Display the Share of Renters Housing Burdened figs based on filter selection
    ast.renter_house_burden(level_selection, us_states)

    
    # Section 3: National Average vs. Select State -- Year over Year
    ## Section title
    tl.write_around_markdown('#### National Average vs. Select State -- Year over Year', 1, 1)

    ## Display the National Average vs. Select State -- Year over Year figs based on filter selection
    ast.yoy_comp_line_charts(state_selection, us_states)

    # Final Section
    ast.housing_terms()


# Create Stock Market Page
elif view_selection == 'Stock Market':
    # Add n random s&p 500 stock tickers
    ss.stock_ticker(6)

    # Add market index time series section
    ss.market_time_series()

    # Add individual selected stock overview section
    ss.selected_stock_summary()


# Create News and Research Page
elif view_selection == 'News and Research':
    ns.news_and_research()


# Create 14ers Page
elif view_selection == 'Colorado 14ers':
    fs.fourteeners_heading()
    fs.fourteeners_table()


# Create Weather Page
elif view_selection == 'Weather':
    ws.weather_main()