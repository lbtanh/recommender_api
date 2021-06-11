import sys
sys.path.insert(0, "./../../recommender_api")
from utils import recommend_utils, constants
from database import models, db_cassandra
from datetime import datetime, timedelta
import time, os
from os.path import dirname, join
from cassandra.query import dict_factory
from FacebookCrawler import facebook_graph_api
from cassandra.cqlengine import columns, connection
import pdb, json
import pandas as pd

def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)
class watch_list():
    def __init__(self):
        # #get session
        # pdb.set_trace()
        try:
            time.sleep(0.5)
            self.loggers = recommend_utils.get_logger('watch_list.log')
            token_path = join(dirname(dirname(os.path.abspath(__file__))),'FacebookCrawler/'+constants.INSTAGRAM_TOKEN_FILE)
            # print(token_path)
            
            self.fb_graph = facebook_graph_api.FacebookGraphApi(token_path)
            # (self.fb_graph.access_token,self.fb_graph.user_id) = constants.TOKENS[4]
            self.db = db_cassandra.db_cassandra(contact_points = constants.HOST_CASSANDRA_DB, factory = dict_factory)
            # print(constants.HOST_CASSANDRA_DB)
            connection.set_session(self.db.session)
            
        except Exception as ex:
            print(ex)    


    def wl_get(self, user_id, wl_obj, convert_to_json = True, acc_type =2):
        result = {}
        try:
            # t1 = time.time()
            query_string="select * from watch_list where user_id = '%s'"%user_id
            re = wl_obj.db.session.execute(query_string)
            list_dict_ = recommend_utils.map_to_dict_factory_1(re.current_rows)#data get from db, list have only one item
        #     list_dict_ = re.current_rows
            
            if len(list_dict_) > 0 :
                if list_dict_[0]['watch_user_list'] is None:
                    result['status'] = 'True'
                    result['data'] = None
                else:    
                    result['status'] = 'True'
                    if convert_to_json:
                        # pdb.set_trace()
                        result['data'] = recommend_utils.convert_info_objects_to_json(list_dict_[0])
                        if acc_type in [1, 2, 3, 4]:
                            # result['data'] = self.convert_info_objects_to_json(list_dict_[0])
                            # if acc_type == 0 or acc_type == 1:
                            result['data']['watch_user_list'] = {k: v for k, v in result['data']['watch_user_list'].items() if v['acc_type']==acc_type}
                    else:    
                        result['data'] = list_dict_[0]
                    # result['data'] = self.convert_info_objects_to_json(list_dict_[0])
            else:
                result['status'] = 'True'
                result['data'] = None
                
        except Exception as ex:
            result['status'] = 'False'
            result['message'] = ex
            self.loggers.exception(ex)
          
        return result

    def wl_add_2(self,user_id,wl_obj, ig_id, picture_url, acc_type = 2):
        result = {}
        # pdb.set_trace()
        try:
            wl_item = self.fb_graph.get_business_info(username = ig_id)
            if 'error' in wl_item:
                # result['status'] = 'False'
                # result['message'] = "Can't get data from user %s: "%ig_id

                wl_item['profile_picture_url'] = picture_url
                wl_item['username'] = ig_id
                wl_item['media_count'] = 0
                wl_item['followers_count'] = 0
                wl_item['id'] = None
                wl_item['website'] = None

                # return result
            wl_item['new_post'] = 0#wl_item['media_count']#
            wl_item['acc_type'] = acc_type#acc_type: # 0: influencer, 1: branch, 2: all
            wl = self.wl_get(user_id,wl_obj, False)
            if wl['status'] == 'True':
                wl = wl['data']
                if wl is None:
                    wl = models.WatchList(user_id = user_id, watch_user_list = {ig_id:models.type_business_info(**wl_item)}, viewed_time = datetime.utcnow(),updated_time = datetime.utcnow())
                    wl.save()
                    result['status'] = 'True'
                    result['data'] = wl_item # try catch here

                else:
                    if wl['watch_user_list'] is None:
                        models.WatchList.objects(user_id = user_id).update(watch_user_list= {ig_id:models.type_business_info(**wl_item)})
                        result['status'] = 'True'
                        result['data'] = wl_item
                    else:   
                        if ig_id in wl['watch_user_list']:
                            result['status'] = 'False'
                            result['data']= "user %s already in watch list"%ig_id
                        else:
                            wl['watch_user_list'][ig_id] = models.type_business_info(**wl_item)     
                            models.WatchList.objects(user_id = user_id).update(watch_user_list= wl['watch_user_list'])
                            result['status'] = 'True'
                            result['data'] = wl_item
            else:
                 result['status'] = 'False' 
                 result['message'] = 'can not get data %s from aify server'% user_id        
        except Exception as ex:
            self.loggers.exception(ex)
            result['status'] = 'False'
            result['message'] = ex
        return result   \


    def wl_add(self,user_id, wl_obj, ig_id, acc_type = 2):
        result = {}
        # pdb.set_trace()
        try:
            wl_item = self.fb_graph.get_business_info(username = ig_id)
            if 'error' in wl_item:
                result['status'] = 'False'
                result['message'] = "Can't get data from user %s: "%ig_id
                return result
            wl_item['new_post'] = 0#wl_item['media_count']#
            wl_item['acc_type'] = acc_type#acc_type: # 0: influencer, 1: branch, 2: all
            wl = self.wl_get(user_id, wl_obj, False)
            if wl['status'] == 'True':
                wl = wl['data']
                if wl is None:
                    wl = models.WatchList(user_id = user_id, watch_user_list = {ig_id:models.type_business_info(**wl_item)}, viewed_time = datetime.utcnow(),updated_time = datetime.utcnow())
                    wl.save()
                    result['status'] = 'True'
                    result['data'] = wl_item # try catch here

                else:
                    if wl['watch_user_list'] is None:
                        models.WatchList.objects(user_id = user_id).update(watch_user_list= {ig_id:models.type_business_info(**wl_item)})
                        result['status'] = 'True'
                        result['data'] = wl_item
                    else:   
                        if ig_id in wl['watch_user_list']:
                            result['status'] = 'False'
                            result['data']= "user %s already in watch list"%ig_id
                        else:
                            wl['watch_user_list'][ig_id] = models.type_business_info(**wl_item)     
                            models.WatchList.objects(user_id = user_id).update(watch_user_list= wl['watch_user_list'])
                            result['status'] = 'True'
                            result['data'] = wl_item
            else:
                 result['status'] = 'False' 
                 result['message'] = 'can not get data %s'% user_id        
        except Exception as ex:
            self.loggers.exception(ex)
            result['status'] = 'False'
            result['message'] = ex
        return result     

    def wl_remove(self,user_id,wl_obj, ig_id):
        result = {}
        try:
            # pdb.set_trace()
            wl = self.wl_get(user_id, wl_obj, False)
            if wl['status'] == 'True':
                wl = wl['data']
                if wl is None:
                    result['status'] = 'False'

                elif wl['watch_user_list'] is not None and ig_id in wl['watch_user_list']:
                    #print('remove %s '%ig_id)
                    del wl['watch_user_list'][ig_id]
                    # wl_tmp_ = wl['watch_user_list']
                    models.WatchList(user_id = user_id, watch_user_list = wl['watch_user_list']).save()

                    # models.WatchList.objects(user_id = user_id).update(watch_user_list= None)
                    # models.WatchList.objects(user_id = user_id).update(watch_user_list= wl_tmp_)
                    result['status'] = 'True'
                else:
                    print('no see %s in database'%ig_id)
                    result['status'] = 'False'
        except Exception as ex:
            self.loggers.exception(ex)
            result['message'] = ex
            result['status'] = 'False'
        return result     
        
    def convert_info_objects_to_json(self,info_object):
        try:
            tmp_dict = info_object['watch_user_list']
            for k, v in tmp_dict.items():
                # print(k)
                tmp_dict[k] = dict(tmp_dict)
            return tmp_dict#info_object
        except Exception as ex:
            self.loggers.exception(ex)
            return info_object    


    def wl_update_new_post(self,user_id,wl_obj, acc_type):
        list_infos = []
        result = {}
        new_post = False
        try:
            wl = self.wl_get(user_id, wl_obj)
            if wl['status'] == 'True':
                wl = wl['data']
                if wl is None:
                    result['status'] = 'False'
                elif wl['watch_user_list'] is not None and (datetime.now() - wl['updated_time']).total_seconds() > constants.TOTAL_SECONDS_TO_REFRESH_WATCH_LIST:
                    # for k, username in enumerate(wl['watch_user_list']):
                    for username, v in wl['watch_user_list'].items(): # iter dictionary    
                        try:
                            if v['acc_type'] == acc_type :

                                request_data = self.fb_graph.get_business_info(username = username)
                    #             list_infos.append(request_data)
                                #
                                num_new_post = request_data['media_count'] - int(wl['watch_user_list'][username]['media_count'])
                                request_data['new_post'] = num_new_post
                                if num_new_post != 0:
                                    new_post = True
                                    list_infos.append(request_data)
                                    
                                    #update db
                                wl['watch_user_list'][username] = models.type_business_info(**request_data) #update item in watch list user
                        except Exception as ex:
                            print(ex)
                    if new_post: 
                        models.WatchList.objects(user_id = user_id).update(updated_time= datetime.utcnow(), watch_user_list= wl['watch_user_list'])        
                        result['status'] = 'True'
                        # result['data'] = wl['watch_user_list']
                        result['data'] = list_infos
                    else:
                        result['status'] = 'False'
                        result['message'] = 'no new post'
                else:
                    result['message']='no have any user in watch list, please add first...'
                    result['status'] = 'False'
        except Exception as ex:
            self.loggers.exception(ex)
            result['status'] = 'False'
        return result    
    # watch_list.objects(user_id = 'anhlbt').update(watch_user_list= {'natje_9999': a2, 'emmaparkerandco': a2})   

    # update_string = "update watch_list set watch_user_list= {'natje_9999': 'a2', 'emmaparkerandco': 'a1'} where user_id = 'anhlbt' if exists"
    # _session.execute(update_string)

    # wl = watch_list(user_id = 'anhlbt3',watch_user_list= a['watch_user_list'], viewed_time = datetime.utcnow(),updated_time = datetime.utcnow())
    # wl.save()

    def get_user_insight_day_history(self, social_id, from_timestamp =datetime.timestamp(datetime.now() - timedelta(days=10)) , until_timestamp = datetime.timestamp(datetime.now())):
        try:
            self.db.session.row_factory = pandas_factory
            rows = self.db.session.execute("select * from aify_db.user_insight_days_history where owner_id = %s"%social_id)
            df = rows._current_rows
            df = df[(df['day']>= datetime.utcfromtimestamp(from_timestamp)) & (df['day']<= datetime.utcfromtimestamp(until_timestamp))]
            df['owner_id']= df.loc[:,'owner_id'].apply(lambda x: str(x))
            js = df.to_json(orient='index', force_ascii = True) #'index=False' is only valid when 'orient' is 'split' or 'table'
            return json.loads(js), df
        except Exception as ex:
            print(ex)
            recommend_utils.bug_info()
            pass

# if __name__ == '__main__':
#     print('running....')
    # pdb.set_trace()
    # wl_inst = watch_list()
    # c = wl_inst.wl_remove(user_id='anhlbt', ig_id='natje_9999')#natje_9999   traveling__pari
    # print(c)
    # a = wl_inst.wl_add(user_id='anhlbta', ig_id='traveling__pari')
    # print(a)
    # b = wl_inst.wl_get(user_id = 'anhlbt', convert_to_json= True, acc_type=0)
    # print(b)
    # pdb.set_trace()
    # d = wl_inst.wl_update_new_post(user_id = 'anhlbt')
    # print(d)

    # e = wl_inst.fb_graph.get_business_info(username = 'annieverywhere')
    # print(e)

    # js, df = wl_inst.get_user_insight_day_history('9c88c600-ac5f-11e8-80f4-eb836fc406ca',1531686400)
    # print(js)
    