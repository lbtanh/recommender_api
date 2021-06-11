# USAGE
# Start the server:
# 	python rs_run_server.py
# Submita a request via Python:
#	python rs_run_client.py
#   $ gunicorn -w 30 -b 0.0.0.0:5000 rs_run_server:aioapp -k aiohttp.worker.GunicornWebWorker

from aiohttp import web
from aiohttp_wsgi import WSGIHandler
from flask import Flask

import numpy as np
import flask
import io
import json
from flask import request
from rs_influencer_recommend import *
import pdb, time
from threading import Thread
from utils import recommend_utils
from utils.constants import PORT_INFLUENCER_RECOMMEND, HOST_INFLUENCER_RECOMMEND,RANDOM_KEYWORD
import random
from FacebookCrawler import update_business_all, facebook_graph_api
from cassandra.query import dict_factory
from datetime import datetime
import pandas as pd
# import gc
# initialize our Flask application 
app = flask.Flask(__name__)
logger = recommend_utils.get_logger('rs_run_server.log')

@app.route("/", methods=["POST", "GET"])
def hello():
    now = datetime.now()
    return "Hello arrivetechnologies.com \n Influencer recommender is working... " + str(now)

@app.route("/predict_inf",methods=["POST"])
def predict():
    now = datetime.now()
    if flask.request.method == "POST":
        try:
            # print (request.is_json)
            content = request.get_json()
            logger.warning("###### request content : %s"%str(content))
            try:
                key_words = content['list_key_word']
                user_id = content['user_id']
                ig_id = 'anhlbt' #content['ig_id']
                acc_type = content['acc_type']
                num_results = content['num_results']
                num_followers = content['num_followers'] # min number of follower
                aify_followers = content['aify_followers'] # min number of follower aify account
            except Exception as ex:
                logger.error(ex)
            if key_words == "" or key_words is None:
                set_business_word = ['Entertainment', 'Fashion', 'Lifestyle', 'Food And Drinks', 'Travel And Tourism','Travel','clothing','Gym Fashion','Photography','Modeling','Fitness Photography','Comercial']
                rnd = random.randint(0,len(set_business_word) - 1)
                key_words = set_business_word[rnd]
        except Exception as ex:
            logger.error(ex)
            print(ex)
            return flask.jsonify({"error":str(ex)})
        # pdb.set_trace()
        try:
            df_result = None
            df_aify = pd.DataFrame()
            df_aify, preds2 = sim_inf2.predict_similar(key_words, sim_inf2.tfidf_matrix, num_results, 0, False,num_followers, aify_followers)
            df_aify['engagement'] = df_aify['id_app'].apply(lambda x: sim_inf2.get_engagement(x))
        except Exception as ex:
            logger.error(ex)
            pass   

        if df_aify.shape[0] > num_results:
            df_result = df_aify[:num_results]
        else:
            try:
                # pdb.set_trace()
                df_crawl = pd.DataFrame()
                df_crawl, preds = sim_inf.predict_similar(key_words, sim_inf.tfidf_matrix, num_results * 4, acc_type,True,num_followers, aify_followers)
                # print(df_crawl)

                # check with updated_date
                ndays = 100

                # print("first: %s"%str(df_crawl.shape))
                df_crawl['DAYS'] = datetime.now()
                df_crawl['num_day'] = df_crawl.apply(recommend_utils.subtract_timestamp, axis = 1)
                df_crawl = df_crawl[df_crawl['num_day'] <= ndays]
                # df_crawl.to_csv('df_crawl.csv')
                # print("second: %s"%str(df_crawl.shape))

                if df_aify.shape[0] >= 0:
                    df_result = pd.concat([df_aify, df_crawl[:num_results - df_aify.shape[0]]], sort= True)
                    # print("third: %s"%str(df_result.shape))
                else:
                    try:
                        df_result =  df_crawl[:num_results]  
                    except Exception as ex:
                        df_result =  df_crawl
                    # print("third: %s"%str(df_result.shape))     
            except Exception as ex:
                logger.error(ex)
                print(ex)
                if df_crawl.shape[0] > 0:
                    df_result =  df_crawl
                elif df_aify.shape[0] > 0:
                    df_result = df_aify
                else:
                    df_result = ""
                return df_result.to_json(orient = 'index')                



        # OverflowError: Unsupported UTF-8 sequence length when encoding string
        # df = df.loc[:, df.columns != 'ts']

        # for x in sorted_inds[:2]:
        # #     print(x, preds[x], sim_inf.dfl['categories'].iloc[x])
        #     print(x, preds[x], sim_inf.df.iloc[x].to_json())
        # print(sim_inf.df.iloc[sorted_inds].to_json(orient='index'))
        
        # return sim_inf.df.iloc[sorted_inds].to_json(orient='index')

        # sample_data_influencer = json.loads(open('./influencer.json').read())
        # sample_data_brand = json.loads(open('./brand.json').read())
        # if acc_type == 0:
        #     return json.dumps(sample_data_influencer)
        # elif acc_type == 1:
        #     return json.dumps(sample_data_brand)
        # else:
        #     return json.dumps(sample_data_influencer)

        # return df_result.to_json(orient = 'index')

        try: 
            # pdb.set_trace()
            df_result = df_result.reset_index(drop = True)
            # remove itself
            df_result = df_result[~df_result.username.isin([ig_id])]
            # check with watch list
            sim_inf2.db.session.row_factory = dict_factory
            wl = sim_inf2.wl_get(user_id= user_id)
            if wl and wl['data'] != None:
                lst_wl = wl['data']
                df_result= df_result[~df_result.username.isin(lst_wl)]
            # print(df_result.columns)    
            df_result = df_result.sort_values(by ='followers_count',ascending=False)
            df_result_ = df_result.to_json(orient = 'index')
            return  df_result_# df_result_[df_result_['username'] not in lst_wl]
        except Exception as ex:
            logger.error(ex)
            print(ex)
            return ""



