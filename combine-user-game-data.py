import steam.webapi
import json
import pandas as pd
import numpy as np
from scipy.stats.mstats import winsorize
import tqdm
import time

def get_keys(path):
    with open(path) as f:
        return json.load(f)

api_key = get_keys(".private/steam_api.json")['API_Key']

with open("data/most_played.json", "r") as infile:
    games_by_players = json.load(infile)

# Function to get reviews dictionary for a game
# Input: game appid, as a string
# Output: dictionary containing 100 reviews 
def get_reviews(appid: int) -> dict:
    URL = "https://store.steampowered.com/appreviews/{}?json=1".format(str(appid))
    
    # Retry marker
    retry = 0
    
    # Check that current appid corresponds to a released game
    try:
        review = steam.webapi.webapi_request(URL, method='GET', params={'key': api_key, 'filter': 'recent', 'num_per_page': 100})
    except:
        retry = 1
        
    if retry == 1:
        time.sleep(2)
        try:
            review = steam.webapi.webapi_request(URL, method='GET', params={'key': api_key, 'filter': 'recent', 'num_per_page': 100})
        except:
            review = {'success': 0}
    return review

# Wilson Score Calculator with 95% confidence
def ci_lower_bound(num_pos, num_total):
    if num_total == 0:
        return 0
    z = 1.96    # 95% confidence interval
    phat = num_pos / num_total
    return (phat + z*z/(2*num_total) - z * np.sqrt((phat*(1-phat)+z*z/(4*num_total))/num_total))/(1+z*z/num_total)
    
# Takes a dataframe of user reviews and returns (unique) list of userids
def list_of_users(user_review_data):
    return np.unique(user_review_data["steamid"])
    

# Calculate average playtime of an app
# Uses Winsorizing to limit affect of outliers
# Motivated by the practice of game-idling
def calculate_avg_playtime(reviews_list: list, appid):
    time_played = []
    for review in reviews_list:
        retry = 0
        param_dict = {'key': api_key, 'steamid':review['author']['steamid'],'include_played_free_games':True, 'appids_filter':[appid]}
        try:
            response = steam.webapi.webapi_request('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/', method='GET', 
                                           params=param_dict)
        except:
            retry = 1
        
        if retry == 1:
            time.sleep(1)
            try:
                response = steam.webapi.webapi_request('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/', method='GET', 
                                            params=param_dict)
            except:
                continue
        if 'games' not in response['response']:
            time.sleep(1)
            try:
                response = steam.webapi.webapi_request('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/', method='GET', 
                                            params=param_dict)
            except:
                continue
        if 'games' not in response['response']:
            continue
        try:
            playtime = response['response']['games'][0]['playtime_forever']
            time_played.append(playtime)
        except:
            continue
        
    w = winsorize(np.array(time_played, dtype=np.float32), limits=[.05,.05])
    print("Times played: "+ str(time_played))
    print("Winsorized: " + str(w))
    print("Average:" + str(np.average(w)))
    return np.average(w)

# Function which takes a sorted list of game dictionaries and returns them with review data
# Input: input_games_dict={"apps":[list of app_dicts]}
# Output: game_data, a dictionary with additional review data
def make_game_data_dict(input_games_dict: dict, num_apps: int) -> dict:
    # Create dictionary to store final game data
    game_data = {}
    counter = 0
    with tqdm.tqdm(total=num_apps) as pbar: # progress bar
        for app_dict in input_games_dict["apps"]: # List of app dictionaries
    
            # current appid
            appid = app_dict["appid"]
            
            # get game review
            reviews_dict = get_reviews(appid)
            
            if reviews_dict['success'] == 0:
                pbar.update(1)
                continue
            
            # add reviews and ratings
            num_positive = reviews_dict['query_summary']['total_positive']
            num_total = reviews_dict['query_summary']['total_reviews']
            
            if num_total > 0:
                app_dict['percent_positive'] = num_positive / num_total
                app_dict['wilson_score'] = ci_lower_bound(num_positive, num_total)
            else:
                app_dict['percent_positive'] = None
                app_dict['wilson_score'] = None
            app_dict['reviews'] = reviews_dict['reviews']
            
            # Get average playtime of the game
            # app_dict['avg_playtime'] = calculate_avg_playtime(reviews_dict['reviews'], appid)
            
            
            # Put game into dictionary, keyed by its appid
            game_data[appid] = app_dict
            pbar.update(1)
            counter += 1
            if counter == num_apps:
                break
    return game_data



# Takes input from make_game_data_dict
# Outputs a dictionary of users with their playtime and rating of each game
# Key = steamid, data = dict of {appid, playtime, playtime / avg_playtime, voted_up?}
def make_user_review_profiles(game_review_data: dict):
    user_data = {}
    print("Creating user_data file")
    with tqdm.tqdm(total=len(game_review_data)) as pbar: # progress bar
        for appid in game_review_data:
            
            # Current app's id
            app_dict = game_review_data[appid]
            
            # Populate user_data with 
            for review in app_dict['reviews']:
                if review['author']['steamid'] not in user_data:
                    user_data[review['author']['steamid']] = {}
                    
                user_data[review['author']['steamid']][appid] = {'total_playtime':review['author']['playtime_forever'],
                                                                        'voted_up?':review['voted_up'],
                                                                        'last_played':review['author']['last_played'],
                                                                        'user_id':review['author']['steamid'],
                                                                        'app_id': appid}
            pbar.update(1)
                
    # print("Filling out user_data file")
    # with tqdm.tqdm(total=len(user_data)) as pbar: # progress bar
    #     for userid in user_data:
    #         for app_dict in game_review_data["apps"]:
    #             appid = app_dict["appid"]
    #             if appid not in user_data[userid]:
                    
    #                 # Call to Steam API for user data
    #                 response = steam.webapi.webapi_request('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/', 
    #                                                     method='GET', params={'key': api_key, 'steamid':userid, 'appids_filter':[227300]})
    #                 if response["game_count"] == 1:
    #                     user_data[userid][appid] = {'total_playtime':response["response"]["games"][0]["playtime_forever"],
    #                                                 'percentage_playtime':response["response"]["games"][0]["playtime_forever"]/app_dict['avg_playtime'],
    #                                                 'voted_up?':None,
    #                                                 "user_id":userid,
    #                                                 "app_id":appid}
        pbar.update(1)
    return user_data

def make_user_dataframe(user_data_dict: dict):
    user_data = pd.DataFrame(columns=["user_id", "app_id", "total_playtime", "last_played", "voted_up?"])
    for user in user_data_dict:
        for app in user_data[user]:
            user_data.append(user_data[user][app], ignore_index=True)
    
    return user_data

    



# add game review data
# path = "data/apps_data/sorted_app_details.json"
# with open(path, "r") as infile:
#     apps_list = json.load(infile)
    
# calculate_avg_playtime(get_reviews(570)["reviews"],570)
    
# game_review_data = make_game_data_dict(apps_list, 15000)
# formatted_response = json.dumps(game_review_data, indent=4)
# with open("data/apps_data/review_data.json", "w") as outfile:
#     outfile.write(formatted_response)
    
# with open("data/apps_data/review_data.json", "r") as infile:
#     game_review_data = json.load(infile)
    
# # print(game_review_data["730"]['appid'])
# user_data = make_user_review_profiles(game_review_data)
# formatted_response = json.dumps(user_data, indent=4)
# with open("data/apps_data/final_user_data.json", "w") as outfile:
#     outfile.write(formatted_response)