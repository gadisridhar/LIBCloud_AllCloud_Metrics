import random
import pandas as pd
import snowflake
import snowflake as sf
from snowflake import connector
from flask import Flask
from flask import request
from flask import jsonify
import urllib
import collections
import os
os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3.6'
import urllib.request, json
app = Flask(__name__)
#cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'



##//
# {
#     "tenantid":"dsds",
#     "userid":"SG6666",
#     "passwordid":"dsadasd",
#     "accountid":"dsddsda",
#     "dbName":"SRIDHAR",
#     "schemaName":"PUBLIC",
#     "tblName":"TBLDATA",
#     "jsonValue":[{"AGE":7,"NAME":"G"},{"AGE":4,"NAME":"A"}]
# }
##//

@app.route('/snowflakeinserttable', methods=['GET', 'POST'])
def connectSNOWFlakeInsertValues():
    try:
        # Gets the version
        bodyJSON = request.get_json()
        tenantid = bodyJSON['tenantid']
        userid = bodyJSON['userid']
        passwordid = bodyJSON['passwordid']
        passwordid = urllib.parse.quote_plus(passwordid)
        accountid = bodyJSON['accountid']
        dbName = bodyJSON['dbName']
        schemaName = bodyJSON['schemaName']
        tblName = bodyJSON['tblName']
        jsonStruct = bodyJSON['jsonValue']
        ctx = snowflake.connector.connect(
            user='gadicloud',
            password='Shekhar@63',
            account='rg54129.west-us-2.azure',
            database=dbName,
            schema=schemaName
        )
        cs = ctx.cursor()

        print(jsonStruct)
        print(type(jsonStruct))
        print("8888888888888888888888888888888888888888")
        print(type(jsonStruct))
        print(len(jsonStruct))

        listLength = len(jsonStruct)

        i = 0
        while i < listLength:
            #jsonValue = json.loads(jsonStruct[i])
            jsonValue = jsonStruct[i]
            print(type(jsonValue))
            print((jsonValue))
            try:
                # cs.execute("SELECT current_version()")
                # cs.execute("select * from " + tblName)
                keyData = []
                for keys in jsonValue.keys():
                    keyData.append(keys)

                keyData = str(keyData)
                keyData = keyData.replace("[", "")
                keyData = keyData.replace("]", "")
                keyData = keyData.replace("'", "")
                print(keyData)

                keyValue = []
                for keys in jsonValue.values():
                    keyValue.append(keys)

                keyValue = str(keyValue)
                keyValue = keyValue.replace("[", "")
                keyValue = keyValue.replace("]", "")
                print(keyValue)

                print("insert into " + tblName + " " + "(" + keyData + ")" + " values " + "(" + keyValue + ")")
                # insert into table1 (id, varchar1, variant1) values (4, 'Fourier', parse_json('{ "key1": "value1", "key2": "value2" }'));
                one_row = cs.execute(
                    "insert into " + tblName + " " + "(" + keyData + ")" + " values " + "(" + keyValue + ")")
                print(one_row.timezone)
                listDB = ["Data inserted into SnowFlake Repository"]
                i += 1
            except Exception as EE:
                print(EE)
                print("0000000000000000000000000000")
                outputException = {}
                outputException["Message"] = str(EE)

        cs.close()
        ctx.close()

        return jsonify(listDB), 200
    except SyntaxError as SYE:
        print("0000000000000000000000000000")
        outputException = {}
        outputException["Message"] = str(SYE)
        print(outputException)
        return jsonify(outputException), 300
    except Exception as e:
        print("111111111111111111111111111")
        print(e)
        outputException = {}
        outputException["Message"] = str(e)
        print(outputException)
        print("##################################")
        print(jsonify(outputException))
        return jsonify(outputException), 500
    except IOError as ioe:
        print("2222222222222222222222222222")
        print(ioe)
        outputException = {}
        outputException["Message"] = str(ioe)
        print(outputException)
        return jsonify(outputException), 300
    except ConnectionRefusedError as cre:
        print("3333333333333333333333333333")
        outputException = {}
        outputException["Message"] = str(cre)
        print(outputException)
        return jsonify(outputException), 501



