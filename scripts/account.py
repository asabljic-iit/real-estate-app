from scripts.db import execute_query

# Account Page Functions
def get_account(user_id):
    query = """
    SELECT * FROM Users 
    FULL JOIN Renter ON renter_id = user_id 
    FULL JOIN Agent ON agent_id=user_id 
    WHERE user_id = %s
    """
    params = [user_id]
    return execute_query(query, tuple(params), fetch_mode = 'one')

def save_renter_prefs(renter_id, desired_move_in_date, preferred_location, budget):
    update_attributes = {
        'desired_move_in_date': desired_move_in_date,
        'preferred_location': preferred_location, 
        'budget': budget 
    }
    updates = []
    params = []

    for column, value in update_attributes.items():
        if value:
            updates.append(f"{column} = %s")
            params.append(value)
    set_clause = ", ".join(updates)

    query = f"""
    UPDATE Renter 
    SET {set_clause}
    WHERE renter_id = %s
    """
    params.append(renter_id)
    return execute_query(query, tuple(params), fetch_mode='commit')

def save_agent_details(agent_id, agency, job_title, phone_number):
    query = """
    UPDATE Agent 
    SET agency = %s, job_title = %s, phone_number = %s WHERE agent_id = %s
    """
    params = [agency, job_title, phone_number, agent_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

# Credit Card Functions
def get_credit_cards(renter_id):
    query = """
    SELECT * FROM CreditCard 
    WHERE renter_id = %s
    """
    params = [renter_id]
    return execute_query(query, tuple(params), fetch_mode='all')

def save_credit_card(renter_id, card_number, address_id, expiration_date):
    query = """
    INSERT INTO CreditCard (renter_id, credit_card_no, 
    card_address_id, expiration_date) VALUES 
    (%s, %s, %s, %s) 
    RETURNING credit_card_id
    """
    params = [renter_id, card_number, address_id, expiration_date]
    credit_card_id = execute_query(query, tuple(params), fetch_mode='return')
    return credit_card_id

def delete_credit_card(renter_id, card_id):
    query = """
    DELETE FROM CreditCard 
    WHERE renter_id = %s AND credit_card_id = %s
    """
    params = [renter_id, card_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

def edit_credit_card(renter_id, card_id, card_number, expiration_date):
    query = """
    UPDATE CreditCard 
    SET credit_card_no = %s, expiration_date = %s
    WHERE renter_id = %s AND credit_card_id = %s
    """
    params = [card_number, expiration_date, renter_id, card_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

# Address Functions
def get_addr(user_id):
    query = """
    SELECT * FROM UserAddress 
    WHERE user_id = %s
    """
    params = [user_id]
    return execute_query(query, tuple(params), fetch_mode='all')

def save_addr(user_id, street, city, state, zip_code):
    query = """
    INSERT INTO UserAddress (user_id, street, city, state, zip_code) VALUES 
    (%s, %s, %s, %s, %s)
    RETURNING address_id
    """
    params = [user_id, street, city, state, zip_code]
    address_id = execute_query(query, tuple(params), fetch_mode='return')
    return address_id

def delete_addr(address_id):
    query = """
    DELETE FROM UserAddress 
    WHERE address_id = %s
    """
    params = [address_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

# Rewards Program Functions
def get_rewards(renter_id):
    query = """
    SELECT * FROM Rewards
    WHERE renter_id = %s
    """
    params = [renter_id]
    return execute_query(query, tuple(params), fetch_mode='one')

def enroll_rewards(renter_id):
    query = """
    UPDATE Rewards
    SET activated = true
    WHERE renter_id = %s
    """
    params = [renter_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

def add_rewards_points(renter_id, points):
    query = """
    UPDATE Rewards 
    SET total_points = total_points + %s 
    WHERE renter_id = %s
    """
    params = [points, renter_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

def redeem_rewards_points(renter_id, total_points):
    query = """
    UPDATE Rewards 
    SET total_points = total_points - %s
    WHERE renter_id = %s
    """
    params = [total_points, renter_id]
    return execute_query(query, tuple(params), fetch_mode='commit')