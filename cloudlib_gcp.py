#https://libcloud.readthedocs.io/en/stable/index.html
import os.path as op
from src.main.util import Names
from src.main.util.ConfigManager import ConfigManager
from src.main.util.LogManager import LogManager
from src.main.commons.DataManager import DataManager
import libcloud
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

from libcloud.pricing import get_size_price, get_pricing, get_pricing_file_path, download_pricing_file

from libcloud.compute.providers import get_driver as get_compute_driver
from libcloud.compute.types import Provider as ComputeProvider

from libcloud.dns.providers import get_driver as get_dns_driver
from libcloud.dns.types import Provider as DNSProvider

from libcloud.pricing import get_pricing as get_price_driver
from libcloud.pricing import get_size_price

from libcloud.pricing import get_pricing, get_size_price, download_pricing_file, get_pricing_file_path

# from libcloud.compute.base import Node, NodeAuthPassword, NodeAuthSSHKey, NodeDriver, \
#     NodeImage, NodeImageMember, NodeImageMemberState, NodeLocation, \
#     NodeSize, NodeState, VolumeSnapshot, Connection, ConnectionKey
#
# from libcloud.security import SSL_VERSION
#
# from libcloud.storage.types import Provider,  ContainerDoesNotExistError
# from libcloud.storage.providers import get_driver
#
# from libcloud.loadbalancer.base import Member, Algorithm
# from libcloud.loadbalancer.types import State, Provider
# from libcloud.loadbalancer.providers import get_driver

import json
import regex
import uuid
now = datetime.now()

def aws_extra(listExtra):
    print(listExtra)

def aws_private(listExtra):
    print(listExtra)



