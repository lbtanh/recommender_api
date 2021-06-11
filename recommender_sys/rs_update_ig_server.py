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
from utils.constants import PORT_UPDATE_IG, HOST_UPDATE_IG
import random
from FacebookCrawler import update_business_all, facebook_graph_api
from cassandra.query import dict_factory
from datetime import datetime


from database import db_cassandra
from utils.constants import PORT_INFLUENCER_RECOMMEND, HOST_INFLUENCER_RECOMMEND,RANDOM_KEYWORD
from database import models
from cassandra.cqlengine import connection
from cassandra.util import uuid_from_time
pd.options.mode.chained_assignment = None

# from rs_influencer_recommend import *
# initialize our Flask application 
app = flask.Flask(__name__)
logger = recommend_utils.get_logger('rs_update_ig_server.log')
logger2 = recommend_utils.get_logger('rs_write_result_db.log')


def thread_update_db_crawl(threadname):#UserBusinessDiscovery
    '''
    update table users_business_discovery
    '''
    while 1:
        try:
            # pdb.set_trace()
            time.sleep(1)        
            #LOCAL
            cass_db = db_cassandra.db_cassandra(constants.HOST_CASSANDRA_DB ,dict_factory)
            #AMAZON
            # cass_db = db_cassandra.db_cassandra(contact_points = ["a084c6ef0b0e511e8b2840e36016edc5-791065256.us-east-1.elb.amazonaws.com"],port_= 9042 ,factory =pandas_factory)
            fb_graph = facebook_graph_api.FacebookGraphApi() # token_file =constants.HOME_DIR+'/FacebookCrawler/instagram_token.csv'
            # (fb_graph.access_token,fb_graph.user_id) = constants.TOKENS[0]
            print('\n=== %s thread_update IG profiles is working...==='%datetime.now())
            # print('running....with account: %s'%fb_graph.user_id)
            #mode update cass, fb_graph, run_continue, run_new_data
            update_business_all.update_influencer_profiles(cass_db, fb_graph, False, False)
            time.sleep(2*86400)
        except Exception as ex:
            logger.error(ex) 
            time.sleep(60)
            pass            

def predict(df, acc_type, num_results):
    now = datetime.now()
    try:
        key_words = df['categories']
        # user_id = df['user_id']
        acc_type = acc_type # # acc_type: # 0: influencer, 1: branch, 2: all
        num_results = num_results #df['num_results']
        num_followers = 10000 #df['num_followers'] # min number of follower
        aify_followers = 1000 #df['aify_followers'] # min number of follower aify account
        if key_words == "" or key_words is None:
            set_business_word = ['Entertainment', 'Fashion', 'Lifestyle', 'Food And Drinks', 'Travel And Tourism','Travel','clothing','Gym Fashion','Photography','Modeling','Fitness Photography','Comercial']
            rnd = random.randint(0,len(set_business_word) - 1)
            key_words = set_business_word[rnd]
    except Exception as ex:
        print(ex)
        return {"error":str(ex)}
    try:
        # pdb.set_trace()
        df_aify = pd.DataFrame()
        df_aify, preds2 = sim_inf2.predict_similar(key_words, sim_inf2.tfidf_matrix, num_results, 0, False,num_followers, aify_followers)
        # remove itself from list recommend
        df_aify = df_aify[~df_aify.username.isin([df['username']])]
        df_aify['engagement'] = df_aify['id_app'].apply(lambda x: sim_inf2.get_engagement(x))
    except Exception as ex:
        logger2.error(ex)
        pass   

    if df_aify.shape[0] > num_results:
        df_result = df_aify[:num_results]
    else:
        try:
            # pdb.set_trace()
            df_crawl = pd.DataFrame()
            df_crawl, preds = sim_inf.predict_similar(key_words, sim_inf.tfidf_matrix, num_results, acc_type,True,num_followers, aify_followers)
            if df_aify.shape[0] >= 0:
                df_result = pd.concat([df_aify, df_crawl[:num_results - df_aify.shape[0]]])
            else:
                df_result =  df_crawl[:num_results]  
        except Exception as ex:
            logger2.error(ex)
            if df_crawl.shape[0] > 0:
                df_result =  df_crawl
            elif df_aify.shape[0] > 0:
                df_result = df_aify
            else:
                df_result = ""
            return df_result                   

    try: 
        # pdb.set_trace()
        df_result = df_result.reset_index(drop = True)

        
        # # check with watch list
        # sim_inf2.db.session.row_factory = dict_factory
        # wl = sim_inf2.wl_get(user_id= user_id)
        # if wl and wl['data'] != None:
        #     lst_wl = wl['data']
        #     df_result= df_result[~df_result.username.isin(lst_wl)]
        # print(df_result.columns)  

        # pdb.set_trace()
        df_result = df_result.sort_values(by ='followers_count',ascending=False)
        # df_result = df_result.to_dict('index')
        df_result = df_result.to_json(orient = 'index')
        return  df_result# df_result_[df_result_['username'] not in lst_wl]
    except Exception as ex:
        logger2.error(ex)
        return ""


