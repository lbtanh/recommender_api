import sys, time
sys.path.insert(0, "./../../recommender_api")
import requests, json
from utils.constants import PORT_INFLUENCER_RECOMMEND, HOST_INFLUENCER_RECOMMEND

# initialize the REST API endpoint URL along with the input
# REST_API_URL = "http://ae7df70d0ada811e8b2840e36016edc5-1453902899.us-east-1.elb.amazonaws.com:5000/predict_inf"
REST_API_URL = "http://localhost:%s/predict_inf"%PORT_INFLUENCER_RECOMMEND
#REST_API_URL = "http://10.107.215.131:5000/predict_inf"
# print('test predict....')

# acc_type: # 0: influencer, 1: branch, 2: all
# num_results: # how many influencer (branhc) you want to get
# list_key_word: # tring, key words seperate by ','

# r = requests.post(REST_API_URL, 
#     headers={'Content-Type': 'application/json'}, 
#     data=json.dumps({"acc_type":1, "num_results": 50, "list_key_word": 'Entertainment, Fashion, Lifestyle, Food And Drinks, Travel And Tourism'}))

t1 = time.time()
r = requests.post(REST_API_URL, 
    headers={'Content-Type': 'application/json'}, 
    data=json.dumps({"user_id":"anhlbt", "ig_id":"tuananhtin" ,"acc_type":0, "num_results": 50, "num_followers":20000,"aify_followers":100,"list_key_word": '"Travel", "Makeup"'}))


print(r.text)
print('time to process: %s' %(time.time() - t1))