#%%
import streamlit as st

def write_around_markdown(message, above=0, below=0):
    if above == 1:
        st.write('')
    st.markdown(f'{message}', unsafe_allow_html=True)
    if below == 1:
        st.write('')
