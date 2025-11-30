'''
Created on Oct 8, 2019
Query data from instructor relation
@author: Yousef
'''
import psycopg2
 
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect("dbname=university user=postgres password=1234")

        # create a cursor
        cur = conn.cursor()
        
        # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT id, name, dept_name FROM instructor')
 
        print("The number of instructors: ", cur.rowcount)
        # fetchone()
        #  fetches the next row in the result set.
        #  It returns a single tuple or None when no more row is available.
        row = cur.fetchone()

        # display the instructors' id, name and dept_name
        while row is not None:
            print(row[0],row[1],row[2], sep ='\t')
            row = cur.fetchone()       
       
       # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
 
 
if __name__ == '__main__':
    connect()