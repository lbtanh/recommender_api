import sys
sys.path.insert(0, '/home/anh_lbt/atvn/sw_follou/recommender_api/database/')
import facebook_graph_api
import argparse, time, os
from threading import Thread
import constants
import models
import db_cassandra
import pandas as pd
from os.path import dirname, join
from cassandra.cqlengine import connection
from cassandra.query import dict_factory
from cassandra.util import uuid_from_time
from datetime import datetime
import pdb

# parser = argparse.ArgumentParser(description='Get Instagram profiles with API')

# parser.add_argument('--b', default=0, type=int, help='index of from')
# parser.add_argument('--e', default=4, type=int, help='index of to')
# parser.add_argument('--n', default='file_name.txt', type=str, help='file name to save')
# args = parser.parse_args()

def get_influencer_profiles(begin, end, cass_session, fb_graph):
    connection.set_session(cass_session)
    list_business_discovery_all = []
    # read instagram id 
    path = join(dirname(dirname(os.path.abspath(__file__))),constants.instagram_id_path_file)

    with open(path, "r") as read_file:
        list_id = read_file.read().split('\n')
#     f = open(writer_file, 'a')
    i = 0
    print('len list %s'%len(list_id[begin:end]))
    for instagram_id in list_id[begin:end]:
        
        if datetime.now().hour >= 8 and datetime.now().hour <= 19:
            time_sleep = 60
        else:
            time_sleep = 20    
        print('sleeping %s'%time_sleep)
        time.sleep(time_sleep)#constants.TIME_SLEEP
        i += 1
        # pdb.set_trace()
        print("====== %s ======" %(i))
        business_discovery_all = ''
        try:
            business_discovery_all = fb_graph.get_business_discovery_all(media_count = constants.MAX_MEDIA, username = instagram_id)#17841401610104138, 17841407517779759
            if 'error' not in business_discovery_all:
                print(business_discovery_all['username'])
                # create list to convert into df and save file
                # list_business_discovery_all.append(self.parser_influencer_data(business_discovery_all))
                dict_result = fb_graph.parser_influencer_data(business_discovery_all)
                dict_result['ts'] = uuid_from_time(time.time())
                event = models.UserBusinessDiscovery(**dict_result)
                event.save()
            else:
                print('error: %s'%instagram_id)
                if '32' in str(business_discovery_all['error']['code']):
                    print('limit reach...sleeping one hour...%s'%datetime.now())
                    time.sleep(3610)
        except Exception as ex:
            print(ex)
            pass
    # save df to csv
    # path = join(dirname(os.path.abspath(__file__)),constants.IG_RESULT_FOLDER)
    # if not os.path.exists(path):
    #     os.makedirs(path)
    # pd.DataFrame(list_business_discovery_all).to_csv(join(path,save_file_name), sep='\t', index=None)
    # return list_business_discovery_all


# def thread1(threadname,fb_graph, begin, end,cass_session):
#     print('start %s....'%threadname)
#     fb_graph.get_influencer_profiles(begin, end,cass_session)
#     print('finished %s....'%threadname)

# def thread2(threadname,fb_graph, begin, end,cass_session):
#     print('start %s....'%threadname)
#     (fb_graph.access_token,fb_graph.user_id) = constants.TOKENS[1]
#     fb_graph.get_influencer_profiles(begin, end,cass_session)
#     print('finished %s....'%threadname)


if __name__=="__main__":
    # begin = args.b
    # end = args.e
    # file_name = args.n

    # begin = 1
    # end = 2
    # file_name = 'text.txt'

    cass_db = db_cassandra.db_cassandra(['172.33.47.9'],dict_factory)
    fb_graph = facebook_graph_api.FacebookGraphApi('./instagram_token.csv')
    #pdb.set_trace()
    get_influencer_profiles(2000, 10000, cass_db.session, fb_graph)

    # thread1 = Thread( target=thread1, args=("Thread-1",fb_graph, 2000, 3000,'3000.txt') )
    # thread2 = Thread( target=thread2, args=("Thread-2",fb_graph, 3000, 4000,'4000.txt' ) )
    # thread1.start()
    # time.sleep(1)
    # thread2.start()
    # time.sleep(1)


    
