from scripts.db import execute_query
from scripts.property import *

# Booking Page Functions
def save_booking(renter_id, property_id, start_date, end_date):
    query = "INSERT INTO booking (renter_id, property_id, start_date, end_date) VALUES (%s, %s, %s, %s)"
    params = [renter_id, property_id, start_date, end_date]
    
    # Use the core function to execute and commit
    execute_query(query, tuple(params), fetch_mode='commit')
    update_availability(property_id, False)

    return True

# Manage Booking Page Functions
def get_renter_bookings(renter_id, agency=None):
    #agent is needed to get bookings under an agency
    if agency is None:
        query = "SELECT * FROM Booking WHERE renter_id = %s ORDER BY start_date DESC"
        params = [renter_id]
        return execute_query(query, tuple(params), fetch_mode='all')
    
    query = "SELECT B.* FROM Booking AS B INNER JOIN Property AS P ON B.property_id = P.property_id WHERE agency = %s ORDER BY start_date DESC"
    params = [agency]
    return execute_query(query, tuple(params), fetch_mode='all')

def cancel_booking(renter_id, booking_id, property_id, agency=None): 
    #agent is needed if an agent is canceling the booking
    if agency is None:
        query = "DELETE FROM Booking WHERE renter_id = %s AND booking_id = %s"
        params = [renter_id, booking_id]
        
        execute_query(query, tuple(params), fetch_mode='commit')
        update_availability(property_id, True)

        return True

    query = "DELETE FROM Booking AS B USING Property AS P WHERE B.property_id = P.property_id AND B.booking_id = %s AND B.property_id = %s AND P.agency = %s"
    params = [booking_id, property_id, agency]
    
    execute_query(query, tuple(params), fetch_mode='commit')
    update_availability(property_id, True)

    return True

def edit_booking(renter_id, booking_id, new_start_date, new_end_date, agency=None):
    if agency is None:
        query = "UPDATE Booking SET start_date = %s, end_date = %s WHERE renter_id = %s AND booking_id = %s"
        params = [new_start_date, new_end_date, renter_id, booking_id]
        
        execute_query(query, tuple(params), fetch_mode='commit')
        return True
    
    query = "UPDATE Booking AS B SET start_date = %s, end_date = %s FROM Property AS P WHERE B.property_id = P.property_id AND B.booking_id = %s AND P.agency = %s"
    params = [new_start_date, new_end_date, booking_id, agency]
    
    execute_query(query, tuple(params), fetch_mode='commit')
    return True