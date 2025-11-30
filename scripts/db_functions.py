import psycopg2
from flask import session

# --- Database Credentials ---
DB_HOST = 'localhost'
DB_NAME = 'real-estate'
DB_USER = 'postgres'
DB_PASSWORD = '1234'

#TODO? add easier way to query db with a function


# Login Page Functions
def login_db(email, pswd):
    if email == "dev@test.com": # remove when finished implementing login
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
# TODO- Renters can add, modify, or delete addresses and credit cards. Billing addresses cannot be deleted before deleting the associated credit card.
# TODO Renter- save info, display saved info (if any), and add rewards program
# TODO Agent- check for agent or renter, then show applicable options (for agents, its job title, agency, contact info (phone num))
def get_account_db():
    pass

def save_account_db():
    pass


# Manage Property Page Functions
# TODO- add, manage, delete properties
def get_properties_db():
    pass

def add_property_db():
    pass

def edit_property_db():
    pass

def delete_property_db():
    pass


# Search Page Functions
def search_properties_db(street, city, state, zip_code):
    conn = None
    cur = None
    results = []
    headers = []
    
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = conn.cursor()
        
        # --- Build the Dynamic SQL Query ---
        query = "SELECT street, city, state, zip_code FROM property WHERE 1=1"
        params = []
        
        # Check for and append filters for non-empty search fields
        if street:
            query += " AND street ILIKE %s" # ILIKE for case-insensitive search
            params.append(f"%{street}%")
        if city:
            query += " AND city ILIKE %s"
            params.append(f"%{city}%")
        if state:
            query += " AND state ILIKE %s"
            params.append(f"%{state}%")
        if zip_code:
            query += " AND zip_code = %s" # = for exact zip match
            params.append(zip_code)
        
        cur.execute(query, tuple(params))
        
        headers = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        return headers, results

    except Exception as e:
        print(f"Error searching properties: {e}")
        return [], []
        
    finally:
        if cur: cur.close()
        if conn: conn.close()


# Booking Page Functions
def get_payment_method():
    pass

def save_booking():
    pass


# Manage Booking Page Functions
def get_bookings():
    pass

def cancel_booking():
    pass





# TEST FUNCTIONS
def get_all_users():
    """Connects to the real-estate database and returns all rows from the users table."""
    conn = None
    cur = None
    users_data = []
    column_names = []
    
    try:
        # Establish Connection
        conn = psycopg2.connect(
            host=DB_HOST, 
            database=DB_NAME,
            user=DB_USER, 
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # Execute Query
        cur.execute("SELECT * FROM users ORDER BY user_id ASC")
        
        # Get column names for the table header
        column_names = [desc[0] for desc in cur.description]

        # Fetch all rows
        users_data = cur.fetchall()
        
        return column_names, users_data

    except psycopg2.OperationalError as e:
        print(f"Connection Error in get_all_users: {e}")
        return [], [] # Return empty lists on failure
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [], []
        
    finally:
        # Clean Up
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

# Example usage (will not run in the final web app)
# headers, data = get_all_users()
# print(headers)
# print(data)
# print('done')

def get_all_properties():
    """Connects to the real-estate database and returns all rows from the properties table."""
    conn = None
    cur = None
    properties_data = []
    column_names = []
    
    try:
        # Establish connection (using existing DB_HOST, DB_NAME, etc.)
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cur = conn.cursor()

        # Execute Query for the new table
        cur.execute("SELECT * FROM property ORDER BY property_id ASC")
        
        column_names = [desc[0] for desc in cur.description]
        properties_data = cur.fetchall()
        
        return column_names, properties_data

    except Exception as e:
        print(f"Error getting properties: {e}")
        return [], []
        
    finally:
        if cur: cur.close()
        if conn: conn.close()

# headers, data = get_all_properties()
# print(headers)
# print(data)