"""


created: 08/07/2018
"""
import sys
sys.path.insert(0, "./../../recommender_api")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json
import pandas as pd
import numpy as np
import os
from database import db_cassandra
from utils import constants, recommend_utils
import pdb
import random, re
from cassandra.query import dict_factory
from cassandra.cqlengine import columns, connection
from datetime import datetime
import math
pd.options.mode.chained_assignment = None

stemmer = PorterStemmer()


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)

class similar_influencer():
    def __init__(self):
        try:
            self.loggers = recommend_utils.get_logger('recommender.log')
            self.db = None
            self.db = db_cassandra.db_cassandra(contact_points = constants.HOST_CASSANDRA_DB,port_= constants.PORT_CASSANDRA_RS ,factory =pandas_factory) # pandas_factory
            # connection.set_session(self.db.session)
            # self.t = datetime.now()
            
        except Exception as ex:
            self.db = None
            self.loggers.error('Can not connect to db cassandra host: %s, port: %s' %(constants.HOST_CASSANDRA_DB, constants.PORT_CASSANDRA_RS))
            self.loggers.exception(ex)

    
    def init_data_from_data_crawl(self):
        # pdb.set_trace()
        # get from crawl data
        try:
        #     if self.db == None or 'self.db' not in locals():
        #         self.db = db_cassandra.db_cassandra(contact_points = constants.HOST_CASSANDRA_DB,port_= constants.PORT_CASSANDRA_RS ,factory =pandas_factory) # pandas_factory

            self.db.session.row_factory = pandas_factory
            # df_api = self.db.exectute_query(constants.SQL_GET_DATA_USER_BUSINESS_DISCOVERY)
            df_api = self.db.session.execute(constants.SQL_GET_DATA_USER_BUSINESS_DISCOVERY)
            df_api = df_api._current_rows
        # df_scrapy = db.exectute_query(constants.SQL_GET_DATA_RECOMMEND_INFLUENCER)
            if df_api.shape[0]< 10:# if db is empty
                self.loggers.warning('db is empty, read data and insert into table users_business_discovery...')
                df_api = pd.read_csv(constants.HOME_DIR+'/data_instagram/users_business_discovery_201809051046.csv', header=0, sep = '\t', index_col = None)
                df_api['updated_date'] = df_api['updated_date'].fillna("").apply(lambda x: x if x !="" else "2018-01-01 0:0:0")
                self.db.insert_into_business_discovery(df_api, constants.KEYSPACE_NAME)
            # pdb.set_trace()
            # df_scrapy = self.db.exectute_query(constants.SQL_GET_DATA_RECOMMEND_INFLUENCER)
            try:
                df_scrapy = self.db.session.execute(constants.SQL_GET_DATA_RECOMMEND_INFLUENCER, timeout = 50)
                df_scrapy=df_scrapy._current_rows
            except Exception as ex:
                self.loggers.exception(ex)
                df_scrapy = None

            # pdb.set_trace()
            if df_scrapy is None or df_scrapy.shape[0]<10:
                df_scrapy = self.read_json_to_df() #read data

                df_scrapy = self.preprocessing_data(df_scrapy) # preprocessing data influencer
                self.loggers.info('read from file json, df_crapy.shape: %s'%str(df_scrapy.shape))
                #insert into db
                # self.db.insert_into_recommend_influencer(df_scrapy)

            #pdb.set_trace()
            df= df_api.merge(df_scrapy[['categories','instagram_id', 'account_type']],left_on='username', right_on='instagram_id')
            df = df.loc[:, df.columns != 'instagram_id']
            df['id'] = df['id'].apply(lambda x: str(x))
            df['type_resource'] = 'crawl'
            df['id_app'] = ""
            
            self.df = df
            self.loggers.warning('***** shape of dataframe init: %s'%str(self.df.shape))
            # print(df.head())
            self.tfidf_matrix, self.tfidf_vectorizer, self.list_business = self.train_matrix(self.df) # buidl matrix distance
            self.df = self.df.reindex(sorted(df.columns), axis=1)#sort index columns by name

        except Exception as ex:
            print(ex)
            self.loggers.exception(ex)

    def init_data_from_aify_app(self):
        def collect_key_word(row):
            try:
                new_string = row['categories'] + row['keyword_by_user']
                return new_string
            except Exception as ex:
                # print(ex)
                return row['categories']
        try:
            # pdb.set_trace()
            # if self.db == None or 'self.db' not in locals():
            #     self.db = db_cassandra.db_cassandra(contact_points = constants.HOST_CASSANDRA_DB,port_= constants.PORT_CASSANDRA_RS ,factory =pandas_factory) # pandas_factory

            self.db.session.row_factory = pandas_factory
            rows = self.db.session.execute("select * from %s.social_user;"%(constants.KEYSPACE_NAME))
            rows2 = self.db.session.execute("select * from %s.user_hashtag_setting;"%(constants.KEYSPACE_NAME))
            df1 = rows._current_rows
            df2 = rows2._current_rows
            df1 = df1[df1.social_type.isin(['instagram_business'])] #only instagram
            #append keyword_by_user into column categories
            df2['categories'] = df2.apply(collect_key_word, axis = 1)

            self.df = df1.merge(df2[['owner_id','categories']],left_on='id', right_on='owner_id')
            # pdb.set_trace()
            self.df = self.df[['social_type', 'external_id', 'access_token', 'account_id',\
                'avatar_url', 'created', 'followers_cnt', 'follows_cnt', 'fullname',\
                'id', 'post_cnt', 'updated', 'username', 'owner_id', 'categories']]
            
            column_name = ['social_type', 'id', 'access_token', 'account_id',
                'profile_picture_url', 'created', 'followers_count', 'follows_cnt', 'name',
                'id_app', 'media_count', 'updated_date', 'username', 'owner_id', 'categories']
            self.df.columns = column_name
            
            self.df = self.df[['id','profile_picture_url', 'followers_count', 'name', 'media_count', 'updated_date', 'username', 'categories', 'id_app']]
            self.df['id_app'] =  self.df['id_app'].apply(lambda x: str(x))  

            self.df['type_resource'] = 'aify'
            self.df['account_type'] = 0
            self.df['biography'] = ''
            self.df['comments_count'] = 0
            self.df['likes_count'] = 0
            
            self.df = self.df.reindex(sorted(self.df.columns), axis=1)
            self.tfidf_matrix, self.tfidf_vectorizer, self.list_business = self.train_matrix(self.df) # buidl matrix distance
            self.loggers.warning('***** shape of aify dataframe init: %s'%str(self.df.shape))
        except Exception as ex:
            print(ex)
            recommend_utils.bug_info()
            self.loggers.exception(ex)  


    def init_data_raw(self):
        df_inf = self.read_json_to_df() #read data
        df_inf = df_inf.drop_duplicates(['bio', 'name', 'path'], keep = 'last') #delete duplicate rows
        self.df = self.preprocessing_data(df_inf) # preprocessing data influencer
        # self.tfidf_matrix, self.tfidf_vectorizer, self.list_business = self.train_matrix(self.df) # buidl matrix distance
        return self.df


    # load data from json file
    def read_json_to_df(self, dir_files = constants.HOME_DIR+'/data_instagram/all_data/'):
        '''
        #input: dir_files: str
        #ouput: dataframe
        '''
        self.loggers.warning("***** begin read json files.... ")
        # with open('data_instagram/fashion/cosmetics-1531820364794.json', "r") as read_file:
        #     data = json.load(read_file)  
        # df_inf = pd.DataFrame.from_dict(data, orient='columns')
        df_inf = pd.DataFrame(index=None)
        
        for json_file in os.listdir(dir_files):
            try:
                if json_file.endswith('.json'):
                    with open(os.path.join(dir_files, json_file), "r") as read_file:
                        data = json.load(read_file)
                        df = pd.DataFrame.from_dict(data, orient='columns')
                        df_inf= pd.concat([df, df_inf], axis=0, sort=True)
            except Exception as ex:
                recommend_utils.bug_info()
                self.loggers.exception(ex)
                pass
        self.loggers.warning("***** read json files and write into db %s "%(str(df_inf.shape)) )        
        return df_inf  

        # load avarta urls to dataframe (crawler in /home/anh_lbt/workspace/instagram-profilecrawl)
    def read_avarta_urls_to_df(self, dir_files = constants.HOME_DIR+'/data_instagram/instagram-profilecrawl/results'):
        # with open('data_instagram/fashion/cosmetics-1531820364794.json', "r") as read_file:
        #     data = json.load(read_file)  
        # df_inf = pd.DataFrame.from_dict(data, orient='columns')
        df_inf = pd.DataFrame(index=None)
        for file in os.listdir(dir_files):
            try:
                if file.endswith('.txt'):
                    with open(os.path.join(dir_files, file), "r") as read_file:
                        data = pd.read_csv(read_file,sep='\t', header=None)
                        df = pd.DataFrame.from_dict(data, orient='columns')
                        df_inf= pd.concat([df, df_inf], axis=0)
            except Exception as ex:
                recommend_utils.bug_info()
                self.loggers.exception(ex)      
        return df_inf

    def train_matrix(self, df): #build matrix to calculate distance between vector
        list_business = list()
        for x in range(len(df['categories'])):
            try:
                if isinstance(df['categories'].iloc[x], list):
                    if len(df['categories'].iloc[x]) > 0:
                        list_business.append(' '.join([stemmer.stem(word) for word in df['categories'].iloc[x]]))
                    else:
                        print('empty list')  
                elif isinstance(df['categories'].iloc[x], str):
                    #column categories with type text (ex: '["hot great","Vehicle service and accessories","Toys and hobbies","Sports and outdoors","Vehicle sales"]')
                    list_business.append(' '.join([stemmer.stem(word) for word in re.sub(r'[\[\]\"]', "", df['categories'].iloc[x]).split(',')]))   
                elif df['categories'].iloc[x] is None or df['categories'].iloc[x] =='':
                    list_business.append('Aify')
            except Exception as ex:
                self.loggers.error(ex)
                recommend_utils.bug_info()
                pass
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    #     tfidf = tfidf_vectorizer.fit(list_business)
    #     tfidf_matrix= tfidf_vectorizer.transform(list_business)
        # print(list_business)
        tfidf_matrix = tfidf_vectorizer.fit_transform(list_business)
       
        return tfidf_matrix, tfidf_vectorizer, list_business
    

    def predict_similar(self, list_business_word, tfidf_matrix, num_sentence_similar=50, account_type = 0, temp_mode = True, num_followers=4000, aify_followers = 0):
