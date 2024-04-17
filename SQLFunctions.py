
#cursor = conn.cursor()
conn = None

def mssql_connect():
    import pyodbc
    #Le cambias el driver al que tienes de sql, agregas el server de SQL y database
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-2SOAT17;DATABASE=POLLOSNARANJA2024;Trusted_Connection=yes')
    return conn

def GetTests():
    import pyodbc
    global conn
    query = "SELECT * FROM Test" 
    try:
        try:
            cursor = conn.cursor()
            cursor.execute(query)
        except Exception as err:
            print("reconnecting...")
            conn = mssql_connect()
            cursor = conn.cursor()
            cursor.execute(query)

        data = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            data.append(dict(zip(columns, row)))
        cursor.close()
        return data
    except Exception as err:
        raise TypeError("sql_read_where:%s" % err)
    
def GetSuccesses():
    import pyodbc
    global conn
    query = "SELECT * FROM Success" 
    try:
        try:
            cursor = conn.cursor()
            cursor.execute(query)
        except Exception as err:
            print("reconnecting...")
            conn = mssql_connect()
            cursor = conn.cursor()
            cursor.execute(query)

        data = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            data.append(dict(zip(columns, row)))
        cursor.close()
        return data
    except Exception as err:
        raise TypeError("sql_read_where:%s" % err)
    
def GetErrors():
    import pyodbc
    global conn
    query = "SELECT * FROM Error" 
    try:
        try:
            cursor = conn.cursor()
            cursor.execute(query)
        except Exception as err:
            print("reconnecting...")
            conn = mssql_connect()
            cursor = conn.cursor()
            cursor.execute(query)

        data = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            data.append(dict(zip(columns, row)))
        cursor.close()
        return data
    except Exception as err:
        raise TypeError("sql_read_where:%s" % err)