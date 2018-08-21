import pandas as pd
import os


def read_multi_file_to_df(dir_files = './data_api_insta/'):
    df_inf = pd.DataFrame(index=None)
    for file in os.listdir(dir_files):
        if file.endswith('.txt'):
            data = pd.read_csv(os.path.join(dir_files, file),sep='\t', header=0)
#             df = pd.DataFrame.from_dict(data, orient='columns')
            df_inf= pd.concat([data, df_inf], axis=0)
    return df_inf


