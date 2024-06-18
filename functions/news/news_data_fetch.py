#%%
import requests
import streamlit as st
import pandas as pd
import xmltodict
import json

@st.cache_data(ttl='1h')
def get_news_data(api_key, country, category, number=15):
    '''
    Fetches news headlines, sources, links, images, and summaries given a category

    Parameters:
        - api_key: NewsAPI API Key
        - country: The 2-letter ISO 3166-1 code of the country you want to get headlines for.
        - category: The category you want to get headlines for. Possible options: business, entertainment, general, health, science, sports, technology
        - number: Articles returned

    Returns:
        - df: A df with all data from the NewsAPI
    '''
    base_url = f"https://newsapi.org/v2/top-headlines?"

    params = {
        "country": country,
        "category": category,
        "apiKey": api_key,
        "pageSize": number
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            df = pd.DataFrame(data['articles'])
            return df
        except Exception as e:
            print(f"Error: {e}")
            return None
    else:
        print(f"Error fetching data: {response.status_code}")
        try:
            error_message = response.json()['message']
            print(f"Error message: {error_message}")
        except Exception as e:
            print(f"Error processing JSON for error message: {e}")
        return None
    

@st.cache_data(ttl='1h')
def get_research_data(title_keyword, author_keyword=None, api_key=None):
    '''
    Fetches economics research articles.

    Parameters:
        - title_keyword: Optional keyword to filter publications by title
        - author_keyword: Optional keyword to filter publications by author
        - api_key: Optional API key

    Returns:
        - df: A df with all data from the arxiv api
    '''
    base_url = f'http://export.arxiv.org/api/query?'

    params = {
        "search_query": f'cat:"econ.GN"+ti:"{title_keyword}"+au:"{author_keyword}"',
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending",
        "max_results": 10
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        try:
            xml_data = response.content
            data_dict = xmltodict.parse(xml_data)
            json_data = json.dumps(data_dict)
            return json_data
        except Exception as e:
            print(f"Error: {e}")
            return None
    else:
        print(f"Error fetching data: {response.status_code}")
        try:
            error_message = response.json()['message']
            print(f"Error message: {error_message}")
        except Exception as e:
            print(f"Error processing JSON for error message: {e}")
        return None
    