#         list_text = []
#         list_text= stemmer.stem(' '.join(list_business_word))
#         print(list_text)
        def calculate(row):
            try:
                # return (row['likes_count'] + row['comments_count']) /(row['media_count'] *row['followers_count']*1.0)
                if row['followers_count'] == 0:
                    return 0
                else:    
                    return (row['likes_count'] + row['comments_count']) /(row['followers_count']*1.0)
            except Exception as ex:
                print(ex)
                self.loggers.exception(ex)
                return 0  

        try:
            # pdb.set_trace()
            list_text = []
            list_text= [stemmer.stem(x) for x in list_business_word.split(',')]
            list_text = ' '.join(list_text)
            # print('list text: %s'%list_text)

            sentence_to_vector = self.tfidf_vectorizer.transform([list_text])#toarray()
            arr = cosine_similarity(sentence_to_vector, tfidf_matrix)
            preds = arr[0, 0:]
            sorted_inds = [i[0] for i in sorted(enumerate(-preds), key=lambda x:x[1])]
            # pdb.set_trace()
            tmp_df = self.df.iloc[sorted_inds]  
            if sys.version_info[0] < 3:
                tmp_df['engagement'] = map(recommend_utils.calculate_engagement, tmp_df.followers_count, tmp_df.likes_count, tmp_df.comments_count)
            else:
                tmp_df['engagement'] = tmp_df.apply(calculate, axis=1)
                # tmp_df['engagement'] = tmp_df.apply(lambda row: recommend_utils.calculate_engagement(row['followers_count'], row['likes_count'], row['comments_count']),axis=1)
                # tmp_df['engagement'] = list(map(recommend_utils.calculate_engagement, \
                #     tmp_df.loc[,('followers_count')], tmp_df.loc[, ('likes_count')], tmp_df.loc[, ('comments_count')]))
            
            if temp_mode: # run from crawl data
                tmp_df = tmp_df[tmp_df['followers_count']>= num_followers]
                if account_type == 2:# account_type 0: influencer, 1: branch, 2: all
                    return tmp_df[:num_sentence_similar], preds
                else:
                    return tmp_df[tmp_df['account_type'] == account_type][:num_sentence_similar], preds
                # return sorted_inds[:num_sentence_similar], preds
            else: # run from aify_db
                aify_df_index = [item for item in sorted_inds if preds[item]>= constants.RS_SIMILAR_SUPPORT_COEF]
                
                if len(aify_df_index) > num_sentence_similar:
                    tmp_df = tmp_df[:num_sentence_similar]   
                else:
                    tmp_df = tmp_df[:len(aify_df_index)]
                    # return tmp_df[:len(aify_df_index)], preds 
                return tmp_df[tmp_df['followers_count']>= aify_followers], preds    

        except Exception as ex:
            recommend_utils.bug_info()
            self.loggers.exception(ex)
    #convert text to numberic (k = 1000, m = 1000000)
    def convert_k_m_value(self, number_in_text):
        try:
            if number_in_text is not None:
                if isinstance(number_in_text, float) and math.isnan(number_in_text):
                    return 0
                if 'k' in number_in_text:
                    str_number = number_in_text.replace('k', '')
                    return int(float(str_number) * 1000)
                elif 'm' in number_in_text:
                    str_number = number_in_text.replace('m', '')
                    return int(float(str_number) * 1000000)
                elif len(number_in_text) > 0:
                    try:
                        return int(float(number_in_text))
                    except:
                        return 0    
                else:
                    return 0    
            else:
                return 0        
        except Exception as ex:
            recommend_utils.bug_info()
            print(ex)
            return 0
    
    
    def get_id_instagram(self, list_of_dict_social_account):
        try:
            for x in list_of_dict_social_account:
                if('instagram' in x['link']):
        #             print(x['link'])
                    return x['link'].split('/')[-1]
        except:
            return ""            

    def get_follower_instagram(self, list_of_dict_social_account):
        try:
            for x in list_of_dict_social_account:
                if('instagram' in x['link']):
        #             print(x['link'])
                    return str(x['follower'])
        except:
            return '0' 

    # def format_mix_data(self, x):
    #     #convert to string
    #     if isinstance(x, float) and math.isnan(x):
    #         return ""           


    def preprocessing_data(self, df):
        try:
            df = df.fillna("")
            df = df.drop_duplicates(['bio', 'name', 'path'], keep = 'last') #delete duplicate rows
            df = df[df.socialAccounts != ""]
            # df['engagementRate']= df['engagementRate'].fillna("")
            # df['bio']= df['bio'].fillna("")
            # df['categories']= df['categories'].fillna("")
            # df['demographics'] = df['demographics'].fillna("")
            # df['website'] = df['website'].fillna("")
            df['reach'] = df['reach'].replace('\n', '',inplace=True)

            # df['socialAccounts'] = df['socialAccounts'].apply(lambda x: str(x))# save with string format
            df['commentPerPost'] = df['commentPerPost'].apply(lambda x: str(x))
            df['likePerPost'] = df['likePerPost'].apply(lambda x: str(x))
            df['follower'] = df['socialAccounts'].apply(lambda x: self.get_follower_instagram(x))

            df['name'] = df['name'].replace('', 'Unknown')
        #     df['categories'] = df['categories'].apply(lambda x: ','.join(x)) # save with string format
        #     df['socialAccounts'] = df['socialAccounts'].apply(lambda x: ','.join(x))

            df['commentPerPost'] = df['commentPerPost'].apply(lambda x: self.convert_k_m_value(x))
            df['likePerPost'] = df['likePerPost'].apply(lambda x: self.convert_k_m_value(x))
            df['follower'] = df['follower'].apply(lambda x: self.convert_k_m_value(x))

            # paser demographics
            df['gender'] = df['demographics'].apply(lambda x: x.split(',')[0])
            df['age'] = df['demographics'].apply(lambda x: x.split(',')[1].split()[0] if ',' in x else np.nan)
            
            df['account_type']= df['engagementRate'].apply(lambda x: 0 if len(x) > 0 else 1)# 0: influencer, 1: branch

            df['instagram_id'] = df['socialAccounts'].apply(lambda x: self.get_id_instagram(x))
            df = df.dropna(how='any', subset= ['instagram_id'])
            #join 2 dataframe, (l)
            # df_avarta_urls = self.read_avarta_urls_to_df()
            # df_avarta_urls.columns = ['instagram_id', 'img_url']
            # df= df.merge(df_avarta_urls,left_on='instagram_id', right_on='instagram_id')
        except Exception as ex:
            recommend_utils.bug_info()
            self.loggers.exception(ex)
            df = pd.DataFrame()
            pass

        return df



