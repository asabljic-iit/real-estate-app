from scripts.db import execute_query

# Manage Property Page Functions
# TODO- add, manage, delete properties
def get_agency_properties(agency): #get properties under agent
    query = """
    SELECT property_id, street, city, state, zip_code, num_rooms, price, description, prop_type
    FROM property 
    WHERE agency = %s
    """
    params = [agency]
    return execute_query(query, tuple(params), fetch_mode='all')

def agency_add_property(agency, neighborhood_id, num_rooms, description, 
                        sq_footage, price, street, city, state, zip_code, 
                        prop_type, building_type, business_type, zoning_type):
    query = """
    INSERT INTO property (agency, neighborhood_id, num_rooms, description, 
    sq_footage, price, street, city, state, zip_code, prop_type) VALUES 
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
    RETURNING property_id
    """
    params = [agency, neighborhood_id, num_rooms, description, 
              sq_footage, price, street, city, state, zip_code, prop_type] 
    prop_id = execute_query(query, tuple(params), fetch_mode='return')

    match prop_type:
        case "House":
            query = """
            INSERT INTO House (house_id) VALUES 
            (%s)
            """
            execute_query(query, tuple([prop_id]), fetch_mode='commit')
        case "Apartment":
            query = """
            INSERT INTO Apartment (apartment_id, building_type) VALUES 
            (%s,%s)
            """
            execute_query(query, tuple([prop_id, building_type]), fetch_mode='commit')
        case "CommercialBuilding":
            query = """
            INSERT INTO CommercialBuilding (building_id, business_type) VALUES 
            (%s, %s)
            """
            execute_query(query, tuple([prop_id, business_type]), fetch_mode='commit')
        case "VacationHome":  
            query = """
            INSERT INTO VacationHome (home_id) VALUES 
            (%s)
            """
            execute_query(query, tuple([prop_id]), fetch_mode='commit')
        case "Land":
            query = """
            INSERT INTO Land (land_id, zoning_type) VALUES 
            (%s, %s)
            """
            execute_query(query, tuple([prop_id, zoning_type]), fetch_mode='commit')
        case _:
            raise ValueError(f"Warning: No property type provided to add property_id={prop_id}.")
    
    return True

def agency_edit_property(agency, property_id, num_rooms, description, price):
    
    update_attributes = {
        'num_rooms': num_rooms,
        'description': description, 
        'price': price
    }

    updates = []
    params = []

    for column, value in update_attributes.items():
        if value:
            updates.append(f"{column}=%s")
            params.append(value)

    if not updates:
        raise ValueError(f"Warning: No fields provided to update property_id={property_id}.")

    set_clause = ", ".join(updates)
    
    query = f"""
    UPDATE property 
    SET {set_clause} 
    WHERE agency=%s AND property_id=%s
    """
    params.append(agency)
    params.append(property_id)
    return execute_query(query, tuple(params), fetch_mode='commit')

def agency_delete_property(agency, property_id):
    query = 'DELETE FROM property WHERE agency=%s AND property_id=%s'
    params = [agency, property_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

def update_availability(property_id, availability):
    query = 'UPDATE property SET availability=%s WHERE property_id=%s'
    params = [availability, property_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

# Search Page Functions
def search_properties(street, city, state, zip_code, num_rooms, price_min, 
                      price_max, prop_type, desired_date, sort_by=None):
    
    query = """
    SELECT property_id, street, city, state, zip_code, description, prop_type, 
    num_rooms, price, availability FROM property 
    WHERE 1=1
    """
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
    if (desired_date):
        query += """ 
        AND property_id NOT IN (
            SELECT property_id FROM Booking 
            WHERE %s BETWEEN start_date AND end_date
        )"""
        params.append(desired_date)
        
    if sort_by == 'price_asc': 
        query += " ORDER BY price ASC"
    elif sort_by == 'price_desc':
        query += " ORDER BY price DESC"
    elif sort_by == 'num_rooms_asc':
        query += " ORDER BY num_rooms ASC"
    elif sort_by == 'num_rooms_desc':
        query += " ORDER BY num_rooms DESC"
    return execute_query(query, tuple(params), fetch_mode='all')

def get_random_properties():
    query = """
    SELECT property_id, street, city, state, description, prop_type, price, num_rooms
    FROM Property 
    WHERE availability IS TRUE 
    ORDER BY RANDOM() LIMIT 4
    """
    params = []
    return execute_query(query, tuple(params), fetch_mode='all')

# Booking Page Functions
def get_property_details(property_id):

    query = """
    SELECT * FROM Property P 
    JOIN Neighborhood N ON N.neighborhood_id = P.neighborhood_id 
    FULL JOIN Apartment A ON A.apartment_id = P.property_id 
    FULL JOIN CommercialBuilding C ON C.building_id = P.property_id
    FULL JOIN Land L ON L.land_id = P.property_id
    WHERE P.property_id = %s
    """
    params = [property_id]
    
    # Use the core function to execute and fetch one result
    return execute_query(query, tuple(params), fetch_mode='one')