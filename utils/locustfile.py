# locustfile.py
from locust import HttpLocust, TaskSet, task
import json, time

class UserBehavior(TaskSet):

    # def on_start(self):
    #     self.login()
    #     print('welcome locust....')

    # def login(self):
    #     # GET login page to get csrftoken from it
    #     response = self.client.get('/accounts/login/')
    #     csrftoken = response.cookies['csrftoken']
    #     # POST to login page with csrftoken
    #     self.client.post('/accounts/login/',
    #                      {'username': 'username', 'password': 'P455w0rd'},
    #                      headers={'X-CSRFToken': csrftoken})

    # @task(1)
    # def login(self):
    #     result = self.client.get("/securities/login") 
    #     token = re.search(r'[0-9]{10}##[a-z0-9]{40}',result.text).group(0)
    #     print token

    @task(1)
    def index(self):
        r = self.client.get('/')
        print(r.text)

    # #rs
    @task(2)
    def predict_inf(self):
        r = self.client.post('/predict_inf',headers={'Content-Type': 'application/json'}, 
        data=json.dumps({"user_id":"tuananhtin@gmail.com", "ig_id":"tuananhtin" ,"acc_type":0, "num_results": 50, "num_followers":20000,"aify_followers":100,"list_key_word": '"Travel", "Makeup"'}))
        print(r.text)

    # @task(3)
    # def predict_inf(self):
    #     r = self.client.get('/wl_get',headers={'Content-Type': 'application/json'}, 
    #     data=json.dumps({"user_id":'anhlbt', "acc_type":0}))
    #     print(r.text)    



class WebsiteUser(HttpLocust):
    min_wait = 2000
    max_wait = 5000
    task_set = UserBehavior


    
# gunicorn -w 24 -b 0.0.0.0:5000 rs_run_server:app
# gunicorn -w 24 --threads 4 -b 0.0.0.0:5000 rs_run_server:app
#  uwsgi --http 0.0.0.0:5000 --module rs_run_server:app   
# gunicorn -w 30 -b 0.0.0.0:5000 rs_run_server:aioapp -k aiohttp.worker.GunicornWebWorker


#how to run
# cd to this directory
#run: locust --host=http://0.0.0.0:5000             
# locust --host=http://ae7df70d0ada811e8b2840e36016edc5-1453902899.us-east-1.elb.amazonaws.com:5000/

# watchlist
# locust --host=http://ab909ba0fada911e8b2840e36016edc5-283609900.us-east-1.elb.amazonaws.com:5001/