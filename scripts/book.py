from scripts.db import execute_query
from scripts.property import *

# Booking Page Functions
def save_booking(property_id, user_id, start_date, end_date):
    query = "INSERT INTO booking (property_id, renter_id, start_date, end_date) VALUES (%s, %s, %s, %s)"
    params = [property_id, user_id, start_date, end_date]
    
    # Use the core function to execute and commit
    execute_query(query, tuple(params), fetch_mode='commit')
    update_availability(property_id,False)

    return True


# Manage Booking Page Functions
def get_bookings(renter_id):
    query = "SELECT * FROM Booking WHERE renter_id = %s ORDER BY booking_date, start_date DESC"
    params = [renter_id]
    return execute_query(query, tuple(params), fetch_mode='all')

def cancel_booking(booking_id):
    query = "DELETE FROM Booking WHERE booking_id = %s"
    params = [booking_id]
    return execute_query(query, tuple(params), fetch_mode='commit')