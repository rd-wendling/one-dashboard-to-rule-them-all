#%%
import streamlit as st

# Function to add proper spacing around streamlit titles using blank st.write()
def write_around_markdown(message, above=0, below=0):
    '''
    Takes a message (title/heading typically) and xreates a st.markdown element with it and surronds that
    on top and bottom with blank st.write()

    Parameters:
        - message: The text to include in the markdown
        - above: 1 to add blank st.write() above markdown
        - below: 1 to add blank st.write() below markdown
    '''
    if above == 1:
        st.write('')
    st.markdown(f'{message}', unsafe_allow_html=True)
    if below == 1:
        st.write('')
