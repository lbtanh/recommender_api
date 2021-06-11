import sys
sys.path.insert(0, "./../../recommender_api")
import requests, json, time
from utils.constants import PORT_WATCH_LIST, HOST_WATCH_LIST
# initialize the REST API endpoint URL along with the input

t1 = time.time()
####add
# WATCH_LIST_URL = "http://localhost:%s/wl_add"%PORT_WATCH_LIST
# r = requests.post(WATCH_LIST_URL, 
#     headers={'Content-Type': 'application/json'}, 
#     data=json.dumps({"user_id":'anhlbt', "ig_id": 'tuananhtin',"picture_url":"tuoitre.com.vn" ,"acc_type":3}))

# # remove
# WATCH_LIST_URL = "http://localhost:%s/wl_remove"%PORT_WATCH_LIST
# r = requests.post(WATCH_LIST_URL, 
#     headers={'Content-Type': 'application/json'}, 
#     data=json.dumps({"user_id":'anhlbt', "ig_id": 'tuananhtin'}))#natje_9999


# get_new_post, not use ()
# WATCH_LIST_URL = "http://localhost:%s/wl_update_now_post"%PORT_WATCH_LIST
# r = requests.get(WATCH_LIST_URL, 
#     headers={'Content-Type': 'application/json'}, 
#     data=json.dumps({"user_id":'anhlbt'}))


# get_wl
WATCH_LIST_URL = "http://localhost:%s/wl_get"%PORT_WATCH_LIST#
###WATCH_LIST_URL = "http://ab909ba0fada911e8b2840e36016edc5-283609900.us-east-1.elb.amazonaws.com:5001/wl_get"
r = requests.get(WATCH_LIST_URL, 
    headers={'Content-Type': 'application/json'}, 
    data=json.dumps({"user_id":'anhlbt', "acc_type":0}))


# # get_wl_info_detail
# WATCH_LIST_URL = "http://localhost:%s/wl_get_info_detail"%PORT_WATCH_LIST
# #WATCH_LIST_URL = "http://ab909ba0fada911e8b2840e36016edc5-283609900.us-east-1.elb.amazonaws.com:5001/wl_get"
# r = requests.get(WATCH_LIST_URL, 
#     headers={'Content-Type': 'application/json'}, 
#     data=json.dumps({"social_id":'9c88c600-ac5f-11e8-80f4-eb836fc406ca', 'from_timestamp':1531686400, 'until_timestamp':1631686400}))
#     # social_id = '9c88c600-ac5f-11e8-80f4-eb836fc406ca'

print(r.text)

print('time to request: %s'%(time.time() - t1))