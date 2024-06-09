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

@app.route("/getSuccessfulTasks", methods=['GET'])
def getSuccessfulTasks():
    TestId = request.args.get('TestId')
    action = request.args.get('action')
    data = sql.getAllSuccessfulTasks(TestId, action)
    if(data):
        return make_response(jsonify({"Tasks": data}), 200)
    else:
        return make_response(jsonify({"Tasks": data}), 404)
    
@app.route("/insertTask", methods=['POST'])
def insertTask():
    request_data = request.get_json()
    if request_data:
        class_bd = request_data.get('class')
        css_selector = request_data.get('css_selector')
        id = request_data.get('id')
        link_text = request_data.get('link_text')
        partial_link_text = request_data.get('partial_link_text')
        name = request_data.get('name')
        tag_name = request_data.get('tag_name')
        xpath = request_data.get('xpath')
        action = request_data.get('action')
        access = request_data.get('access')
        quantity = request_data.get('quantity')
        selector = request_data.get('selector')
        text = request_data.get('text')
        position = request_data.get('position')
        success_id = request_data.get('success_id')
        error_id = request_data.get('error_id')
    data = sql.insertTask(class_bd, css_selector, id, link_text, partial_link_text, name, tag_name, xpath, action, access, quantity, selector, text, position, success_id, error_id)
    if data:
        return make_response(jsonify({"Response": True, "Task": data}), 201)
    else:
        return make_response(jsonify({"Response": False, "Error": "Error inserting Error"}), 400)

if __name__ == '__main__':
    print ("Running API...")
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=10206, debug=True)
    
    app.run()