def write_rs_result_into_db(cass_session, num_results = 100): #update UsersBusinessDiscovery
    try:
        # sim_inf2.db.session.row_factory = dict_factory
        connection.set_session(cass_session)
    except Exception as ex:
        logger2.error(ex)    
    for index, row in sim_inf2.df.iterrows():
        time.sleep(1)

        try:
            # dict_result['ts'] = uuid_from_time(time.time())
            # pdb.set_trace()
            # dict_result['updated_date'] = datetime.utcnow()
            pre_result_0 = predict(sim_inf2.df.iloc[index], 0, num_results)
            pre_result_1 = predict(sim_inf2.df.iloc[index], 1, num_results)
            res = {}
            res['influencer_0'] = pre_result_0
            res['brand_1'] = pre_result_1   

            res_obj = models.RecommendResult(owner_id = row['id_app'], results= res, num_count = 100, updated = datetime.now())
            res_obj.save()
            logger2.warning('#### Recommend Updated ...%s, index %s'%(row['username'], index))
            # LOGGER.warning('########%s'%datetime.now())
               
        except Exception as ex:
            logger2.error(ex)
            pass


def thread_pull_from_db(threadname):
    global sim_inf
    # sim_inf = None
    # sim_inf = similar_influencer()
    while 1:
        try:
            sim_inf = similar_influencer()
            sim_inf.init_data_from_data_crawl()
            logger2.info('\n===== %s thread_pull_data_crawl is working...====='%datetime.now())
            # time.sleep(600) #300
            break
        except Exception as ex:
            logger2.error(ex)
            pass   

def thread_pull_from_aify(threadname):
    global sim_inf2
    # sim_inf2 = None
    # sim_inf2 = similar_influencer()
    while 1:
        try:
            # pdb.set_trace()
            sim_inf2 = similar_influencer()
            sim_inf2.init_data_from_aify_app()
            logger2.info('\n===== %s thread_pull_data_aify is working...====='%datetime.now())
            # time.sleep(600) #300
            break
        except Exception as ex:
            logger2.error(ex) 
            pass   

def thread_write_db(threadname):# write recommend result into db
    global cass_db
    while 1:
        try:
            time.sleep(1)
            cass_db = db_cassandra.db_cassandra(contact_points = constants.HOST_CASSANDRA_DB,port_= constants.PORT_CASSANDRA_RS ,factory =pandas_factory) # pandas_factory
            write_rs_result_into_db(cass_db.session)
            time.sleep(constants.RS_TIME_SLEEP_GET_NEW_DATA) #1/2 day
        except Exception as ex:
            logger2.error(ex)  
            pass            

# load the tfidf_matrix for predict jobs and
# then start the server

def setup(app):
    try: 
        # logger2.info("* Loading tfidf_matrix and Flask starting server...\nplease wait until server has fully started")
        # time.sleep(2)
        # thread_pull_data = Thread( target = thread_pull_from_db, args =('Thread pull data data scrawl', ))
        # thread_pull_data.start()
        
        # time.sleep(1)
        # thread_pull_data_aify = Thread(target = thread_pull_from_aify, args =('Thread pull data aify', ))
        # thread_pull_data_aify.start()

        # time.sleep(10)
        # thread_write_rs = Thread(target = thread_write_db, args =('Thread write recommend list....', ))
        # thread_write_rs.start() 

        time.sleep(1)
        thread_update_data_crawl = Thread(target = thread_update_db_crawl, args =('Thread update data draw aify', ))
        thread_update_data_crawl.start() 
    except Exception as ex:
        logger.error(ex)  


setup(app)

if __name__ == "__main__":
    while(1):
        try:
            app.run(host = HOST_UPDATE_IG, port=PORT_UPDATE_IG, debug=False)    
            time.sleep(1)
            break
        except Exception as ex:
            logger.error(ex)
            time.sleep(60)
       
