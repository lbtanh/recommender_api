import pandas as pd
import os
from cassandra.util import OrderedMapSerializedKey


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