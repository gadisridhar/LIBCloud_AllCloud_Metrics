


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

from src.main.api.config import PROVIDERS
from src.main.api.exceptions import RequiredParameterMissingError, BadRequestError
from src.main.api.params import params_from_request
API_HOST = "localhost"
API_PORT = 5007

from src.main.api import exceptions
#from src.main.api.config import  PROVIDERS

os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3.6'
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



# @view_config(route_name='api_v1_providers', request_method='GET',
#              renderer='json')
def list_supported_providers():
    """
    Tags: providers
    ---
    Lists supported providers.
    Return all of our SUPPORTED PROVIDERS
    ---
    """
    #return {'supported_providers': list(PROVIDERS.values())}
    return {'supported_providers': list(PROVIDERS.values())}





if __name__ == '__main__':
    print("SETTING ")
    #app.run(host="localhost", port=5007)
    print(list_supported_providers())

