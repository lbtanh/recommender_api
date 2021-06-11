
import numpy as np

import io
import json
from rs_influencer_recommend import *
import pdb, time
from threading import Thread
from utils import recommend_utils
from database import db_cassandra
from utils.constants import PORT_INFLUENCER_RECOMMEND, HOST_INFLUENCER_RECOMMEND,RANDOM_KEYWORD
import random
from cassandra.query import dict_factory
from datetime import datetime
from database import models
from cassandra.cqlengine import connection
from cassandra.util import uuid_from_time
logger = recommend_utils.get_logger('rs_write_result_db.log')
pd.options.mode.chained_assignment = None

def predict(df, acc_type, num_results):
    now = datetime.now()
    try:
        # print (request.is_json)
        # print("request: %s"%now)l
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
    # pdb.set_trace()
    try:
        # pdb.set_trace()
        df_aify = pd.DataFrame()
        df_aify, preds2 = sim_inf2.predict_similar(key_words, sim_inf2.tfidf_matrix, num_results, 0, False,num_followers, aify_followers)
        # remove itself
        df_aify = df_aify[~df_aify.username.isin([df['username']])]
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
            df_crawl, preds = sim_inf.predict_similar(key_words, sim_inf.tfidf_matrix, num_results, acc_type,True,num_followers, aify_followers)
            # print(df_crawl)
            if df_aify.shape[0] >= 0:
                df_result = pd.concat([df_aify, df_crawl[:num_results - df_aify.shape[0]]])
            else:
                df_result =  df_crawl[:num_results]  
        except Exception as ex:
            logger.error(ex)
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
        logger.error(ex)
        return ""


def write_rs_result_into_db(cass_session, num_results = 100): #update UsersBusinessDiscovery
    try:
        # sim_inf2.db.session.row_factory = dict_factory
        connection.set_session(cass_session)

    except Exception as ex:
        logger.error(ex)    
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
            # res = json.dumps(res)    

            res_obj = models.RecommendResult(owner_id = row['id_app'], results= res, num_count = 100, updated = datetime.now())
            res_obj.save()
            logger.warning('#### Updated ...%s, index %s'%(row['username'], index))
            # LOGGER.warning('########%s'%datetime.now())
               
        except Exception as ex:
            logger.error(ex)
            pass



def thread_pull_from_db(threadname):
    global sim_inf
    # sim_inf = None
    # sim_inf = similar_influencer()
    while 1:
        try:
            sim_inf = similar_influencer()
            sim_inf.init_data_from_data_crawl()
            logger.info('\n======== %s thread_pull_data_crawl is working...========'%datetime.now())
            # time.sleep(600) #300
            break
        except Exception as ex:
            logger.error(ex)
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
            logger.info('\n======== %s thread_pull_data_aify is working...========'%datetime.now())
            # time.sleep(600) #300
            break
        except Exception as ex:
            logger.error(ex) 
            pass   

def thread_write_db(threadname):# write recommend result into db
    global cass_db
    while 1:
        try:
            time.sleep(1)
            cass_db = db_cassandra.db_cassandra(contact_points = constants.HOST_CASSANDRA_DB,port_= constants.PORT_CASSANDRA_RS ,factory =pandas_factory) # pandas_factory
            write_rs_result_into_db(cass_db.session)
            time.sleep(constants.RS_SIMILAR_SUPPORT_COEF) #1/2 day
        except Exception as ex:
            logger.error(ex)  
            pass            

# load the tfidf_matrix for predict jobs and
# then start the server

def setup():
    try: 
        logger.info("* Loading tfidf_matrix and Flask starting server...\nplease wait until server has fully started")
        time.sleep(2)
        thread_pull_data = Thread( target = thread_pull_from_db, args =('Thread pull data data scrawl', ))
        thread_pull_data.start()
        
        time.sleep(1)
        
        thread_pull_data_aify = Thread(target = thread_pull_from_aify, args =('Thread pull data aify', ))
        thread_pull_data_aify.start()

        time.sleep(10)
        thread_write_rs = Thread(target = thread_write_db, args =('Thread write recommend list....', ))
        thread_write_rs.start() 
    except Exception as ex:
        logger.error(ex)  


if __name__ == "__main__":
   
    setup()
    
    # pdb.set_trace()
    # pre_result = predict(sim_inf2.df.iloc[0], 0)
    # print(pre_result)
    # try:
    #     cass_db = db_cassandra.db_cassandra(contact_points = constants.HOST_CASSANDRA_DB,port_= constants.PORT_CASSANDRA_RS ,factory =dict_factory) # pandas_factory
    #     write_rs_result_into_db(cass_db.session)
    # except Exception as ex:
    #     print(ex)    
    
    
    '''
    ['categories', 'id_app','id']
    ['account_type', 'biography', 'categories', 'comments_count',
       'followers_count', 'id', 'id_app', 'likes_count', 'media_count', 'name',
       'profile_picture_url', 'type_resource', 'updated_date', 'username']
    '''
    # while(1):
    #     try:
    #         setup()
    #         if sim_inf.df.shape[0] > 0 and sim_inf2.df.shape[0] > 0:
    #             # do something here
    #             # get data user categories, keyword_by_user

    #             owner_id = ''
    #             pre_result = predict(owner_id)

    #         else:
    #             time.sleep(1)
    #     except Exception as ex:
    #         logger.error(ex) 
       
