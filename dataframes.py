import json
import pandas as pd
import numpy as np

# Purpose: Only keep users with at least 5 reviews
# Parameters: final_user_data, a dict of all users from the review bank
# Produces: pruned_user_data, a dict with users of at least 5 reviews
def prune_users(final_user_data: dict):
    pruned_user_data = {}
    for userid in final_user_data:
        if len(final_user_data[userid]) >= 5:
            pruned_user_data[userid] = final_user_data[userid]
    return pruned_user_data

def make_user_dataframe(user_data_dict: dict):
    user_data = pd.DataFrame(columns=["user_id", "app_id", "total_playtime", "last_played", "voted_up?"])
    for userid in user_data_dict:
        for appid in user_data_dict[userid]:
            user_data.append(user_data_dict[userid][appid], ignore_index=True)
    return user_data
            
def make_app_dataframe(final_app_data: dict):
    app_data = pd.DataFrame(columns=["appid, wilson_score, tags, price, developers"])
    for appid in final_app_data:
        app_data.append(final_app_data[appid])
    return app_data
    


with open("data/apps_data/final_user_data.json", "r") as infile:
    final_user_data = json.load(infile)
    
pruned_user_data = prune_users(final_user_data)
formatted_response = json.dumps(pruned_user_data, indent=4)
with open("data/apps_data/pruned_user_data.json", "w") as outfile:
    outfile.write(formatted_response)