@app.route('/snowflakedb', methods=['GET', 'POST'])
def connectSNOWFlakeDB():
    try:
        tenantid = request.args.get('tenantid')
        userid = request.args.get('userid')
        passwordid = request.args.get('passwordid')
        passwordid = urllib.parse.quote_plus(passwordid)
        accountid = request.args.get('accountid')
        # Gets the version
        ctx = snowflake.connector.connect(
            user='gadicloud',
            password='Shekhar@63',
            account='rg54129.west-us-2.azure'
        )
        cs = ctx.cursor()
        try:
            # cs.execute("SELECT current_version()")
            cs.execute("show databases")
            one_row = cs.fetchall()
            # print(one_row[0])
            print(one_row)
            listDB = []
            for row in one_row:
                listDB.append(row[1])

            print(listDB)
        finally:
            cs.close()
        ctx.close()
        return jsonify(listDB), 200

    except SyntaxError as SYE:
        print("0000000000000000000000000000")
        outputException = {}
        outputException["Message"] = str(SYE)
        print(outputException)
        return jsonify(outputException), 300
    except Exception as e:
        print("111111111111111111111111111")
        print(e)
        outputException = {}
        outputException["Message"] = str(e)
        print(outputException)
        print("##################################")
        print(jsonify(outputException))
        return jsonify(outputException), 500
    except IOError as ioe:
        print("2222222222222222222222222222")
        print(ioe)
        outputException = {}
        outputException["Message"] = str(ioe)
        print(outputException)
        return jsonify(outputException), 300
    except ConnectionRefusedError as cre:
        print("3333333333333333333333333333")
        outputException = {}
        outputException["Message"] = str(cre)
        print(outputException)
        return jsonify(outputException), 501


@app.route('/snowflaketblselect', methods=['GET', 'POST'])
def connectSNOWFlakeShowTablesSelection():
    try:
        # Gets the version
        tenantid = request.args.get('tenantid')
        userid = request.args.get('userid')
        passwordid = request.args.get('passwordid')
        passwordid = urllib.parse.quote_plus(passwordid)
        accountid = request.args.get('accountid')
        dbName = request.args.get('dbName')
        schemaName = request.args.get('schemaName')
        ctx = snowflake.connector.connect(
            user='gadicloud',
            password='Shekhar@63',
            account='rg54129.west-us-2.azure',
            database=dbName,
            schema=schemaName
        )
        cs = ctx.cursor()
        try:
            # cs.execute("SELECT current_version()")
            cs.execute("show tables")
            one_row = cs.fetchall()
            # print(one_row[0])
            print(one_row)
            listDB = []
            for row in one_row:
                listDB.append(row[1])

            print(listDB)
        finally:
            cs.close()
        ctx.close()
        return jsonify(listDB), 200
    except SyntaxError as SYE:
        print("0000000000000000000000000000")
        outputException = {}
        outputException["Message"] = str(SYE)
        print(outputException)
        return jsonify(outputException), 300
    except Exception as e:
        print("111111111111111111111111111")
        print(e)
        outputException = {}
        outputException["Message"] = str(e)
        print(outputException)
        print("##################################")
        print(jsonify(outputException))
        return jsonify(outputException), 500
    except IOError as ioe:
        print("2222222222222222222222222222")
        print(ioe)
        outputException = {}
        outputException["Message"] = str(ioe)
        print(outputException)
        return jsonify(outputException), 300
    except ConnectionRefusedError as cre:
        print("3333333333333333333333333333")
        outputException = {}
        outputException["Message"] = str(cre)
        print(outputException)
        return jsonify(outputException), 501

@app.route('/snowflakeschemaselect', methods=['GET', 'POST'])
def connectSNOWFlakeSchema():
    try:
        # Gets the version
        tenantid = request.args.get('tenantid')
        userid = request.args.get('userid')
        passwordid = request.args.get('passwordid')
        passwordid = urllib.parse.quote_plus(passwordid)
        accountid = request.args.get('accountid')
        dbName = request.args.get('dbName')
        ctx = snowflake.connector.connect(
            user='gadicloud',
            password='Shekhar@63',
            account='rg54129.west-us-2.azure',
            database=dbName
        )
        cs = ctx.cursor()
        try:
            # cs.execute("SELECT current_version()")
            cs.execute("show schemas")
            one_row = cs.fetchall()
            # print(one_row[0])
            print(one_row)
            listDB = []
            for row in one_row:
                listDB.append(row[1])

            print(listDB)
        finally:
            cs.close()
        ctx.close()
        return jsonify(listDB), 200
    except SyntaxError as SYE:
        print("0000000000000000000000000000")
        outputException = {}
        outputException["Message"] = str(SYE)
        print(outputException)
        return jsonify(outputException), 300
    except Exception as e:
        print("111111111111111111111111111")
        print(e)
        outputException = {}
        outputException["Message"] = str(e)
        print(outputException)
        print("##################################")
        print(jsonify(outputException))
        return jsonify(outputException), 500
    except IOError as ioe:
        print("2222222222222222222222222222")
        print(ioe)
        outputException = {}
        outputException["Message"] = str(ioe)
        print(outputException)
        return jsonify(outputException), 300
    except ConnectionRefusedError as cre:
        print("3333333333333333333333333333")
        outputException = {}
        outputException["Message"] = str(cre)
        print(outputException)
        return jsonify(outputException), 501


