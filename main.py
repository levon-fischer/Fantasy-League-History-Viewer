import streamlit as st
import pandas as pd
from sleeper_wrapper import League

st.set_page_config(
    page_title='LHDB',
    layout='wide',
    menu_items={
        'Get Help': None,
        'Report a bug': 'mailto:levon.fischer@gmail.com',
        'About': None
    }
)

# INPUT: the current season's league ID (str or int)
# OUTPUT: a dictionary of all the leagues years ({'year': 'league ID'})
@st.cache
def get_all_league_ids(current_league_id):
    more_years = True
    league_ids = {}
    while more_years:
        curr_league = League(current_league_id).get_league()
        prev_league_id = curr_league['previous_league_id']
        curr_year = curr_league['season']
        league_ids[curr_year] = current_league_id
        if prev_league_id is None:
            more_years = False
        else:
            current_league_id = prev_league_id
    return league_ids

# INPUT: a dictionary of all the leagues years ({'year': 'League ID'})
# OUTPUT: a list of all the owners
@st.cache
def get_all_time_owners(league_ids):
    owners = []
    for year in league_ids:
        season = League(league_ids[year])
        rosters = season.get_rosters()
        for roster in rosters:
            oid = roster['owner_id']
            if oid in owners:
                continue
            else:
                owners.append(oid)
    return owners


# INPUT: dictionary of all the leagues years ({'year': 'League ID'})
# OUTPUT: dictionary of all the users mapped to thier names ({'UID': 'username'})
@st.cache
def get_all_time_users(league_ids):
    mapped_users = {}
    for year in league_ids:
        season = League(league_ids[year])
        users = season.get_users()
        for user in users:
            uid = user['user_id']
            name = user['display_name']
            if uid in mapped_users:
                continue
            else:
                mapped_users[uid] = name

    return mapped_users


# INPUT: dictionary of all the leagues years ({'year': 'League ID'})
# OUTPUT: dictionary of each matchup for the league (can be converted to dataframe)
@st.cache
def get_all_time_matchups(league_ids):
    # create an empty list for each column of the result dataframe
    year_lst, week_lst, user1, tm1, tm1_score, user2, tm2, tm2_score = [], [], [], [], [], [], [], []

    # go through each season
    for year in league_ids:
        # initialize the current season
        season = League(league_ids[year])

        # map the current season's roster IDs to their Owner IDs
        rosters = season.get_rosters()
        rosters_dict = season.map_rosterid_to_ownerid(rosters)

        # map the current season's Owner IDs to their Team Names
        users = season.get_users()
        users_dict = season.map_users_to_team_name(users)

        # get the total number of weeks in the season and then iterate over them
        num_weeks = season.get_league()['settings']['playoff_week_start']
        for week in range(1, num_weeks):
            # request all the matchups for this week
            matchups = season.get_matchups(week)

            # create a dictionary to hold each matchup for this week
            matchup_ids = {}

            # go through the matchups that were returned from the sleeper API and
            # add them to our matchup_ids dictionary in the format we want:
            #   {'matchup_id':
            #                 {'tm1': rosterID,
            #                  'tm1_score': score,
            #                  'tm2': rosterID,
            #                  'tm2_score': score}}
            for team in matchups:
                if team['matchup_id'] not in matchup_ids:
                    matchup_ids[team['matchup_id']] = {'tm1': team['roster_id'],
                                                       'tm1_score': team['points']}
                else:
                    matchup_ids[team['matchup_id']]['tm2'] = team['roster_id']
                    matchup_ids[team['matchup_id']]['tm2_score'] = team['points']

            # Now that we have our matchups for this week, append the info about
            # each one to its corresponding column list
            for matchup in matchup_ids:
                # map the roster IDs to the user ID and team names
                uid1 = rosters_dict[matchup_ids[matchup]['tm1']]
                uid2 = rosters_dict[matchup_ids[matchup]['tm2']]
                team1 = users_dict[uid1]
                team2 = users_dict[uid2]

                # Append the matchups to the corresponding lists
                year_lst.append(year)
                week_lst.append(week)
                user1.append(uid1)
                tm1.append(team1)
                tm1_score.append(matchup_ids[matchup]['tm1_score'])
                user2.append(uid2)
                tm2.append(team2)
                tm2_score.append(matchup_ids[matchup]['tm2_score'])

    # Put the filled out lists into a dictionary to be created into a DataFrame
    all_matchups = {'year': year_lst,
                    'week': week_lst,
                    'uid1': user1,
                    'team1': tm1,
                    'team1_score': tm1_score,
                    'uid2': user2,
                    'team2': tm2,
                    'team2_score': tm2_score}

    return all_matchups


# INPUT: LHDB dataframe
# OUTPUT: DataFrame with each team's individule score for each matchup
#             Columns: ['uid', 'score']
@st.cache
def get_ind_matchup_scores(df):
    # take the LHDB and get just a single list of all the scores for each user
    cols1 = df[['uid1', 'team1_score']]
    cols2 = df[['uid2', 'team2_score']]
    cols1 = cols1.rename(columns={'uid1': 'uid', 'team1_score': 'score'})
    cols2 = cols2.rename(columns={'uid2': 'uid', 'team2_score': 'score'})
    df = pd.concat([cols1, cols2], axis=0)

    return df


# INPUT: LHDB dataframe
# OUTPUT: tuple with the UID of the highest scorer and their total score
@st.cache
def get_highest_scorer(df):
    # take the LHDB and get just a single list of all the scores for each user
    df = get_ind_matchup_scores(df)

    # group the users and get their total scores
    grouped_users = df.groupby('uid')['score'].sum()

    # get the
    highest_scorer = grouped_users.idxmax()
    score = grouped_users[highest_scorer]

    return highest_scorer, score


def list_of_gms(users):
    usernames = []
    for uid in users:
        usernames.append(users[uid])
    return usernames





st.title('The League History DataBase')

curr_league_id = st.text_input(label='Enter your league ID', value='784428347810816000')

with st.spinner('Loading League History...'):
    league_ids = get_all_league_ids(curr_league_id)
    matchups = get_all_time_matchups(league_ids)
    columns = ['year', 'week', 'uid1', 'team1', 'team1_score', 'uid2', 'team2', 'team2_score']
    lhdb = pd.DataFrame(matchups)
    ind_matchups = get_ind_matchup_scores(lhdb)
    uid_to_names = get_all_time_users(league_ids)
    usernames = list_of_gms(uid_to_names)
    st.dataframe(lhdb, use_container_width=True)

# Set variables for metric displayers
total_matchups = lhdb.shape[0]
total_points = lhdb['team1_score'].sum() + lhdb['team2_score'].sum()
highest_scorer, score = get_highest_scorer(lhdb)
total_seasons = lhdb['year'].nunique()
total_gms = ind_matchups['uid'].nunique()
max_score = ind_matchups['score'].max()

col1, col2, col3 = st.columns(3)
col1.metric(label='Totals Games', value=total_matchups)
col2.metric(label='Total Points', value=total_points)
col3.metric(label='Highest total Score', value=uid_to_names[highest_scorer])

col1, col2, col3 = st.columns(3)
col1.metric(label='Total Seasons', value=total_seasons)
col2.metric(label='Total GMs', value=total_gms)
col3.metric(label='Highest score', value=max_score)
