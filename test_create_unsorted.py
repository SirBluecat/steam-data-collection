import pandas as pd
# import tqdm
import time
import numpy as np
import json
import steam.webapi

# Private API key
def get_keys(path):
    with open(path) as f:
        return json.load(f)

api_key = get_keys(".private/steam_api.json")['API_Key']

path = "data/apps_list_0.json"
with open(path, "r") as infile:
    apps_list = json.load(infile)

# Euro Truck Sim 2
app_dict = apps_list['response']['apps'][1725]
print(app_dict['name'])

# skip empty entries
if app_dict['name'] == "":
    raise Exception("Name is empty.")

# appid of current game
appid = str(app_dict["appid"])

# Check that current appid corresponds to a released game
try:
    game_info = steam.webapi.webapi_request('http://store.steampowered.com/api/appdetails', method='GET', params={'key': api_key, 'appids': appid})
except:
    raise Exception("Could not get app details from API")

if game_info[appid]["success"] == False:
    raise Exception("game_info[appid][success] is False.")

if game_info[appid]['data']['release_date']['coming_soon'] == True:
    raise Exception("Release date is coming soon")

# Pull number of players for the current game
try:
    concurrent_players_dict = steam.webapi.webapi_request('https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/', method='GET', params={'key': api_key, 'appid': appid})
except:
    raise Exception("Could not get current number of players from API.")

# put in other app data
if 'genres' in game_info[appid]['data']:
    app_dict['genres'] = game_info[appid]['data']['genres']
if 'developers' in game_info[appid]['data']:
    app_dict['developers'] = game_info[appid]['data']['developers']
if 'publishers' in game_info[appid]['data']:
    app_dict['publishers'] = game_info[appid]['data']['publishers']
if 'price_overview' in game_info[appid]['data']:
    app_dict['price_overview'] = game_info[appid]['data']['price_overview']

# Put number of players into the app's dictionary
if concurrent_players_dict["response"]["result"] == 1:
    num_concurrent_players = concurrent_players_dict["response"]["player_count"]
    app_dict['concurrent_players'] = num_concurrent_players
else:
    raise Exception("Concurrent number of players API response result was 0")


# Append the new app dictionary to the list
print("Everything went well.")
        