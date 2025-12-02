from scripts.db import execute_query

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

def property_availability(property_id, availability):
    query = 'UPDATE property SET availability=%s WHERE property_id=%s'
    params = [availability, property_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

# Search Page Functions
def search_properties(street, city, state, zip_code, 
                      num_rooms, price_min, price_max, prop_type, desired_date):
    
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
    if num_rooms:
        query += " AND num_rooms = %s"
        params.append(num_rooms)
    if prop_type: 
        query += " AND prop_type = %s"
        params.append(prop_type)
    if price_min:
        query += " AND price >= %s"
        params.append(price_min)
    if (price_min and price_max and price_min <= price_max) or (
        price_max and not price_min): 
        query += " AND price <= %s"
        params.append(price_max)            
    
    return execute_query(query, tuple(params), fetch_mode='all')

def get_random_properties():
    query = "Select property_id, street, state, description, price, prop_type FROM Property WHERE availability IS TRUE ORDER BY RANDOM() LIMIT 4"
    params = []
    return execute_query(query, tuple(params), fetch_mode='all')

# Booking Page Functions
def get_property_details(property_id):

    query = "SELECT * FROM property WHERE property_id = %s"
    
    # Use the core function to execute and fetch one result
    return execute_query(query, tuple([property_id]), fetch_mode='one')