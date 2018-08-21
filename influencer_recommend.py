"""
@author: anhlbt
created: 08/07/2018
"""

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
from FacebookCrawler import constants
import pdb

stemmer = PorterStemmer()
def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)

class similar_influencer():
    
    def __init__(self):
        db = db_cassandra.db_cassandra(contact_points = ['172.33.47.9'], factory = pandas_factory)
        df_api = db.exectute_query(constants.SQL_GET_DATA_USER_BUSINESS_DISCOVERY)
        df_scrapy = db.exectute_query(constants.SQL_GET_DATA_RECOMMEND_INFLUENCER)

        #pdb.set_trace()
        # categories influencer_id
        df= df_api.merge(df_scrapy[['categories','instagram_id', 'account_type']],left_on='username', right_on='instagram_id')
        self.df = df
        self.tfidf_matrix, self.tfidf_vectorizer, self.list_business = self.train_matrix(self.df) # buidl matrix distance


    def init_data_raw(self):
        df_inf = self.read_json_to_df() #read data
        df_inf = df_inf.drop_duplicates(['bio', 'name', 'path'], keep = 'last') #delete duplicate rows
        self.df = self.preprocessing_data(df_inf) # preprocessing data influencer
        self.tfidf_matrix, self.tfidf_vectorizer, self.list_business = self.train_matrix(self.df) # buidl matrix distance


    # load data from json file
    def read_json_to_df(self, dir_files = 'data_instagram/fashion/'):

        # with open('data_instagram/fashion/cosmetics-1531820364794.json', "r") as read_file:
        #     data = json.load(read_file)  
        # df_inf = pd.DataFrame.from_dict(data, orient='columns')
        df_inf = pd.DataFrame(index=None)
        try:
            for json_file in os.listdir(dir_files):
                if json_file.endswith('.json'):
                    with open(os.path.join(dir_files, json_file), "r") as read_file:
                        data = json.load(read_file)
                        df = pd.DataFrame.from_dict(data, orient='columns')
                        df_inf= pd.concat([df, df_inf], axis=0)
        except Exception as ex:
            print(ex)
            pass
        return df_inf   

        # load avarta urls to dataframe (crawler in /home/anh_lbt/workspace/instagram-profilecrawl)
    def read_avarta_urls_to_df(self, dir_files = './data_instagram/instagram-profilecrawl/results'):
        # with open('data_instagram/fashion/cosmetics-1531820364794.json', "r") as read_file:
        #     data = json.load(read_file)  
        # df_inf = pd.DataFrame.from_dict(data, orient='columns')
        df_inf = pd.DataFrame(index=None)
        for file in os.listdir(dir_files):
            if file.endswith('.txt'):
                with open(os.path.join(dir_files, file), "r") as read_file:
                    data = pd.read_csv(read_file,sep='\t', header=None)
                    df = pd.DataFrame.from_dict(data, orient='columns')
                    df_inf= pd.concat([df, df_inf], axis=0)
        return df_inf

    def train_matrix(self, df): #build matrix to calculate distance between vector
        list_business = list()
        for x in range(len(df['categories'])):
            if len(df['categories'].iloc[x])> 0:
        
                list_business.append(' '.join([stemmer.stem(x) for x in df['categories'].iloc[x]]))
            else:
                print(len(df['categories'][x]))

        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    #     tfidf = tfidf_vectorizer.fit(list_business)
    #     tfidf_matrix= tfidf_vectorizer.transform(list_business)

        tfidf_matrix = tfidf_vectorizer.fit_transform(list_business)
        return tfidf_matrix, tfidf_vectorizer, list_business

    def predict_similar(self, list_business_word, tfidf_matrix, num_sentence_similar=10, account_type = 0):
        #     list_business_word = ['Entertainment', 'Fashion', 'Lifestyle', 'Food And Drinks', 'Travel And Tourism']

#         list_text = []
#         list_text= stemmer.stem(' '.join(list_business_word))
#         print(list_text)

        list_text = []
        list_text= [stemmer.stem(x) for x in list_business_word.split(',')]
        list_text = ' '.join(list_text)


        sentence_to_vector = self.tfidf_vectorizer.transform([list_text])#toarray()
        arr = cosine_similarity(sentence_to_vector, tfidf_matrix)
        preds = arr[0, 0:]
        sorted_inds = [i[0] for i in sorted(enumerate(-preds), key=lambda x:x[1])]
        #pdb.set_trace()
        tmp_df = self.df.iloc[sorted_inds]
        if account_type == 2:
            return tmp_df[:num_sentence_similar], preds
        else:
            return tmp_df[tmp_df['account_type'] == account_type][:num_sentence_similar], preds
        # return sorted_inds[:num_sentence_similar], preds



    #convert text to numberic (k = 1000, m = 1000000)
    def convert_k_m_value(self, number_in_text):
        try:
            if 'k' in number_in_text:
                str_number = number_in_text.replace('k', '')
                return int(float(str_number) * 1000)
            elif 'm' in number_in_text:
                str_number = number_in_text.replace('m', '')
                return int(float(str_number) * 1000000)
            else:
                return int(number_in_text)
        except Exception as ex:
    #         print(ex)
            return 0
    
    
    def get_id_instagram(self, list_of_dict_social_account):
        for x in list_of_dict_social_account:
            if('instagram' in x['link']):
    #             print(x['link'])
                return x['link'].split('/')[-1]


    def preprocessing_data(self, df):
        try:
            df['bio']= df['bio'].fillna("")
            df['categories']= df['categories'].fillna("")
            df['demographics'] = df['demographics'].fillna("")
            df['website'] = df['website'].fillna("")
            df['reach'] = df['reach'].replace('\n', '',inplace=True)
        #     df['socialAccounts'] = df['socialAccounts'].apply(lambda x: str(x))# save with string format
            # df['commentPerPost'] = df['commentPerPost'].apply(lambda x: int(x))
            # df['likePerPost'] = df['likePerPost'].apply(lambda x: int(x))
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

            #join 2 dataframe, (l)
            df_avarta_urls = self.read_avarta_urls_to_df()
            df_avarta_urls.columns = ['instagram_id', 'img_url']
            df= df.merge(df_avarta_urls,left_on='instagram_id', right_on='instagram_id')
        except Exception as ex:
            print(ex)
            pass

        return df



# json_ = df.iloc[1].to_json()
# a = pd.read_json(json_, typ='series', orient='records')

if __name__=="__main__":
#     # calculate distance from a sentence to list of sentences
#     # list_business_word = 'entertainment fashion lifestyle food and drinks travel and tour'
    #pdb.set_trace()
    sim_inf = similar_influencer()

    num_results = 2
    acc_type = 0
    list_business_word = 'Entertainment, Fashion, Lifestyle, Food And Drinks, Travel And Tourism]'
    df, preds = sim_inf.predict_similar(list_business_word, sim_inf.tfidf_matrix, num_results, acc_type)
    print(df)


