import steam.webapi
import json
import bisect
import tqdm
import time

# Private API key
def get_keys(path):
    with open(path) as f:
        return json.load(f)

api_key = get_keys(".private/steam_api.json")['API_Key']

# Function to get lists of steam games
def get_games_from_steam():
    # GetAppList Parameters
    GetAppsList = {'key': api_key, 'include_dlc':False, 'include_software':False, 'include_videos':False,
                'include_hardware':False, 'max_results':5000, 'last_appid': 0}

    # Retrieve apps_list from steam
    response = steam.webapi.webapi_request('https://api.steampowered.com/IStoreService/GetAppList/v1/', method='GET', params=GetAppsList)

    # Put apps_list into file
    formatted_response = json.dumps(response, indent=4)
    with open("data/apps_list/apps_list_0.json", "w") as outfile:
        outfile.write(formatted_response)
        
    # Continue retrieving apps_lists
    file_num = 1
    while 'last_appid' in response['response']:
        GetAppsList['last_appid'] = response['response']['last_appid']
        response = steam.webapi.webapi_request('https://api.steampowered.com/IStoreService/GetAppList/v1/', method='GET', params=GetAppsList)
        
        formatted_response = json.dumps(response, indent=4)
        path = "data/apps_list_{}.json".format(str(file_num))
        # print(path)
        with open(path, "w") as outfile:
            outfile.write(formatted_response)
        
        file_num += 1



# Overestimate number of apps
num_apps = 86000

# Get concurrent players
def get_concurrent_players():
    with tqdm.tqdm(total=num_apps) as pbar: # progress bar
        for i in range(18):
            
            # Dictionary which will store list of app dictionaries
            dict_of_games = {"apps":[]}
            
            # Open i-th apps_list file
            path = "data/apps_list/apps_list_{}.json".format(str(i))
            with open(path, "r") as infile:
                apps_list = json.load(infile)
                
            for app_dict in apps_list["response"]["apps"]:
                # skip empty entries
                if app_dict['name'] == "":
                    pbar.update(1)
                    continue
                
                # appid of current game
                appid = str(app_dict["appid"])
                
                # Retry Marker
                retry = 0
                
                # Pull number of players for the current game
                try:
                    concurrent_players_dict = steam.webapi.webapi_request('https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/', method='GET', params={'key': api_key, 'appid': appid})
                except:
                    retry = 1
                
                if retry == 1:
                    time.sleep(2)
                    try:
                        concurrent_players_dict = steam.webapi.webapi_request('https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/', method='GET', params={'key': api_key, 'appid': appid})
                    except:
                        pbar.update(1)
                        continue

                # Put number of players into the app's dictionary
                try:
                    num_concurrent_players = concurrent_players_dict["response"]["player_count"]
                    app_dict['concurrent_players'] = num_concurrent_players
                except:
                    pbar.update(1)
                    continue
                
                # Append the new app dictionary to the list
                dict_of_games["apps"].append(app_dict)
                
                pbar.update(1)
            
            formatted_response = json.dumps(dict_of_games, indent=4)
            with open("data/apps_concurrent/apps_concurrent_{}.json".format(str(i)), "w") as outfile:
                outfile.write(formatted_response)

# Function to get data about games
# Input: num_apps, number of applications to include in final data list
#        path, the path to the input file (from sort-data.py)
def get_game_data(num_apps, path):
    with tqdm.tqdm(total=num_apps) as pbar: # progress bar
        
        # Open i-th apps_list file
        with open(path, "r") as infile:
            apps_list = json.load(infile)
            
        for i in range(num_apps):
            
            app_dict = apps_list["apps"][i]
            
            # appid of current game
            appid = str(app_dict["appid"])
            
            # Retry marker
            retry = 0
            
            # Check that current appid corresponds to a released game
            try:
                game_info = steam.webapi.webapi_request('http://store.steampowered.com/api/appdetails', method='GET', params={'key': api_key, 'appids': appid})
            except:
                retry = 1
                
            if retry == 1:
                time.sleep(2)
                try:
                    game_info = steam.webapi.webapi_request('http://store.steampowered.com/api/appdetails', method='GET', params={'key': api_key, 'appids': appid})
                except:
                    pbar.update(1)
                    continue
            if game_info[appid]["success"] == False or game_info[appid]['data']['release_date']['coming_soon'] == True:
                pbar.update(1)
                continue
            
            # put in other app data
            if 'genres' in game_info[appid]['data']:
                app_dict['genres'] = game_info[appid]['data']['genres']
            if 'developers' in game_info[appid]['data']:
                app_dict['developers'] = game_info[appid]['data']['developers']
            if 'publishers' in game_info[appid]['data']:
                app_dict['publishers'] = game_info[appid]['data']['publishers']
            if 'price_overview' in game_info[appid]['data'] and game_info[appid]['data']['price_overview']['currency']=='USD':
                app_dict['price'] = game_info[appid]['data']['price_overview']['final']
            
            pbar.update(1)
        
        formatted_response = json.dumps(apps_list, indent=4)
        with open("data/apps_data/sorted_app_details.json", "w") as outfile:
            outfile.write(formatted_response)
                
                
# get_games_from_steam()
# get_concurrent_players()
get_game_data(10000, "data/most_played.json")