import steam.webapi
import json

# Defining api to call most played games
# Reference: https://steam.readthedocs.io/en/stable/api/steam.webapi.html
# most_played_api = WebAPI(key='DA3BA54FF1CECDD242659388A3951404', format='json', https=True, apihost='api.steampowered.com')

def get_keys(path):
    with open(path) as f:
        return json.load(f)

api_key = get_keys(".private/steam_api.json")['API_Key']

# Dictionary of parameters for GetMostPlayedGames
MostPlayedDict = {'key': api_key, 'appids': 270880}

# GetAppList Parameters
GetAppsList = {'key': api_key, 'include_dlc':False, 'include_software':False, 'include_videos':False,
               'include_hardware':False, 'max_results':25000, 'last_appid': 0}

# Returns 100 most played games
# response = steam.webapi.webapi_request('http://store.steampowered.com/api/appdetails', method='GET', params=MostPlayedDict)
# response = steam.webapi.webapi_request('https://api.steampowered.com/ISteamChartsService/GetGamesByConcurrentPlayers/v1/', method='GET', params=MostPlayedDict)
response = steam.webapi.webapi_request('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/', method='GET', params={'key': api_key, 'steamid':76561197970650133, 'include_played_free_games':True, 'appids_filter':[570]})
# response = steam.webapi.webapi_request('https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/', method='GET', params={'key': api_key, 'appid': "8780"})
# response = steam.webapi.webapi_request('https://api.steampowered.com/IStoreService/GetAppList/v1/', method='GET', params=GetAppsList)
# response = steam.webapi.webapi_request('https://api.steampowered.com/ISteamApps/GetAppList/v2/', method='GET', params={'key': api_key})
# response = steam.webapi.webapi_request('https://store.steampowered.com/appreviews/270880?json=1', method='GET', params={'key': api_key, 'filter': 'recent', 'num_per_page': 100})

# create app reviews URL
appid = "1860510"
URL = "https://store.steampowered.com/appreviews/{}?json=1".format(appid)

# response = steam.webapi.webapi_request(URL, method='GET', params={'key': api_key, 'day_range': 365, 'num_per_page': 100})

# print(response["258550"]['data']['release_date']['coming_soon'])

print(response['response']['game_count'])

formatted_response = json.dumps(response, indent=4)

with open("sample_data/owned_games_dota.json", "w") as outfile:
    outfile.write(formatted_response)