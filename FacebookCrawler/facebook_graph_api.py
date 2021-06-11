import sys
sys.path.insert(0, './../../recommender_api')
import os
import requests
import logging
# from constants import *
from utils import constants, recommend_utils
import json
import datetime, time
from requests.exceptions import RequestException
import pandas as pd
from os.path import dirname, join
import pdb
from database import db_cassandra
import random



class FacebookGraphApi(object):

    def __init__(self, token_file_path = ''):
        # print(os.getcwd())
        try:
            self.LOGGER = recommend_utils.get_logger('FacebookGraphApi.log')
            if len(constants.TOKENS) == 0:
                # self.load_token_file(token_file_path)
                self.load_token_db()
            self.lst_tokens = self.test_tokens_valid()
            token_index = random.choice(self.lst_tokens)
             
            (self.access_token,self.user_id) = constants.TOKENS[token_index]
            self.version = constants.default_version
            # self.session = requests
            
        except Exception as ex:
            print(ex)
            # self.LOGGER.exception(ex)   

    def load_token_file(self,token_file_path):
        try:
            with open(token_file_path, "r") as token_file:
                for line in token_file:
                    token = line.split(",")[0].strip()
                    instagram_business_id = line.split(",")[1].strip()
                    self.add_token_and_ig_business_id(token, instagram_business_id)
        except Exception as ex:
            self.LOGGER.exception(ex)

    def load_token_db(self,):
        try:
            # pdb.set_trace()
            db = db_cassandra.db_cassandra(contact_points = constants.HOST_CASSANDRA_DB,port_= constants.PORT_CASSANDRA_RS ,factory =recommend_utils.pandas_factory) # pandas_factory
            db.session.row_factory = recommend_utils.pandas_factory
            df = db.exectute_query("select * from %s.social_user;"%(constants.KEYSPACE_NAME))
            # df = rows._current_rows
            df = df[['access_token', 'external_id', 'account_id', 'social_type']]
            df = df[df.social_type.isin(['instagram_business'])]
            
            for index, row in df.iterrows():
                self.add_token_and_ig_business_id(row['access_token'], row['external_id'])
                
        except Exception as ex:
            self.LOGGER.exception(ex)            

    def add_token_and_ig_business_id(self, token,instagram_business_id):
        try:
            constants.TOKENS.append((token,instagram_business_id))
        except Exception as ex:
            self.LOGGER.exception(ex)    

    def test_tokens_valid(self):
        # print("Testing tokens and account number")
        list_valid_token = []
        for token, account in constants.TOKENS:
            try:
                row = pd.Series()
                row[constants.TARGETING_FIELD] = constants.TEST_VALID_TOKEN + "/business_users"
                res = self.call_request_fb(row, token, account)
                if res.status_code == 200:
                    # self.LOGGER.exception('token of account: %s is valid' %account)
                    list_valid_token.append(constants.TOKENS.index((token, account)))
                    # break
                else:
                    self.LOGGER.exception('token of account: %s is UNvalid' %account)
                      
            except Exception as ex:
                self.LOGGER("Token or Account Number Error:")
                self.LOGGER("Token:" + token)
                self.LOGGER("Account:" + account)
                self.LOGGER.exception(ex)

        # print("All tokens and respective account number are valid.")
        return list_valid_token #index

    def call_request_fb(self,row, token, account):
        target_request = row[constants.TARGETING_FIELD]
        # print(target_request)
        payload = {
            'currency': 'USD',
            'optimize_for': "NONE",
            'optimization_goal': "AD_RECALL_LIFT",
            'targeting_spec': json.dumps(target_request),
            'access_token': token,
        }
    #    payload_str = str(payload)
    #    print_warning("\tSending in request: %s"%(payload_str))
        url = constants.TEST_VALID_TOKEN.format(account)
        # print('url: {}'.format(url))
        response = self.send_request(url, payload)
        return response


    def handle_send_request_error(self,response, url, params, tryNumber):
        try:
            error_json = json.loads(response.text)
            if error_json["error"]["code"] == constants.API_UNKOWN_ERROR_CODE_1 or error_json["error"]["code"] == constants.API_UNKOWN_ERROR_CODE_2:
                self.LOGGER.error("Error code: %s "%(error_json["error"]["code"]))
                # business_discovery = json.loads('{"error":"%s"}'%(resp.json()['error']))
                time.sleep(constants.INITIAL_TRY_SLEEP_TIME * tryNumber)
                return self.send_request(url, params, tryNumber)
            else:
                self.LOGGER.error("Error Code:" + str(error_json["error"]["code"]))
                if "message" in error_json["error"]:
                    self.LOGGER.error("Error Message:" + str(error_json["error"]["message"]))
                if "error_subcode" in error_json["error"]:
                    self.LOGGER.error("Error Subcode:" + str(error_json["error"]["error_subcode"]))
                    if error_json["error"]["error_subcode"] == constants.API_PERMISSION_ERROR_CODE_33:
                        (self.access_token,self.user_id) = constants.TOKENS[random.choice(self.test_tokens_valid())]
                return response
                
        except Exception as e:
            self.LOGGER.error(e)

    def send_request(self,url, params, tryNumber = 0):
        tryNumber += 1
        try:
            resp = requests.get(url, params=params)
            if resp.status_code == 200:
                return resp
            else:
                if tryNumber >= constants.MAX_NUMBER_TRY:
                    self.LOGGER.warning('Maxium Number of Tries reached. Failing')
                else:    
                    return self.handle_send_request_error(resp, url, params, tryNumber)        
            
        except Exception as ex:
            self.LOGGER.exception(ex)

    def get_user_medias(self, user_id, **kwargs):
        """
        Get medias of user and comments of these medias

        :param user_id: User facebook Id
        :param kwargs:
            media_count: number of medias return
            media_fields: set response fields for media from facebook
        :return: list of media and comments of it
        """
        media_count = kwargs.get("media_count", constants.MAX_MEDIA)
        media_fields = kwargs.get("media_fields", constants.DEFAULT_MEDIA_FIELDS)

        if media_count < constants.MAX_MEDIA:
            craw_media_count = media_count
        else:
            craw_media_count = constants.MAX_MEDIA

        request_param = {
            'fields': media_fields,
            'limit': craw_media_count,
            'access_token': self.access_token
        }

        url = "%s/%s/%s/media" % (constants.FB_INSTAGRAM_BASE_URL, self.version, user_id)
        medias = []
        is_more_available = True

        while len(medias) < media_count and is_more_available:
            try:
                self.LOGGER.info(url)
                resp = requests.get(url, params=request_param)
                if resp.status_code != 200:
                    self.LOGGER.error("Get media of user %s fails: %s " % (user_id, resp.content))
                    break
                json_resp = resp.json()

                medias.extend(json_resp['data'])
                if 'next' in json_resp['paging']:
                    request_param['after'] = json_resp['paging']['cursors']['after']
                    limit = media_count - len(medias)
                    if limit > constants.MAX_MEDIA:
                        limit = constants.MAX_MEDIA
                    request_param['limit'] = limit
                else:
                    is_more_available = False
            except RequestException as e:
                self.LOGGER.error("Error when request medias of user %s, err: %s, param: %s" %
                             (user_id, e, request_param), exc_info=True)
                break
        return medias

    def get_business_discovery(self, **kwargs):
        media_count = kwargs.get("media_count", constants.MAX_MEDIA)
        # media_fields = kwargs.get("media_fields", self.DEFAULT_MEDIA_FIELDS)
        username = kwargs.get("username", "richardleedsint")

        if media_count < constants.MAX_MEDIA:
            craw_media_count = media_count
        else:
            craw_media_count = constants.MAX_MEDIA
        request_param = {
            'fields': constants.DEFAULT_BUSINESS_DISCOVERY_FIELDS_MEDIA %(username, media_count),
            'limit': craw_media_count,
            'access_token': self.access_token
        }
        url = "%s/%s/%s/" % (constants.FB_INSTAGRAM_BASE_URL, self.version, self.user_id)

        business_discovery = []
        is_more_available = True

        while len(business_discovery) < media_count and is_more_available:
            try:
                self.LOGGER.info(url)
                resp = requests.get(url, params=request_param)
                if resp.status_code != 200:
                    business_discovery = json.loads('{"error":"%s"}'%(resp.json()['error']))
                    self.LOGGER.error("Get business discovery of username %s fails: %s " % (username, resp.content))
                    # business_discovery=json.loads('"business_discovery":"not business account"')
                    break

                json_resp = resp.json()
                #get all media data
                business_discovery.extend(json_resp['business_discovery']['media']['data'])#json_resp['business_discovery']['media']['data']

                if 'paging' in json_resp['business_discovery']['media']:
                    request_param['after'] = json_resp['business_discovery']['media']['paging']['cursors']['after']
                    limit = media_count - len(business_discovery)
                    if limit > constants.MAX_MEDIA:
                        limit = constants.MAX_MEDIA
                    request_param['limit'] = limit
                else:
                    is_more_available = False
            except RequestException as e:
                self.LOGGER.error("Error when request medias of username %s, err: %s, param: %s" %
                             (username, e, request_param), exc_info=True)
                break
        return business_discovery
    
    # biography	comments_count	followers_count	id	likes_count	media_count	name	profile_picture_url	username	website
    def get_business_discovery_all(self,  **kwargs):
        media_count = kwargs.get("media_count", constants.MAX_MEDIA)
        # media_fields = kwargs.get("media_fields", self.DEFAULT_MEDIA_FIELDS)
        username = kwargs.get("username", "richardleedsint")
        request_param = {
            'fields': constants.DEFAULT_BUSINESS_DISCOVERY_FIELDS_ALL %(username, media_count),
            'access_token': self.access_token
        }
        url = "%s/%s/%s/" % (constants.FB_INSTAGRAM_BASE_URL, self.version, self.user_id)
        # pdb.set_trace()
        try:
            self.LOGGER.info(url)
            # resp = requests.get(url, params=request_param)
            resp = self.send_request(url,params=request_param)
            if resp.status_code != 200:
                
                # business_discovery = json.loads('{"error":"%s"}'%(resp.json()['error']))
                business_discovery = json.loads(resp.text)
                self.LOGGER.error("Get business discovery of username %s fails: %s " % (username, resp.content))
            else:
                json_resp = resp.json()
                #get all media data
                business_discovery= json_resp['business_discovery']#json_resp['business_discovery']['media']['data']
        except RequestException as e:
            self.LOGGER.error("Error when request medias of username %s, err: %s, param: %s" %
                            (username, e, request_param), exc_info=True)
            business_discovery = json.loads('{"error":"%s"}'%(resp.json()['error']))               
        return business_discovery


    def get_business_info(self, **kwargs):
        username = kwargs.get("username", "richardleedsint")
        request_param = {
            'fields': constants.DEFAULT_BUSINESS_DISCOVERY_FIELDS_INFO %username,
            'access_token': self.access_token
        }
        url = "%s/%s/%s/" % (constants.FB_INSTAGRAM_BASE_URL, self.version, self.user_id)
        try:
            self.LOGGER.info(url)
            resp = requests.get(url, params=request_param)
            if resp.status_code != 200:
                business_info= json.loads('{"error":"%s"}'%(resp.json()['error']))
                self.LOGGER.error("Get business info of username %s fails: %s " % (username, resp.content))
            else:
                json_resp = resp.json()
                business_info = json_resp['business_discovery']
        except RequestException as e:
            self.LOGGER.error("Error when request medias of username %s, err: %s, param: %s" %
                            (username, e, request_param), exc_info=True)
            business_info= json.loads('{"error":"%s"}'%(resp.json()['error']))
        return business_info


    def parser_influencer_data(self, business_discovery_all):
        # df_media = pd.DataFrame(result['media']['data'])
        json_media = business_discovery_all.pop('media')
        df_media = pd.DataFrame(json_media['data'])
        business_discovery_all['comments_count'] = df_media.comments_count.sum()
        business_discovery_all['likes_count'] = df_media.like_count.sum()
        return business_discovery_all





