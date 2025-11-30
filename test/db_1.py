import psycopg2

def PyhtonDBExample(id,passwd):
    conn = None
    try:
        # connect to the Database
        conn = psycopg2.connect(host="localhost", database="university", user=id, password=passwd)
        # cursor
        cur = conn.cursor()
        try:
            # Pyhton equivalent of JDBC prepared statement, with parameters identified in the SQL query by "%s" 
            # and parameter values provided as a list
            cur.execute("insert into instructor values(%s,%s,%s,%s)", ("12345","Alice","Physics",98000))
        
            # Updates are not commited to teh DB automatically; hence commit() is needed to commit an update
            conn.commit()
        except Exception as e:
            print("Could not insert tuple", e)
            conn.rollback()
        cur.execute("select dept_name, avg(salary)"
                "from instructor group by dept_name")
        for dept in cur:
            print (dept[0], dept[1])
        cur.close()

    except Exception as e:
        print("Exception: ",e)
    finally:
        if conn is not None:
            # Close the Connection
            conn.close()
            print("DB connection closed.")

if __name__=='__main__':
    PyhtonDBExample("postgres","1234")
