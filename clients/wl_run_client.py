import requests, json

# initialize the REST API endpoint URL along with the input
WATCH_LIST_URL = "http://linuxsws009:5001/wl_update_now_post"


# r = requests.post(WATCH_LIST_URL, 
#     headers={'Content-Type': 'application/json'}, 
#     data=json.dumps({"user_id":'anhlbt', "ig_id": 'natje_9999'}))

r = requests.get(WATCH_LIST_URL, 
    headers={'Content-Type': 'application/json'}, 
    data=json.dumps({"user_id":'anhlbt'}))

print(r.text)