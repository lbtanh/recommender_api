
import numpy as np
import flask
import io
import json, datetime
from flask import request
import pdb, time
from threading import Thread
from wl_watch_list import *
from datetime import datetime
from utils import constants, recommend_utils
from aiohttp import web
from aiohttp_wsgi import WSGIHandler

# initialize our Flask application 
app = flask.Flask(__name__)
# wl_inst = watch_list()
logger = recommend_utils.get_logger('wl_run_sever.log')

@app.route("/")
def hello():
    now = datetime.now()
    return "Hello arrivetechnologies\n Watch List is working... " + str(now)


@app.route("/wl_add", methods=['POST'])
def wl_add():
    try:
        if flask.request.method == "POST":
            # print (request.is_json)
            content = request.get_json()
            logger.warning("request wl_add: content: %s"%content)
            
            user_id = content['user_id']
            ig_id = content['ig_id']
            acc_type = content['acc_type']
            picture_url = content['picture_url']
            a = wl_inst.wl_add_2(user_id=user_id,wl_obj = wl_inst, ig_id=ig_id,picture_url = picture_url, acc_type=acc_type)
            # print(a)
            # pdb.set_trace()
            return flask.jsonify(a)
    except Exception as ex:
        logger.error(ex)
        return flask.jsonify({"error": str(ex)})        

@app.route("/wl_remove", methods=['POST'])
def wl_remove():
    try:
        if flask.request.method == "POST":
            content = request.get_json()
            logger.warning("request wl_remove: content: %s"% content)
            user_id = content['user_id']
            ig_id = content['ig_id']
            a = wl_inst.wl_remove(user_id=user_id,wl_obj = wl_inst, ig_id=ig_id)
            # print(a)
            return flask.jsonify(a)
    except Exception as ex:
        logger.error(ex)
        return flask.jsonify({"error": str(ex)})        

@app.route("/wl_get")
def wl_get_wl():
    try:
        if flask.request.method == "GET":
            content = request.get_json()
            logger.warning("request wl_get: content: %s"%content)
            user_id = content['user_id']
            acc_type = content['acc_type']
            # pdb.set_trace()
            wl_inst.wl_update_new_post(user_id=user_id,wl_obj = wl_inst, acc_type = acc_type)
            re = wl_inst.wl_get(user_id=user_id, wl_obj = wl_inst, convert_to_json=True, acc_type=acc_type)
            # print(re)
            # return a
            return flask.jsonify(re)
    except Exception as ex:
        logger.error(ex)
        return flask.jsonify({"error": str(ex), "status":"False"})       
     

# @app.route("/wl_update_now_post")
# def wl_update_now_post():
#     if flask.request.method == "GET":
#         content = request.get_json()
#         print(content)
#         user_id = content['user_id']
#         a = wl_inst.wl_update_new_post(user_id=user_id)
#         print(a)
#         return flask.jsonify(a)


@app.route("/wl_get_info_detail")
def wl_get_info_detail():
    try:
        if flask.request.method == "GET":
            content = request.get_json()
            logger.warning("request wl_get_info_detail: content: %s"%content)

            social_id = '9c88c600-ac5f-11e8-80f4-eb836fc406ca'
            social_id = content['social_id']
            from_timestamp = content['from_timestamp']
            until_timestamp = content['until_timestamp']
            js, df = wl_inst.get_user_insight_day_history(social_id,from_timestamp,until_timestamp)

            # print(js)
            return flask.jsonify(js)
    except Exception as ex:
        logger.error(ex)
        return flask.jsonify({"error": str(ex)})    



def thread_init_watch_list(threadname):
    global wl_inst
    while 1:
        try:
            wl_inst = watch_list()
            logger.warning('\n====== %s thread connect db is working...====='%datetime.now())
            time.sleep(86400) #300
        except Exception as ex:
            logger.error(ex)
            pass   


def setup(app):
    try: 
        time.sleep(1)
        thread_init_obj = Thread( target = thread_init_watch_list, args =('Thread init watch list....', ))
        thread_init_obj.start() 
    except Exception as ex:
        logger.error(ex)

def make_aiohttp_app(app):
    wsgi_handler = WSGIHandler(app)
    aioapp = web.Application()
    aioapp.router.add_route('*', '/{path_info:.*}', wsgi_handler)
    return aioapp

setup(app)

if __name__ == "__main__":
    while 1:
        try: 
            logger.warning("* Running watch list and Flask starting server...\nplease wait until server has fully started")
            if 'wl_inst' not in globals():
                wl_inst = watch_list()
            app.run(host = constants.HOST_WATCH_LIST, port=constants.PORT_WATCH_LIST, debug=False)   
            logger.warning('service is running....')
            break
        except Exception as ex:
            logger.error(ex)
            time.sleep(5) 