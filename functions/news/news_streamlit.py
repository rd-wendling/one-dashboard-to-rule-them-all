#%% 
import streamlit as st
import functions.news.news_data_fetch as nf
import functions.tools as t
import pandas as pd
from datetime import datetime

news_api_key = st.secrets["news_api_key"]

# Function to get names out of the research api return
def extract_names(lst):
    try:
        return ', '.join(item['name'] for item in lst)
    except:
        pass


# Function to create the news and research section
def news_and_research():
    # Create two columns to show each selection side by side
    cols = st.columns([50, 5, 40])

    # Top US Headline Section
    with cols[0]:
        # Add title
        t.write_around_markdown('#### Top US Headlines by Category', 0, 1)

        # Create a dropdown filter for new category
        news_cats = ['Business', 'Entertainment', 'General', 'Health', 'Science', 'Sports', 'Technology']
        cat_selection = st.selectbox("**Select News Category**", news_cats, index=news_cats.index('General'))
        st.write('')

        # Get headlines based on category selection
        country = "us"
        df = nf.get_news_data(news_api_key, country, cat_selection)

        # Loop through new api results to create the news divs
        for index, row in df.iterrows():
            if row['urlToImage']:
                source = row['source']['name']
                article_link = row['url']
                img_url = row['urlToImage']
                title = row['title']
                summary = row['description']

                st.markdown(
                    f"""
                    <a href="{article_link}" class="news-article-link" target="_blank">
                        <div id="top-headlines-category">
                            <div>
                                <h3 style="margin: 0; padding: 2px; font-size: 1.2em;">{title}</h3>
                                <p style="margin: 0; color: gray;"><b>Source:</b> {source}</p>
                                <p style="margin: 5px 0 0 0;">{summary}</p>
                            </div>
                            <img src="{img_url}" alt="News Image" style="width: 200px; height: auto; margin-left: 20px; border-radius: 8px;">
                        </div>
                    </a>
                """,
                    unsafe_allow_html=True
                )

    # New Economics Research Section
    with cols[2]:
        # Add title
        t.write_around_markdown('#### New Economics Research', 0, 1)

        # Create two columns to show each keyword filter side by side
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            title_keyword = st.text_input("**Title Keyword Search:**")
        with subcol2:
            author_keyword = st.text_input("**Author Keyword Search:**")

        # Validate keywords entered are single words, raise warning if not
        if ' ' in title_keyword.strip() or ' ' in author_keyword.strip():
            st.warning("Please enter a single word keywords.")

        # If keywords are valid, get research papers
        else:
            st.write('')

            # get the research papers data
            data = nf.get_research_data(title_keyword, author_keyword)
            df = pd.read_json(data)
            df = pd.DataFrame(df.loc['entry']['feed'])
            
            # Loop through new api results to create the news divs
            for index, row in df.iterrows():
                # Only do this for papers with authors
                if extract_names(row['author']):
                    title = row['title']
                    published_date = row['published']
                    published_date = datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
                    author = extract_names(row['author'])
                    summary = row['summary']

                    # Cutoff summary at 400 chars
                    if len(summary) > 400:
                        summary = summary[:400] + '...'
                    article_link = row['link'][0]['@href']

                    st.markdown(
                            f"""
                            <a href="{article_link}" class="news-article-link" target="_blank">
                                <div id="top-headlines-category">
                                    <div>
                                        <h3 style="margin: 0; padding: 2px; font-size: 1.2em;">{title}</h3>
                                        <p style="margin: 0; color: gray;"><b>Authors:</b> {author}</p>
                                        <p style="margin: 0; color: gray;"><b>Published:</b> {published_date}</p>
                                        <p style="margin: 5px 0 0 0;">{summary}</p>
                                    </div>
                                </div>
                            </a>
                        """,
                            unsafe_allow_html=True
                        )

        