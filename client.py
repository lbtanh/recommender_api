import requests, json

# initialize the REST API endpoint URL along with the input
REST_API_URL = "http://linuxsws009:5000/predict_inf"
# print('test predict....')

# acc_type: # 0: influencer, 1: branch, 2: all
# num_results: # how many influencer (branhc) you want to get
# list_key_word: # tring, key words seperate by ','

r = requests.post(REST_API_URL, 
    headers={'Content-Type': 'application/json'}, 
    data=json.dumps({"acc_type":0, "num_results": 10, "list_key_word": 'Entertainment, Fashion, Lifestyle, Food And Drinks, Travel And Tourism'}))

print(r.text)