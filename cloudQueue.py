from flask import Flask
from flask import request
import urllib.request, json
from flask import jsonify
import mysql.connector
import collections
import pika
from pika.exceptions import ConnectionClosedByBroker, AMQPChannelError, AMQPConnectionError
from pika import PlainCredentials, BlockingConnection, ConnectionParameters
import json
import sys
import traceback
from typing import Any, Text, Dict, List, Union
import requests
import urllib
import collections
import os.path as op
from sqlalchemy import false
from src.main.util import Names
API_HOST = "localhost"
API_PORT = 5007
API_QUEUENAME = "CMPQueue"
API_QUEUEVIRTUALHOST = "vinci"
app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
from datetime import datetime, timedelta, time
import json
import regex
import uuid
from src.main.api.cloudlib_aws import awsComputation
from src.main.api.cloudlib_azure import azureComputation
from src.main.api.cloudlib_gcp import gcpComputation
from src.main.util.ConfigManager import ConfigManager

class VQLPayloadBack():
    def callback(ch, method, properties, body):
        #print(" [x] Received %r" % body)
        body = body.decode('utf-8')
        datapack.append(json.loads(body))
        print(str(datapack))
        #return datapack

global datapack
datapack = []

class VQLPayload(object):
    global datapacks

    CONNECTION_POOL = {}
    def __init__(self, queue, virtualhost="/"):
        self.queue = queue
        self.vhost = virtualhost

    def queueData(self, data):
        return data


    def callback(ch, method, properties, body):
        datapacks = []
        # print(" [x] Received %r" % body)
        body = body.decode('utf-8')
        datapacks.append(json.loads(body))
        cloudTemplate(datapacks)


    def MSGQ(self):
        self.init()

    def init(self):
        credentials = PlainCredentials(self.user, self.password)
        connection = BlockingConnection(ConnectionParameters(host='{}'.format(self.host),
                                                             virtual_host=self.vhost,
                                                             credentials=credentials, socket_timeout=2))
        self.CONNECTION_POOL[self] = connection

    def startconsumer(self):

        host = "172.17.7.50"
        user = "admin"
        password = "Pass@word1"
        # self.vhost = vhost
        port = 5672
        while True:
            try:    
                print("connecting...")
                credentials = PlainCredentials(user, password)
                connection = BlockingConnection(ConnectionParameters(host='{}'.format(host),
                                                                     virtual_host=self.vhost,
                                                                     credentials=credentials, socket_timeout=2))

                try:
                    print("starting consumer")
                    channel = connection.channel()
                    channel.queue_declare(queue=self.queue, durable=True)
                    channel.basic_consume(on_message_callback=VQLPayload.callback, queue=self.queue, auto_ack=True)
                    channel.start_consuming()


                except KeyboardInterrupt:
                    channel.stop_consuming()
                    connection.close()
                    break
                connection.close()
            except ConnectionClosedByBroker:
                continue
            except AMQPChannelError as err:
                print("Caught a channel error: {}, stopping...".format(err))
                break
            except AMQPConnectionError:
                print("Connection was closed, retrying...")
                continue
            except Exception as e:
                print("exception: " + str(e))
                continue
        #channel.stop_consuming()
        #connection.close()
        return datapack

def cloudTemplate(template):
    print("SETTING ")
    app_route = op.dirname(op.realpath(__file__))
    resourcepath = op.join(app_route, "resources")
    configfile = op.join(resourcepath, "config.json")
    ConfigManager.loadconfigfile(configfile)
    cfgDatabase = ConfigManager.getconfig(Names.CONFIG_STORE)

    cloudPayload = template[0]
    jsonResponseList = []

    if(Names.CLOUD_PROVIDER_AWS.lower() == str(cloudPayload[Names.CLOUD_PROVIDER]).lower()):
        jsonResponseList = awsComputation(cloudPayload,cfgDatabase)
    elif(Names.CLOUD_PROVIDER_AZURE.lower() == str(cloudPayload[Names.CLOUD_PROVIDER]).lower()):
        jsonResponseList = azureComputation(cloudPayload,cfgDatabase)
    elif(Names.CLOUD_PROVIDER_GCP.lower() == str(cloudPayload[Names.CLOUD_PROVIDER]).lower()):
        jsonResponseList = gcpComputation(cloudPayload,cfgDatabase)
    elif (Names.CLOUD_PROVIDER_VMWARE.lower() == str(cloudPayload[Names.CLOUD_PROVIDER]).lower()):
        jsonResponseList = awsComputation(cloudPayload,cfgDatabase)
    elif (Names.CLOUD_PROVIDER_OPENSHIFT.lower() == str(cloudPayload[Names.CLOUD_PROVIDER]).lower()):
        jsonResponseList = awsComputation(cloudPayload,cfgDatabase)
    else:
        print("nope")

    return "Provider Details : " + str(cloudPayload[Names.CLOUD_PROVIDER]).lower(), jsonResponseList

def queueConnect(queueName, virtualHost):
    subscriber = VQLPayload(queueName, virtualHost)
    subscriber.startconsumer()
    return "CONNECTED"

    # sourceType = (bodyJSON['sourceType'])
    # tenantID = (bodyJSON['tenantID'])

def loadQueueData():
    print("inside load training data")
    print("inside TENANT training data")
    # logger.info("----------  LOADING TENANT CREDENTIALS  ----------")
    # json_string = {'provider': 'ec2', '_cls' : 'Cloud.AmazonCloud' ,'machine_count' : 0  ,
    #                'apisecret' : 'h+***********' ,'apikey' : '*************' ,
    #                'polling_interval' : 1800 ,'deleted' : '' , 'created_by' : '519883c4a4e74ca0bcc1c60f23271e38'  ,
    #                'owned_by' : '519883c4a4e74ca0bcc1c60f23271e38' ,'enabled': 'true' , 'dns_enabled' : 'false',
    #                'object_storage_enabled' : 'false', 'observation_logs_enabled' : 'true' ,'region' : 'eu-central-1',
    #                'title' : 'AWS P9 acc', 'apikey' : '*********', 'apisecret' : 'h+*************'}
    # data = json.dumps(json_string)
    # print(type(data))
    # print(data)

    #app.run(host=API_HOST, port=API_PORT)
    # QUEUE INITIATION TO  START CMPQUEUE
    print(API_QUEUEVIRTUALHOST)
    queueConnect(API_QUEUENAME,API_QUEUEVIRTUALHOST)
    #print(str(datapack))
    print("=-----------data handle below-------")
    #print(str(dataHandle))



if __name__ == '__main__':
    print("QUEUE INITIATION DATA READ SETTING ")
    loadQueueData()