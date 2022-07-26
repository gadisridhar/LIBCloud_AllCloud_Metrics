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
from time import *
from libcloud.compute.providers import get_driver as get_compute_driver
from libcloud.compute.types import Provider as ComputeProvider



from libcloud.dns.providers import get_driver as get_dns_driver
from libcloud.dns.types import Provider as DNSProvider

from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver as get_storage_driver

from libcloud.pricing import get_size_price, get_pricing, get_pricing_file_path, download_pricing_file


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


def load_anaon(datahex, cloudPayload, cfgDB):
    cls = get_storage_driver(Provider.AZURE_BLOBS)
    driver = cls(tenant_id=str(cloudPayload[Names.AZURE_TENANTID]),
                 subscription_id=str(cloudPayload[Names.AZURE_SUBSCRIPTIONID]),
                 key=str(cloudPayload[Names.AZURE_APIKEY]),
                 secret=str(cloudPayload[Names.AZURE_APISECRET]),
                 region=str(cloudPayload[Names.AZURE_REGION]))

    driver.list_containers()

    return ""

def loadazure_compute_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.AZURE_ARM)
        driver = cls(tenant_id=str(cloudPayload[Names.AZURE_TENANTID]),
                     subscription_id=str(cloudPayload[Names.AZURE_SUBSCRIPTIONID]),
                     key=str(cloudPayload[Names.AZURE_APIKEY]),
                     secret=str(cloudPayload[Names.AZURE_APISECRET]),
                     region=str(cloudPayload[Names.AZURE_REGION]))
        nodeDetails = driver.list_nodes()

        print(len(nodeDetails))
        machineCount_Running = 0
        machineCount_Stopped = 0

        computeList = []
        machineRunning = []
        machineStopped = []

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
                extra[Names.IMAGE] = node.image
                extra[Names.PUBLIC_IP] = node.public_ips
                extra[Names.PRIVATE_IP] = node.private_ips
                extra[Names.CREATED_AT] = node.created_at
                extra[Names.EXTRA] = node.extra
                extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                       "%d/%m/%Y %H:%M:%S")
                extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                        "%d/%m/%Y %H:%M:%S")

                if ((Names.NETWORK_INTERFACES) in tuple(node.extra)):
                    if (node.extra[Names.NETWORK_INTERFACES]) is None:
                        netLISTMain = []
                        extra[Names.NETWORK] = netLISTMain
                    else:
                        netLISTMain = []
                        netLIST = node.extra[Names.NETWORK_INTERFACES]
                        for nl in netLIST:
                            extraJSON = {}
                            extranl = nl.extra
                            id = nl.id
                            state = nl.state
                            name = nl.name
                            extraJSON[Names.EXTRAID] = id
                            extraJSON[Names.STATE] = state
                            extraJSON[Names.EXTRANAME] = name

                            del extranl[Names.TAGS]
                            extraJSON[Names.EXTRA] = extranl
                            netLISTMain.append(extraJSON)

                        extra[Names.NETWORK] = netLISTMain
                        del extra[Names.EXTRA][Names.NETWORK_INTERFACES]
                else:
                    extra[Names.NETWORK] = []

                computeList.append(extra)
                extraMachines[Names.MACHINE_STOPPED] = machineStopped
                extraMachines[Names.MACHINE_RUNNING] = machineRunning

                machineDetails = {}
                machinesCount = len(nodeDetails)
                machineDetails[Names.MACHINE_COUNT] = machinesCount
                machineDetails[Names.MACHINE_RUNNING] = machineCount_Running
                machineDetails[Names.MACHINE_STOPPED] = machineCount_Stopped

            print(machineDetails)
            DataManager.compute_Data(computeList, cfgDB)
            DataManager.cloud_Compute_Upsert(datahex, machineDetails, cfgDB)
            DataManager.cloud_ComputeMachines_Upsert(datahex, extraMachines, cfgDB)
            message[Names.RESPONSE_MESSAGE] = "Azure Compute Details Added"
        else:
            print("empty")
            message[Names.RESPONSE_MESSAGE] = "Empty Compute Details"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message



