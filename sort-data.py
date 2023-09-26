import steam.webapi
import json
import bisect
import tqdm

# Private API key
def get_keys(path):
    with open(path) as f:
        return json.load(f)

api_key = get_keys(".private/steam_api.json")['API_Key']

# List to put app dictionaries in, then sort
final_apps_list = []

for i in range(18):
    with open("data/apps_concurrent/apps_concurrent_{}.json".format(str(i)), "r") as infile:
        apps_dict = json.load(infile)
    
    final_apps_list.extend(apps_dict["apps"])
        
final_apps_list.sort(key=lambda d : -d['concurrent_players'])

output_dict = json.dumps({"apps":final_apps_list}, indent=4)
with open("data/most_played.json", "w") as outfile:
    outfile.write(output_dict)

print("Done Sorting!")