import streamlit as st
from sleeper_wrapper import League


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
# OUTPUT: dictionary of all the users mapped to their names ({'UID': 'username'})
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


def list_of_gms(users):
    usernames = []
    for uid in users:
        usernames.append(users[uid])
    return usernames

