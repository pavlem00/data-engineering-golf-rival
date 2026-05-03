from datetime import datetime

#Extracting user with info from cleaned events
def get_users(events):
    users={}

    for event in events:
        et=event.get("event_type")
    
        if et == "registration":
            userId=event.get("user_id")
            data=event.get("event_data")
            ts=event.get("timestamp")
            eventDate=datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")            
    
            if userId not in users or eventDate < users[userId]["registration_date"]:
                users[userId]={"username":data["username"], "country":data["country"], "registration_date":eventDate}
    
    return users



#Extracting only "session" events from cleaned events
def get_session_events(events):
    sessionEvents=[]
    
    for event in events:
        et=event.get("event_type")
        if et == "session_ping":
            sessionEvents.append(event)
    
    return sessionEvents



#Extracting only "match" events from cleaned events
def get_match_events(events):
    matchEvents=[]
    matchType={"match_start", "match_finish"}
    
    for event in events:
        et=event.get("event_type")
        if et in matchType:
            matchEvents.append(event)
    
    return matchEvents



#Making list of cleaned events for each user
def group_by_user(events):
    groupedEvents={}

    for event in events:
        userId=event.get("user_id")
        groupedEvents.setdefault(userId, []).append(event)

    return groupedEvents



#Sorting fucntion, by timestamp ascending, can be used on sessions or matches
def sort_by_timestamp(grouped):

    for item in grouped.values():
        item.sort(key=lambda x: x["timestamp"])

    return grouped



#Splitting each session by user, after having them grouped and sorted
def track_sessions(sessionEvents):
    dif=120
    sessionBuilder={}

    for user, items in sessionEvents.items():
        sessions=[]
        current=[]

        for item in items:
            if len(current) == 0:
                current.append(item)
            else:
                if item["timestamp"]-current[-1]["timestamp"] > dif:
                    sessions.append(current)
                    current=[]
                current.append(item)

        if len(current) != 0:
            sessions.append(current)
        sessionBuilder[user]=sessions

    return sessionBuilder



#Making a structure (dict), from already grouped, sorted and splitted sessions
#with start, end and calculated duration of session for each one
def session_metrics(sessionBuilder):
    
    metrics={}
    for user, sessions in sessionBuilder.items():    
        metrics[user] = []   
        for session in sessions:
            start = session[0]["timestamp"]
            end = session[-1]["timestamp"]
            duration = end - start
            metrics[user].append({
                "start": start,
                "end": end,
                "duration": duration
            })
    
    return metrics



#Grouping matches, with key being, map_id for that match
#and id for each of two competing players
def group_matches(matchEvents):
    groupedMatches={}
    
    for match in matchEvents:
        player1=match["user_id"]
        player2=match["event_data"]["opponent_id"]
        mapId=match["event_data"]["map_id"]
        key=tuple(sorted([player1, player2]))+(mapId, )
        groupedMatches.setdefault(key, []).append(match)
    
    return groupedMatches



#Validating matches already grouped matches
def valid_matches(groupedMatches):
    validMatches={}

    for key, values in groupedMatches.items():
        hasStart=False
        hasFinish=False

        for value in values:
            if value["event_type"]=="match_start":
                hasStart=True
            elif value["event_type"]=="match_finish":
                hasFinish=True
            else:
                continue

        if hasFinish and hasStart:
            validMatches[key]=values
        else:
            continue

    return validMatches



#Reconstructing each match for competing players and their map_id after validation
def construct_matches(validMatches):
    matchConstructor=[]

    for key, values in validMatches.items():
        player1, player2, mapId=key
        values=sorted(values, key=lambda x:x["timestamp"])
        startEvent=None

        for value in values:
            if value["event_type"]=="match_start":
                startEvent=value
                break

        finishEvents=[]
        for value in values:
            if value["event_type"]=="match_finish":
                finishEvents.append(value)
        finishEvent=max(finishEvents, key=lambda x:x["timestamp"])
        
        if startEvent is None or finishEvent is None:
            continue
        
        startTime=startEvent["timestamp"]
        finishTime=finishEvent["timestamp"]
        outcome=finishEvent["event_data"]["outcome"]
        user=finishEvent["user_id"]
        opponent=finishEvent["event_data"]["opponent_id"]
        
        if outcome==1:
            winner=user
        elif outcome==0:
            winner=opponent
        else:
            winner=None
        
        construct={"players":(player1, player2), 
                   "map_id":mapId, 
                   "start_time":startTime, 
                   "finish_time":finishTime, 
                   "duration":finishTime-startTime, 
                   "winner":winner}
        matchConstructor.append(construct)
    
    return matchConstructor



#grouping matches by map, for each user
def group_by_map_user(users, matches):
    group={}
    
    for user in users:
        maps={}

        for match in matches:
            if user in match["players"]:
                mapId=match["map_id"]
                if mapId not in maps:
                    maps[mapId]=[]
                maps[mapId].append(match)
        
        group[user]=maps
    
    return group



#calc for total_playtime
def get_total_playtime(metrics):
    totalPlaytime={}

    for user in metrics:
        for session in metrics[user]:
            if user not in totalPlaytime:
                totalPlaytime[user]=0
            totalPlaytime[user]+=session["duration"]
    
    return totalPlaytime



#calc for total_matches
def get_total_matches(matches):
    totalMatches={}

    for match in matches:
        for player in match["players"]:
            if player not in totalMatches:
                totalMatches[player]=0
            totalMatches[player]+=1
    
    return totalMatches



#calc for wins per each user
def get_wins_per_user(matches):
    wins={}

    for match in matches:
        winner=match["winner"]
        
        if winner is None:
            continue
        
        if winner not in wins:
            wins[winner]=0
        wins[winner]+=1
    
    return wins



