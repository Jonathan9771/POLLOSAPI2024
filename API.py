import os
from flask import Flask, jsonify, make_response, request, send_file
import pyodbc
import SQLFunctions as sql
import sys
import SeleniumFunctions as SF
from flask_cors import CORS, cross_origin
import pandas as pd
from io import BytesIO
import re

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


try:
    sql.conn = sql.pgsql_connect()
except Exception as e:
    print("Cannot connect to postgres server!: {}".format(e))
    sys.exit()

@app.route("/makeTest", methods=['POST'])
def makeTest():
    request_data = request.get_json()
    if request_data:
        url = request_data.get('url')
        tasks = request_data.get('tasks')
        ip = request_data.get('ip')
    if not url:
        return make_response(jsonify({"error": "Missing url in request"}), 400)
    elif not ip:
        return make_response(jsonify({"error": "Missing ip in request"}), 400)
    result, response = SF.testing(url, ip, tasks)
    if (result['EType'] == "Success"):
        return make_response(jsonify({'Results': result['EType'], 'Success': response}), 200)
    else:
        return make_response(jsonify({'Results': result['EType'], 'Success': response}), 400)

@app.route("/getTests", methods=['GET'])
def getTests():
    data = sql.getTests()
    if(data):
        return make_response(jsonify({"Tests": data}), 200)
    else:
        return make_response(jsonify({"Tests": data}), 404)

@app.route("/getSuccesses", methods=['GET'])
def getSuccesses():
    data = sql.getSuccesses()
    if(data):
        return make_response(jsonify({"Successes": data}), 200)
    else:
        return make_response(jsonify({"Successes": data}), 404)

@app.route("/getErrors", methods=['GET'])
def getErrors():
    data = sql.getErrors()
    if(data):
        return make_response(jsonify({"Errors": data}), 200)
    else:
        return make_response(jsonify({"Errors": data}), 404)

@app.route("/getTestById", methods=['GET'])
def getTestById():
    Id = request.args.get('Id', None)
    data = sql.getTestById(Id)
    if(data):
        return make_response(jsonify({"Test": data}), 200)
    else:
        return make_response(jsonify({"Test": data}), 404)

@app.route("/insertTest", methods=['POST'])
def insertTest():
    request_data = request.get_json()
    if request_data:
        ip = request_data.get('IP')
        url = request_data.get('Webpage')
        browser = request_data.get('Browser')
    Id = ip + ":" + url
    data = sql.insertTest(Id, url, browser)
    if data:
        return make_response(jsonify({"Response": True, "Test": data}), 201)
    else:
        return make_response(jsonify({"Response": False, "Error": "Error inserting Test"}), 400)
    

@app.route("/insertSuccess", methods=['POST'])
def insertSuccess():
    request_data = request.get_json()
    if request_data:
        TestId = request_data.get('TestId')
        Steps = request_data.get('Steps')
    data = sql.insertSuccess(TestId, Steps)
    if data:
        return make_response(jsonify({"Response": True, "Success": data}), 201)
    else:
        return make_response(jsonify({"Response": False, "Error": "Error inserting Success"}), 400)

@app.route("/insertError", methods=['POST'])
def insertError():
    request_data = request.get_json()
    if request_data:
        TestId = request_data.get('TestId')
        EType = request_data.get('EType')
        Steps = request_data.get('Steps')
    data = sql.insertError(TestId, EType, Steps)
    if data:
        return make_response(jsonify({"Response": True, "Error": data}), 201)
    else:
        return make_response(jsonify({"Response": False, "Error": "Error inserting Error"}), 400)

@app.route("/getHistory", methods=['GET'])
def getHistory():
    from urllib.parse import unquote
    TestId = request.args.get('TestId')
    decoded_TestId = unquote(TestId)
    data = sql.getTestHistory(decoded_TestId)
    if(data):
        return make_response(jsonify({"History": data}), 200)
    else:
        return make_response(jsonify({"History": data}), 404)

if __name__ == '__main__':
    print ("Running API...")
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=10206, debug=True)
    
    app.run()
