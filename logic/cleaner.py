#Discarding duplicates by id
def discard_copies(events):
        original={}
        for event in events:
                eventId=event['id']
                eventTs=event['timestamp']  
                if eventId not in original or eventTs < original[eventId]['timestamp']:
                        original[eventId]=event
        cleanedEvents=list(original.values())
        return cleanedEvents

#Filtering events, returning only valid events by type, 4 possible
def check_event_type(event):
                validEventTypes={"registration", "session_ping", "match_start", "match_finish"}
                et=event.get("event_type")
                if et in validEventTypes:
                        return et
                else:
                        return None

#Validating event_data section, checking if its dict
def valid_data(event):
        return isinstance(event.get("event_data"), dict)


#Checking event_data items, by event_type
def check_event_data(event):
                validMap={
                        "registration" : {"country", "device_os", "username"},
                        "session_ping" : {"state", "device_os"},
                        "match_start" : {"map_id", "opponent_id"},
                        "match_finish" : {"map_id", "opponent_id", "outcome"}
                }
                et=check_event_type(event)
                if et is None:
                        return False
                else:
                     if not valid_data(event):
                             return False
                     else:
                             return validMap[et].issubset(event["event_data"].keys())   


#Validating events by timestamp, it has to be positive
def check_timestamp(event):
        ts=event.get("timestamp")
        if isinstance(ts,int) and ts > 0:
                return True
        else:
                return False


#Validating events by outcomes: 1-win, 0.5-draw, 0-loss
def check_outcome(event):
        oc=event.get("event_data", {}).get("outcome")
        possibleOutcomes={1, 0.5, 0}
        if isinstance(oc, (float, int)) and oc in possibleOutcomes:
                return True
        else:
                return False

#Validating events by deviceOS: Android, iOS
def check_deviceOS(event):
        et=check_event_type(event)
        validDeviceOS={"iOS", "Android"}
        validEventTypes={"registration", "session_ping"}
        if et not in validEventTypes:
                return False
        else:
                dos=event.get("event_data", {}).get("device_os")
                if isinstance(dos, str) and dos in validDeviceOS:
                        return True
                else:
                        return False


#PlayerId has to be string - event validation
def check_playerId(playerId):
        return isinstance(playerId, str) and playerId !=""

#UserId has to be string - event validation
def check_userId(event):
        userId=event.get("user_id")
        return check_playerId(userId)


#Player and his opponent need to have different user_id - event validation
def check_opponentId(event):
        et=check_event_type(event)
        validEventTypes={"match_start", "match_finish"}
        if et not in validEventTypes:
                return False
        else:
                userId=event.get("user_id")
                opponentId=event.get("event_data", {}).get("opponent_id")
                if not check_playerId(userId) or not check_playerId(opponentId):
                        return False
                else:
                        if userId == opponentId:
                                return False
                        else:
                                return True

#Main function for event validation, using previous help functions
def check_valid_event(event):
        typeGroup1={"registration", "session_ping"}
        typeGroup2={"match_start", "match_finish"}
        et=check_event_type(event)
        if et is None:
                return False
        if not check_event_data(event):
                return False
        if not check_timestamp(event):
                return False
        if not check_userId(event):
                return False
        if et in typeGroup1:
                if not check_deviceOS(event):
                        return False
        if et in typeGroup2:
                if not check_opponentId(event):
                        return False
        if et=="match_finish":
                if not check_outcome(event):
                        return False
        return True

#Main event cleaning function, using previous help functions
def clean_events(events):
        noCopies=discard_copies(events)

        cleaned=[]
        for event in noCopies:
                if check_valid_event(event):
                        cleaned.append(event)
        
        return cleaned