

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


def loadtrainingdata():
    print("inside load training data")
    print("inside TENANT training data")
    # logger.info("----------  LOADING TENANT CREDENTIALS  ----------")
    #app.run(host=API_HOST, port=API_PORT)
    json_string = {'provider': 'ec2', '_cls' : 'Cloud.AmazonCloud' ,'machine_count' : 0  ,'apisecret' : 'h+***************' ,'apikey' : '***************' , 'polling_interval' : 1800 ,'deleted' : '' , 'created_by' : '519883c4a4e74ca0bcc1c60f23271e38'  , 'owned_by' : '519883c4a4e74ca0bcc1c60f23271e38' ,'enabled': 'true' , 'dns_enabled' : 'false',  'object_storage_enabled' : 'false', 'observation_logs_enabled' : 'true' ,'region' : 'eu-central-1','title' : 'AWS P9 acc', 'apikey' : '************', 'apisecret' : 'h+*************'}



    data = json.dumps(json_string)

    #data = json.dumps(json_string)
    print(type(data))
    print(data)
    add_cloud(data)
    #app.run(host="localhost", port=5007)


def validate_cloud_title(title):
    if not regex.search(r'^[0-9a-zA-Z]+[0-9a-zA-Z-_ .]{0,}[0-9a-zA-Z]+$', title):
        raise BadRequestError(
            "Cloud title may only contain ASCII letters, "
            "numbers, dashes and dots")
    return title

def add_cloud_v_2(owner, title, provider, params):
    """Add cloud to owner"""
    # FIXME: Some of these should be explicit arguments, others shouldn't exist
    fail_on_error = params.pop('fail_on_error',
                               params.pop('remove_on_error', True))
    params.pop('title', None)
    params.pop('provider', None)
    # Find proper Cloud subclass.
    if not provider:
        raise RequiredParameterMissingError(provider)

    title = validate_cloud_title(title)
    print("Adding new cloud in provider '%s'", provider)

    cloud_cls = 'amazon'
    # Add the cloud.
    # cloud = cloud_cls.add(owner, title, fail_on_error=fail_on_error,
    #                       fail_on_invalid_params=False, **params)
    # cloud = cloud_cls.add(owner, title, fail_on_error=fail_on_error,fail_on_invalid_params=False, **params)
    # cloud = cloud.add(cloud_cls,owner,title,"12121212")
    #print(cloud)

    datahex = uuid.uuid4().hex
    print(datahex)
    ret = {
        'cloud_id': datahex,#cloud.id,
        'errors': "getattr(cloud,'errors', [])",  # just an attribute, not a field
    }

    #print("Cloud with id '%s' added succesfully.", cloud.id)

    # print("RET DATA------------", ret)
    # print("Cloud with id '%s' added succesfully.", cloud.id)

    #     c_count = Cloud.objects(owner=owner, deleted=None).count()
    #     if owner.clouds_count != c_count:
    #         owner.clouds_count = c_count
    #         owner.save()

    return ret


# ADD CLOUD TO DB

def add_cloud(request):
    # auth_context = auth_context_from_request(request)
    cloud_tags, _ = "AWS", "SAMPLE"
    owner = "519883c4a4e74ca0bcc1c60f23271e38"
    params = params_from_request(request)
    #params = request
    print(params)
    #     # remove spaces from start/end of string fields that are often included
    #     # when pasting keys, preventing thus succesfull connection with the
    #     # cloud
    for key in list(params.keys()):
        if type(params[key]) in [str, str]:
            params[key] = params[key].rstrip().lstrip()

    # api_version = request.headers.get('Api-Version', 1)
    print(params)
    title = params.get('title')
    print(' title --------' + title)

    provider = params.get('provider')
    print(' provider --------' + provider)

    if not provider:
        raise RequiredParameterMissingError('provider')

    monitoring = None
    result = add_cloud_v_2(owner, title, provider, params)
    cloud_id = result['cloud_id']
    monitoring = monitoring
    errors = result.get('errors')

    print(cloud_id)
    print(monitoring)
    print(errors)


    cdict = {
        '_id': cloud_id,
        'title': params.get('title'),
        "_cls": params.get('_cls'),
        'owner' : params.get('owned_by'),
        'provider': params.get('provider'),
        'enabled': params.get('enabled'),
        'dns_enabled': params.get('dns_enabled'),
        'object_storage_enabled': params.get('object_storage_enabled'),
        'observation_logs_enabled': params.get('observation_logs_enabled'),
        'state': 'online' if params.get('enabled') else 'offline',
        'polling_interval': params.get('polling_interval'),
        'apikey' : params.get('apikey'),
        'apisecret': params.get('apisecret'),
        "region": params.get('region'),
        "machine_count": params.get('machine_count'),
        "starred": [],
        "unstarred": [],
        'tags': {
            # tag.key: tag.value
            # for tag in Tag.objects(
            #     owner=self.owner,
            #     resource_id=self.id,
            #     resource_type='cloud').only('key', 'value')
        },
        'owned_by': params.get('owned_by'),
            #self.owned_by.id if self.owned_by else '',
        'created_by': params.get('created_by'),
        'deleted' : datetime.now().isoformat()
            #self.created_by.id if self.created_by else '',
    }

    ##---------------------- WRITE BELOW FIELDS TO MONGO DB CLOUDS COLLECTION

    # cdict = {
    #     'id': self.id,
    #     'title': self.title,
    #     'provider': self.ctl.provider,
    #     'enabled': self.enabled,
    #     'dns_enabled': self.dns_enabled,
    #     'object_storage_enabled': self.object_storage_enabled,
    #     'observation_logs_enabled': self.observation_logs_enabled,
    #     'state': 'online' if self.enabled else 'offline',
    #     'polling_interval': self.polling_interval,
    #     'tags': {
    #         tag.key: tag.value
    #         for tag in Tag.objects(
    #             owner=self.owner,
    #             resource_id=self.id,
    #             resource_type='cloud').only('key', 'value')
    #     },
    #     'owned_by': self.owned_by.id if self.owned_by else '',
    #     'created_by': self.created_by.id if self.created_by else '',
    # }

    ##----------------------
    print(cdict)
    print("------------------------")




if __name__ == '__main__':
    print("SETTING ")
    #app.run(host="localhost", port=5007)
    loadtrainingdata()
