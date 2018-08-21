# USAGE
# Start the server:
# 	python run_server.py
# Submita a request via Python:
#	python client.py

# import the necessary packages
import numpy as np
import flask
import io
import json, datetime
from flask import request
from influencer_recommend import *
import pdb

# initialize our Flask application 
app = flask.Flask(__name__)
# model = None

@app.route("/")
def hello():
    now = datetime.datetime.now()
    return "Hello arrivetechnologies.com  " + str(now)

@app.route("/predict_inf",methods=["POST"])
def predict():
    now = datetime.datetime.now()
    if flask.request.method == "POST":
        # print (request.is_json)
        print("request: %s"%now)
        content = request.get_json()
        print(content)
        key_words = content['list_key_word']
        acc_type = content['acc_type']
        num_results = content['num_results']
        # pdb.set_trace()
        df, preds = sim_inf.predict_similar(key_words, sim_inf.tfidf_matrix, num_results, acc_type)
        # OverflowError: Unsupported UTF-8 sequence length when encoding string
        df = df.loc[:, df.columns != 'ts']

        # print(df)

        # for x in sorted_inds[:2]:
        # #     print(x, preds[x], sim_inf.dfl['categories'].iloc[x])
        #     print(x, preds[x], sim_inf.df.iloc[x].to_json())
        # print(sim_inf.df.iloc[sorted_inds].to_json(orient='index'))
        
        # return sim_inf.df.iloc[sorted_inds].to_json(orient='index')
        return df.to_json(orient = 'index')



# load the tfidf_matrix for predict jobs and
# then start the server
if __name__ == "__main__":
    print("* Loading tfidf_matrix and Flask starting server...\nplease wait until server has fully started")
	# calculate distance from a sentence to list of sentences
    sim_inf = similar_influencer()
    app.run(host = '0.0.0.0', port=5000, debug=False)    