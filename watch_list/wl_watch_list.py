import sys
sys.path.insert(0, "./../../recommender_api")
from utils import recommend_utils, constants
from database import models
from datetime import datetime
import time, os
from os.path import dirname, join
from database import db_cassandra
from cassandra.query import dict_factory
from FacebookCrawler import facebook_graph_api
from cassandra.cqlengine import columns, connection


class watch_list():
    def __init__(self):
        # #get session
        token_path = join(dirname(dirname(os.path.abspath(__file__))),'FacebookCrawler/'+constants.INSTAGRAM_TOKEN_FILE)
        print(token_path)
        self.fb_graph = facebook_graph_api.FacebookGraphApi(token_path)
        (self.fb_graph.access_token,self.fb_graph.user_id) = constants.TOKENS[4]
        self.db = db_cassandra.db_cassandra(contact_points = constants.HOST_CASSANDRA_DB, factory = dict_factory)
        connection.set_session(self.db.session)


    def wl_get(self, user_id):
        try:
            query_string="select * from aify_recommend.watch_list where user_id = '%s'"%user_id
            re = self.db.session.execute(query_string)
            list_dict_ = recommend_utils.map_to_dict_factory_1(re.current_rows)#data get from db, list have only one item
        #     list_dict_ = re.current_rows
            return list_dict_[0]
        except Exception as ex:
            return None

    def wl_add(self,user_id, ig_id):
        try:
            wl_item = self.fb_graph.get_business_info(username = ig_id)
            wl_item['new_post'] = 0
            wl = self.wl_get(user_id)
            if wl is None:
                wl = models.WatchList(user_id = user_id, watch_user_list = {ig_id:models.type_business_info(**wl_item)}, viewed_time = datetime.utcnow(),updated_time = datetime.utcnow())
                wl.save()
            else:
                if wl['watch_user_list'] is None:
                    models.WatchList.objects(user_id = user_id).update(watch_user_list= {ig_id:models.type_business_info(**wl_item)})
                else:   
                    if ig_id in wl['watch_user_list']:
                        print("user %s already in watch list"%ig_id)
                        return False
                    else:
                        wl['watch_user_list'][ig_id] = models.type_business_info(**wl_item)     
                        models.WatchList.objects(user_id = user_id).update(watch_user_list= wl['watch_user_list'])
            return True
            
        except Exception as ex:
            print(ex)
            return False

    def wl_remove(self,user_id, ig_id):
        try:
            wl = self.wl_get(user_id)
            if wl is None:
                return False
            elif wl['watch_user_list'] is not None and ig_id in wl['watch_user_list']:
                #print('remove %s '%ig_id)
                del wl['watch_user_list'][ig_id]
                models.WatchList.objects(user_id = user_id).update(watch_user_list= None)
                models.WatchList.objects(user_id = user_id).update(watch_user_list= wl['watch_user_list'])
                return True
            else:
                print('no see %s in database'%ig_id)
                return False
        except Exception as ex:
            print(ex)
            return False    
        
    def convert_info_objects_to_json(self,info_object):
        tmp_dict = info_object['watch_user_list']
        for k, v in tmp_dict.items():
            print(k)
            tmp_dict[k] = dict(tmp_dict[k])
        return info_object


    def wl_update_new_post(self,user_id):
    #     list_infos = []
        try:
            wl = self.wl_get(user_id)
            if wl is None:
                return False
            elif wl['watch_user_list'] is not None:
                for k, username in enumerate(wl['watch_user_list']):
            #     for k, v in list_dict_[0]['watch_user_list'].items(): # iter dictionary
                    print(username)
                    request_data = self.fb_graph.get_business_info(username = username)
        #             list_infos.append(request_data)
                    #
                    num_new_post = request_data['media_count'] - int(wl['watch_user_list'][username].media_count)
                    request_data['new_post'] = num_new_post
                    if num_new_post != 0:
                        #update db
                        wl['watch_user_list'][username] = models.type_business_info(**request_data) #update item in watch list user
                        print('you have %s new post'%num_new_post)
                        return True
                    else:
                        print('no changes')
                        return False    
                        
            else:
                print('no have any user in watch list, please add first...')
                return False
                    
            models.WatchList.objects(user_id = user_id).update(watch_user_list= wl['watch_user_list'])      

        except Exception as ex:
            print(ex)
            
    # watch_list.objects(user_id = 'anhlbt').update(watch_user_list= {'natje_9999': a2, 'emmaparkerandco': a2})   

    # update_string = "update watch_list set watch_user_list= {'natje_9999': 'a2', 'emmaparkerandco': 'a1'} where user_id = 'anhlbt' if exists"
    # _session.execute(update_string)

    # wl = watch_list(user_id = 'anhlbt3',watch_user_list= a['watch_user_list'], viewed_time = datetime.utcnow(),updated_time = datetime.utcnow())
    # wl.save()


if __name__ == '__main__':
    wl_inst = watch_list()
    a = wl_inst.wl_add(user_id='anhlbt', ig_id='natje_9999')
    a = wl_inst.wl_get(user_id = 'anhlbt')
    print(a)
    