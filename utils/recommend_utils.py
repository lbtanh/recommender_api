import pandas as pd
import os, sys
import logging
from os.path import dirname, join, exists
from cassandra.util import OrderedMapSerializedKey
import logging
from os.path import join, dirname, exists
from logging.handlers import RotatingFileHandler
  

def read_multi_file_to_df(dir_files = './data_api_insta/'):
    df_inf = pd.DataFrame(index=None)
    for file in os.listdir(dir_files):
        if file.endswith('.txt'):
            data = pd.read_csv(os.path.join(dir_files, file),sep='\t', header=0)
#             df = pd.DataFrame.from_dict(data, orient='columns')
            df_inf= pd.concat([data, df_inf], axis=0)
    return df_inf


#convert OrderedMapSerializedKey to dict (from cassandra)


def OrderedMapSerializedKeyToDict(map_data): 
    lst = []
    for idx_value, i_value in enumerate(map_data):
        if type(i_value) is OrderedMapSerializedKey:
#             print(i_value) #{'follower': '15.6k', 'link': 'https://instagram.com/martilenia', 'type': 'Instagram Link Click'}
            lst.append(dict(i_value))
    return lst
# OrderedMapSerializedKeyToDict(row[0])


def map_to_dict_factory_2(dict_):
    try:
        for key, value in dict_.items():
            if isinstance(value, OrderedMapSerializedKey):
                d = dict()
                for key2, value2 in dict(value).items():
                    if isinstance(value2, OrderedMapSerializedKey):
                        d[key2] = dict(value2)
                dict_[key] = d    
    except Exception as ex:
        print(ex)
        pass
    return dict_

#return list of dict
def map_to_dict_factory_1(list_of_dict):
    try:
        ls_dic_re = []
        for idx_value, i_value in enumerate(list_of_dict):
            for key, value in i_value.items():
                if isinstance(value, OrderedMapSerializedKey):
                    i_value[key] = dict(value)
            ls_dic_re.append(i_value)
    except Exception as ex:
        print(ex)
        pass
    return ls_dic_re


def calculate_engagement(followers_count, likes_count, comments_count):
    try:
        if followers_count > 0:
            # return (int(comments_count) + int(likes_count))/int(followers_count) *int(media_count) * 1.0
            return (int(comments_count) + int(likes_count))/int(followers_count) * 1.0
        else:
            return 0    
    except Exception as ex:
        return 0
        # print(ex, followers_count, likes_count, comments_count)     

def bug_info():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)         


def convert_info_objects_to_json(info_object):
    tmp_dict = {}
    for k, v in info_object['watch_user_list'].items():
        try:
            # print(k)
            # tmp_dict[k] = dict(**v)
            tmp_dic_2 = {}
            for i in v._fields: 
                # print("%s:%s" %(i, j))
                tmp_dic_2[i] = v[i]
        except Exception as ex:
            pass 
        tmp_dict[k] = tmp_dic_2  
    info_object['watch_user_list'] = tmp_dict            
    return info_object #info_object     



def get_logger(log_file = 'rs_log.log'):
    try:
        directory = join(os.getcwd(), 'logs')
        
        if not exists(directory):
            os.makedirs(directory)
        file_path = join(directory, log_file)

        # if not os.path.isfile(file_path):
        #     file = open(file_path, 'w+')
            # file.close()
        # if(os.access(file_path, os.W_OK)):
        #         print(file_path + " is writable.") 

        service_name = os.getenv("SERVICE_NAME", None)
        if service_name:
            logger = logging.getLogger("%s.%s" % (service_name, __name__))
        else:
            logger = logging.getLogger(log_file)

        # Create the Handler for logging data to a file
        logger_handler = logging.FileHandler(file_path)
        logger_handler.setLevel(logging.WARNING)
        #set maximum size for logger file
        logger_handler = RotatingFileHandler(file_path, mode='a', maxBytes=100*1024*1024, 
                                 backupCount=2, encoding=None, delay=0)
            
        # Create a Formatter for formatting the log messages
        # formater = '%(name)s - %(levelname)s - %(message)s'
        logger_formatter = logging.Formatter('[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s')
        # Add the Formatter to the Handler
        logger_handler.setFormatter(logger_formatter)
        # Add the Handler to the Logger
        logger.addHandler(logger_handler)

        # logging.basicConfig(filename=file_path, level=logging.INFO,
        # format = '[%(filename)s:%(lineno)s - %(funcName)s %(asctime)s;%(levelname)s] %(message)s',
        # datefmt = '%a, %d %b %Y %H:%M:%S'
        # )
        # loggers = logging.getLogger('rs_log')
        # logger_handler = logging.FileHandler(file_path)  
        # loggers.addHandler(logger_handler)
        return logger
    except Exception as ex:
        print(ex)    


def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def subtract_timestamp(row):
    try:
        total_s = (row['DAYS'] - row['updated_date']).total_seconds()
        return total_s/86400
    except Exception as ex:
        # print(ex)
        return 0
