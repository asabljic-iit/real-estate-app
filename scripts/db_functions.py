import psycopg2
from flask import session

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
                          'one' for fetchone(), or 
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
        if fetch_mode == 'all':
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
        print(f"DB Operational Error: {e}")
    except Exception as e:
        print(f"General DB Error: {e}")
        
    finally:
        # Clean Up
        if cur: cur.close()
        if conn: conn.close()
        
    # Return None on any failure
    return None


# Login Page Functions
def login_db(email, pswd):
    # Remove when finished implementing login
    if email == "dev@test.com":
        session.clear()
        session['user_id'] = 9999

    try:
        user = None #TODO- lookup user, should return user_id
    except Exception as error:
        return Exception(error)
    
    if user is None:
        return ValueError("Incorrect email.")
    elif pswd is None: #TODO- check pswd
        return ValueError("Incorrect email and/or password.")
    
    session.clear()
    session['user_id'] = None # user['id']

#TODO- return user_id, email name
def get_user(user_id):
    pass

def is_agent(user_id):
    pass


# Register Page Functions
# Both agents and prospective renters can register with an email and personal information.
def register_db(email, pswd):
    if email is None:
        return ValueError("Email is required.")
    elif pswd is None:
        return ValueError("Password is required.")

    try:
        # TODO- insert new user, see db_1.py
        print('todo')
    except Exception as error:
        return Exception(error)

   
# Account Page Functions
# TODO- Renters can add, modify, or delete addresses and credit cards.
#  Billing addresses cannot be deleted before deleting the associated credit card.
# TODO Renter- save info, display saved info (if any), and add rewards program
# TODO Agent- check for agent or renter, then show applicable options
#  (for agents, its job title, agency, contact info (phone num))
def get_account():
    pass

def save_account():
    pass


# Manage Property Page Functions
# TODO- add, manage, delete properties
def get_properties():
    pass

def add_property():
    pass

def edit_property():
    pass

def delete_property():
    pass


# Search Page Functions
def search_properties(street, city, state, zip_code):
    
    # --- Build the Dynamic SQL Query ---
    query = "SELECT property_id, street, city, state, zip_code FROM property WHERE 1=1"
    params = []
    
    if street:
        query += " AND street ILIKE %s"
        params.append(f"%{street}%")
    if city:
        query += " AND city ILIKE %s"
        params.append(f"%{city}%")
    if state:
        query += " AND state ILIKE %s"
        params.append(f"%{state}%")
    if zip_code:
        query += " AND zip_code = %s"
        params.append(zip_code)
    
    return execute_query(query, tuple(params), fetch_mode='all')


# Booking Page Functions
def get_property_details(property_id):

    query = "SELECT * FROM property WHERE property_id = %s"
    
    # Use the core function to execute and fetch one result
    return execute_query(query, (property_id,), fetch_mode='one')

def get_payment_method():
    pass

def save_booking(property_id, user_id):
    query = "INSERT INTO booking (property_id, renter_id, booking_date) VALUES (%s, %s, NOW())"
    params = (property_id, user_id)
    
    # Use the core function to execute and commit
    return execute_query(query, params, fetch_mode='commit')


# Manage Booking Page Functions
def get_bookings():
    pass

def cancel_booking():
    pass