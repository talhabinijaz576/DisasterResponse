

def getDefaultContext(tab="Simulation"):
    context = {}
    context["nav_items"] = getNavItems(tab)
    context["CenterType"] = tab 
    return context


def getNavItems(tab):

    nav_items = { 
                 "Simulation" : [[False, "/controlroom/home", "play_arrow"]],
                 "Police Stations" : [[False, "/manager/policestations", "local_police"]],
                 "Hospitals" : [[False, "/manager/hospitals", "local_hospital"]],
                 "Fire Stations" : [[False, "/manager/firestations", "local_fire_department"]],
    #             "Dispatch Centers": [ [False, "/developer/assets", "security"], 
    #                                    {"Police Stations": [False, "/developer/assets", "PS"], 
    #                                     "Hospitals": [False, "/developer/assets", "HS"], 
    #                                     "Firestations": [False, "/developer/asset_access_keys", "FS"]} ]
    }



    if(type(tab)==str):
        nav_items[tab][0][0] = True

    return nav_items
