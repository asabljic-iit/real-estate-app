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
        print(f"DB Operational Error: {e}")
        raise e
    except Exception as e:
        print(f"General DB Error: {e}")
        raise e
        
    finally:
        # Clean Up
        if cur: cur.close()
        if conn: conn.close()
    
    return None


# Register Page Functions
# Both agents and prospective renters can register with an email and personal information.
def register_user(agency, email, name, pswd):
    """Register user. W"""

    if email is None:
        raise ValueError("Email is required.")
    elif pswd is None:
        raise ValueError("Password is required.")
    
    query = 'INSERT INTO Users (email_address, name, password) ' \
    'VALUES (%s, %s, %s) RETURNING user_id'
    params = [email, name, pswd]    
    new_user_id = execute_query(query, tuple(params), fetch_mode='return')

    if agency:
        query = 'INSERT INTO Agent (agent_id, agency) ' \
        'VALUES (%s, %s)'   
        execute_query(query, tuple([new_user_id, agency]), fetch_mode='commit')
    else:
        query = 'INSERT INTO Renter (renter_id) ' \
        'VALUES (%s)'   
        execute_query(query, tuple([new_user_id]), fetch_mode='commit')

    return True


# Login Page Functions
def login_user(email, pswd):
    """
    desc

    Args:
        a

    Return:
        a
    """

    query = "SELECT * FROM users WHERE email_address=%s"
    user = execute_query(query, tuple([email]), fetch_mode='one')
    
    if user is None:
        raise ValueError("Incorrect email.")
    elif not user["password"] == pswd:
        raise ValueError("Incorrect email and/or password.")
    
    session.clear()
    session['user_id'] = user['user_id']

    return True

def get_user(user_id):
    """
    Get user_id, name, and agency from user.

    Args:
        user_id

    Returns:
        dict
    """
    query = "SELECT user_id, name, agency FROM Users LEFT JOIN Agent ON agent_id=user_id WHERE user_id=%s"
    return execute_query(query, tuple([user_id]), fetch_mode='one')


def get_agency(agent_id):
    query = "SELECT agency FROM agent"
    params = [agent_id]
    return execute_query(query, tuple(params), fetch_mode='one')

   
# Account Page Functions
# TODO- Renters can add, modify, or delete addresses and credit cards.
#  Billing addresses cannot be deleted before deleting the associated credit card.
# TODO Renter- save info, display saved info (if any), and add rewards program
# TODO Agent- check for agent or renter, then show applicable options
#  (for agents, its job title, agency, contact info (phone num))
def get_account(user_id):
    query = 'SELECT * FROM Users FULL JOIN Renter ON renter_id = user_id FULL JOIN Agent ON agent_id=user_id WHERE user_id = %s'
    params = [user_id]
    return execute_query(query, tuple(params), fetch_mode = 'one')

def save_renter_prefs(renter_id, desired_move_in_date, preferred_location, budget):
    query = 'UPDATE Renter SET desired_move_in_date = %s, preferred_location = %s, budget = %s WHERE renter_id = %s'
    params = [desired_move_in_date, preferred_location, budget, renter_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

def save_agent_details(agent_id, agency, job_title, phone_number):
    query = 'UPDATE Agent SET agency = %s, job_title = %s, phone_number = %s WHERE agent_id = %s'
    params = [agency, job_title, phone_number, agent_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

def get_CCN(renter_id):
    query = 'SELECT * FROM CreditCard WHERE renter_id = %s;' 
    params = [renter_id]
    return execute_query(query, tuple(params), fetch_mode='all')

def save_CCN(renter_id, card_number, expiration_date):
    query = 'INSERT INTO CreditCard (credit_card_no, user_id, expiration_date) ' \
    'VALUES (%s, %s, %s)'
    params = [card_number, renter_id, expiration_date]
    return execute_query(query, tuple(params), fetch_mode='commit')

def get_addr(user_id):
    query = 'SELECT * FROM UserAddress WHERE user_id = %s;' 
    params = [user_id]
    return execute_query(query, tuple(params), fetch_mode='all')

def save_addr(user_id, street, city, state, zip_code):
    query = 'INSERT INTO UserAddress (user_id, street, city, state, zip_code) ' \
    'VALUES (%s, %s, %s, %s, %s)'
    params = [user_id, street, city, state, zip_code]
    return execute_query(query, tuple(params), fetch_mode='commit')

# Manage Property Page Functions
# TODO- add, manage, delete properties
def get_properties(agent_id): #get properties under agent
    query = "SELECT property_id, street, city, state, zip_code FROM property p JOIN agent a ON a.agency = p.agency WHERE agent_id = %s"
    params = [agent_id]
    return execute_query(query, tuple(params), fetch_mode='all')

def add_property(agency, neighborhood_id, location, num_rooms, description, sq_footage, price, street, city, state, zip_code):
    query = 'INSERT INTO property (agency, neighborhood_id, location, num_rooms, description, sq_footage, price, street, city, state, zip_code) ' \
    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    params = [agency, neighborhood_id, location, num_rooms, description, sq_footage, price, street, city, state, zip_code]    
    execute_query(query, tuple(params), fetch_mode='commit')
    
    return True

def edit_property(property_id, agency, neighborhood_id, location, num_rooms, description, sq_footage, price, street, city, state, zip_code):
    query = 'UPDATE property SET agency=%s, neighborhood_id=%s, location=%s, num_rooms=%s, description=%s, sq_footage=%s, price=%s, street=%s, city=%s, state=%s, zip_code=%s WHERE property_id=%s'
    params = [agency, neighborhood_id, location, num_rooms, description, sq_footage, price, street, city, state, zip_code, property_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

def delete_property(property_id):
    query = 'DELETE FROM property WHERE property_id=%s'
    params = [property_id]
    return execute_query(query, tuple(params), fetch_mode='commit')


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
    return execute_query(query, tuple([property_id]), fetch_mode='one')

def save_booking(property_id, user_id):
    query = "INSERT INTO booking (property_id, renter_id, booking_date) VALUES (%s, %s, NOW())"
    params = [property_id, user_id]
    
    # Use the core function to execute and commit
    execute_query(query, tuple(params), fetch_mode='commit')

    return True


# Manage Booking Page Functions
def get_bookings():
    pass

def cancel_booking():
    pass

def random_properties():
    query = "Select * FROM Property ORDER BY RANDOM() LIMIT 4"
    params = []
    return execute_query(query, tuple(params), fetch_mode='all')

# Rewards Program Functions
def get_rewards(renter_id):
    pass