# json_ = df.columns
# a = pd.read_json(json_, typ='series', orient='records')
    def get_engagement(self, owner_id):
        try:
            query = "select sum(post_score) from %s.post where owner_id = %s"%(constants.KEYSPACE_NAME,str(owner_id))
            # print(query)
            
            self.db.session.row_factory = pandas_factory
            df = self.db.exectute_query(query)
            # df = rows._current_rows
            enga = float(df.iloc[0,0])
            return enga
        except Exception as ex: 
            # recommend_utils.bug_info()
            self.loggers.exception(ex)
            return 0

    # copy from watch list
    def wl_get(self, user_id):
        result = {}
        try:
            # t1 = time.time()
            # print(self.db.session.row_factory)
            query_string="select * from %s.watch_list where user_id = '%s';"%(constants.KEYSPACE_NAME, user_id)
            re = self.db.session.execute(query_string)
            # print(re)
            list_dict_ = recommend_utils.map_to_dict_factory_1(re.current_rows)#data get from db, list have only one item
        #     list_dict_ = re.current_rows           
            if len(list_dict_) > 0 :
                if list_dict_[0]['watch_user_list'] is None:
                    result['data'] = None
                else:      
                    result['data'] = [key for key, value in list_dict_[0]['watch_user_list'].items()]
            else:
                result['data'] = None
        except Exception as ex:
            result['data'] = None
            result['message'] = ex
            self.loggers.error(ex)
        return result        
        