def loadgcp_compute_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        # --------------------------------------------DRIVER DETAILS FOR GCP ACCOUNT
        cls = get_compute_driver(ComputeProvider.GCE)
        driver = cls(str(cloudPayload[Names.GCP_ACCOUNT_ID]),
                     str(cloudPayload[Names.GCP_PEMFILE]),
                     project=str(cloudPayload[Names.GCP_ACCOUNT_NAME]),
                     datacenter=str(cloudPayload[Names.GCP_DATACENTER]))

        # cls('tools-api-sa@cloud-devops-298213.iam.gserviceaccount.com','cloud-devops-298213-82bbca210566.pem',project='cloud-devops-298213',datacenter='us-west1-a')

        print("----------------------")
        nodeDetails = driver.list_nodes()

        print(len(nodeDetails))
        machineCount_Running = 0
        machineCount_Stopped = 0

        computeList = []
        machineRunning = []
        machineStopped = []

        data = []
        if (len(nodeDetails) > 0):
            for node in nodeDetails:
                extra = {}
                extraMachines = {}

                if (node.state == 'stopped'):
                    machineCount_Stopped = machineCount_Stopped + 1
                    machineStopped.append(node.id)

                elif (node.state == 'running'):
                    machineCount_Running = machineCount_Running + 1
                    machineRunning.append(node.id)
                else:
                    print("Nothing")

                datahex_Unique = uuid.uuid4().hex

                extra[Names.UNIVERSALID] = datahex
                extra[Names.OWNERID] = datahex
                extra[Names.ID] = datahex_Unique
                extra[Names.CID] = node.id
                extra[Names.EXTRANAME] = node.name
                extra[Names.UUID] = node.uuid
                extra[Names.IMAGE] = node.image
                extra[Names.PUBLIC_IP] = node.public_ips
                extra[Names.PRIVATE_IP] = node.private_ips
                extra[Names.CREATED_AT] = node.created_at
                del node.extra[Names.GCP_ZONE]
                del node.extra[Names.GCP_BOOTDISK]
                extra[Names.EXTRA] = node.extra
                extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                       "%d/%m/%Y %H:%M:%S")
                extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                        "%d/%m/%Y %H:%M:%S")

                netLISTMain = []
                netLIST = node.extra[Names.GCP_NETWORK_INTERFACES]

                for nl in netLIST:
                    # print("---------------------")
                    extraJSON = {}
                    networkIP = nl[Names.NETWORK_IP]
                    name = nl[Names.EXTRANAME]
                    extraDepth = nl[Names.NETWORK_CONFIG]
                    nameAgain = extraDepth[0][Names.NETWORK_NAME]
                    networkTier = extraDepth[0][Names.NETWORK_TIER]
                    networkType = extraDepth[0][Names.NETWORK_TYPE]
                    extraJSON[Names.NETWORK_IP] = networkIP
                    extraJSON[Names.EXTRANAME] = name

                    extraJSON[Names.NETWORK_NAME] = nameAgain
                    extraJSON[Names.NETWORK_TIER] = networkTier
                    extraJSON[Names.NETWORK_TYPE] = networkType
                    netLISTMain.append(extraJSON)

                extra[Names.NETWORK] = netLISTMain
                del extra[Names.EXTRA][Names.GCP_NETWORK_INTERFACES]
                extra[Names.CREATED_AT] = datetime.now().isoformat()
                extra[Names.MODIFIED_AT] = datetime.now().isoformat()
                computeList.append(extra)

                extraMachines[Names.MACHINE_STOPPED] = machineStopped
                extraMachines[Names.MACHINE_RUNNING] = machineRunning

                machineDetails = {}
                machinesCount = len(nodeDetails)
                machineDetails[Names.MACHINE_COUNT] = machinesCount
                machineDetails[Names.MACHINE_RUNNING] = machineCount_Running
                machineDetails[Names.MACHINE_STOPPED] = machineCount_Stopped
                print(machineDetails)

            DataManager.GCP_compute_Data(computeList, cfgDB)
            DataManager.cloud_Compute_Upsert(datahex, machineDetails, cfgDB)
            DataManager.cloud_ComputeMachines_Upsert(datahex, extraMachines, cfgDB)
            message[Names.RESPONSE_MESSAGE] = "GCP Compute Details Added"
        else:
            print("empty")
            message[Names.RESPONSE_MESSAGE] = "GCP Empty Compute Details"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadaws_dns_data():
    message = {}
    try:
        # --------------------------------------------DNS DETAILS FOR AWS ACCOUNT
        cls_dns = get_dns_driver(DNSProvider.ROUTE53)
        driver_dns = cls_dns('AKIATDZ2GFEQ2IDD6DVZ', 'h+w1dMRqEgjYANZzBYu4FtMbUmXOlMKIxNQvJrjx', region="us-west-2")
        # ----------------------------------------------------------------------------
        print("----------------------")
        foo = driver_dns.list_zones()
        print(foo)

        data1 = []
        for node in foo:
            extra = {}
            # print("NODE ID --------- ",node.id)
            extra["UNIVERSALID"] = 1111111111
            extra["ID"] = node.id
            extra["TYPE"] = node.type
            extra["DOMAIN"] = node.domain
            extra["EXTRA"] = node.extra
            # extra["DOMAIN"] = node.type
            # extra["EXTRA"] = node.L
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")
            data1.append(extra)
        message[Names.RESPONSE_MESSAGE] = "GCP DNS Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadaws_pricing_data(datahex):
    message = {}
    try:
        # --------------------------------------------DNS DETAILS FOR AWS ACCOUNT

        cls = get_compute_driver(ComputeProvider.EC2)
        driver = cls('AKIATDZ2GFEQ2IDD6DVZ', 'h+w1dMRqEgjYANZzBYu4FtMbUmXOlMKIxNQvJrjx', region="us-west-2")

        sizes = driver.list_sizes()
        print(sizes)
        data1 = []
        for size in sizes:
            extra = {}
            extra["UNIVERSALID"] = datahex
            extra["UUID"] = size.uuid
            extra["ID"] = size.id
            extra["NAME"] = size.name
            extra["PRICE"] = size.price
            extra["DISK"] = size.disk
            extra["RAM"] = size.ram
            extra["EXTRA"] = size.extra
            extra["BANDWIDTH"] = size.bandwidth
            extra["DRIVER"] = size.driver
            extra["DRIVER_TYPE"] = size.driver.type
            extra["DRIVER_NAME"] = size.driver.name
            extra["DRIVER_REGION"] = size.driver.region
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")

            # AWS ------COMPUTE PRICE CALCULATE
            get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="ec2_linux", size_id=size.uuid,
                                                 region=size.driver.region)
            # get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="ec2_windows", size_id=size.uuid,region=size.driver.region)

            # AZURE ------COMPUTE PRICE CALCULATE
            # get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="azure_linux", size_id=size.uuid,region=size.driver.region)
            # get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="azure_windows", size_id=size.uuid,region=size.driver.region)

            # ------STORAGE PRICE CALCULATE
            # get_CalculatedPrice = get_size_price(driver_type="storage", driver_name="ec2_linux", size_id=size.uuid,region=size.driver.region)

            print(get_CalculatedPrice)
            extra["COMPUTE_PRICE"] = get_CalculatedPrice

            data1.append(extra)
        message[Names.RESPONSE_MESSAGE] = "GCP Pricing Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadaws_sizing_data(datahex):
    message = {}
    try:
        # --------------------------------------------DNS DETAILS FOR AWS ACCOUNT

        cls = get_compute_driver(ComputeProvider.EC2)
        driver = cls('AKIATDZ2GFEQ2IDD6DVZ', 'h+w1dMRqEgjYANZzBYu4FtMbUmXOlMKIxNQvJrjx', region="us-west-2")

        sizes = driver.list_sizes()
        print(sizes)
        data1 = []
        for size in sizes:
            extra = {}
            extra["UNIVERSALID"] = datahex
            extra["UUID"] = size.uuid
            extra["ID"] = size.id
            extra["NAME"] = size.name
            extra["PRICE"] = size.price
            extra["DISK"] = size.disk
            extra["RAM"] = size.ram
            extra["EXTRA"] = size.extra
            extra["BANDWIDTH"] = size.bandwidth
            extra["DRIVER"] = size.driver
            extra["DRIVER_TYPE"] = size.driver.type
            extra["DRIVER_NAME"] = size.driver.name
            extra["DRIVER_REGION"] = size.driver.region
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")

            # AWS ------COMPUTE PRICE CALCULATE
            get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="ec2_linux", size_id=size.uuid,
                                                 region=size.driver.region)
            # get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="ec2_windows", size_id=size.uuid,region=size.driver.region)

            # AZURE ------COMPUTE PRICE CALCULATE
            # get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="azure_linux", size_id=size.uuid,region=size.driver.region)
            # get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="azure_windows", size_id=size.uuid,region=size.driver.region)

            # ------STORAGE PRICE CALCULATE
            # get_CalculatedPrice = get_size_price(driver_type="storage", driver_name="ec2_linux", size_id=size.uuid,region=size.driver.region)

            print(get_CalculatedPrice)
            extra["COMPUTE_PRICE"] = get_CalculatedPrice

            data1.append(extra)
        message[Names.RESPONSE_MESSAGE] = "GCP Sizing Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadgcp_images_data(datahex,cloudPayload,cfgDB):
    message = {}
    try:
        # logger.info("----------  LOADING TENANT CREDENTIALS  ----------")
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.GCE)
        driver = cls(str(cloudPayload[Names.GCP_ACCOUNT_ID]),
                     str(cloudPayload[Names.GCP_PEMFILE]),
                     project=str(cloudPayload[Names.GCP_ACCOUNT_NAME]),
                     datacenter=str(cloudPayload[Names.GCP_DATACENTER]))
        # ----------------------------------------------------------------------------


        imageDetails = driver.list_images()



        imageList = []
        for image in imageDetails:
            extra = {}
            driverInner = {}
            driverConnInner = {}
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = image.id
            extra[Names.UUID] = image.uuid
            extra[Names.EXTRANAME] = image.name
            # extra["DRIVER"] = image.driver

            if((image.driver.api_name) == None):
                driverInner["DRIVER_APINAME"] = ""
            else:
                driverInner["DRIVER_APINAME"] = image.driver.api_name

            if ((image.driver.api_version) == None):
                driverInner["DRIVER_APIVERSION"] = ""
            else:
                driverInner["DRIVER_APIVERSION"] = image.driver.api_version

            if ((image.driver.region.name) == None):
                driverInner["DRIVER_REGION"] = ""
            else:
                driverInner["DRIVER_REGION"] = image.driver.region.name

            if ((image.driver.secret) == None):
                driverInner["DRIVER_SECRET"] = ""
            else:
                driverInner["DRIVER_SECRET"] = image.driver.secret

            if ((image.driver.secure) == None):
                driverInner["DRIVER_SECURE"] = ""
            else:
                driverInner["DRIVER_SECURE"] = image.driver.secure

            if ((image.driver.type) == None):
                driverInner["DRIVER_TYPE"] = ""
            else:
                driverInner["DRIVER_TYPE"] = image.driver.type


            if ((image.driver.name) == None):
                driverInner["DRIVER_NAME"] = ""
            else:
                driverInner["DRIVER_NAME"] = image.driver.name

            #driverInner["DRIVER_REGION"] = image.driver.region.name  # image.driver.region
            # driverInner["DRIVER_NAME"] = image.driver.region_name
            #driverInner["DRIVER_SECRET"] = image.driver.secret
            #driverInner["DRIVER_SECURE"] = image.driver.secure
            # driverInner["DRIVER_SIGNATUREVERSION"] = image.driver.signature_version
            #driverInner["DRIVER_TYPE"] = image.driver.type
            #driverInner["DRIVER_NAME"] = image.driver.name

            if ((image.driver.connectionCls.host) == None):
                driverConnInner[Names.DRIVER_CONNECTIONS_HOST] = ""
            else:
                driverConnInner[Names.DRIVER_CONNECTIONS_HOST] = image.driver.connectionCls.host

            if ((image.driver.connectionCls.request_method) == None):
                driverConnInner[Names.DRIVER_CONNECTIONS_METHOD] = ""
            else:
                driverConnInner[Names.DRIVER_CONNECTIONS_METHOD] = image.driver.connectionCls.request_method

            driverInner[Names.DRIVER_CONNECTIONS] = driverConnInner

            # driverConnInner[Names.DRIVER_CONNECTIONS_HOST] = image.driver.connectionCls.host
            # driverConnInner[Names.DRIVER_CONNECTIONS_METHOD] = image.driver.connectionCls.request_method


            extra[Names.DRIVER_DETAILS] = driverInner
            # extra["STATE"] = node.state


            if("description" in image.extra):
                extra["description"] = image.extra["description"]
            else:
                extra["description"] = ""

            if ("family" in image.extra):
                extra["family"] = image.extra["family"]
            else:
                extra["family"] = ""

            if ("rawDisk" in image.extra):
                extra["rawDisk"] = image.extra["rawDisk"]
            else:
                extra["rawDisk"] = {}

            if ("status" in image.extra):
                extra["status"] = image.extra["status"]
            else:
                extra["status"] = ""

            if ("labels" in image.extra):
                extra["labels"] = image.extra["labels"]
            else:
                extra["labels"] = ""

            if ("labelFingerprint" in image.extra):
                extra["labelFingerprint"] = image.extra["labelFingerprint"]
            else:
                extra["labelFingerprint"] = ""

            # extra["family"] = image.extra["family"]
            # extra["rawDisk"] = image.extra["rawDisk"]
            # extra["status"] = image.extra["status"]
            # extra["labels"] = image.extra["labels"]
            # extra["labelFingerPrint"] = image.extra["labelFingerprint"]
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")
            imageList.append(extra)
            print("~~~~~~~~~~~~~~~~~~~~~")
            print(imageList)

        print(imageList)
        DataManager.images_Data(imageList, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "GCP Image Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadgcp_location_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.GCE)
        driver = cls(str(cloudPayload[Names.GCP_ACCOUNT_ID]),
                     str(cloudPayload[Names.GCP_PEMFILE]),
                     project=str(cloudPayload[Names.GCP_ACCOUNT_NAME]),
                     datacenter=str(cloudPayload[Names.GCP_DATACENTER]))
        locDetails = driver.list_locations()

        locationList = []
        for location in locDetails:
            datahex_Unique = uuid.uuid4().hex
            extra = {}
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = datahex_Unique
            extra[Names.LOCATION_ID] = location.id
            extra[Names.COUNTRY] = location.country
            extra[Names.AVAILABLITYZONE_NAME] = location.driver.zone.name
            extra[Names.AVAILABLITYZONE_REGION] = location.driver.zone.country
            extra[Names.AVAILABLITYZONE_STATE] = location.driver.zone.status
            extra[Names.AVAILABLITYZONE_SIZES] = []
            extra[Names.AVAILABLITYZONE_IMAGES] = []
            extra[Names.EXTRA] = location.extra
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")
            locationList.append(extra)
        DataManager.location_Data(locationList, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "GCP Location Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def load_cloudGCP_data(datahex, cloudPayload,cfgDB):
    message = {}
    try:
        extra = {}
        datahex_Unique = uuid.uuid4().hex
        extra[Names.UNIVERSALID] = datahex
        extra[Names.OWNERID] = datahex
        extra[Names.ID] = datahex_Unique
        extra[Names.TITLE] = cloudPayload[Names.TITLE]
        extra[Names.ENABLED] = cloudPayload[Names.ENABLED]
        extra[Names.MACHINE_COUNT] = 0
        extra[Names.MACHINE_RUNNING] = 0
        extra[Names.MACHINE_STOPPED] = 0
        extra[Names.MACHINE_DETAILS] = {}
        extra[Names.STARRED] = []
        extra[Names.UNSTARRED] = []
        extra[Names.POLLING] = 1800
        extra[Names.STORAGE_ENABLED] = cloudPayload[Names.STORAGE_ENABLED]
        extra[Names.LOGS_ENABLED] = cloudPayload[Names.LOGS_ENABLED]

        extra[Names.GCP_ACCOUNT_ID] = cloudPayload[Names.GCP_ACCOUNT_ID]
        extra[Names.GCP_PEMFILE] = cloudPayload[Names.GCP_PEMFILE]
        extra[Names.GCP_ACCOUNT_NAME] = cloudPayload[Names.GCP_ACCOUNT_NAME]
        extra[Names.GCP_DATACENTER] = cloudPayload[Names.GCP_DATACENTER]
        extra[Names.CLOUD_PROVIDER] = cloudPayload[Names.CLOUD_PROVIDER]
        extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"), "%d/%m/%Y %H:%M:%S")
        extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"), "%d/%m/%Y %H:%M:%S")
        print("-------------------------------", extra)
        jsonData = DataManager.cloudGCP_Data(extra, cfgDB)
        message[Names.MESSAGE] = jsonData[Names.MESSAGE]
        message[Names.RESPONSE_MESSAGE] = "GCP Cloud Account Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadgcp_polling_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        extra = {}
        datahex_Unique = uuid.uuid4().hex
        extra[Names.UNIVERSALID] = datahex
        extra[Names.OWNERID] = datahex
        extra[Names.ID] = datahex_Unique
        extra["name"] = "push_metering_info(" + datahex + ")"
        extra["default_interval"] = 1800
        extra["override_intervals"] = []
        extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"), "%d/%m/%Y %H:%M:%S")
        extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"), "%d/%m/%Y %H:%M:%S")
        extra["override_intervals"] = []
        DataManager.CMP_PollingData(extra, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "GCP Polling Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadgcp_volumes_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        cls = get_compute_driver(ComputeProvider.GCE)
        driver = cls(str(cloudPayload[Names.GCP_ACCOUNT_ID]),
                     str(cloudPayload[Names.GCP_PEMFILE]),
                     project=str(cloudPayload[Names.GCP_ACCOUNT_NAME]),
                     datacenter=str(cloudPayload[Names.GCP_DATACENTER]))
        nodeDetails = driver.list_volumes()

        volumeList = []
        for node in nodeDetails:
            extra = {}
            extraJson = {}
            datahex_Unique = uuid.uuid4().hex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = datahex_Unique
            extra[Names.UUID] = node.uuid
            extra[Names.CID] = node.id
            extra[Names.EXTRANAME] = node.name
            extra[Names.SIZE] = node.size
            extra[Names.STATE] = node.state
            nodeExtra = node.extra
            extraJson['selfLink'] = nodeExtra['selfLink']
            extraJson['status'] = nodeExtra['status']
            extraJson['description'] = nodeExtra['description']
            extraJson['sourceImage'] = nodeExtra['sourceImage']
            extraJson['sourceSnapshot'] = nodeExtra['sourceSnapshot']
            extraJson['sourceSnapshotId'] = nodeExtra['sourceSnapshotId']
            extraJson['sourceImageId'] = nodeExtra['sourceImageId']
            extraJson['country'] = nodeExtra['zone'].country
            extraJson['zoneName'] = nodeExtra['zone'].name
            extraJson['maintenance_Window'] = nodeExtra['zone'].maintenance_windows
            extraJson['type'] = nodeExtra['type']
            extra[Names.EXTRA] = extraJson
            del node.extra
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")
            volumeList.append(extra)
            print(volumeList)

        print(volumeList)
        DataManager.volume_Data(volumeList, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "GCP Volume Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadgcp_volumesSnapshot_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        cls = get_compute_driver(ComputeProvider.GCE)
        driver = cls(str(cloudPayload[Names.GCP_ACCOUNT_ID]),
                     str(cloudPayload[Names.GCP_PEMFILE]),
                     project=str(cloudPayload[Names.GCP_ACCOUNT_NAME]),
                     datacenter=str(cloudPayload[Names.GCP_DATACENTER]))
        # ----------------------------------------------------------------------------
        countVolums = len(driver.list_volumes())
        volumeSnapShotList = []
        for i in range(countVolums):
            extra = {}
            datahex_Unique = uuid.uuid4().hex
            volumeprint = driver.list_volumes()[i]
            volumeSnapShotName = driver.list_volumes()[i].name
            volumeSnapShotID = driver.list_volumes()[i].id
            volumeSnapShotUUID = driver.list_volumes()[i].uuid
            extra[Names.OWNERID] = datahex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.ID] = datahex_Unique
            extra[Names.VOLUMESNAPSHOT_ID] = volumeSnapShotID
            extra[Names.VOLUMESNAPSHOT_UUID] = volumeSnapShotUUID
            extra[Names.VOLUMESNAPSHOT_NAME] = volumeSnapShotName
            volSnapShotListMain = []
            volSnapShotList = driver.list_volume_snapshots(volumeprint)

            for vssl in volSnapShotList:
                extraJSON = {}
                name = vssl.name
                id = vssl.id
                size = vssl.size
                state = vssl.state
                extraJSON[Names.VOLSNAPSHOT_INTERNALID] = id
                extraJSON[Names.VOLSNAPSHOT_SIZE] = size
                extraJSON[Names.VOLSNAPSHOT_STATE] = state
                extraJSON[Names.VOLSNAPSHOT_NAME] = name
                volSnapShotListMain.append(extraJSON)
            extra[Names.VOLUMESNAPSHOT_DETAILS] = volSnapShotListMain
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")
            volumeSnapShotList.append(extra)

        DataManager.volumeSnapShot_Data(volumeSnapShotList, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "GCP Volume Snapshot Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadgcp_subnet_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        # logger.info("----------  LOADING TENANT CREDENTIALS  ----------")
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.GCE)
        driver = cls(str(cloudPayload[Names.GCP_ACCOUNT_ID]),
                     str(cloudPayload[Names.GCP_PEMFILE]),
                     project=str(cloudPayload[Names.GCP_ACCOUNT_NAME]),
                     datacenter=str(cloudPayload[Names.GCP_DATACENTER]))
        nodeDetails = driver.list_nodes()

        for node in nodeDetails:
            extra = {}
            extra[Names.MACHINE_ID] = node.id
            datahex_Unique = uuid.uuid4().hex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = datahex_Unique

            if ('name' in node.extra) == True:
                extra['name'] = node.extra['name']
            else:
                extra['name'] = ""

            if ('description' in node.extra) == True:
                extra['description'] = node.extra['description']
            else:
                extra['description'] = ""

            #extra['status'] = node.extra['status']
            if ('status' in node.extra) == True:
                extra['status'] = node.extra['status']
            else:
                extra['status'] = ""

            #extra['subnet_id'] = node.extra['subnet_id']
            #extra['name'] = node.extra['subnet_id']
            if ('subnet_id' in node.extra) == True:
                extra['subnet_id'] = node.extra['subnet_id']
            else:
                extra['subnet_id'] = ""


            #extra['vpc_id'] = node.extra['id']  # node.extra['vpc_id']
            if ('vpc_id' in node.extra) == True:
                extra['vpc_id'] = node.extra['id']
            else:
                extra['vpc_id'] = ""


            #extra['availability'] = node.extra['zone'].name  # node.extra['availability']
            if('name' in node.extra['zone'].name) == True:
                extra['availability'] = node.extra['zone'].name
            else:
                extra['availability'] = ""

            if ('labelFingerprint' in node.extra) == True:
                extra['labelFingerprint'] = node.extra['labelFingerprint']
            else:
                extra['labelFingerprint'] = ""


            if ('tags' in node.extra) == True:
                extra['tags'] = node.extra['tags']
            else:
                extra['tags'] = []

            # extra['status'] = node.extra['status']
            # extra['subnet_id'] = node.extra['subnet_id']
            # extra['name'] = node.extra['subnet_id']
            # extra['vpc_id'] = node.extra['vpc_id'] #node.extra['id']
            # extra['availability'] = node.extra['availability'] #node.extra['zone'].name



            if (Names.GCP_NETWORK_INTERFACES in node.extra) == True:
                netLIST = node.extra[Names.GCP_NETWORK_INTERFACES]
            else:
                netLIST = []

            for nl in netLIST:
                extraJSON = {}
                #extraJSON["network"] = nl["network"]
                if('network' in nl) == True :
                    extraJSON['network'] = nl["network"]
                    extraJSON['vpc_id'] = nl["network"].rpartition('/')[-1]
                else:
                    extraJSON['network'] = ""
                    extraJSON['vpc_id'] = ""

                #extraJSON["subnetwork"] = nl["subnetwork"]
                if('subnetwork' in nl) == True :
                    extraJSON['subnetwork'] = nl['subnetwork']
                    extraJSON['subnet_id'] = nl['subnetwork'].rpartition('/')[-1]
                else:
                    extraJSON['subnetwork'] = ""
                    extraJSON['subnet_id'] = ""

                #extraJSON["networkIP"] = nl["networkIP"]
                if('networkIP' in nl) == True :
                    extraJSON['networkIP'] = nl['networkIP']
                else:
                    extraJSON['networkIP'] = ""

                #extraJSON["name"] = nl["name"]
                if('name' in nl) == True :
                    extraJSON['name'] = nl['name']
                else:
                    extraJSON['name'] = ""

                #extraJSON["fingerprint"] = nl["fingerprint"]
                if('fingerprint' in nl) == True :
                    extraJSON['fingerprint'] = nl['fingerprint']
                else:
                    extraJSON['fingerprint'] = ""

                #extraJSON["kind"] = nl["kind"]
                if('kind' in nl) == True :
                    extraJSON['kind'] = nl['kind']
                else:
                    extraJSON['kind'] = ""

                if ('description' in nl) == True:
                    extraJSON['description'] = nl['description']
                else:
                    extraJSON['description'] = ""

                if ('owner_id' in nl) == True:
                    extraJSON['owner_id'] = nl['owner_id']
                else:
                    extraJSON['owner_id'] = ""

                if ('mac_address' in nl) == True:
                    extraJSON['mac_address'] = nl['mac_address']
                else:
                    extraJSON['mac_address'] = ""

                # exsubnet_id = nl.extra['subnet_id']
                # exvpc_id = nl.extra['vpc_id']
                # exzone = nl.extra['zone']
                # exdescription = nl.extra['description']
                # exowner_id = nl.extra['owner_id']
                # exmac_address = nl.extra['mac_address']
                #
                # exattachment_id = nl.extra['attachment']['attachment_id']
                # exstatus = nl.extra['attachment']['status']
                # exprivateIP_Details = nl.extra['private_ips']
                # exgroup_Details  = nl.extra['groups']
                # extraJSON["subnet_id"] = exsubnet_id
                # extraJSON["vpc_id"] = exvpc_id
                # extraJSON["zone"] = exzone
                # extraJSON["description"] = exdescription
                # extraJSON["owner_id"] = exowner_id
                # extraJSON["mac_address"] = exmac_address
                # extraJSON["attachment_id"] = exattachment_id
                # extraJSON["attachmentstatus"] = exstatus
                # extraJSON["privateIPDetails"] = exprivateIP_Details
                # extraJSON["groupDetails"] = exgroup_Details
                extra[Names.NETWORK_DETAILS] = extraJSON
                extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                       "%d/%m/%Y %H:%M:%S")
                extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                        "%d/%m/%Y %H:%M:%S")
            #print(extra)
            DataManager.CMP_SubnetData(extra, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "GCP Subnet Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message

def loadgcp_network_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        # logger.info("----------  LOADING TENANT CREDENTIALS  ----------")
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.GCE)
        driver = cls(str(cloudPayload[Names.GCP_ACCOUNT_ID]),
                     str(cloudPayload[Names.GCP_PEMFILE]),
                     project=str(cloudPayload[Names.GCP_ACCOUNT_NAME]),
                     datacenter=str(cloudPayload[Names.GCP_DATACENTER]))
        nodeDetails = driver.list_nodes()

        for node in nodeDetails:
            extra = {}
            extra[Names.MACHINE_ID] = node.id
            datahex_Unique = uuid.uuid4().hex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = datahex_Unique
            # extra['network_id'] = node.extra['id']  # node.extra['vpc_id']
            # extra['name'] = node.extra['id']  # node.extra['vpc_id']

            extra['cidr'] = ""

            if ('vpc_id' in node.extra) == True:
                extra['vpc_id'] = node.extra['id']
                extra['network_id'] = node.extra['id']  # node.extra['vpc_id']
            else:
                extra['vpc_id'] = ""
                extra['network_id'] =  ""

            netLIST = node.extra[Names.GCP_NETWORK_INTERFACES]
            for nl in netLIST:
                extraJSON = {}
                # exnetwork_id = nl.extra['vpc_id']
                # exname = nl.extra['vpc_id']
                # extraJSON["network_id"] = exnetwork_id
                # extraJSON["name"] = exname

                if ('network' in nl) == True:
                    extraJSON['network'] = nl["network"]
                    extraJSON['vpc_id'] = nl["network"].rpartition('/')[-1]
                else:
                    extraJSON['network'] = ""
                    extraJSON['vpc_id'] = ""

                    # extraJSON["subnetwork"] = nl["subnetwork"]
                if ('subnetwork' in nl) == True:
                    extraJSON['subnetwork'] = nl['subnetwork']
                    extraJSON['subnet_id'] = nl['subnetwork'].rpartition('/')[-1]
                else:
                    extraJSON['subnetwork'] = ""
                    extraJSON['subnet_id'] = ""

                    # extraJSON["networkIP"] = nl["networkIP"]
                if ('networkIP' in nl) == True:
                    extraJSON['networkIP'] = nl['networkIP']
                else:
                    extraJSON['networkIP'] = ""

                if ('name' in nl) == True:
                    extraJSON['name'] = nl['name']
                else:
                    extraJSON['name'] = ""

                    # extraJSON["fingerprint"] = nl["fingerprint"]
                if ('fingerprint' in nl) == True:
                    extraJSON['fingerprint'] = nl['fingerprint']
                else:
                    extraJSON['fingerprint'] = ""

                    # extraJSON["kind"] = nl["kind"]
                if ('kind' in nl) == True:
                    extraJSON['kind'] = nl['kind']
                else:
                    extraJSON['kind'] = ""


                # extraJSON["network"] = nl["network"]
                # extraJSON["subnetwork"] = nl["subnetwork"]
                # extraJSON["networkIP"] = nl["networkIP"]
                # extraJSON["name"] = nl["name"]
                # extraJSON["fingerprint"] = nl["fingerprint"]
                # extraJSON["kind"] = nl["kind"]

                extra[Names.NETWORK_DETAILS] = extraJSON
                extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                       "%d/%m/%Y %H:%M:%S")
                extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                        "%d/%m/%Y %H:%M:%S")
            print(extra)
            DataManager.CMP_NetworkData(extra, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "GCP Network Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message



async def gcpComputationCheck(cloudPayload,cfgDB):
    print("GCP CHECK")
    DataManager.deleteCloudDetails(cloudPayload, cfgDB)
    DataManager.deletePollingDetails(cloudPayload, cfgDB)
    DataManager.deleteComputeDetails(cloudPayload, cfgDB)
    DataManager.deleteVolDetails(cloudPayload, cfgDB)
    DataManager.deleteVolSnapshotDetails(cloudPayload, cfgDB)
    DataManager.deleteLocationDetails(cloudPayload, cfgDB)
    DataManager.deleteSubnetDetails(cloudPayload, cfgDB)
    DataManager.deleteNetworkDetails(cloudPayload, cfgDB)
    DataManager.deleteImageDetails(cloudPayload, cfgDB)

    datahex = cloudPayload[Names.UNIVERSALID]
    load_cloudGCP_data(datahex, cloudPayload, cfgDB)
    loadgcp_polling_data(datahex, cloudPayload, cfgDB)
    loadgcp_compute_data(datahex, cloudPayload, cfgDB)
    loadgcp_volumes_data(datahex, cloudPayload, cfgDB)
    loadgcp_volumesSnapshot_data(datahex, cloudPayload, cfgDB)
    loadgcp_location_data(datahex, cloudPayload, cfgDB)  # --- LOCATION CLOUD RELATED DATA FOR AWS
    loadgcp_subnet_data(datahex, cloudPayload, cfgDB)  # --- worked
    loadgcp_network_data(datahex, cloudPayload, cfgDB)  # --worked
    loadgcp_images_data(datahex, cloudPayload, cfgDB)  # --worked


def gcpComputation(cloudPayload,cfgDB):
    print("GCP")
    datahex = uuid.uuid4().hex
    jsonData = load_cloudGCP_data(datahex, cloudPayload, cfgDB)  # ---  CLOUD CONFIGURATION RELATED DATA FOR AZURE
    responseMessage = {}
    responseList = []
    if (jsonData[Names.MESSAGE] == Names.NOTEXISTS):
        responseMessage["pollingDetails"] = loadgcp_polling_data(datahex, cloudPayload, cfgDB)
        responseMessage["computeDetails"] = loadgcp_compute_data(datahex, cloudPayload, cfgDB)  # --- COMPUTE CLOUD RELATED DATA FOR AZURE
        responseMessage["volumeDetails"] = loadgcp_volumes_data(datahex, cloudPayload, cfgDB)
        responseMessage["volumeSnapshotDetails"] = loadgcp_volumesSnapshot_data(datahex, cloudPayload, cfgDB)
        responseMessage["locationDetails"] = loadgcp_location_data(datahex, cloudPayload, cfgDB)  # --- LOCATION CLOUD RELATED DATA FOR AWS
        responseMessage["subnetDetails"] = loadgcp_subnet_data(datahex, cloudPayload, cfgDB)  # --- worked
        responseMessage["networkDetails"] = loadgcp_network_data(datahex, cloudPayload, cfgDB) #--worked
        responseMessage["imageDetails"] = loadgcp_images_data(datahex, cloudPayload, cfgDB) #--worked
        responseMessage["accountDetails"] = "Account Details Added"
        responseList.append(responseMessage)
        #loadazure_location_data(datahex, cloudPayload, cfgDB)  # ---works
        #loadazure_images_data(datahex, cloudPayload, cfgDB)  # --------NT WORKING
        #load_anaon(datahex, cloudPayload, cfgDB)
    else:
        print("Account Details Already ", Names.EXISTS)
        responseMessage["accountDetails"] = "Account Details already exists"
        responseList.append(responseMessage)

    print("GCP CLOUD DETAILS CAPTURED")
    return  responseList

if __name__ == '__main__':
    print("SETTING ")
    app_route = op.dirname(op.realpath(__file__))
    resourcepath = op.join(app_route, "resources")
    configfile = op.join(resourcepath, "config.json")
    ConfigManager.loadconfigfile(configfile)

    cfgDatabase = ConfigManager.getconfig(Names.CONFIG_STORE)
    datahex = uuid.uuid4().hex
    #app.run(host="localhost", port=5007)
    #loadgcp_compute_data(datahex) #--works
    #loadaws_volumes_data(datahex) #--works
    #loadaws_volumesSnapshot_data(datahex) #--works
    #loadgcp_images_data(datahex,configfile)#-works
    #loadgcp_location_data(datahex, configfile)  # ---works


    # loadaws_dns_data(datahex)
    #loadaws_sizing_data(datahex)
    #loadaws_pricing_data(datahex)

    # size = 't2.medium'
    # driver_name = "ecs-i-067d1ac4509ea9863"
    #
    # pricing = get_price_driver(driver_type='compute',driver_name=driver_name).get(size,{})
    # print(pricing)
    # print(pricing.values())


'''
DETAILS SHOWS HOW TO CAPTURE THE AWS MACHINE DETAILS, UNDER ANY ACCOUNT WITH 
[
{'NODEID': 'i-067d1ac4509ea9863', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.9.178'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0995971fbf5e1abd4', 'instance_id': 'i-067d1ac4509ea9863', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-07-17T07:41:26.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-9-178.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-07-20 12:13:51 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 4, 6, 4, 36, 8, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0a1000050fa87a1e4'}}], 'groups': [{'group_id': 'sg-02a4f10ac9020b125', 'group_name': 'launch-wizard-42'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0aea4ee4c17ecb5ff, name=eni-0aea4ee4c17ecb5ff], 'product_codes': [], 'tags': {'Name': 'Yasmin'}}}, 

{'NODEID': 'i-03eef37b276c6f5e2', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.30.189'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0995971fbf5e1abd4', 'instance_id': 'i-03eef37b276c6f5e2', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-08T07:52:31.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-30-189.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-08 08:43:10 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 1, 6, 48, 49, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0cd3055a6da0f8093'}}], 'groups': [{'group_id': 'sg-093330a4e5eaf4bb5', 'group_name': 'launch-wizard-67'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0c27211e4070ee44e, name=eni-0c27211e4070ee44e], 'product_codes': [], 'tags': {'Name': 'kishor_N'}}}, 

{'NODEID': 'i-06c37234b23df11e9', 'IMAGE': None, 'PUBLIC_IP': ['34.212.50.155'], 'PRIVATE_IP': ['172.31.26.95'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-34-212-50-155.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-04575ca2f90309974', 'instance_id': 'i-06c37234b23df11e9', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'demo_instance', 'launch_index': 1, 'launch_time': '2021-10-05T13:25:16.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-26-95.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 5, 7, 8, 39, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0f12dadc9e7583433'}}], 'groups': [{'group_id': 'sg-09e042a72acdf7e63', 'group_name': 'launch-wizard-71'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-01f3b08d8c85d5c6e, name=eni-01f3b08d8c85d5c6e], 'product_codes': [], 'tags': {'Name': 'Pavan_MIN1'}}}, 

{'NODEID': 'i-037245d0f8b27cb05', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.17.150'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-04575ca2f90309974', 'instance_id': 'i-037245d0f8b27cb05', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'demo_instance', 'launch_index': 0, 'launch_time': '2021-08-02T10:06:55.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-17-150.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-09-02 06:59:05 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 5, 7, 8, 39, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-03209b28c0b02a203'}}], 'groups': [{'group_id': 'sg-09e042a72acdf7e63', 'group_name': 'launch-wizard-71'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0408e472d81a1f39b, name=eni-0408e472d81a1f39b], 'product_codes': [], 'tags': {'Name': 'Pavan_CIN2'}}}, 

{'NODEID': 'i-0575f42bfe4a00c4b', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.21.25'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-04575ca2f90309974', 'instance_id': 'i-0575f42bfe4a00c4b', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'Jasmin', 'launch_index': 0, 'launch_time': '2021-08-05T07:37:25.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-21-25.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-08-25 10:43:46 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 19, 9, 53, 29, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-08b89d2fffc24a3a5'}}], 'groups': [{'group_id': 'sg-0b7ab676916f9eba9', 'group_name': 'launch-wizard-78'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0bd8a349c0f43d3a7, name=eni-0bd8a349c0f43d3a7], 'product_codes': [], 'tags': {'Name': 'jasmin'}}}, 

{'NODEID': 'i-05116991006f7aeb9', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.16.25'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0e5634635a4c8fcbb', 'instance_id': 'i-05116991006f7aeb9', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-07-21T04:59:58.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-16-25.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-07-21 14:12:47 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 19, 10, 37, 1, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0470e5a55e645e5b9'}}], 'groups': [{'group_id': 'sg-0a22126593dc97a1c', 'group_name': 'launch-wizard-80'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-08265bc9c121c5086, name=eni-08265bc9c121c5086], 'product_codes': [], 'tags': {'Name': 'jumpServer'}}}, {'NODEID': 'i-03ace8f083c3ff652', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.25.212'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0a098e7677e311b11', 'instance_id': 'i-03ace8f083c3ff652', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-07-27T13:35:50.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-25-212.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-08-11 11:52:47 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 27, 13, 35, 51, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-09b7a1979e944d29c'}}, {'device_name': '/dev/sdb', 'ebs': {'attach_time': datetime.datetime(2021, 7, 27, 13, 35, 51, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0ef6b59c5bf2006b8'}}], 'groups': [{'group_id': 'sg-0360a1de18949031a', 'group_name': 'launch-wizard-89'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0169040c9af7872cb, name=eni-0169040c9af7872cb], 'product_codes': [], 'tags': {}}}, {'NODEID': 'i-0dbd34165484f071d', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.30.64'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-045703c65a2dc64a0', 'instance_id': 'i-0dbd34165484f071d', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.small', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-08-18T05:40:57.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-30-64.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-04 14:37:57 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 28, 12, 35, 54, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-038e8a6217049283b'}}], 'groups': [{'group_id': 'sg-0571aca0362e4aa9c', 'group_name': 'launch-wizard-90'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0908c27b246d0a0f8, name=eni-0908c27b246d0a0f8], 'product_codes': [], 'tags': {'Name': 'postgresNiv'}}}, {'NODEID': 'i-0d4d0580dcd280ea1', 'IMAGE': None, 'PUBLIC_IP': ['34.219.17.177'], 'PRIVATE_IP': ['172.31.19.73'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-34-219-17-177.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-04575ca2f90309974', 'instance_id': 'i-0d4d0580dcd280ea1', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'jasmin1', 'launch_index': 0, 'launch_time': '2021-08-27T10:37:04.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-19-73.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 28, 16, 9, 22, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-077c853fdfba4512d'}}], 'groups': [{'group_id': 'sg-0787dcdb219d9792d', 'group_name': 'launch-wizard-92'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0baa3d8ffd8eff8c9, name=eni-0baa3d8ffd8eff8c9], 'product_codes': [], 'tags': {'Name': 'jasmin1'}}}, {'NODEID': 'i-075326e4d6262e5a1', 'IMAGE': None, 'PUBLIC_IP': ['34.219.122.253'], 'PRIVATE_IP': ['172.31.27.101'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-34-219-122-253.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0b9f0d248fcd3aff1', 'instance_id': 'i-075326e4d6262e5a1', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.small', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-08-16T04:47:52.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-27-101.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/xvda', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/xvda', 'ebs': {'attach_time': datetime.datetime(2021, 7, 29, 12, 51, 8, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0f11dc2b0dcee6808'}}, {'device_name': '/dev/sdf', 'ebs': {'attach_time': datetime.datetime(2021, 7, 29, 12, 51, 8, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0c6319eb8491270ad'}}, {'device_name': '/dev/sdg', 'ebs': {'attach_time': datetime.datetime(2021, 7, 29, 12, 51, 8, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-099edc115efdb1bbb'}}], 'groups': [{'group_id': 'sg-0a3458b24569ab360', 'group_name': 'launch-wizard-94'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-09a0fdad4f51d67af, name=eni-09a0fdad4f51d67af], 'product_codes': [], 'tags': {'Name': 'Abhijit_oracle'}}}, {'NODEID': 'i-09e1a65bf453cfb91', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.41.188'], 'EXTRA': {'availability': 'us-west-2b', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-04575ca2f90309974', 'instance_id': 'i-09e1a65bf453cfb91', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.small', 'key_name': 'atgkey', 'launch_index': 2, 'launch_time': '2021-06-25T09:51:29.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-41-188.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-06-26 12:49:40 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-25acb16e', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 5, 28, 10, 10, 24, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0080db3d9522ca0fe'}}], 'groups': [{'group_id': 'sg-02573334330f7dbe3', 'group_name': 'launch-wizard-56'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0fac85b8e31609e20, name=eni-0fac85b8e31609e20], 'product_codes': [], 'tags': {'Name': 'mongodb'}}}, {'NODEID': 'i-0589c80f5ca7836b5', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.8.154'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0995971fbf5e1abd4', 'instance_id': 'i-0589c80f5ca7836b5', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-08T07:52:31.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-8-154.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-08 08:43:10 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 6, 2, 6, 0, 48, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0eb2269e2cbdcf818'}}], 'groups': [{'group_id': 'sg-0b7d6cdc85d714ca3', 'group_name': 'launch-wizard-57'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-005fee1747b1530c0, name=eni-005fee1747b1530c0], 'product_codes': [], 'tags': {'Name': 'kishorDB2+SQLSERV'}}}, {'NODEID': 'i-047ea5c9f5a63412d', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.13.111'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0bc1fb7794781cb38', 'instance_id': 'i-047ea5c9f5a63412d', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-09T11:41:56.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-13-111.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-09 13:10:20 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 6, 25, 5, 38, 32, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-00a947c64a67dc543'}}], 'groups': [{'group_id': 'sg-03d8154ce5b705892', 'group_name': 'launch-wizard-61'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-06fa25e39513818b9, name=eni-06fa25e39513818b9], 'product_codes': [], 'tags': {'Name': 'New_SQL_DB2'}}}, {'NODEID': 'i-0f1efafcefc15d09a', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.29.123'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0d1ae3c9fd552e569', 'instance_id': 'i-0f1efafcefc15d09a', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-08-24T10:17:11.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-29-123.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-08-25 10:43:46 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 8, 12, 12, 49, 50, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'false', 'status': 'attached', 'volume_id': 'vol-0e043c7a888803fdb'}}], 'groups': [{'group_id': 'sg-0f81c7e3236ca233c', 'group_name': 'launch-wizard-98'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-08f03f44c1609b8e8, name=eni-08f03f44c1609b8e8], 'product_codes': [], 'tags': {'Name': 'atgappl'}}}, {'NODEID': 'i-0c0422f3ecb48d570', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.21.47'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0b13c8f0db89ca38b', 'instance_id': 'i-0c0422f3ecb48d570', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'Abhi_DMS', 'launch_index': 0, 'launch_time': '2021-08-17T09:23:28.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-21-47.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-09-16 12:23:30 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 8, 17, 9, 23, 29, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0b378c96e37d0cfee'}}], 'groups': [{'group_id': 'sg-00aa78ceb0e72a9b1', 'group_name': 'launch-wizard-99'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-006f2b4843dd21e5e, name=eni-006f2b4843dd21e5e], 'product_codes': [], 'tags': {'Name': 'Abhi_DMS'}}}, {'NODEID': 'i-0422934dbde082f8f', 'IMAGE': None, 'PUBLIC_IP': ['54.185.25.200'], 'PRIVATE_IP': ['172.31.28.226'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-54-185-25-200.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-00743963c3d3a2bfe', 'instance_id': 'i-0422934dbde082f8f', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.small', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-09-01T10:14:47.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-28-226.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 8, 23, 10, 1, 31, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-03f6c10b5cc7b3849'}}], 'groups': [{'group_id': 'sg-021b73e5e6d4ef628', 'group_name': 'launch-wizard-101'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0fd746c3193a07604, name=eni-0fd746c3193a07604], 'product_codes': [], 'tags': {'Name': 'postgresYasmin'}}}, {'NODEID': 'i-00a436d2ebd4d9c6c', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.27.25'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-03d5c68bab01f3496', 'instance_id': 'i-00a436d2ebd4d9c6c', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-08-24T04:38:57.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-27-25.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-06 09:36:46 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 8, 24, 4, 39, 1, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0d0b15362acde9b55'}}], 'groups': [{'group_id': 'sg-05f67c71a04e0cd07', 'group_name': 'launch-wizard-102'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-04b03890110c7c105, name=eni-04b03890110c7c105], 'product_codes': [], 'tags': {'Name': 'oracle New'}}}, {'NODEID': 'i-049b5a483d8730621', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.20.40'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0b9f0d248fcd3aff1', 'instance_id': 'i-049b5a483d8730621', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-08-26T05:55:57.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-20-40.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/xvda', 'reason': 'User initiated (2021-10-06 09:37:13 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/xvda', 'ebs': {'attach_time': datetime.datetime(2021, 8, 26, 5, 55, 58, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-00982adf01e32c46b'}}, {'device_name': '/dev/sdf', 'ebs': {'attach_time': datetime.datetime(2021, 8, 26, 5, 55, 58, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-02728a6916e4d0575'}}, {'device_name': '/dev/sdg', 'ebs': {'attach_time': datetime.datetime(2021, 8, 26, 5, 55, 58, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-09e991cda3cb1af16'}}], 'groups': [{'group_id': 'sg-0a08fdaf19885164b', 'group_name': 'launch-wizard-104'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-03ce277a98634a87a, name=eni-03ce277a98634a87a], 'product_codes': [], 'tags': {'Name': 'oracleyasmine'}}}, {'NODEID': 'i-08955ddbeda9d0f4a', 'IMAGE': None, 'PUBLIC_IP': ['52.25.192.37'], 'PRIVATE_IP': ['172.31.26.162'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-52-25-192-37.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-00743963c3d3a2bfe', 'instance_id': 'i-08955ddbeda9d0f4a', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-08-27T15:27:06.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-26-162.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 8, 27, 15, 27, 7, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0d9cb2ff84b8fe425'}}], 'groups': [{'group_id': 'sg-0ece87ca31031112a', 'group_name': 'launch-wizard-106'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-01d4ae9acb8362461, name=eni-01d4ae9acb8362461], 'product_codes': [], 'tags': {'Name': ''}}}, {'NODEID': 'i-04375f35828bef657', 'IMAGE': None, 'PUBLIC_IP': ['54.187.115.171'], 'PRIVATE_IP': ['172.31.19.56'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-54-187-115-171.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-00743963c3d3a2bfe', 'instance_id': 'i-04375f35828bef657', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-08-27T15:39:04.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-19-56.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 8, 27, 15, 39, 5, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-03a2fd8be7f51e492'}}], 'groups': [{'group_id': 'sg-0238ec41b565fd1f8', 'group_name': 'launch-wizard-107'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-00a3ce3937b449990, name=eni-00a3ce3937b449990], 'product_codes': [], 'tags': {'Name': 'jas-New-Ansible'}}}, {'NODEID': 'i-0db38bbbde78dd41f', 'IMAGE': None, 'PUBLIC_IP': ['54.187.24.49'], 'PRIVATE_IP': ['172.31.3.254'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-54-187-24-49.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-04575ca2f90309974', 'instance_id': 'i-0db38bbbde78dd41f', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'SQLDEMO', 'launch_index': 0, 'launch_time': '2021-10-20T12:58:33.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-3-254.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 13, 12, 24, 50, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0090bb68ccd91be4f'}}], 'groups': [{'group_id': 'sg-04888bc1909441abf', 'group_name': 'launch-wizard-77'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0c6c994cdd807077b, name=eni-0c6c994cdd807077b], 'product_codes': [], 'tags': {'Name': 'SG_SQLINS1'}}}, {'NODEID': 'i-00f346172312c2a12', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.7.239'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0b13c8f0db89ca38b', 'instance_id': 'i-00f346172312c2a12', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-09-18T12:06:35.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-7-239.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-09-18 12:14:51 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 7, 24, 7, 35, 33, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0e944568f87bfd531'}}], 'groups': [{'group_id': 'sg-0002ee10a1eb4c752', 'group_name': 'launch-wizard-85'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-03e029a5131ece169, name=eni-03e029a5131ece169], 'product_codes': [], 'tags': {'Name': 'sct'}}}, {'NODEID': 'i-0d5f0539bcd13fb42', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.11.227'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0b9f0d248fcd3aff1', 'instance_id': 'i-0d5f0539bcd13fb42', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-09-20T07:11:21.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-11-227.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/xvda', 'reason': 'User initiated (2021-09-20 11:19:30 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/xvda', 'ebs': {'attach_time': datetime.datetime(2021, 8, 24, 7, 53, 47, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-048b9b04c18a6ffdb'}}, {'device_name': '/dev/sdf', 'ebs': {'attach_time': datetime.datetime(2021, 8, 24, 7, 53, 47, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0ffb5f060958cdd09'}}, {'device_name': '/dev/sdg', 'ebs': {'attach_time': datetime.datetime(2021, 8, 24, 7, 53, 47, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-04847ebdef52afba0'}}, {'device_name': '/dev/sdh', 'ebs': {'attach_time': datetime.datetime(2021, 8, 30, 7, 16, 23, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'false', 'status': 'attached', 'volume_id': 'vol-0b48b35cfc95312ff'}}], 'groups': [{'group_id': 'sg-08b940f01501a6cd1', 'group_name': 'launch-wizard-103'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-027170ae2487d8442, name=eni-027170ae2487d8442], 'product_codes': [], 'tags': {'Name': 'kishor_linux'}}}, {'NODEID': 'i-02d375a7ed4c2f490', 'IMAGE': None, 'PUBLIC_IP': ['34.220.199.146'], 'PRIVATE_IP': ['172.31.2.11'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-34-220-199-146.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-04575ca2f90309974', 'instance_id': 'i-02d375a7ed4c2f490', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'SQL DEMO2', 'launch_index': 0, 'launch_time': '2021-10-20T12:58:57.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-2-11.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 2, 12, 20, 46, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0ddd411ab31c76e5d'}}], 'groups': [{'group_id': 'sg-03cee1f635b47ac67', 'group_name': 'launch-wizard-109'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-01564aefa5b7d3b87, name=eni-01564aefa5b7d3b87], 'product_codes': [], 'tags': {'Name': 'SG_SQLINS2'}}}, {'NODEID': 'i-004b9d9e0906ba3ce', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.1.124'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0af5b4396152ac7ce', 'instance_id': 'i-004b9d9e0906ba3ce', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-09-08T06:55:31.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-1-124.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-09-15 13:09:46 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 3, 6, 48, 48, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-049cd23b1c3107d30'}}], 'groups': [{'group_id': 'sg-0c7c568cb0bca98e0', 'group_name': 'launch-wizard-110'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0d3316d3642ad2a05, name=eni-0d3316d3642ad2a05], 'product_codes': [], 'tags': {'Name': 'Nive_SQL'}}}, {'NODEID': 'i-092b1b24d1bcced70', 'IMAGE': None, 'PUBLIC_IP': ['54.218.163.145'], 'PRIVATE_IP': ['172.31.24.133'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-54-218-163-145.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0cd49f6efe9dbddc2', 'instance_id': 'i-092b1b24d1bcced70', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'Abhi_Niv_PG', 'launch_index': 0, 'launch_time': '2021-09-16T07:08:40.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-24-133.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 16, 7, 8, 41, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0e640c4bb7c5c71f0'}}], 'groups': [{'group_id': 'sg-07beb17aadec38f25', 'group_name': 'launch-wizard-112'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0534f67af2f82fe4b, name=eni-0534f67af2f82fe4b], 'product_codes': [], 'tags': {'Name': 'Abhi_Niv_PG'}}}, {'NODEID': 'i-0ceb5ced5444715ef', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.27.250'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-00743963c3d3a2bfe', 'instance_id': 'i-0ceb5ced5444715ef', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-09-27T05:23:08.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-27-250.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-09-27 17:49:51 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 17, 5, 25, 33, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-05d8fd1cc1260138e'}}, {'device_name': '/dev/sdb', 'ebs': {'attach_time': datetime.datetime(2021, 9, 17, 5, 25, 33, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-02e3dc1abac8cea37'}}], 'groups': [{'group_id': 'sg-0525313a2ee1ebbb7', 'group_name': 'launch-wizard-113'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0256e21f82cd510c6, name=eni-0256e21f82cd510c6], 'product_codes': [], 'tags': {'Name': 'Kishor_Ansible'}}}, {'NODEID': 'i-07249fc0e7649d531', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.29.96'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-059c283593d064ad5', 'instance_id': 'i-07249fc0e7649d531', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-01T17:00:47.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-29-96.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-01 17:03:55 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 17, 6, 6, 29, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0a7c9220dbd8f6d09'}}], 'groups': [{'group_id': 'sg-05a127def2b853e37', 'group_name': 'launch-wizard-115'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0c9819bbd5d77abe5, name=eni-0c9819bbd5d77abe5], 'product_codes': [], 'tags': {'Name': 'nivedita_sqldb2_target'}}}, {'NODEID': 'i-03d81465aebb165ec', 'IMAGE': None, 'PUBLIC_IP': ['52.12.66.167'], 'PRIVATE_IP': ['172.31.18.179'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-52-12-66-167.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0b2c054878a616e8f', 'instance_id': 'i-03d81465aebb165ec', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-11-01T07:12:29.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-18-179.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 17, 6, 4, 20, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0dfd3838f19930f1c'}}], 'groups': [{'group_id': 'sg-0ed8968bb544c54f2', 'group_name': 'launch-wizard-114'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0b18b9ebc1a7629eb, name=eni-0b18b9ebc1a7629eb], 'product_codes': [], 'tags': {'Name': 'Nivedita_SQLDB2_Source'}}}, {'NODEID': 'i-0b54992e2e8210fd6', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.17.30'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0995971fbf5e1abd4', 'instance_id': 'i-0b54992e2e8210fd6', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-17T09:23:17.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-17-30.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-17 10:29:16 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 19, 13, 58, 18, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-02f98e147e1d617b2'}}], 'groups': [{'group_id': 'sg-0c129ab2fb672740e', 'group_name': 'launch-wizard-116'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0ae6dfefede9b6776, name=eni-0ae6dfefede9b6776], 'product_codes': [], 'tags': {'Name': 'NiveditaSQLGG'}}}, {'NODEID': 'i-03d6b8801d86e607c', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.25.53'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-01d3b163ee3b22662', 'instance_id': 'i-03d6b8801d86e607c', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-22T11:54:08.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-25-53.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/xvda', 'reason': 'User initiated (2021-10-27 17:33:35 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/xvda', 'ebs': {'attach_time': datetime.datetime(2021, 9, 20, 5, 28, 18, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-065550b22e77b8fad'}}], 'groups': [{'group_id': 'sg-0fa323e0d99d1d2ab', 'group_name': 'launch-wizard-117'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-07a4d9fc3bf87d3bd, name=eni-07a4d9fc3bf87d3bd], 'product_codes': [], 'tags': {'Name': 'NiveOracleGG'}}}, {'NODEID': 'i-020f04138484ff692', 'IMAGE': None, 'PUBLIC_IP': ['54.218.77.78'], 'PRIVATE_IP': ['172.31.17.247'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-54-218-77-78.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0c2d06d50ce30b442', 'instance_id': 'i-020f04138484ff692', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-09-20T09:04:38.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-17-247.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/xvda', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/xvda', 'ebs': {'attach_time': datetime.datetime(2021, 9, 20, 9, 4, 38, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-03b01dce6320eddd8'}}], 'groups': [{'group_id': 'sg-075199a9474ef5db5', 'group_name': 'launch-wizard-118'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-098fb90b62d790670, name=eni-098fb90b62d790670], 'product_codes': [], 'tags': {'Name': 'check'}}}, {'NODEID': 'i-0121fa987e937751a', 'IMAGE': None, 'PUBLIC_IP': ['52.43.28.139'], 'PRIVATE_IP': ['172.31.26.63'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-52-43-28-139.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0cd49f6efe9dbddc2', 'instance_id': 'i-0121fa987e937751a', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'ABhi_Niv_PG_1', 'launch_index': 0, 'launch_time': '2021-09-24T05:20:32.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-26-63.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 24, 5, 20, 33, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-094919c0783739c9e'}}], 'groups': [{'group_id': 'sg-0442404708017effa', 'group_name': 'launch-wizard-119'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0316150dc4f0602ef, name=eni-0316150dc4f0602ef], 'product_codes': [], 'tags': {'Name': 'Abhi_Niv_PG_1'}}}, {'NODEID': 'i-088c6f1e4326d6441', 'IMAGE': None, 'PUBLIC_IP': ['54.213.75.231'], 'PRIVATE_IP': ['172.37.100.58'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': 'B294F2CA-9E1E-4862-A367-B5B5999B1780', 'dns_name': 'ec2-54-213-75-231.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0b37e9efc396e4c38', 'instance_id': 'i-088c6f1e4326d6441', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'manager_vm', 'launch_index': 0, 'launch_time': '2021-10-01T13:39:31.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-37-100-58.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'false', 'status': 'running', 'subnet_id': 'subnet-01edb6352a177e165', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-030dc5072b4189325', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 1, 13, 39, 32, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-06fa6cc4bfdcab214'}}], 'groups': [{'group_id': 'sg-0cb44d542eebdaafe', 'group_name': 'NVSG-4'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-01aeddac803ac8c67, name=eni-01aeddac803ac8c67], 'product_codes': [], 'tags': {'NVClusterName': 'test', 'NVState': 'Building', 'ClusterID': '4', 'Name': 'manager'}}}, {'NODEID': 'i-0481e64f3bacbe706', 'IMAGE': None, 'PUBLIC_IP': ['34.219.137.88'], 'PRIVATE_IP': ['172.31.21.101'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-34-219-137-88.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-04575ca2f90309974', 'instance_id': 'i-0481e64f3bacbe706', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-05T13:00:50.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-21-101.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 5, 13, 0, 53, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-07ea74ce2d0ba5135'}}], 'groups': [{'group_id': 'sg-06e41ba0d1d1319a3', 'group_name': 'launch-wizard-127'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0bffe3d2de03e75df, name=eni-0bffe3d2de03e75df], 'product_codes': [], 'tags': {'Name': 'test2.db'}}}, {'NODEID': 'i-07b971c405d127ab3', 'IMAGE': None, 'PUBLIC_IP': ['34.217.206.219'], 'PRIVATE_IP': ['10.0.1.39'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '1c65f1f7-b2d9-c8e4-64a3-7d7bee632d37', 'dns_name': 'ec2-34-217-206-219.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': 'AIPATDZ2GFEQRUKQCC2U5', 'image_id': 'ami-0a62a78cfedc09d76', 'instance_id': 'i-07b971c405d127ab3', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'wind1', 'launch_index': 0, 'launch_time': '2021-10-14T08:30:39.000Z', 'kernel_id': None, 'monitoring': 'enabled', 'platform': None, 'private_dns': 'ip-10-0-1-39.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-0d6a28da36dc5a2bc', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-0657ff9e14d9ec8c8', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 8, 30, 41, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0f4f5abfa7910fc6d'}}, {'device_name': '/dev/sdb', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 8, 30, 41, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0733700064e2b4ed4'}}], 'groups': [{'group_id': 'sg-00fece7f97ee08220', 'group_name': 'instance-7e1cab27-e975-44c2-a7ce-97921de92749'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-05950fd22069d5629, name=eni-05950fd22069d5629], 'product_codes': [], 'tags': {'ClusterName': 'trillio1-7e1cab27', 'ClusterUuid': '7e1cab27-e975-44c2-a7ce-97921de92749', 'Name': 'pf9-master-trillio1-7e1cab27', 'kubernetes.io/cluster/7e1cab27-e975-44c2-a7ce-97921de92749': 'owned', 'aws:autoscaling:groupName': 'master-7e1cab27-e975-44c2-a7ce-97921de92749', 'DuFQDN': 'pmkft-1632505444-98478.platform9.io', 'k8s.io/cluster-autoscaler/enabled': 'true', 'k8s.io/cluster-autoscaler/7e1cab27-e975-44c2-a7ce-97921de92749': 'true'}}}, {'NODEID': 'i-0a6419a5fba1118e1', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.25.194'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-00743963c3d3a2bfe', 'instance_id': 'i-0a6419a5fba1118e1', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-14T12:46:59.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-25-194.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-25 06:06:35 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 12, 47, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-02b5744258c50659f'}}], 'groups': [{'group_id': 'sg-0d4997316dc3d6cd7', 'group_name': 'launch-wizard-128'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-041620c45293a9c9c, name=eni-041620c45293a9c9c], 'product_codes': [], 'tags': {'Name': 'Accelerator'}}}, {'NODEID': 'i-09bb8d0792c917bd6', 'IMAGE': None, 'PUBLIC_IP': ['52.26.88.105'], 'PRIVATE_IP': ['172.31.28.229'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-52-26-88-105.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0b9f0d248fcd3aff1', 'instance_id': 'i-09bb8d0792c917bd6', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-17T10:43:41.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-28-229.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/xvda', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/xvda', 'ebs': {'attach_time': datetime.datetime(2021, 10, 17, 10, 43, 42, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0c8dad4da00c38dc2'}}, {'device_name': '/dev/sdf', 'ebs': {'attach_time': datetime.datetime(2021, 10, 17, 10, 43, 42, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0317af068801c49a0'}}, {'device_name': '/dev/sdg', 'ebs': {'attach_time': datetime.datetime(2021, 10, 17, 10, 43, 42, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-01ed1346060f04632'}}], 'groups': [{'group_id': 'sg-073d8e169d41fbf2f', 'group_name': 'launch-wizard-130'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-00ac656e148976ed1, name=eni-00ac656e148976ed1], 'product_codes': [], 'tags': {'Name': 'oracle_nive1'}}}, {'NODEID': 'i-06f451110c3ffc90f', 'IMAGE': None, 'PUBLIC_IP': ['52.43.143.186'], 'PRIVATE_IP': ['10.0.2.108'], 'EXTRA': {'availability': 'us-west-2b', 'architecture': 'x86_64', 'client_token': 'bf55f1f7-b2cd-b48a-9170-95c694cdce15', 'dns_name': 'ec2-52-43-143-186.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': 'AIPATDZ2GFEQRUKQCC2U5', 'image_id': 'ami-0a62a78cfedc09d76', 'instance_id': 'i-06f451110c3ffc90f', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'wind1', 'launch_index': 0, 'launch_time': '2021-10-14T08:30:39.000Z', 'kernel_id': None, 'monitoring': 'enabled', 'platform': None, 'private_dns': 'ip-10-0-2-108.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-0121609060842c40b', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-0657ff9e14d9ec8c8', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 8, 30, 40, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-08efa4d72026101e8'}}, {'device_name': '/dev/sdb', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 8, 30, 40, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0fca0fc8dcb019550'}}], 'groups': [{'group_id': 'sg-00fece7f97ee08220', 'group_name': 'instance-7e1cab27-e975-44c2-a7ce-97921de92749'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0c04096e4c65f0bd9, name=eni-0c04096e4c65f0bd9], 'product_codes': [], 'tags': {'k8s.io/cluster-autoscaler/7e1cab27-e975-44c2-a7ce-97921de92749': 'true', 'DuFQDN': 'pmkft-1632505444-98478.platform9.io', 'Name': 'pf9-worker-trillio1-7e1cab27', 'k8s.io/cluster-autoscaler/enabled': 'true', 'kubernetes.io/cluster/7e1cab27-e975-44c2-a7ce-97921de92749': 'owned', 'ClusterName': 'trillio1-7e1cab27', 'ClusterUuid': '7e1cab27-e975-44c2-a7ce-97921de92749', 'aws:autoscaling:groupName': 'worker-7e1cab27-e975-44c2-a7ce-97921de92749'}}}, {'NODEID': 'i-035623c3cce6cd519', 'IMAGE': None, 'PUBLIC_IP': ['35.86.134.85'], 'PRIVATE_IP': ['172.31.37.184'], 'EXTRA': {'availability': 'us-west-2b', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-35-86-134-85.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-03dc92e1d6276268b', 'instance_id': 'i-035623c3cce6cd519', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'Abhi_PG_master', 'launch_index': 0, 'launch_time': '2021-10-18T06:41:44.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-37-184.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-25acb16e', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 18, 6, 41, 45, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-06fa75a8382120fed'}}], 'groups': [{'group_id': 'sg-02779ac2482ae5219', 'group_name': 'launch-wizard-131'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0521d7490687425f0, name=eni-0521d7490687425f0], 'product_codes': [], 'tags': {'Name': 'Abhi_PG_master'}}}, {'NODEID': 'i-0799d6d0ae49d427c', 'IMAGE': None, 'PUBLIC_IP': ['34.213.218.29'], 'PRIVATE_IP': ['172.31.37.128'], 'EXTRA': {'availability': 'us-west-2b', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-34-213-218-29.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-03dc92e1d6276268b', 'instance_id': 'i-0799d6d0ae49d427c', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'Abhi_PG_slave', 'launch_index': 0, 'launch_time': '2021-10-18T06:44:19.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-37-128.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-25acb16e', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 18, 6, 44, 20, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-066e332093f1f0dc1'}}], 'groups': [{'group_id': 'sg-0b23c3875f1ac89d0', 'group_name': 'launch-wizard-132'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0d845edcb8447bdc6, name=eni-0d845edcb8447bdc6], 'product_codes': [], 'tags': {'Name': 'Abhi_PG_slave'}}}, {'NODEID': 'i-07acd20d7958a28f5', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.7.213'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-09423afb0d27cf252', 'instance_id': 'i-07acd20d7958a28f5', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.large', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-20T06:55:32.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': 'windows', 'private_dns': 'ip-172-31-7-213.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-20 15:26:35 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 24, 5, 56, 19, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0c6f6521861797266'}}], 'groups': [{'group_id': 'sg-02d9516fc5b2733f0', 'group_name': 'launch-wizard-120'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0cb57ec3bb0e5f693, name=eni-0cb57ec3bb0e5f693], 'product_codes': [], 'tags': {'Name': 'APPS'}}}, {'NODEID': 'i-0dcd39ae6d73554f2', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.2.168'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-00743963c3d3a2bfe', 'instance_id': 'i-0dcd39ae6d73554f2', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-09-26T14:53:43.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-2-168.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-25 16:08:27 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 26, 14, 53, 44, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-091af90835e5ebd86'}}], 'groups': [{'group_id': 'sg-0b4bdaa0f8b2a9899', 'group_name': 'launch-wizard-121'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0dbf2b61b218af32a, name=eni-0dbf2b61b218af32a], 'product_codes': [], 'tags': {'Name': 'jas2'}}}, {'NODEID': 'i-0920ea7a12735317d', 'IMAGE': None, 'PUBLIC_IP': ['54.190.89.137'], 'PRIVATE_IP': ['172.31.14.77'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-54-190-89-137.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0cd49f6efe9dbddc2', 'instance_id': 'i-0920ea7a12735317d', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'Abhi_Niv_PG_2', 'launch_index': 0, 'launch_time': '2021-09-27T06:52:55.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-14-77.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 27, 6, 52, 58, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0a171de340c4e4253'}}], 'groups': [{'group_id': 'sg-019f34e179d6fce95', 'group_name': 'launch-wizard-122'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-06bef2b7ef876b30e, name=eni-06bef2b7ef876b30e], 'product_codes': [], 'tags': {'Name': 'Abhi_Niv_PG_2'}}}, {'NODEID': 'i-00547ec27b3aa0633', 'IMAGE': None, 'PUBLIC_IP': ['34.211.148.49'], 'PRIVATE_IP': ['172.31.1.39'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-34-211-148-49.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0badea49b42012014', 'instance_id': 'i-00547ec27b3aa0633', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'Abhi_Ansible_plain', 'launch_index': 0, 'launch_time': '2021-09-28T08:55:22.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-1-39.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 28, 8, 55, 23, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-050dd70035a8ae460'}}], 'groups': [{'group_id': 'sg-0a5346dfc994353b8', 'group_name': 'launch-wizard-123'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-033f63470b74883ba, name=eni-033f63470b74883ba], 'product_codes': [], 'tags': {'Name': 'Abhi_Ansible_plain'}}}, {'NODEID': 'i-0001087a2bf5c2f95', 'IMAGE': None, 'PUBLIC_IP': ['54.244.161.133'], 'PRIVATE_IP': ['172.31.3.235'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-54-244-161-133.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0badea49b42012014', 'instance_id': 'i-0001087a2bf5c2f95', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'Abhi_Ansible_plain_1', 'launch_index': 0, 'launch_time': '2021-09-28T09:15:34.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-3-235.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 28, 9, 15, 35, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0f1a829cbc4036372'}}], 'groups': [{'group_id': 'sg-04e84532209eb21c8', 'group_name': 'launch-wizard-124'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0d84f356357bfb96c, name=eni-0d84f356357bfb96c], 'product_codes': [], 'tags': {'Name': 'Abhi_Ansible_plain_1'}}}, {'NODEID': 'i-06f6d40e01b19249f', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['172.31.3.244'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-00743963c3d3a2bfe', 'instance_id': 'i-06f6d40e01b19249f', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.small', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-14T05:45:17.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-3-244.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': 'User initiated (2021-10-25 06:09:45 GMT)', 'source_dest_check': 'true', 'status': 'stopped', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 30, 5, 59, 25, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-05ed854d5d5e94804'}}], 'groups': [{'group_id': 'sg-01e6651788f1b5ef5', 'group_name': 'launch-wizard-125'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-01e8b8855c8529aae, name=eni-01e8b8855c8529aae], 'product_codes': [], 'tags': {'Name': 'Yasmin_ansible_mysql'}}}, {'NODEID': 'i-0c6e43e4730169a2b', 'IMAGE': None, 'PUBLIC_IP': ['34.221.250.63'], 'PRIVATE_IP': ['10.0.0.134'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '163299155927040405', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': 'AIPATDZ2GFEQ6W6BKUZIT', 'image_id': 'ami-0038c1f564f7d78c7', 'instance_id': 'i-0c6e43e4730169a2b', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'platform9', 'launch_index': 0, 'launch_time': '2021-09-30T08:39:06.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-10-0-0-134.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-0e5e10506eee1f998', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-0393525952c21a53b', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 9, 30, 8, 39, 7, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0891e9ce80d5e2539'}}], 'groups': [{'group_id': 'sg-07666ffbfa2f5ac33', 'group_name': 'Sunlight Infrastructure Manager -SIM- Dashboard-2-0-4-AutogenByAWSMP-'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-044b946096ab5d94b, name=eni-044b946096ab5d94b], 'product_codes': [], 'tags': {'Name': 'Sunlight SIM'}}}, {'NODEID': 'i-0204aee3a4a1a10f7', 'IMAGE': None, 'PUBLIC_IP': ['52.35.25.23'], 'PRIVATE_IP': ['172.31.1.168'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-52-35-25-23.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-04575ca2f90309974', 'instance_id': 'i-0204aee3a4a1a10f7', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-05T10:09:36.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-1-168.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-bc2eece1', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 5, 10, 9, 37, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0b24e63437ba9757f'}}], 'groups': [{'group_id': 'sg-05d369ac25ab37c42', 'group_name': 'launch-wizard-126'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-009f84fe81eceff46, name=eni-009f84fe81eceff46], 'product_codes': [], 'tags': {'Name': 'Test database'}}}, {'NODEID': 'i-09ec0d39e344dc4b3', 'IMAGE': None, 'PUBLIC_IP': ['54.203.187.152'], 'PRIVATE_IP': ['10.0.4.111'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': 'ee95f1f7-b181-409d-6090-827234eae1ba', 'dns_name': 'ec2-54-203-187-152.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': 'AIPATDZ2GFEQRUKQCC2U5', 'image_id': 'ami-0a62a78cfedc09d76', 'instance_id': 'i-09ec0d39e344dc4b3', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.medium', 'key_name': 'wind1', 'launch_index': 0, 'launch_time': '2021-10-14T08:30:17.000Z', 'kernel_id': None, 'monitoring': 'enabled', 'platform': None, 'private_dns': 'ip-10-0-4-111.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-0585f719c66134cf2', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-0657ff9e14d9ec8c8', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 8, 30, 18, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-076a9886a79512b72'}}, {'device_name': '/dev/sdb', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 8, 30, 18, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-04c15f931b6e4885b'}}], 'groups': [{'group_id': 'sg-00fece7f97ee08220', 'group_name': 'instance-7e1cab27-e975-44c2-a7ce-97921de92749'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-05e4f05bdbfc04c0c, name=eni-05e4f05bdbfc04c0c], 'product_codes': [], 'tags': {'DuFQDN': 'pmkft-1632505444-98478.platform9.io', 'k8s.io/cluster-autoscaler/enabled': 'true', 'k8s.io/cluster-autoscaler/7e1cab27-e975-44c2-a7ce-97921de92749': 'true', 'kubernetes.io/cluster/7e1cab27-e975-44c2-a7ce-97921de92749': 'owned', 'aws:autoscaling:groupName': 'worker-7e1cab27-e975-44c2-a7ce-97921de92749', 'ClusterUuid': '7e1cab27-e975-44c2-a7ce-97921de92749', 'ClusterName': 'trillio1-7e1cab27', 'Name': 'pf9-worker-trillio1-7e1cab27'}}}, {'NODEID': 'i-00c008ec5f1c08fd4', 'IMAGE': None, 'PUBLIC_IP': ['18.237.170.236'], 'PRIVATE_IP': ['10.0.0.164'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-013a129d325529d4d', 'instance_id': 'i-00c008ec5f1c08fd4', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'platform9', 'launch_index': 0, 'launch_time': '2021-10-14T11:49:01.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-10-0-0-164.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/xvda', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-0e5e10506eee1f998', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-0393525952c21a53b', 'block_device_mapping': [{'device_name': '/dev/xvda', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 11, 49, 2, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0833dda3d7a323a01'}}], 'groups': [{'group_id': 'sg-0538228e8bd0df003', 'group_name': 'Netfoundry Jump'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0335c9eef963fd189, name=eni-0335c9eef963fd189], 'product_codes': [], 'tags': {'Name': 'NF-Jump'}}}, {'NODEID': 'i-0f9977d9f7596754f', 'IMAGE': None, 'PUBLIC_IP': [], 'PRIVATE_IP': ['10.0.1.173'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-013a129d325529d4d', 'instance_id': 'i-0f9977d9f7596754f', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'platform9', 'launch_index': 0, 'launch_time': '2021-10-14T11:49:57.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-10-0-1-173.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/xvda', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-058c572bd2b68a531', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-0393525952c21a53b', 'block_device_mapping': [{'device_name': '/dev/xvda', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 11, 49, 58, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-042e371c6e20a7c1b'}}], 'groups': [{'group_id': 'sg-0538228e8bd0df003', 'group_name': 'Netfoundry Jump'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-00cff0a2f0f31d5cd, name=eni-00cff0a2f0f31d5cd], 'product_codes': [], 'tags': {'Name': 'NF-Private'}}}, {'NODEID': 'i-0c4d999aa1325ad61', 'IMAGE': None, 'PUBLIC_IP': ['34.211.56.15'], 'PRIVATE_IP': ['10.0.0.66'], 'EXTRA': {'availability': 'us-west-2c', 'architecture': 'x86_64', 'client_token': '163421359313881426', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0e2f549dad4f4b240', 'instance_id': 'i-0c4d999aa1325ad61', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't3.small', 'key_name': 'platform9', 'launch_index': 0, 'launch_time': '2021-10-14T12:13:11.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-10-0-0-66.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'false', 'status': 'running', 'subnet_id': 'subnet-0e5e10506eee1f998', 'virtualization_type': 'hvm', 'ebs_optimized': 'true', 'vpc_id': 'vpc-0393525952c21a53b', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 14, 12, 13, 12, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-028f17388ca6a7312'}}], 'groups': [{'group_id': 'sg-0360d68001257d18f', 'group_name': 'NetFoundry Edge Router-1-4-20210907-AutogenByAWSMP-'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-03319025a93fb7b22, name=eni-03319025a93fb7b22], 'product_codes': [], 'tags': {'Name': 'NF-Router01'}}}, {'NODEID': 'i-0f55c8076660ad8c4', 'IMAGE': None, 'PUBLIC_IP': ['34.219.22.176'], 'PRIVATE_IP': ['172.31.30.212'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-34-219-22-176.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-0badea49b42012014', 'instance_id': 'i-0f55c8076660ad8c4', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-25T16:22:24.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-30-212.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 25, 16, 22, 25, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0d00c7156a92d2087'}}], 'groups': [{'group_id': 'sg-0c28d208349515c34', 'group_name': 'launch-wizard-133'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0701eead91404b66c, name=eni-0701eead91404b66c], 'product_codes': [], 'tags': {'Name': ' db'}}}, {'NODEID': 'i-0d14cd95f1e696a96', 'IMAGE': None, 'PUBLIC_IP': ['54.245.158.127'], 'PRIVATE_IP': ['172.31.27.26'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': 'ec2-54-245-158-127.us-west-2.compute.amazonaws.com', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-00743963c3d3a2bfe', 'instance_id': 'i-0d14cd95f1e696a96', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.micro', 'key_name': 'atgkey', 'launch_index': 0, 'launch_time': '2021-10-25T16:25:51.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-172-31-27-26.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/sda1', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-12fa096a', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-1baec863', 'block_device_mapping': [{'device_name': '/dev/sda1', 'ebs': {'attach_time': datetime.datetime(2021, 10, 25, 16, 25, 52, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-01e4959967949f959'}}], 'groups': [{'group_id': 'sg-0a2624a62f5466f8d', 'group_name': 'launch-wizard-134'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-0f83b3de0fc68c077, name=eni-0f83b3de0fc68c077], 'product_codes': [], 'tags': {'Name': 'db2'}}}, {'NODEID': 'i-0fd5eea3a9f5a0ae4', 'IMAGE': None, 'PUBLIC_IP': ['34.216.61.51'], 'PRIVATE_IP': ['10.0.0.46'], 'EXTRA': {'availability': 'us-west-2a', 'architecture': 'x86_64', 'client_token': '', 'dns_name': '', 'hypervisor': 'xen', 'iam_profile': None, 'image_id': 'ami-013a129d325529d4d', 'instance_id': 'i-0fd5eea3a9f5a0ae4', 'instance_lifecycle': None, 'instance_tenancy': 'default', 'instance_type': 't2.small', 'key_name': 'platform9', 'launch_index': 0, 'launch_time': '2021-10-29T05:30:25.000Z', 'kernel_id': None, 'monitoring': 'disabled', 'platform': None, 'private_dns': 'ip-10-0-0-46.us-west-2.compute.internal', 'ramdisk_id': None, 'root_device_type': 'ebs', 'root_device_name': '/dev/xvda', 'reason': '', 'source_dest_check': 'true', 'status': 'running', 'subnet_id': 'subnet-05c33b24150cd4ea4', 'virtualization_type': 'hvm', 'ebs_optimized': 'false', 'vpc_id': 'vpc-063ab63e9b56a2903', 'block_device_mapping': [{'device_name': '/dev/xvda', 'ebs': {'attach_time': datetime.datetime(2021, 10, 29, 5, 30, 26, tzinfo=<libcloud.utils.iso8601.Utc object at 0x000001FB3F863EB8>), 'delete': 'true', 'status': 'attached', 'volume_id': 'vol-0d07f759deecb3e67'}}], 'groups': [{'group_id': 'sg-04db7c29a53c9c309', 'group_name': 'ZenKNI-Jump'}], 'network_interfaces': [<EC2NetworkInterface: id=eni-088a7b60c24387d44, name=eni-088a7b60c24387d44], 'product_codes': [], 'tags': {'Name': 'ZenKNI-Jump', 'Owner': 'Aravind'}}}]
'''