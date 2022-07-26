

import json
import sys
import traceback
from typing import Any, Text, Dict, List, Union
import requests
from flask import Flask
from flask import request
from flask import jsonify
#from flask_cors import CORS
import urllib
import collections
#import findspark
#from codebase.main.predictors.vqlPayload_Cluster_Join import callback
#findspark.init()
import os

from sqlalchemy import false

from src.main.api.exceptions import RequiredParameterMissingError, BadRequestError
from src.main.api.params import params_from_request
API_HOST = "localhost"
API_PORT = 5007

from src.main.api import exceptions


import urllib.request, json
app = Flask(__name__)
#cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
my_spark = None
globalCredentials = None
from datetime import datetime, timedelta, time


import json

import regex
import uuid



def loadtrainingdata():
    """
       Tags: machines
       ---
       Gets machines and their metadata from all clouds.
       Check Permissions take place in filter_list_machines.
       READ permission required on cloud.
       READ permission required on location.
       READ permission required on machine.
       """
    print("inside load training data")
    print("inside TENANT training data")
    # logger.info("----------  LOADING TENANT CREDENTIALS  ----------")
    #app.run(host=API_HOST, port=API_PORT)
    json_string = {'provider': 'ec2', '_cls' : 'Cloud.AmazonCloud' ,'machine_count' : 0  ,'apisecret' : 'h+*********' ,'apikey' : '**********' , 'polling_interval' : 1800 ,'deleted' : '' , 'created_by' : '519883c4a4e74ca0bcc1c60f23271e38'  , 'owned_by' : '519883c4a4e74ca0bcc1c60f23271e38' ,'enabled': 'true' , 'dns_enabled' : 'false',  'object_storage_enabled' : 'false', 'observation_logs_enabled' : 'true' ,'region' : 'eu-central-1','title' : 'AWS P9 acc', 'apikey' : '**************', 'apisecret' : 'h+********'}
    data = json.dumps(json_string)
    #print(type(data))
    #print(data)
    params = params_from_request(data)
    print(params)

    machines = []






if __name__ == '__main__':
    print("SETTING ")
    #app.run(host="localhost", port=5007)
    loadtrainingdata()
