# -*- coding: utf-8 -*-
#parameter for the crawler
import random
from os.path import dirname, abspath
HOME_DIR = dirname(dirname(abspath(__file__)))
default_version = "v3.1"
REACHESTIMATE_URL = "https://graph.facebook.com/%s/act_{}/delivery_estimate"%default_version
GRAPH_SEARCH_URL = "https://graph.facebook.com/%s/search"%default_version
TARGETING_SEARCH_URL = "https://graph.facebook.com/%s/act_{}/targetingsearch"%default_version
TEST_VALID_TOKEN = "https://graph.facebook.com/%s/me"%default_version
INSTAGRAM_GRAPH_API = ""
TARGETING_FIELD = "targeting"

FB_INSTAGRAM_BASE_URL = "https://graph.facebook.com"
DEFAULT_USER_INFO_FIELDS = "biography,followers_count,follows_count,id,ig_id,media_count,name," \
                            "profile_picture_url,username,website"
DEFAULT_MEDIA_FIELDS = "caption,id,ig_id,comments_count,like_count,media_type,owner,media_url," \
                        "shortcode,permalink,timestamp,thumbnail_url"
DEFAULT_COMMENT_FIELDS = "id,like_count,text,timestamp,username"
DEFAULT_INSIGHTS_FIELDS = "insights.metric(impressions,reach,engagement)"

DEFAULT_BUSINESS_DISCOVERY_FIELDS_ALL = 'business_discovery.username(%s)'\
'{id,biography,website,followers_count,media_count, name,username,profile_picture_url,'\
'media.limit(%s){like_count, comments_count, media_type, permalink, timestamp, username}}'

DEFAULT_BUSINESS_DISCOVERY_FIELDS_INFO = 'business_discovery.username(%s)'\
    '{id,website,followers_count,media_count, name,username,profile_picture_url}'

DEFAULT_BUSINESS_DISCOVERY_FIELDS_MEDIA = 'business_discovery.username(%s)'\
        '{id,biography,website,followers_count,media_count, name,username,profile_picture_url,'\
         'media.limit(%s){like_count, comments_count, media_type, permalink, timestamp, username}}'

MAX_COMMENT = 50
MAX_REPLIES = 100
MAX_MEDIA = 100000
TOKENS = []
TIME_SLEEP = 60
INITIAL_TRY_SLEEP_TIME = 10
API_UNKOWN_ERROR_CODE_1 = 1
API_UNKOWN_ERROR_CODE_2 = 2
MAX_NUMBER_TRY = 3

# path
IG_RESULT_FOLDER = 'IG_profiles'
INSTAGRAM_ID_PATH = 'data_instagram/instagram-profilecrawl/instagram_id'
INSTAGRAM_TOKEN_FILE = 'instagram_token.csv'
KEYSPACE_NAME = 'aify_db'
USERS_BUSINESS_DISCOVERY = 'data_instagram/instagram-profilecrawl/data_users_business_discovery.csv'


RANDOM_KEYWORD = ['Beauty']

# query strings
SQL_GET_DATA_USER_BUSINESS_DISCOVERY = "select * from %s.users_business_discovery"%KEYSPACE_NAME
SQL_GET_DATA_RECOMMEND_INFLUENCER = "select * from %s.recommend_influencer"%KEYSPACE_NAME

# FLASK
HOST_INFLUENCER_RECOMMEND = '0.0.0.0'
PORT_INFLUENCER_RECOMMEND = 5000

HOST_WATCH_LIST = '0.0.0.0'
PORT_WATCH_LIST = 5001

HOST_UPDATE_IG = '0.0.0.0'
PORT_UPDATE_IG = 5002



import sys, os
CONFIG_SOURCE = os.getenv("CONFIG_SOURCE", "local_config")
if CONFIG_SOURCE == "aws_config":
    HOST_CASSANDRA_DB = ['100.68.122.230']
    PORT_CASSANDRA_RS = 9042
else :
    HOST_CASSANDRA_DB = ['172.33.47.10']
    PORT_CASSANDRA_RS = 61003#random.choice([61003, 61005])
    # HOST_CASSANDRA_DB = ["a084c6ef0b0e511e8b2840e36016edc5-791065256.us-east-1.elb.amazonaws.com"]
    # PORT_CASSANDRA_RS = 9042

TOTAL_SECONDS_TO_REFRESH_WATCH_LIST = 2

RS_SIMILAR_SUPPORT_COEF = 0.5 # should be in range(0, 1)

RS_TIME_SLEEP_REFRESH_DATA = 86400




