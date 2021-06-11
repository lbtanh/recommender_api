import sys
sys.path.insert(0, './../../recommender_api')
from FacebookCrawler import facebook_graph_api
import argparse, time, os
from threading import Thread
from utils import constants, recommend_utils
from database import models
from database import db_cassandra
import pandas as pd
from os.path import dirname, join
from cassandra.cqlengine import connection
from cassandra.query import dict_factory
from cassandra.util import uuid_from_time
from datetime import datetime
import pdb
import random
LOGGER = recommend_utils.get_logger('update_business_profife.log')
#crawl new account

def update_influencer_profiles(cass, fb_graph, run_continue, run_new_data): #update UsersBusinessDiscovery
    '''
    cass: cass connection
    fb_gragh: facebookAPI object
    run_continue: (boolen) update on next instagram_id (when stoped) otherwise run at begin
    run_new_data: (boolen) run on 
    
    '''
    try:
        
        connection.set_session(cass.session)
        list_business_discovery_all = []

        # pdb.set_trace()

        try:
            f = open("current_index", "r+")
        except FileNotFoundError:
            f = open("current_index", "w+")
        f.seek(0)
        current_index = f.read()
        
        try:
            current_index = int(current_index)
        except Exception as ex:
            current_index = 0
   
        if not run_continue:
            current_index = 0   
        #read instagram id from file
        # path = join(dirname(dirname(os.path.abspath(__file__))),constants.USERS_BUSINESS_DISCOVERY)
        # df = pd.read_csv(path, header=0, sep='\t')
        #read instagram id from database
        
        
        cass.session.row_factory = recommend_utils.pandas_factory
        # df = cass.exectute_query("select instagram_id from %s.recommend_influencer"%constants.KEYSPACE_NAME)
        # try:
        #     df= cass.session.execute("select instagram_id from %s.recommend_influencer"%constants.KEYSPACE_NAME, timeout = 50)
        #     df=df._current_rows
        # except Exception as ex:
        #     LOGGER.exception(ex)
        #     df = None
        # if df is None:

        path = join(dirname(dirname(os.path.abspath(__file__))),constants.INSTAGRAM_ID_PATH)
        df = pd.read_csv(path, header=0, sep='\t')
        
        # pdb.set_trace()
        df_exist = cass.exectute_query("select username from %s.users_business_discovery"%constants.KEYSPACE_NAME)
        # df_exist = cass.session.execute("select username from %s.users_business_discovery"%constants.KEYSPACE_NAME)
        df_exist.rename(columns = {'username':'instagram_id'}, inplace=True)

        # df = cass.session.execute("select instagram_id from %s.recommend_influencer"%constants.KEYSPACE_NAME)
        #run on different data from db
        if run_new_data:
            df_subtract = df.append(df_exist)
            df_subtract = df_subtract.drop_duplicates(keep = False)
            df = df_subtract
            # run_continue = False
        else:# run update 
            df = df_exist
        df = df.reset_index(drop = True)    
    except Exception as ex:
        LOGGER.error(ex) 

    cass.session.row_factory = dict_factory
    # data = {'instagram_id': ['jenjen7777', 'vnbeachhotel', 'tuananhtin']}
    # df = pd.DataFrame(data, columns = ['instagram_id'])
    # pdb.set_trace()
    if current_index > df.shape[0] - 110:
        current_index = 0

    for index, row in df.iterrows():

        if run_continue and index < current_index:
            continue
        # print(row['id'], row['username'])
        # if datetime.now().hour >= 8 and datetime.now().hour <= 20:
        #     time_sleep = constants.TIME_SLEEP
        # else:
        #     time_sleep = int(constants.TIME_SLEEP/2)
        # print('sleeping %s'%constants.TIME_SLEEP)
        # time.sleep(5)
        time.sleep(60)
        business_discovery_all = ''
        try:
            business_discovery_all = fb_graph.get_business_discovery_all(media_count = constants.MAX_MEDIA, username = row['instagram_id'])#17841401610104138, 17841407517779759
            if 'error' not in business_discovery_all:
                dict_result = fb_graph.parser_influencer_data(business_discovery_all)
                ##### dict_result['ts'] = uuid_from_time(time.time())
                # models.UserBusinessDiscovery.objects(id = dict_result['id'], username = dict_result['username'])\
                # .update(biography=dict_result['biography'], comments_count=dict_result['comments_count'], followers_count=dict_result['followers_count'], likes_count=dict_result['likes_count'], media_count = dict_result['media_count'], name = dict_result['name'], profile_picture_url = dict_result['profile_picture_url'], updated_date = datetime.now())
                
                #set overwrite
                dict_result['updated_date'] = datetime.utcnow()
                event = models.UserBusinessDiscovery(**dict_result)
                event.save()
                LOGGER.warning('#### Updated ...%s, index %s'%(row['instagram_id'], index))

                #write current_index to start at this user's index when system restart
                if f.closed:
                    f = open("current_index", "w+")
                f.seek(0)         
                f.write(str(index))
                f.close()

                (fb_graph.access_token,fb_graph.user_id) = constants.TOKENS[random.choice(fb_graph.test_tokens_valid())]
                LOGGER.warning('CHANGE TOKEN to: %s' %fb_graph.user_id)
            else:
                LOGGER.error('error: %s'%row['instagram_id'])
                if '32' in str(business_discovery_all['error']['code']):
                    # LOGGER.warning('***** limit reach...sleeping one hour...%s'%datetime.now())
                    LOGGER.warning('***** limit reach...CHANGE token to: %s'%fb_graph.user_id)
                    (fb_graph.access_token,fb_graph.user_id) = constants.TOKENS[random.choice(fb_graph.test_tokens_valid())]
                    
                    time.sleep(10)
                    
        except Exception as ex:
            LOGGER.error(ex)
            pass

# if __name__=="__main__":
#     try:
#         cass_db = db_cassandra.db_cassandra(constants.HOST_CASSANDRA_DB ,dict_factory)
#         fb_graph = facebook_graph_api.FacebookGraphApi('./instagram_token.csv')
#         # (fb_graph.access_token,fb_graph.user_id) = constants.TOKENS[0]
            
#         print('running....with account: %s'%fb_graph.user_id)
#         #pdb.set_trace()
#         update_influencer_profiles(cass_db.session, fb_graph, True)
#     except Exception as ex:
#         LOGGER.exception(ex)    



    
