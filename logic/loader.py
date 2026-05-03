import json

#Loading events.jsonl
def load_events(path):
        events=[]

        with open(path,"r") as f:
                for line in f:
                        line=line.strip()
                        if len(line)==0:
                                continue
                        
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                               continue
        return events


#Checking keys in events
def check_event(event):
        eventKeys={"id", "timestamp", "event_type", "user_id", "event_data"}
        return eventKeys.issubset(event.keys())


#Filtering, saving only valid events
def get_valid(events):
        validEvents=[]
        for event in events:
                if check_event(event):
                       validEvents.append(event)
        return validEvents


#Loading maps.jsonl
def load_maps(path):
        maps=[]

        with open(path,"r") as f:
                for line in f:
                        line=line.strip()
                        if len(line)==0:
                                continue
                        
                        try:
                            maps.append(json.loads(line))
                        except json.JSONDecodeError:
                               continue
        return maps


#Validating maps by keys, same as events
def check_maps(m):
       mapKeys={"id", "name"}
       return mapKeys.issubset(m.keys())


#Filtering, saving only valid maps, same as events
def get_valid_maps(maps):
        validMaps=[]
        for m in maps:
                if check_maps(m):
                     validMaps.append(m)
        return validMaps