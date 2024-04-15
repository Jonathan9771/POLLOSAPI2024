
#cursor = conn.cursor()
conn = None

def mssql_connect():
    import pyodbc
    #Le cambias el driver al que tienes de sql, agregas el server de SQL y database
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=;DATABASE=;Trusted_Connection=yes')
    return conn
