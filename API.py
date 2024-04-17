import os
from flask import Flask, jsonify, make_response, request, send_file
import pyodbc
import SQLFunctions as sql
import sys

app = Flask(__name__)

try:
    sql.conn = sql.mssql_connect()
except Exception as e:
    print("Cannot connect to mssql server!: {}".format(e))
    sys.exit()


@app.route("/getTests", methods=['GET'])
def getTests():
    data = sql.GetTests()
    return make_response(jsonify({"Tests": data}))

@app.route("/getSuccesses", methods=['GET'])
def getSuccesses():
    data = sql.GetSuccesses()
    return make_response(jsonify({"Tests": data}))

@app.route("/getErrors", methods=['GET'])
def getErrors():
    data = sql.GetErrors()
    return make_response(jsonify({"Tests": data}))

if __name__ == '__main__':
    print ("Running API...")
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=10206, debug=True)
    
    app.run()