if __name__ == "__main__":
    print('test...')

    # access_token = 'EAACLXTuiZBKkBAJZBxOEcwblSFcFfnr13bzq5soAWUsKIqxx7hGRvSPFPbPg2J7GrirqhHy4bnylZCZCZAyWh6MdRvx9imTSxS4K7yNJrZCHxHhRCz1mTAPCrZAQ9QZC9NvxWsL66vm8uV65CAu0DMuH3QZB7xf0kY5qTKFip0ioPtBZB0F2fZBiyCbd4DZBE8bhkMgZD'
    # fb_graph = FacebookGraphApi(version='v3.1', token=access_token)
    # sinceTimeStamp =  int(time.time()-24*60*60)
    # sinceTimeStamp = int(time.time() - 20 * 24 * 60 * 60)
    # untilTimeStamp = int(time.time())
    # # audience_gender_age, audience_country, audience_city,
    # a = fb_graph.get_user_insights("17841407517779759", start=sinceTimeStamp, end=untilTimeStamp, period="lifetime",
    #                                 metric="online_followers")
    # print(a)
# ======================================

    # #17841401610104138, 17841407517779759
    path_instagram_token = join(dirname(os.path.abspath(__file__)),constants.INSTAGRAM_TOKEN_FILE)

    # fb_graph = FacebookGraphApi(path_instagram_token)
    # # test = fb_graph.get_business_discovery_all( username = 'emmaparkerandco', media_count = 100)#17841401610104138, 17841407517779759
    # s_time = time.time()
    # test = fb_graph.get_business_info(username = 'emmaparkerandco')#17841401610104138, 17841407517779759
    # print(test)
    # print(time.time() - s_time)

    fb_graph = FacebookGraphApi(path_instagram_token)
    # fb_graph.load_token_db()
    token_index = fb_graph.test_tokens_valid()
    print(token_index)

