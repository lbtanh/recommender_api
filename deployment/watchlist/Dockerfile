FROM   python:3
MAINTAINER vanvv <vanvv@atvn.com.vn>

COPY sw_follou_recommendation.tar.gz /sw_follou_recommendation.tar.gz
RUN mkdir sw_follou
RUN tar -zxvf sw_follou_recommendation.tar.gz -C /sw_follou

WORKDIR /sw_follou/recommender_api
RUN pip3 install -r requirements.txt
WORKDIR /sw_follou/recommender_api/watch_list
EXPOSE 5001
CMD [ "sh", "wl_run_server.sh"]
