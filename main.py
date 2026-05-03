import json
import os
import sys
import pandas
from logic.loader import load_events, get_valid, load_maps, get_valid_maps
from logic.cleaner import clean_events
from logic.core import get_users, get_session_events, group_by_user, sort_by_timestamp
from logic.core import track_sessions, session_metrics
from logic.core import get_match_events, group_matches, valid_matches, construct_matches
from logic.core import user_stats, get_map_stats

#map_name - > map_id - helping function
def map_id_by_map_name(mapName, mapData):
    for m in mapData:
        if m["name"]==mapName:
            return m["id"]
    return None

#Help function for map_name output
def map_id_to_map_name(userStats, validMaps):
    mapTemp={}

    for m in validMaps:
        mapTemp[m["id"]]=m["name"]

    for user in userStats:
        mapId=userStats[user]["fav_map"]
        userStats[user]["fav_map"]=mapTemp.get(mapId, None)

    return userStats


#invalid entry in terminal
def printWarning():
    print("Please enter command!")
    print("1) user-stats")
    print("2) map-stats <map-name>")

#Pandas conversion from json format
def user_stats_to_df(userStats):
    df=pandas.DataFrame.from_dict(userStats, orient="index")
    return df.reset_index(drop=True)
#-||-
def map_stats_to_df(mapStats):
    return pandas.DataFrame(mapStats)

if __name__ == "__main__":
    eventsPath=os.path.join(os.path.dirname(__file__), "data", "events.jsonl")
    mapsPath=os.path.join(os.path.dirname(__file__), "data", "maps.jsonl")

    rawEvents=load_events(eventsPath)
    validEvents=get_valid(rawEvents)

    rawMaps=load_maps(mapsPath)
    validMaps=get_valid_maps(rawMaps)

    cleanedEvents=clean_events(validEvents)

    users=get_users(cleanedEvents)

    sessionEvents=get_session_events(cleanedEvents)
    groupedSessions=group_by_user(sessionEvents)
    sortSessions=sort_by_timestamp(groupedSessions)
    sessionTracker=track_sessions(sortSessions)
    sessions=session_metrics(sessionTracker)

    matchEvents=get_match_events(cleanedEvents)
    groupedMatches=group_matches(matchEvents)
    validMatches=valid_matches(groupedMatches)
    matches=construct_matches(validMatches)


    userStats=user_stats(users, matches, sessions)


    args=sys.argv

    if len(args)<2:
        printWarning()
        sys.exit()
    
    command=args[1]

    if command == "user-stats":
        if len(args) != 2:
            printWarning()
            sys.exit()
            
        userStats=map_id_to_map_name(userStats, validMaps)
        df=user_stats_to_df(userStats)
        print(df.to_string(index=False))
        sys.exit()
    
    elif command=="map-stats":

        if len(args)!=3:
            printWarning()
            sys.exit()
        
        mapName=args[2]
        mapId=map_id_by_map_name(mapName, validMaps)

        if mapId is None:
            print("Map not found")
            sys.exit()

        mapStats=get_map_stats(matches, mapId, users)        
        
        df=map_stats_to_df(mapStats)
        print(df)
        sys.exit()
    
    else:
        printWarning()
        sys.exit()