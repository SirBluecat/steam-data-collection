import steam.webapi
import json
import bisect
import tqdm
import time
import requests

# r = requests.get('https://steamspy.com/api.php', {'request': 'appdetails', 'appid': 730})
# print(r.json()['tags'])

def combine_data(review_data: dict, sorted_app_details: dict):
    final_app_data = review_data
    with tqdm.tqdm(total=len(review_data)) as pbar: # progress bar
        for appid in review_data:
            final_app_data[appid].pop('reviews')
            retry = 0
            
            try:
                info = requests.get('https://steamspy.com/api.php', {'request': 'appdetails', 'appid': appid})
                tags = info.json()['tags']
                final_app_data[appid]['tags'] = tags
            except:
                retry = 1
                
            if retry == 1:
                time.sleep(1)
                try:
                    info = requests.get('https://steamspy.com/api.php', {'request': 'appdetails', 'appid': appid})
                    tags = info.json()['tags']
                    final_app_data['tags'] = tags
                except:
                    print("API failure")
            
            # info = requests.get('https://steamspy.com/api.php', {'request': 'appdetails', 'appid': appid})
            # tags = info.json()['tags']
            # print(tags)
            # final_app_data['tags'] = tags
            
            try:
                final_app_data['price'] = sorted_app_details['price']
            except:
                pass
            
            pbar.update(1)
    return final_app_data
    
with open("data/apps_data/review_data.json", "r") as infile:
    review_data = json.load(infile)
    
with open("data/apps_data/sorted_app_details.json", "r") as infile:
    sorted_app_data = json.load(infile)
    
# print(game_review_data["730"]['appid'])
final_app_data = combine_data(review_data,sorted_app_data)
formatted_response = json.dumps(final_app_data, indent=4)
with open("data/apps_data/final_app_data.json", "w") as outfile:
    outfile.write(formatted_response)