@app.route('/snowflakecreatetable', methods=['GET', 'POST'])
def connectSNOWFlakeCreateTable():
    try:
        # Gets the version
        tenantid = request.args.get('tenantid')
        userid = request.args.get('userid')
        passwordid = request.args.get('passwordid')
        passwordid = urllib.parse.quote_plus(passwordid)
        accountid = request.args.get('accountid')
        dbName = request.args.get('dbName')
        schemaName = request.args.get('schemaName')
        tblName = request.args.get('tblName')
        ctx = snowflake.connector.connect(
            user='gadicloud',
            password='Shekhar@63',
            account='rg54129.west-us-2.azure',
            database=dbName,
            schema=schemaName
        )
        cs = ctx.cursor()
        try:
            # cs.execute("SELECT current_version()")
            # cs.execute("select * from " + tblName)
            cs.execute("Create Table " + tblName)
            one_row = cs.fetchall()
            # print(one_row[0])
            print(one_row)
            listDB = []
            for row in one_row:
                jsonSchema = {}
                jsonSchema["key"] = row[0]
                jsonSchema["keyDataType"] = row[1]
                listDB.append(jsonSchema)

            print(listDB)
            listDB = ["Table Created into SnowFlake Repository by Name : " + tblName]
        finally:
            cs.close()
        ctx.close()
        return jsonify(listDB), 200

    except SyntaxError as SYE:
        print("0000000000000000000000000000")
        outputException = {}
        outputException["Message"] = str(SYE)
        print(outputException)
        return jsonify(outputException), 300
    except Exception as e:
        print("111111111111111111111111111")
        print(e)
        outputException = {}
        outputException["Message"] = str(e)
        print(outputException)
        print("##################################")
        print(jsonify(outputException))
        return jsonify(outputException), 500
    except IOError as ioe:
        print("2222222222222222222222222222")
        print(ioe)
        outputException = {}
        outputException["Message"] = str(ioe)
        print(outputException)
        return jsonify(outputException), 300
    except ConnectionRefusedError as cre:
        print("3333333333333333333333333333")
        outputException = {}
        outputException["Message"] = str(cre)
        print(outputException)
        return jsonify(outputException), 501

@app.route('/snowflakedesctable', methods=['GET', 'POST'])
def connectSNOWFlakeQueryTable():
    try:
        # Gets the version
        tenantid = request.args.get('tenantid')
        userid = request.args.get('userid')
        passwordid = request.args.get('passwordid')
        passwordid = urllib.parse.quote_plus(passwordid)
        accountid = request.args.get('accountid')
        dbName = request.args.get('dbName')
        schemaName = request.args.get('schemaName')
        tblName = request.args.get('tblName')
        ctx = snowflake.connector.connect(
            user='gadicloud',
            password='Shekhar@63',
            account='rg54129.west-us-2.azure',
            database=dbName,
            schema=schemaName
        )
        cs = ctx.cursor()
        try:
            # cs.execute("SELECT current_version()")
            # cs.execute("select * from " + tblName)
            cs.execute("DESCRIBE " + tblName)
            one_row = cs.fetchall()
            # print(one_row[0])
            print(one_row)
            listDB = []
            for row in one_row:
                jsonSchema = {}
                jsonSchema["key"] = row[0]
                jsonSchema["keyDataType"] = row[1]
                listDB.append(jsonSchema)

            print(listDB)
        finally:
            cs.close()
        ctx.close()
        return jsonify(listDB), 200
    except SyntaxError as SYE:
        print("0000000000000000000000000000")
        outputException = {}
        outputException["Message"] = str(SYE)
        print(outputException)
        return jsonify(outputException), 300
    except Exception as e:
        print("111111111111111111111111111")
        print(e)
        outputException = {}
        outputException["Message"] = str(e)
        print(outputException)
        print("##################################")
        print(jsonify(outputException))
        return jsonify(outputException), 500
    except IOError as ioe:
        print("2222222222222222222222222222")
        print(ioe)
        outputException = {}
        outputException["Message"] = str(ioe)
        print(outputException)
        return jsonify(outputException), 300
    except ConnectionRefusedError as cre:
        print("3333333333333333333333333333")
        outputException = {}
        outputException["Message"] = str(cre)
        print(outputException)
        return jsonify(outputException), 501