def thread_pull_from_db(threadname):
    global sim_inf
    # sim_inf = None
    # sim_inf = similar_influencer()
    # sim_inf.init_data_from_data_crawl()
    while 1:
        try:
            # sim_inf = None
            sim_inf = similar_influencer()
            sim_inf.init_data_from_data_crawl()
            logger.info('\n======== %s thread_pull_data_crawl is working...========'%str(datetime.now()))
            # gc.collect(sim_inf2)
            time.sleep(86400) #300
            # time.sleep(60)
        except Exception as ex:
            print(ex)
            logger.error(ex)
            time.sleep(60)
            pass   

def thread_pull_from_aify(threadname):
    global sim_inf2
    # sim_inf2 = None
    # sim_inf2 = similar_influencer()
    # sim_inf2.init_data_from_aify_app()
    while 1:
        try:
            # pdb.set_trace()
            
            # sim_inf2 = None
            
            sim_inf2 = similar_influencer()
            # print('time" %s'%str(sim_inf2.t))
            sim_inf2.init_data_from_aify_app()
            logger.info('\n======== %s thread_pull_data_aify is working...========'%str(datetime.now()))
            # break
            # gc.collect(sim_inf2)
            # time.sleep(60)
            time.sleep(86400) #300
            
        except Exception as ex:
            print(ex)
            logger.error(ex)
            time.sleep(60)
            pass   
     

# load the tfidf_matrix for predict jobs and
# then start the server

def setup(app):
    try: 
        logger.info("* Loading tfidf_matrix and Flask starting server...\nplease wait until server has fully started")
        time.sleep(1)
        thread_pull_data = Thread( target = thread_pull_from_db, args =('Thread pull data data scrawl', ))
        thread_pull_data.start()
        
        time.sleep(10)
        
        thread_pull_data_aify = Thread(target = thread_pull_from_aify, args =('Thread pull data aify', ))
        thread_pull_data_aify.start()
        sim_inf.init_data_from_data_crawl()
        sim_inf2.init_data_from_aify_app()

        time.sleep(10)

    except Exception as ex:
        print(ex)
        logger.error(ex)  

def make_aiohttp_app(app):
    wsgi_handler = WSGIHandler(app)
    aioapp = web.Application()
    aioapp.router.add_route('*', '/{path_info:.*}', wsgi_handler)
    return aioapp

setup(app)
aioapp = make_aiohttp_app(app)

if __name__ == "__main__":
      
    while(1):
        try:
            # setup(app)
            # aioapp = make_aiohttp_app(app)
            time.sleep(2)
            if sim_inf.df.shape[0] > 0 and sim_inf2.df.shape[0] > 0:
                app.run(host = HOST_INFLUENCER_RECOMMEND, port=PORT_INFLUENCER_RECOMMEND, debug=False)    
                logger.warning("Service is running...")
                break
            else:
                time.sleep(5)
                print('not ready')
        except Exception as ex:
            print(ex)
            logger.error(ex) 
            time.sleep(10)
       
