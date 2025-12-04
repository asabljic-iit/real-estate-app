import psycopg2

# --- Database Credentials ---
DB_HOST = 'localhost'
DB_NAME = 'real-estate'
DB_USER = 'postgres'
DB_PASSWORD = '1234'

def execute_query(query, params=None, fetch_mode='all'):
    """
    Connects to the DB, executes a query, and returns results based on fetch_mode.
    
    Args:
        query (str): The SQL query string.
        params (tuple/list): Parameters to safely substitute into the query.
        fetch_mode (str): 'all' for fetchall(), 
                          'one' for fetchone() (as dict), or 
                          'return' for fetchone()[0] (for RETURNING), or
                          'commit' for non-SELECT queries.
        
    Returns:
        tuple or dict: Query results (or None for 'commit').
    """
    conn = None
    cur = None
    results = None
    
    try:
        # Establish Connection
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, 
                                user=DB_USER, password=DB_PASSWORD)
        cur = conn.cursor()

        # Execute Query
        cur.execute(query, params)
        
        # Handle Fetching or Commit
        if fetch_mode == 'return':
            row = cur.fetchone()
            conn.commit()
            if row:
                return row[0]  # Return the first column value (e.g., the ID)
            return None
        elif fetch_mode == 'all':
            results = cur.fetchall()
            headers = [desc[0] for desc in cur.description]
            return headers, results
        elif fetch_mode == 'one':
            # Returns a single row
            row = cur.fetchone()
            if row:
                headers = [desc[0] for desc in cur.description]
                # Returns a dictionary for easy template access
                return dict(zip(headers, row)) 
            return None
        elif fetch_mode == 'commit':
            conn.commit()
            # Indicate success for INSERT/UPDATE/DELETE
            return True 
        
    except psycopg2.OperationalError as e:
        print(f"DB Operational Error: {str(e)}")
        raise e
    except Exception as e:
        print(f"General DB Error: {str(e)}")
        raise e
        
    finally:
        # Clean Up
        if cur: cur.close()
        if conn: conn.close()
    
    return None