# if __name__=="__main__":
#     print('running....')
#     # calculate distance from a sentence to list of sentences
#     # list_business_word = 'entertainment fashion lifestyle food and drinks travel and tour'
    # pdb.set_trace()
    # from crawl data
    # sim_inf = similar_influencer()
    # sim_inf.init_data_from_data_crawl()

    # num_results = 3
    # acc_type = 0
    # list_business_word = 'Entertainment, Fashion, Lifestyle, Food And Drinks, Travel And Tourism]'
    # df, preds = sim_inf.predict_similar(list_business_word, sim_inf.tfidf_matrix, num_results, acc_type)
    # print(df)

    # from aify
    # list_business_word2 = 'travel'
    # sim_inf2 = similar_influencer()
    # sim_inf2.init_data_from_aify_app()
    # print('===============')
    # # pdb.set_trace()
    # df2, preds2 = sim_inf2.predict_similar(list_business_word2, sim_inf2.tfidf_matrix, -1, 0, False)
    # print(df2)
    # print(df2['engagement'])

    # print(sim_inf2.get_engagement('ba5ee910-aaa8-11e8-a25d-bbf697a6eaed'))
          

    
    
    # sim_inf2 = similar_influencer()
    # sim_inf2.db.session.row_factory = dict_factory
    # res_wl = sim_inf2.wl_get('anhlbt')

    # print(res_wl['data'])



