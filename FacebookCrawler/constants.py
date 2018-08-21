# -*- coding: utf-8 -*-
default_version = "v3.1"
REACHESTIMATE_URL = "https://graph.facebook.com/%s/act_{}/delivery_estimate"%default_version
GRAPH_SEARCH_URL = "https://graph.facebook.com/%s/search"%default_version
TARGETING_SEARCH_URL = "https://graph.facebook.com/%s/act_{}/targetingsearch"%default_version
TEST_VALID_TOKEN = "https://graph.facebook.com/%s"%default_version
INSTAGRAM_GRAPH_API = ""


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
TIME_SLEEP = 50
INITIAL_TRY_SLEEP_TIME = 10
API_UNKOWN_ERROR_CODE_1 = 1
API_UNKOWN_ERROR_CODE_2 = 2
MAX_NUMBER_TRY = 3

# path
IG_RESULT_FOLDER = 'IG_profiles'
SQL_GET_DATA_RECOMMEND_INFLUENCERinstagram_id_path_file = 'data_instagram/instagram-profilecrawl/instagram_id'

# query strings
SQL_GET_DATA_USER_BUSINESS_DISCOVERY = "select * from aify_recommend.user_business_discovery"
SQL_GET_DATA_RECOMMEND_INFLUENCER = "select * from aify_recommend.recommend_influencer"




