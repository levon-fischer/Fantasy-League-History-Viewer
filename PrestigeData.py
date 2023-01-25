import streamlit as st
import pandas as pd
from sleeper_wrapper import League


# INPUT: the current season's league ID (str or int)
# OUTPUT: a dictionary of all the leagues years ({'year': 'league ID'})
@st.cache
def all_league_ids(current_league_id):
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


# INPUT: dictionary of all the leagues years ({'year': 'League ID'})
# OUTPUT: dictionary of each matchup for the league (can be converted to dataframe)
@st.cache
def alltime_rg_matchups(league_ids):
    # create an empty list for each column of the result dataframe
    year_lst, week_lst, user1, tm1, tm1_score, user2, tm2, tm2_score, g_type = [], [], [], [], [], [], [], [], []

    game_type = 'R'

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
                g_type.append(game_type)

    # Put the filled out lists into a dictionary to be created into a DataFrame
    all_matchups = {'year': year_lst,
                    'week': week_lst,
                    'uid1': user1,
                    'team1': tm1,
                    'team1_score': tm1_score,
                    'uid2': user2,
                    'team2': tm2,
                    'team2_score': tm2_score,
                    'game_type': g_type}

    return all_matchups


# INPUT: dictionary of all the leagues years ({'year': 'League ID'})
# OUTPUT: dictionary of each playoff matchup for the league (can be converted to dataframe)
@st.cache
def alltime_po_matchups(league_ids):
    # create an empty list for each column of the result dataframe
    year_lst, week_lst, user1, tm1, tm1_score, user2, tm2, tm2_score, g_type = [], [], [], [], [], [], [], [], []

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
        start_week = season.get_league()['settings']['playoff_week_start']
        end_week = start_week + 3
        for week in range(start_week, end_week):
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

                if matchup is None:
                    continue
                elif matchup < 4:
                    game_type = 'P'
                else:
                    game_type = 'T'

                # Append the matchups to the corresponding lists
                year_lst.append(year)
                week_lst.append(week)
                user1.append(uid1)
                tm1.append(team1)
                tm1_score.append(matchup_ids[matchup]['tm1_score'])
                user2.append(uid2)
                tm2.append(team2)
                tm2_score.append(matchup_ids[matchup]['tm2_score'])
                g_type.append(game_type)

    # Put the filled out lists into a dictionary to be created into a DataFrame
    all_po_matchups = {'year': year_lst,
                       'week': week_lst,
                       'uid1': user1,
                       'team1': tm1,
                       'team1_score': tm1_score,
                       'uid2': user2,
                       'team2': tm2,
                       'team2_score': tm2_score,
                       'game_type': g_type}

    return all_po_matchups


# INPUT: 2 DataFrames (all regular season and all post season matchups)
# OUTPUT: a DataFrame with all the leagues matchups
@st.cache
def all_matchups(reg_szn, post_szn):
    all_matchups_df = pd.concat([reg_szn, post_szn], ignore_index=True)
    return all_matchups_df


# INPUT: LHDB dataframe
# OUTPUT: DataFrame with each team's individual score for each matchup
#             Columns: ['uid', 'score']
@st.cache
def ind_matchup_scores(df):
    # take the LHDB and get just a single list of all the scores for each user
    cols1 = df[['year', 'week', 'uid1', 'team1', 'team1_score']]
    cols2 = df[['year', 'week', 'uid2', 'team2', 'team2_score']]
    cols1 = cols1.rename(columns={'uid1': 'uid', 'team1': 'team', 'team1_score': 'score'})
    cols2 = cols2.rename(columns={'uid2': 'uid', 'team2': 'team', 'team2_score': 'score'})
    df = pd.concat([cols1, cols2], axis=0)

    return df
