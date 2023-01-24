import streamlit as st
import PrestigeData


# INPUT: LHDB dataframe
# OUTPUT: tuple with the UID of the highest scorer and their total score
@st.cache
def get_highest_scorer(df):
    # take the LHDB and get just a single list of all the scores for each user
    df = PrestigeData.get_ind_matchup_scores(df)

    # group the users and get their total scores
    grouped_users = df.groupby('uid')['score'].sum()

    # get the
    highest_scorer = grouped_users.idxmax()
    score = grouped_users[highest_scorer]

    return highest_scorer, score
