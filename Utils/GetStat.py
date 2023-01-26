import streamlit as st
import pandas as pd
import PrestigeData


# INPUT: LHDB dataframe
# OUTPUT: tuple with the UID of the highest scorer and their total score
@st.cache
def highest_scorer(df: pd.DataFrame) -> tuple:
    # take the LHDB and get just a single list of all the scores for each user
    df = PrestigeData.ind_matchup_scores(df)

    # group the users and get their total scores
    grouped_users = df.groupby('uid')['score'].sum()

    # get the
    high_scorer = grouped_users.idxmax()
    score = grouped_users[high_scorer]

    return high_scorer, score


# INPUT: Individual matchups dataframe
# OUTPUT: Dictionary with the number of seasons mapped to the UID
@st.cache
def seasons_per_owner(df: pd.DataFrame) -> dict:
    num_seasons = df.groupby('uid')['year'].nunique().to_dict()

    return num_seasons