@app.route('/snowflakeinserttable_bkp', methods=['GET', 'POST'])
def connectSNOWFlakeInsertValues_bkp():
    try:
        # Gets the version
        bodyJSON = request.get_json()
        tenantid = bodyJSON['tenantid']
        userid = bodyJSON['userid']
        passwordid = bodyJSON['passwordid']
        passwordid = urllib.parse.quote_plus(passwordid)
        accountid = bodyJSON['accountid']
        dbName = bodyJSON['dbName']
        schemaName = bodyJSON['schemaName']
        tblName = bodyJSON['tblName']
        jsonStruct = bodyJSON['jsonValue']
        ctx = snowflake.connector.connect(
            user='gadicloud',
            password='Shekhar@63',
            account='rg54129.west-us-2.azure',
            database=dbName,
            schema=schemaName
        )
        cs = ctx.cursor()

        print(jsonStruct)
        print(type(jsonStruct))
        print("8888888888888888888888888888888888888888")
        print(type(jsonStruct))
        print(len(jsonStruct))

        listLength = len(jsonStruct)

        i = 0
        while i < listLength:
            #jsonValue = json.loads(jsonStruct[i])
            jsonValue = jsonStruct[i]
            print(type(jsonValue))
            print((jsonValue))
            try:
                # cs.execute("SELECT current_version()")
                # cs.execute("select * from " + tblName)
                keyData = []
                for keys in jsonValue.keys():
                    keyData.append(keys)

                keyData = str(keyData)
                keyData = keyData.replace("[", "")
                keyData = keyData.replace("]", "")
                keyData = keyData.replace("'", "")
                print(keyData)

                keyValue = []
                for keys in jsonValue.values():
                    keyValue.append(keys)

                keyValue = str(keyValue)
                keyValue = keyValue.replace("[", "")
                keyValue = keyValue.replace("]", "")
                print(keyValue)

                print("insert into " + tblName + " " + "(" + keyData + ")" + " values " + "(" + keyValue + ")")
                # insert into table1 (id, varchar1, variant1) values (4, 'Fourier', parse_json('{ "key1": "value1", "key2": "value2" }'));
                one_row = cs.execute(
                    "insert into " + tblName + " " + "(" + keyData + ")" + " values " + "(" + keyValue + ")")
                print(one_row.timezone)
                listDB = ["Data inserted into SnowFlake Repository"]
                i += 1
            except Exception as EE:
                print(EE)
                print("0000000000000000000000000000")
                outputException = {}
                outputException["Message"] = str(EE)

        cs.close()
        ctx.close()

        return jsonify(listDB), 200
    except SyntaxError as SYE:
        print("0000000000000000000000000000")
        outputException = {}
        outputException["Message"] = str(SYE)
        print(outputException)
        return jsonify(outputException), 300
    except Exception as e:
        print("111111111111111111111111111")
        print(e)
        outputException = {}
        outputException["Message"] = str(e)
        print(outputException)
        print("##################################")
        print(jsonify(outputException))
        return jsonify(outputException), 500
    except IOError as ioe:
        print("2222222222222222222222222222")
        print(ioe)
        outputException = {}
        outputException["Message"] = str(ioe)
        print(outputException)
        return jsonify(outputException), 300
    except ConnectionRefusedError as cre:
        print("3333333333333333333333333333")
        outputException = {}
        outputException["Message"] = str(cre)
        print(outputException)
        return jsonify(outputException), 501





# if __name__ == '__main__':
#     print("SETTING SNOWFLAKE")
#     #mytest()
#     listDB = connectSNOWFlakeDB()
#     print(listDB)
#     print("----------------------------")
#     listSchema = connectSNOWFlakeSchema("SRIDHAR")
#     print(listSchema)
#     print("----------------------------")
#     listTable  = connectSNOWFlakeShowTablesSelection("SRIDHAR","PUBLIC")
#     print(listTable)
#     print("----------------------------")
#     queryTableSchema = connectSNOWFlakeQueryTable("SRIDHAR","PUBLIC","TBLDATA")
#     print(queryTableSchema)
#     print("----------------------------")
#     jsonInsert = {}
#     jsonInsert["AGE"] =  random.randint(0, 85)
#     jsonInsert["NAME"] = names.get_full_name()
#     listVal = []
#     listVal.append(jsonInsert)
#     queryTableSchemaInsert = connectSNOWFlakeInsertValues("SRIDHAR", "PUBLIC", "TBLDATA", jsonInsert)
#     print("----------------------------")

# url = URL(
#     account = 'GC',
#     user = 'GC',
#     database = 'DB',
#     schema = 'PUBLIC',
#     warehouse= 'TEST',
#     role = 'ACCOUNTADMIN',
#     authenticator='externalbrowser',
# )
# engine = create_engine(url)
# connection = engine.connect()



if __name__ == '__main__':
    print("SETTING SNOWFLAKE API")
    app.run(host="localhost", port=5008)
