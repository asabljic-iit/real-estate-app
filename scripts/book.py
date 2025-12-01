from scripts.db import execute_query

# Booking Page Functions
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