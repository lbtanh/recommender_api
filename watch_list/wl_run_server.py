
import numpy as np
import flask
import io
import json, datetime
from flask import request
import pdb, time
from threading import Thread
from wl_watch_list import *
from datetime import datetime
from utils import constants

# initialize our Flask application 
app = flask.Flask(__name__)
# model = None

@app.route("/")
def hello():
    now = datetime.now()
    return "Hello arrivetechnologies\n Watch List is working... " + str(now)


@app.route("/wl_add", methods=['POST'])
def wl_add():
    if flask.request.method == "POST":
        # print (request.is_json)
        content = request.get_json()
        print(content)
        user_id = content['user_id']
        ig_id = content['ig_id']
        a = wl_inst.wl_add(user_id=user_id, ig_id=ig_id)
        print(a)
        # pdb.set_trace()
        return flask.jsonify(a)

@app.route("/wl_remove", methods=['POST'])
def wl_remove():
    if flask.request.method == "POST":
        content = request.get_json()
        print(content)
        user_id = content['user_id']
        ig_id = content['ig_id']
        a = wl_inst.wl_remove(user_id=user_id, ig_id=ig_id)
        print(a)
        return flask.jsonify(a)

@app.route("/wl_get")
def wl_get_wl():
    if flask.request.method == "GET":
        content = request.get_json()
        print(content)
        user_id = content['user_id']
        a = wl_inst.wl_get(user_id=user_id)
        a = wl_inst.convert_info_objects_to_json(a)
        print(a)
        return flask.jsonify(a)
     

@app.route("/wl_update_now_post")
def wl_update_now_post():
    if flask.request.method == "GET":
        content = request.get_json()
        print(content)
        user_id = content['user_id']
        a = wl_inst.wl_update_new_post(user_id=user_id)
        print(a)
        return flask.jsonify(a)



if __name__ == "__main__":
    print("* Running watch list and Flask starting server...\nplease wait until server has fully started")
    wl_inst = watch_list()
    

    app.run(host = constants.HOST_WATCH_LIST, port=constants.PORT_WATCH_LIST, debug=False)    