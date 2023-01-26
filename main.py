import streamlit as st
import pandas as pd
from Utils import GetStat, Mapping, PrestigeData

##################
## Page Config ###
##################

st.set_page_config(
    page_title='LHDB',
    layout='wide',
    menu_items={
        'Get Help': None,
        'Report a bug': 'mailto:levon.fischer@gmail.com',
        'About': None
    }
)


##################
## Title #########
##################

st.title('The League History DataBase')

##################
## Sidebar #######
##################

curr_league_id = st.sidebar.text_input(label='Enter your league ID',
                                       value='784428347810816000')

##################
## Load Data #####
##################

with st.spinner('Loading League History...'):
    #load all the league ids
    league_ids = PrestigeData.all_league_ids(curr_league_id)

    #load the regular season matchups
    reg_szn = PrestigeData.alltime_rg_matchups(league_ids)
    reg_df = pd.DataFrame(reg_szn)
    #load the post season matchups
    post_szn = PrestigeData.alltime_po_matchups(league_ids)
    post_df = pd.DataFrame(post_szn)
    #Get All matchups
    matchups_df = PrestigeData.all_matchups(reg_df, post_df)
    #Create DF with each individual matchup scores
    ind_matchups = PrestigeData.ind_matchup_scores(matchups_df)

    #Dictionary to map all the UIDs to names
    uid_to_names = Mapping.get_all_time_users(league_ids)
    usernames = Mapping.list_of_gms(uid_to_names)

####################
## League Metrics ##
####################

# Set variables for metric displays
total_matchups = matchups_df.shape[0]
total_points = reg_df['team1_score'].sum() + reg_df['team2_score'].sum()
high_scorer, score = GetStat.highest_scorer(reg_df)
total_seasons = reg_df['year'].nunique()
total_gms = ind_matchups['uid'].nunique()
max_score = ind_matchups['score'].max()

col1, col2, col3 = st.columns(3)
col1.metric(label='Totals Games', value=total_matchups)
col2.metric(label='Total Points', value=total_points)
col3.metric(label='Highest total Score', value=uid_to_names[high_scorer])

col1, col2, col3 = st.columns(3)
col1.metric(label='Total Seasons', value=total_seasons)
col2.metric(label='Total GMs', value=total_gms)
col3.metric(label='Highest score', value=max_score)

#####################
## Table Filters ####
#####################

years = matchups_df['year'].unique()
weeks = matchups_df['week'].unique()
#game_types =

st.write('Filter')
col1, col2, col3 = st.columns(3)
year = col1.selectbox('YEAR', years)
week = col2.selectbox('WEEK', weeks)
game_type = col3.multiselect('Game Type', ['Regular', 'Playoffs', 'Toilet Bowl', 'All'])

filt = ((matchups_df['year'] == year) & (matchups_df['week'] == week))
filtered_df = matchups_df.loc[filt]

####################
## Matchup Table ###
####################

st.dataframe(filtered_df, use_container_width=True)
