
#cursor = conn.cursor()
conn = None

def pgsql_connect():
    import psycopg2
    conn = psycopg2.connect(
            dbname="pollosampleDB",
            user="postgres",
            password="pollosbase2024",
            host="pollos-cloud.c920ce4ysda2.us-west-1.rds.amazonaws.com",
            port="5432"
        )
    return conn

def execute_query(query, params=None, fetch=True):
    global conn
    import psycopg2
    import psycopg2.extras

    def reconnect():
        global conn
        print("Reconnecting...")
        conn = pgsql_connect()
    
    try:
        if conn is None or conn.closed != 0:
            reconnect()
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(query, params)
        
        if fetch:
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return [dict(zip(columns, row)) for row in data]
        else:
            if "RETURNING" in query:
                data = cursor.fetchone()
                columns = [desc[0] for desc in cursor.description]
                cursor.close()
                conn.commit()
                return dict(zip(columns, data))
            else:
                conn.commit()
                cursor.close()
                return True
    except psycopg2.IntegrityError as err:
        print("Integrity error:", err)
        conn.rollback()  # Rollback the transaction to reset the connection state
        return None
    except (psycopg2.InterfaceError, psycopg2.DatabaseError) as err:
        print(f"Database error: {err}")
        conn.rollback()  # Rollback the transaction to reset the connection state
        reconnect()
        return execute_query(query, params, fetch)
    except Exception as err:
        conn.rollback()  # Rollback the transaction to reset the connection state
        raise TypeError("sql_read_where:%s" % err)



def getTests():
    query = "SELECT * FROM Test"
    return execute_query(query)

    
def getSuccesses():
    query = "SELECT * FROM Success"
    return execute_query(query)

    
def getErrors():
    query = "SELECT * FROM Error"
    return execute_query(query)

    

def getTestById(Id):
    query = "SELECT * FROM Test WHERE Id = %s"
    return execute_query(query, (Id,))

    
def insertTest(Id, Webpage, Browser):
    query = "INSERT INTO Test (Id, webpage, timecreated, browser) VALUES (%s, %s, CURRENT_TIMESTAMP, %s) RETURNING *"
    return execute_query(query, (Id, Webpage, Browser), fetch=False)

    
def insertSuccess(TestId, Steps):
    query_check = "SELECT Id FROM Test WHERE Id = %s"
    if execute_query(query_check, (TestId,)):
        query_insert = "INSERT INTO Success (TestId, Timecreated, Steps) VALUES (%s, CURRENT_TIMESTAMP, %s) RETURNING *"
        return execute_query(query_insert, (TestId, Steps), fetch=False)
    else:
        return False

def insertError(TestId, EType, Steps):
    query_check = "SELECT Id FROM Test WHERE Id = %s"
    if execute_query(query_check, (TestId,)):
        query_insert = "INSERT INTO Error (TestId, EType, Timecreated, Steps) VALUES (%s, %s, CURRENT_TIMESTAMP, %s) RETURNING *"
        return execute_query(query_insert, (TestId, EType, Steps), fetch=False)
    else:
        return False

def getTestHistory(TestId):
    query = """
    SELECT Id, Timecreated, 'Failed' as Status, Steps, EType FROM Error WHERE TestId = %s
    UNION 
    SELECT Id, Timecreated, 'Completed' as Status, Steps, NULL as EType FROM Success WHERE TestId = %s 
    ORDER BY Timecreated;
    """
    return execute_query(query, (TestId, TestId))

def insertTask(class_bd, css_selector, id, link_text, partial_link_text, name, tag_name, xpath, action, access, quantity, selector, text, position, success_id, error_id):
    if (success_id):
        Tablename = 'Success'
        TableId = success_id
    else:
        Tablename = 'Error'
        TableId = error_id
    
    query_check = f"SELECT Id FROM {Tablename} WHERE Id = %s"
    if execute_query(query_check, (TableId,)):
        query_insert = "INSERT INTO Tasks (class, css_selector, id, link_text, partial_link_text, name, tag_name, xpath, action, access, quantity, selector, text, position, SuccessId, ErrorId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *"

        return execute_query(query_insert, (class_bd, css_selector, id, link_text, partial_link_text, name, tag_name, xpath, action, access, quantity, selector, text, position, success_id, error_id), fetch=False)
    else:
        return False
    
def getAllSuccessfulTasks(TestId, action):
    query = "SELECT * FROM Tasks T JOIN Success S ON T.SuccessId = S.id WHERE T.SuccessId IS NOT NULL AND S.TestId = %s AND action = %s"
    return execute_query(query, (TestId, action))
