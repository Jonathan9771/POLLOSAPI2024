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


@app.route("/")
def hello_world():
    return "POLLOS A LA NARANJA API, NARANJA Y EL POLLO, LAS BASES DE TODA VIDA DIGNA"

if __name__ == '__main__':
    print ("Running API...")
    #app.run(host='0.0.0.0', port=10206, debug=True)
    
    app.run()