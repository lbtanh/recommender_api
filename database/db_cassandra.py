from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.auth import PlainTextAuthProvider
import sys, time
import pandas as pd
from cassandra.query import dict_factory
import cassandra.util
import sys
sys.path.insert(0, "./../../recommender_api")
from utils import constants, recommend_utils
from datetime import datetime

log = recommend_utils.get_logger('db_cassandra.log')

# return format dataframe when query results from cassandra
def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)

class db_cassandra:
    def __init__(self, contact_points, factory, port_ = constants.PORT_CASSANDRA_RS):
        while 1:
            try:
                self.cluster = Cluster(contact_points, port = port_,connect_timeout = 100) # cluster = Cluster(['172.33.47.10', '0.0.0.0'])
                self.session = self.cluster.connect(constants.KEYSPACE_NAME)
                self.session.default_fetch_size = 10000000 #needed for large queries, otherwise driver will do pagination. Default is 50000.
                self.session.row_factory = factory # use: pandas_factory or dict_factory 
                log.warning("connected to db....host: %s, port: %s"%(str(contact_points),str(constants.PORT_CASSANDRA_RS)))
                break
            except Exception as ex:
                log.error(ex)
                log.warning('sleeping in 60s then try connect to db')
                time.sleep(60)
            #try to connect db again

    # create new keyspace
    def create_keyspace(self, keyspace_name):
        # create new keyspace
        self.session.execute("""
                CREATE KEYSPACE %s
                WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
                """ % keyspace_name)

    def exectute_query(self, string_query):
        try:
            return self.session.execute(string_query)._current_rows
        except Exception as ex:
            print(ex)
            pass    

    def create_db(self, KEYSPACE = constants.KEYSPACE_NAME):
        #drop exist keyspace
        # self.session.execute("drop keyspace IF EXISTS aify_recommend")
        #====================================
        # log.info("creating aify_recommend keyspace ...")
        # self.session.execute("""
        #     CREATE KEYSPACE IF NOT EXISTS %s
        #     WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
        #     """ % KEYSPACE)

        log.info("setting keyspace...")
        self.session.set_keyspace(KEYSPACE)
        #====================================
        log.info("creating table...")

        self.session.execute("""
            CREATE TABLE IF NOT EXISTS recommend_influencer (
                influencer_name TEXT, -- SocialUser
                bio TEXT, /*LIST < list of characteristics >  not see */
                categories list<text>, /*LIST < list of business catagory >, hashtag, keyword*/
                commentPerPost int,
                demographics TEXT, --age, gender, 
                engagementRate TEXT,
                follower int,
                account_type int, -- 0: influencer, 1: branch, 2: all
                likePerPost int, --everage
                location TEXT,
                path TEXT,
                reach TEXT,
                website TEXT,
                posts_starting BIGINT,
                currency TEXT,
                socialAccounts list<frozen <map<text, text>>>,
                created TIMESTAMP,
                updated TIMESTAMP,
                activate TIMESTAMP,
                influencer_id INT,
                img_url TEXT,
                ts timeuuid,
                instagram_id text,
                PRIMARY KEY (instagram_id)
            ) ;
            """)
        print('create table finished...')

# insert dataframe into cassandra
    def insert_into_recommend_influencer(self,df):
        prepared = self.session.prepare("""
            INSERT INTO recommend_influencer (influencer_id, bio, categories, commentPerPost, demographics, engagementRate,
            follower,account_type, likePerPost, location, influencer_name, path, reach,
            socialAccounts, website, ts, instagram_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """)

        for i in range(df.shape[0]):
        #     print('i value: %i' %i)
            self.session.execute(prepared, (i, df.iloc[i]['bio'], df.iloc[i]['categories'], df.iloc[i]['commentPerPost'] \
                                    , df.iloc[i]['demographics'], df.iloc[i]['engagementRate'], df.iloc[i]['follower'] \
                                    , df.iloc[i]['account_type'], df.iloc[i]['likePerPost'], df.iloc[i]['location'], df.iloc[i]['name'] \
                                    , df.iloc[i]['path'], df.iloc[i]['reach'], df.iloc[i]['socialAccounts'] \
                                    , df.iloc[i]['website'], cassandra.util.uuid_from_time(time.time()) \
                                    , df.iloc[i]['instagram_id']
                                    )) #str(i)
        print('insert finished...')
        # delete keyspace
        # session.execute("DROP KEYSPACE test_keyspace")

    def create_table(self, KEYSPACE = constants.KEYSPACE_NAME, table_name = 'users_business_discovery'):
        self.session.set_keyspace(KEYSPACE)

        self.session.execute("""
            CREATE TABLE %s.users_business_discovery (
                id bigint,
                username text,
                biography text,
                comments_count int,
                followers_count int,
                likes_count int,
                media_count int,
                name text,
                profile_picture_url text,
                updated_date timestamp,
                PRIMARY KEY (id, username)
            ) WITH CLUSTERING ORDER BY (username DESC)
            """%(KEYSPACE))

    def insert_into_business_discovery(self, df, KEYSPACE = constants.KEYSPACE_NAME):
        self.session.set_keyspace(KEYSPACE)
        prepared = self.session.prepare("""
            INSERT INTO %s.users_business_discovery (id, username, biography, 
            comments_count, followers_count, likes_count, media_count, name,
             profile_picture_url, updated_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """%KEYSPACE)

        for i in range(df.shape[0]):
        #     print('i value: %i' %i)
            self.session.execute(prepared, (int(df.iloc[i]['id']), str(df.iloc[i]['username']), str(df.iloc[i]['biography']), int(df.iloc[i]['comments_count']) \
                                    , int(df.iloc[i]['followers_count']), int(df.iloc[i]['likes_count']), int(df.iloc[i]['media_count']) \
                                    , str(df.iloc[i]['name']), str(df.iloc[i]['profile_picture_url']) \
                                    ,  datetime.strptime(df.iloc[i]['updated_date'], '%Y-%m-%d %H:%M:%S')
                                    )) #str(i)
        print('insert finished...')


