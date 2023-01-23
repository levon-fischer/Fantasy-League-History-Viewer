import streamlit as st
import main

gm1 = st.selectbox(
    'Select GM 1',
    options=main.usernames,
    index=0
)
gm2 = st.selectbox(
    'Select GM 2',
    options=main.usernames,
    index=1
)