def loadazure_volumes_data(datahex,cloudPayload,cfgDB):
    message = {}
    try:
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.AZURE_ARM)
        driver = cls(tenant_id=str(cloudPayload[Names.AZURE_TENANTID]),
                     subscription_id=str(cloudPayload[Names.AZURE_SUBSCRIPTIONID]),
                     key=str(cloudPayload[Names.AZURE_APIKEY]),
                     secret=str(cloudPayload[Names.AZURE_APISECRET]),
                     region=str(cloudPayload[Names.AZURE_REGION]))
        # ----------------------------------------------------------------------------
        nodeDetails = driver.list_volumes()
        volumeList = []
        for node in nodeDetails:
            extra = {}
            extraJSON = {}
            datahex_Unique = uuid.uuid4().hex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = datahex_Unique
            extra[Names.CID] = node.id
            extra[Names.UUID] = node.uuid
            extra[Names.EXTRANAME] = node.name
            extra[Names.SIZE] = node.size
            extra[Names.STATE] = node.state
            extra[Names.EXTRA] = node.extra
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")

            if ([Names.OSTYPE] in tuple(node.extra[Names.PROPERTIES])):
                extraJSON[Names.OSTYPE] = node.extra[Names.PROPERTIES][Names.OSTYPE]
            else:
                extraJSON[Names.OSTYPE] = ""

            if ([Names.PROVISIONSTATE] in tuple(node.extra[Names.PROPERTIES])):
                extraJSON[Names.PROVISIONSTATE] = node.extra[Names.PROPERTIES][Names.PROVISIONSTATE]
            else:
                extraJSON[Names.PROVISIONSTATE] = ""

            extra[Names.VOLUME_DETAILS] = extraJSON
            volumeList.append(extra)

        DataManager.volume_Data(volumeList, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "Azure Volume Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message

def loadazure_volumesSnapshot_data(datahex,cloudPayload,cfgDB):
    message = {}
    try:
        # --------------------------------------------DRIVER DETAILS FOR AZURE ACCOUNT
        cls = get_compute_driver(ComputeProvider.AZURE_ARM)
        driver = cls(tenant_id=str(cloudPayload[Names.AZURE_TENANTID]),
                     subscription_id=str(cloudPayload[Names.AZURE_SUBSCRIPTIONID]),
                     key=str(cloudPayload[Names.AZURE_APIKEY]),
                     secret=str(cloudPayload[Names.AZURE_APISECRET]),
                     region=str(cloudPayload[Names.AZURE_REGION]))

        # ----------------------------------------------------------------------------
        countVolums = len(driver.list_volumes())
        volumeSnapShotList = []
        for i in range(countVolums):
            extra = {}
            datahex_Unique = uuid.uuid4().hex
            volumeprint = driver.list_volumes()[i]
            # print(volumeprint)
            volumeSnapShotName = driver.list_volumes()[i].name
            volumeSnapShotID = driver.list_volumes()[i].id
            volumeSnapShotUUID = driver.list_volumes()[i].uuid
            extra[Names.OWNERID] = datahex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.ID] = datahex_Unique
            extra[Names.VOLUMESNAPSHOT_ID] = volumeSnapShotID
            extra[Names.VOLUMESNAPSHOT_UUID] = volumeSnapShotUUID
            extra[Names.VOLUMESNAPSHOT_NAME] = volumeSnapShotName
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")

            volSnapShotListMain = []
            sleep(1)
            print("----------", i)
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
            volumeSnapShotList.append(extra)
            DataManager.volumeSnapShot_Data(extra, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "Azure volumes Snapshot Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message



def loadazure_images_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.AZURE_ARM)
        driver = cls(tenant_id=str(cloudPayload[Names.AZURE_TENANTID]),
                     subscription_id=str(cloudPayload[Names.AZURE_SUBSCRIPTIONID]),
                     key=str(cloudPayload[Names.AZURE_APIKEY]),
                     secret=str(cloudPayload[Names.AZURE_APISECRET]),
                     region=str(cloudPayload[Names.AZURE_REGION]))
        # ----------------------------------------------------------------------------
        print("Azureeeeeeeeeeeeee 1")

        imageDetails = driver.list_images()

        print("Azureeeeeeeeeeeeee 2")

        imageList = []
        for image in imageDetails:
            extra = {}
            driverInner = {}
            datahex_Unique = uuid.uuid4().hex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = datahex_Unique
            extra[Names.UUID] = image.uuid
            extra[Names.EXTRANAME] = image.name
            extra[Names.DRIVER] = image.driver
            driverInner[Names.DRIVER_APINAME] = image.driver.api_name
            driverInner[Names.DRIVER_APIVERSION] = image.driver.api_version
            driverInner[Names.DRIVER_REGION] = image.driver.region
            driverInner[Names.DRIVER_REGIONNAME] = image.driver.region_name
            driverInner[Names.DRIVER_SECRET] = image.driver.secret
            driverInner[Names.DRIVER_SECURE] = image.driver.secure
            driverInner[Names.DRIVER_SIGNATUREVERSION] = image.driver.signature_version
            driverInner[Names.DRIVER_TYPE] = image.driver.type
            driverInner[Names.DRIVER_NAME] = image.driver.name
            driverInner[Names.DRIVER_CONNECTIONS] = image.driver.connectionCls
            extra[Names.DRIVER_DETAILS] = driverInner
            extra[Names.EXTRA] = image.extra
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")
            imageList.append(extra)

        DataManager.images_Data(imageList, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "Azure images Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadazure_location_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        cls = get_compute_driver(ComputeProvider.AZURE_ARM)
        driver = cls(tenant_id=str(cloudPayload[Names.AZURE_TENANTID]),
                     subscription_id=str(cloudPayload[Names.AZURE_SUBSCRIPTIONID]),
                     key=str(cloudPayload[Names.AZURE_APIKEY]),
                     secret=str(cloudPayload[Names.AZURE_APISECRET]),
                     region=str(cloudPayload[Names.AZURE_REGION]))

        locDetails = driver.list_locations()

        locationList = []
        for location in locDetails:
            extra = {}
            datahex_Unique = uuid.uuid4().hex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = datahex_Unique
            extra[Names.LOCATION_ID] = location.id
            extra[Names.COUNTRY] = location.country
            extra[Names.AVAILABLITYZONE_NAME] = location.name
            extra[Names.AVAILABLITYZONE_REGION] = location.driver.region
            extra[Names.AVAILABLITYZONE_STATE] = ""
            extra[Names.AVAILABLITYZONE_SIZES] = []
            extra[Names.AVAILABLITYZONE_IMAGES] = []
            extra[Names.EXTRA] = location.extra
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")

            locationList.append(extra)

        DataManager.location_Data(locationList, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "Azure Location Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadazure_dns_data():
    message = {}
    try:
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_dns_driver(DNSProvider.AURORADNS)
        driver_dns = cls(tenant_id="*************",
                         subscription_id="1*************",
                         key="***********",
                         secret="*************", region="eastus")
        foo = driver_dns.list_zones()
        print(foo)

        data1 = []
        for node in foo:
            extra = {}
            # print("NODE ID --------- ",node.id)
            extra["UNIVERSALID"] = 2222222222
            extra["NODEID"] = node.extra
            # extra["DOMAIN"] = node.type
            # extra["EXTRA"] = node.L
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")
            data1.append(extra)
        message[Names.RESPONSE_MESSAGE] = "Azure DNS Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message



def loadazure_pricing_data(datahex):
    message = {}
    try:
        # --------------------------------------------DNS DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.AZURE_ARM)
        driver = cls(tenant_id="**************",
                     subscription_id="="*************",", key="="*************",",
                     secret="="*************",", region="eastus")

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
            # get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="ec2_linux", size_id=size.uuid, region=size.driver.region)
            # get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="ec2_windows", size_id=size.uuid,region=size.driver.region)

            # AZURE ------COMPUTE PRICE CALCULATE
            get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="azure_linux", size_id=size.uuid,
                                                 region=size.driver.region)
            # get_CalculatedPrice = get_size_price(driver_type="compute", driver_name="azure_windows", size_id=size.uuid,region=size.driver.region)

            # ------STORAGE PRICE CALCULATE
            # get_CalculatedPrice = get_size_price(driver_type="storage", driver_name="ec2_linux", size_id=size.uuid,region=size.driver.region)

            print(get_CalculatedPrice)
            extra["COMPUTE_PRICE"] = get_CalculatedPrice

            data1.append(extra)
        message[Names.RESPONSE_MESSAGE] = "Azure Pricing Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def load_cloud_data(datahex, cloudPayload,cfgDB):
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

        extra[Names.API_TENANT_ID] = cloudPayload[Names.API_TENANT_ID]
        extra[Names.API_SUBSCRIPTION_ID] = cloudPayload[Names.API_SUBSCRIPTION_ID]
        extra[Names.APIKEY] = cloudPayload[Names.APIKEY]
        extra[Names.APISECRET] = cloudPayload[Names.APISECRET]
        extra[Names.REGION] = cloudPayload[Names.REGION]
        extra[Names.CLOUD_PROVIDER] = cloudPayload[Names.CLOUD_PROVIDER]
        extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                               "%d/%m/%Y %H:%M:%S")
        extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                "%d/%m/%Y %H:%M:%S")

        jsonData = DataManager.cloud_Data(extra, cfgDB)
        message[Names.MESSAGE] = jsonData[Names.MESSAGE]
        message[Names.RESPONSE_MESSAGE] = "Azure Cloud Account Details Added"

    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadazure_polling_data(datahex, cloudPayload, cfgDB):
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
        extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                               "%d/%m/%Y %H:%M:%S")
        extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                "%d/%m/%Y %H:%M:%S")
        DataManager.CMP_PollingData(extra, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "Azure Polling Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadazure_subnet_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        # logger.info("----------  LOADING TENANT CREDENTIALS  ----------")
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.AZURE_ARM)
        driver = cls(tenant_id=str(cloudPayload[Names.AZURE_TENANTID]),
                     subscription_id=str(cloudPayload[Names.AZURE_SUBSCRIPTIONID]),
                     key=str(cloudPayload[Names.AZURE_APIKEY]),
                     secret=str(cloudPayload[Names.AZURE_APISECRET]),
                     region=str(cloudPayload[Names.AZURE_REGION]))
        nodeDetails = driver.list_nodes()

        for node in nodeDetails:
            extra = {}
            extra[Names.MACHINE_ID] = node.id
            datahex_Unique = uuid.uuid4().hex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = datahex_Unique
            if('id' in str(node)) == True:
                extra['subnet_id'] = node.id
            else:
                extra['subnet_id'] = ""

            if ('name' in str(node)) == True:
                extra['name'] = node.name
            else:
                extra['name'] = ""

            if ('description' in node.extra) == True:
                extra['description'] = node.extra['description']
            else:
                extra['description'] = ""

            if ('state' in str(node)) == True:
                extra['status'] = node.state
            else:
                extra['status'] = ""

            if ('vpc_id' in node.extra) == True:
                extra['vpc_id'] = node.extra['vpc_id']
            else:
                extra['vpc_id'] = ""

            if ('availability' in node.extra) == True:
                extra['availability'] = node.extra['availability']
            else:
                extra['availability'] = ""

            if ('tags' in node.extra) == True:
                extra['tags'] = node.extra['tags']
            else:
                extra['tags'] = []

            #-----------------------------------WORK FROM HERE---------------------
            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")



            if (Names.NETWORK_INTERFACES in node.extra) == True:
                netLIST = node.extra[Names.NETWORK_INTERFACES]
            else:
                netLIST = []


            for nl in netLIST:
                extraJSON = {}

                if ('network' in nl) == True:
                    extraJSON['network'] = nl["network"]
                    extraJSON['vpc_id'] = nl["network"] #.rpartition('/')[-1]
                else:
                    extraJSON['network'] = ""
                    extraJSON['vpc_id'] = ""

                    # extraJSON["subnetwork"] = nl["subnetwork"]
                if ('subnetwork' in nl) == True:
                    extraJSON['subnetwork'] = nl['subnetwork']
                    #extraJSON['subnet_id'] = nl['subnetwork'].rpartition('/')[-1]
                else:
                    extraJSON['subnetwork'] = ""
                    #extraJSON['subnet_id'] = ""

                    # extraJSON["networkIP"] = nl["networkIP"]
                if ('networkIP' in nl) == True:
                    extraJSON['networkIP'] = nl['networkIP']
                else:
                    extraJSON['networkIP'] = ""

                    # extraJSON["name"] = nl["name"]
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

                # if ('subnet_id' in nl.extra) == True:
                #     exsubnet_id = nl.extra['subnet_id']
                # else:
                #     exsubnet_id = ""
                #
                # #exsubnet_id = nl.extra['subnet_id']
                # exvpc_id = nl.extra['vpc_id']
                # exzone = nl.extra['zone']
                # exdescription = nl.extra['description']
                # exowner_id = nl.extra['owner_id']
                # exmac_address = nl.extra['mac_address']
                #
                # exattachment_id = nl.extra['attachment']['attachment_id']
                # exstatus = nl.extra['attachment']['status']
                # exprivateIP_Details = nl.extra['private_ips']
                # exgroup_Details = nl.extra['groups']
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
            DataManager.CMP_SubnetData(extra, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "Azure Subnet Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def loadazure_network_data(datahex, cloudPayload, cfgDB):
    message = {}
    try:
        # logger.info("----------  LOADING TENANT CREDENTIALS  ----------")
        # --------------------------------------------DRIVER DETAILS FOR AWS ACCOUNT
        cls = get_compute_driver(ComputeProvider.AZURE_ARM)
        driver = cls(tenant_id=str(cloudPayload[Names.AZURE_TENANTID]),
                     subscription_id=str(cloudPayload[Names.AZURE_SUBSCRIPTIONID]),
                     key=str(cloudPayload[Names.AZURE_APIKEY]),
                     secret=str(cloudPayload[Names.AZURE_APISECRET]),
                     region=str(cloudPayload[Names.AZURE_REGION]))
        nodeDetails = driver.list_nodes()

        for node in nodeDetails:
            extra = {}
            extra[Names.MACHINE_ID] = node.id
            datahex_Unique = uuid.uuid4().hex
            extra[Names.UNIVERSALID] = datahex
            extra[Names.OWNERID] = datahex
            extra[Names.ID] = datahex_Unique

            extra['cidr'] = ""

            if ('vpc_id' in node.extra) == True:
                extra['vpc_id'] = node.extra['vpc_id']
                extra['network_id'] = node.extra['vpc_id']
            else:
                extra['vpc_id'] = ""
                extra['network_id'] = ""

            extra[Names.ROW_CREATED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                   "%d/%m/%Y %H:%M:%S")
            extra[Names.ROW_MODIFIED_TIMESTAMP] = datetime.strptime(now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                    "%d/%m/%Y %H:%M:%S")


            if (Names.NETWORK_INTERFACES in node.extra) == True:
                netLIST = node.extra[Names.NETWORK_INTERFACES]
            else:
                netLIST = []

            for nl in netLIST:
                extraJSON = {}
                # exnetwork_id = nl.extra['vpc_id']
                # exname = nl.extra['vpc_id']
                # extraJSON["network_id"] = exnetwork_id
                # extraJSON["name"] = exname

                if ('network' in nl) == True:
                    extraJSON['network'] = nl["network"]
                    extraJSON['vpc_id'] = nl["network"] #.rpartition('/')[-1]
                else:
                    extraJSON['network'] = ""
                    extraJSON['vpc_id'] = ""

                    # extraJSON["subnetwork"] = nl["subnetwork"]
                if ('subnetwork' in nl) == True:
                    extraJSON['subnetwork'] = nl['subnetwork']
                    #extraJSON['subnet_id'] = nl['subnetwork'].rpartition('/')[-1]
                else:
                    extraJSON['subnetwork'] = ""
                    #extraJSON['subnet_id'] = ""

                    # extraJSON["networkIP"] = nl["networkIP"]
                if ('networkIP' in nl) == True:
                    extraJSON['networkIP'] = nl['networkIP']
                else:
                    extraJSON['networkIP'] = ""

                    # extraJSON["name"] = nl["name"]
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

                extra[Names.NETWORK_DETAILS] = extraJSON
            print(extra)
            DataManager.CMP_NetworkData(extra, cfgDB)
        message[Names.RESPONSE_MESSAGE] = "Azure Network Details Added"
    except Exception as e:
        print("exception: " + str(e))
        message[Names.RESPONSE_MESSAGE] = str(e)

    return message


def azureComputation(cloudPayload,cfgDB):
    print("AZURE")
    datahex = uuid.uuid4().hex
    jsonData = load_cloud_data(datahex, cloudPayload, cfgDB)  # ---  CLOUD CONFIGURATION RELATED DATA FOR AZURE
    responseMessage = {}
    responseList = []
    if (jsonData[Names.MESSAGE] == Names.NOTEXISTS):
        print("------------")
        responseMessage["pollingDetails"] = loadazure_polling_data(datahex, cloudPayload, cfgDB)
        responseMessage["computeDetails"] = loadazure_compute_data(datahex, cloudPayload, cfgDB)
        responseMessage["volumeDetails"] = loadazure_volumes_data(datahex, cloudPayload, cfgDB)
        responseMessage["volumeSnapshotDetails"] = loadazure_volumesSnapshot_data(datahex, cloudPayload, cfgDB)
        responseMessage["locationDetails"] = loadazure_location_data(datahex, cloudPayload, cfgDB)
        responseMessage["subnetDetails"] = loadazure_subnet_data(datahex, cloudPayload, cfgDB) #---------------------------NOT WORKING
        responseMessage["networkDetails"] = loadazure_network_data(datahex, cloudPayload, cfgDB) #---------------------------NOT WORKING
        responseMessage["imageDetails"] = loadazure_images_data(datahex, cloudPayload, cfgDB) #---------------------------NOT WORKING
        responseMessage["accountDetails"] = "Account Details Added"
        responseList.append(responseMessage)
    else:
        print("Account Details Already ", Names.EXISTS)
        responseMessage["accountDetails"] = "Account Details already exists"
        responseList.append(responseMessage)

    print("AZURE CLOUD DETAILS CAPTURED")
    return responseList


async def azureComputationCheck(cloudPayload,cfgDB):
    print("AZURE CHECK")
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
    load_cloud_data(datahex, cloudPayload, cfgDB)
    loadazure_polling_data(datahex, cloudPayload, cfgDB)
    loadazure_compute_data(datahex, cloudPayload, cfgDB)
    loadazure_volumes_data(datahex, cloudPayload, cfgDB)
    loadazure_volumesSnapshot_data(datahex, cloudPayload, cfgDB)
    loadazure_location_data(datahex, cloudPayload, cfgDB)
    loadazure_subnet_data(datahex, cloudPayload, cfgDB)
    loadazure_network_data(datahex, cloudPayload, cfgDB)
    loadazure_images_data(datahex, cloudPayload, cfgDB)

if __name__ == '__main__':
    print("SETTING ")
    app_route = op.dirname(op.realpath(__file__))
    resourcepath = op.join(app_route, "resources")
    configfile = op.join(resourcepath, "config.json")
    ConfigManager.loadconfigfile(configfile)
    cfgDatabase = ConfigManager.getconfig(Names.CONFIG_STORE)

    datahex = uuid.uuid4().hex
    #app.run(host="localhost", port=5007)
    #loadazure_compute_data(datahex, cloudPayload, cfgDB) #---WORKS
    #loadazure_dns_data()
    #loadazure_pricing_data(datahex)----checking
    #loadazure_volumes_data(datahex,cfgDatabase) #---WORKS
    #loadazure_volumesSnapshot_data(datahex,cfgDatabase) ---WORKS
    #loadazure_images_data(datahex, cfgDatabase)  # --------NT WORKING
    #loadazure_location_data(datahex, cfgDatabase)  # ---works

    # size = 't2.medium'
    # driver_name = "ecs-i-067d1ac4509ea9863"
    #
    # pricing = get_price_driver(driver_type='compute',driver_name=driver_name).get(size,{})
    # print(pricing)
    # print(pricing.values())


'''
DETAILS SHOWS HOW TO CAPTURE THE AWS MACHINE DETAILS, UNDER ANY ACCOUNT WITH 

'''