#calc for win ratio
def get_total_win_ratio(totalMatches, wins):
    totalWinRatio={}

    for user in totalMatches:
        tm=totalMatches[user]
        win=wins.get(user, 0)

        if tm == 0:
            totalWinRatio[user]=0
        else:
            totalWinRatio[user]=win/tm
    
    return totalWinRatio



#calc for avg matches per session
def get_avg_matches_per_session(totalMatches, metrics):
    avgMatchesPerSession={}

    for user in totalMatches:
        tm=totalMatches[user]
        numSessions=len(metrics.get(user,[]))

        if numSessions==0:
            avgMatchesPerSession[user]=0
        else:
            avgMatchesPerSession[user]=tm/numSessions

    return avgMatchesPerSession



#calc for favourite map and favourite map win ratio
def get_fav_map_with_win_ratio(groupedMaps):
    favMap={}
    favMapWinRatio={}

    for user, maps in groupedMaps.items():
        bestMap=None
        bestRatio=-1

        for mapId, matchList in maps.items():
            numMatch=len(matchList)
            winNum=0

            for match in matchList:
                if match["winner"]==user:
                    winNum+=1

            if numMatch > 0:
                ratio=winNum/numMatch
            else:
                ratio=0
            
            if ratio>bestRatio:
                bestRatio=ratio
                bestMap=mapId
            
        favMap[user]=bestMap

        if bestRatio != -1:
            favMapWinRatio[user]=bestRatio
        else:
            favMapWinRatio[user]=0
    return favMap, favMapWinRatio



#main function for getting user-stats
def user_stats(users, matches, metrics):
    stats={}
   
    totalPlaytime=get_total_playtime(metrics)
    totalMatches=get_total_matches(matches) 
    wins=get_wins_per_user(matches)
    totalWinRatio=get_total_win_ratio(totalMatches, wins)
    avgMatchesPerSession=get_avg_matches_per_session(totalMatches, metrics)
    groupedMaps=group_by_map_user(users, matches)
    
    (favMap, favMapWinRatio)=get_fav_map_with_win_ratio(groupedMaps)
    for user, info in users.items():
        stats[user]={
            "username": info["username"],
            "country": info["country"],
            "registration_date": info["registration_date"],
            "fav_map": favMap.get(user, None),
            "fav_map_win_ratio": favMapWinRatio.get(user, 0),
            "total_playtime": totalPlaytime.get(user, 0),
            "total_win_ratio": totalWinRatio.get(user, 0),
            "avg_matches_per_session": avgMatchesPerSession.get(user, 0)
        }
    
    return stats



#Grouping matches(after reconstructing them), with map_id being the key
def group_matches_by_map(matches):
    grouped={}

    for match in matches:
        mapId=match["map_id"]

        if mapId not in grouped:
            grouped[mapId]=[]
        grouped[mapId].append(match)
    
    return grouped



#Grouping matches in dict, with date parsed from timestamp as key
def group_matches_by_date(matches):
    group={}

    for match in matches:
        time=match["finish_time"]
        date=datetime.utcfromtimestamp(time).strftime("%Y-%m-%d")

        if date not in group:
            group[date]=[]
        group[date].append(match)

    return group



#Calc number of matches per date, and average playtime per date
def calc_cnt_avg(matchesByDate):
    res={}
    for date, matchList in matchesByDate.items():
        match_cnt=len(matchList)

        totalDuration=0
        for match in matchList:
            totalDuration+=match["duration"]
        
        if match_cnt > 0:
            avg_playtime=totalDuration/match_cnt
        else:
            avg_playtime=0
        res[date]={"match_cnt": match_cnt, "avg_playtime": avg_playtime}
    
    return res




def best_player_by_map(matchesByDate, users):
    sortedDates=sorted(matchesByDate.keys())

    wins={}
    matches={}
    bestPlayer={}

    for date in sortedDates:
        currentMatches=matchesByDate[date]
        
        userPlayed=set()

        for match in currentMatches:
            player1, player2=match["players"]
            winner=match["winner"]

            if player1 in matches:
                matches[player1]+=1
            else:
                matches[player1]=1
            
            if player2 in matches:
                matches[player2]+=1
            else:
                matches[player2]=1
            
            userPlayed.add(player1)
            userPlayed.add(player2)

            if winner is not None:
                if winner in wins:
                    wins[winner]+=1
                else:
                    wins[winner]=1

        bestUser=None
        bestRatio=-1

        for user in userPlayed:
            if user not in users:
                continue
            
            userWins=wins.get(user, 0)
            userMatches=matches[user]

            ratio=userWins/userMatches

            if ratio > bestRatio:
                bestRatio=ratio
                bestUser=user
            
        bestPlayer[date]=users[bestUser]["username"]
    
    return bestPlayer



#Making subset of matches, using specified map_id
def filter_matches_by_map(matches, mapId):
    filtered=[]

    for match in matches:
        if match["map_id"]==mapId:
            filtered.append(match)
    
    return filtered



#Map-stats final function, using previous help functions
#dateRange, from-to, optional
def get_map_stats(matches, mapId, users):

    filtered=filter_matches_by_map(matches, mapId)
    matchesByDate=group_matches_by_date(filtered)
    
    statsByDate=calc_cnt_avg(matchesByDate)
    bestPlayers=best_player_by_map(matchesByDate, users)

    result=[]

    for date in matchesByDate:
        result.append({"date": date,
                       "avg_playtime": statsByDate[date]["avg_playtime"],
                       "match_cnt": statsByDate[date]["match_cnt"],
                       "best_player_username": bestPlayers[date], 
                       })
    
    return result