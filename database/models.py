import sys
sys.path.insert(0, "./../../recommender_api")
from utils import constants

from cassandra.cqlengine.models import Model
from cassandra.cqlengine import connection
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from cassandra.util import uuid_from_time
from cassandra.cqlengine.columns import *
from cassandra.cqlengine.usertype import UserType
from datetime import datetime

class UserBusinessDiscovery(Model):
    __keyspace__ = constants.KEYSPACE_NAME
    __table_name__ = "users_business_discovery"
    id = BigInt(primary_key=True)
    name = Text()
    biography = Text()
    media_count = Integer()
    comments_count = Integer()
    likes_count = Integer()
    followers_count = Integer()
    username = Text(primary_key = True)
    profile_picture_url = Text()
    updated_date = DateTime()
    # ts = columns.UUID(primary_key=True)
    
class type_business_info(UserType):
    id = Text()
    website = Text()
    media_count = Integer()
    followers_count = Integer()
    name = Text()
    username = Text()
    profile_picture_url = Text()
    new_post = Integer(default = 0)
    acc_type = Integer(default = 2)

    
class WatchList(Model):
    __keyspace__ = constants.KEYSPACE_NAME
    __table_name__ = "watch_list"
    user_id= Text(primary_key=True)
    watch_user_list= Map(Text(), UserDefinedType(type_business_info))
    viewed_time =DateTime(default=  datetime.utcnow())
    updated_time =DateTime(default=  datetime.utcnow())


class recommend_influencer(Model):
    __keyspace__ = constants.KEYSPACE_NAME
    __table_name__ = "recommend_influencer"
    influencer_name = Text()
    bio = Text()
    categories = List(Text())
    commentPerPost =Integer()
    demographics = Text()
    engagementRate = Text()
    follower = Integer()
    account_type =Integer()
    likePerPost = Integer()
    location = Text()
    path =Text()
    reach =Text()
    website =Text()
    posts_starting =Integer()
    currency =Text()
    socialAccounts = List(Map(Text(), Text()))
    created =DateTime(default=  datetime.utcnow())
    updated =DateTime(default=  datetime.utcnow())
    activate =DateTime(default=  datetime.utcnow())
    influencer_id = Integer(primary_key=True)
    img_url = Text()
    ts = UUID(primary_key=True)
    
    
class RecommendResult(Model):
    __keyspace__ = constants.KEYSPACE_NAME
    __table_name__ = "recommend_result"
    num_count = Integer()
    results = Map(Text(), Text())
    created = DateTime(default= datetime.utcnow())
    updated = DateTime(default= datetime.utcnow())
    owner_id = UUID(primary_key=True)


class Person(Model):
    __keyspace__ = constants.KEYSPACE_NAME
    __table_name__ = "person"
    id = UUID(primary_key=True)
    user_name = Text(primary_key=True)
    first_name  = Text()
    last_name = Text()
    updated_date = DateTime()