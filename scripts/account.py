from scripts.db import execute_query

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

# Credit Card Functions
def get_credit_cards(renter_id):
    query = 'SELECT * FROM CreditCard WHERE renter_id = %s' 
    params = [renter_id]
    return execute_query(query, tuple(params), fetch_mode='all')

def save_credit_card(renter_id, card_number, address_id, expiration_date):
    query = 'INSERT INTO CreditCard (renter_id, credit_card_no, card_address_id, expiration_date) ' \
    'VALUES (%s, %s, %s, %s)'
    params = [renter_id, card_number, address_id, expiration_date]
    return execute_query(query, tuple(params), fetch_mode='commit')

def delete_credit_card(renter_id, card_id):
    query = 'DELETE FROM CreditCard WHERE renter_id = %s AND credit_card_id = %s'
    params = [renter_id, card_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

# Address Functions
def get_addr(user_id):
    query = 'SELECT * FROM UserAddress WHERE user_id = %s' 
    params = [user_id]
    return execute_query(query, tuple(params), fetch_mode='all')

def save_addr(user_id, street, city, state, zip_code):
    query = 'INSERT INTO UserAddress (user_id, street, city, state, zip_code) ' \
    'VALUES (%s, %s, %s, %s, %s)'
    params = [user_id, street, city, state, zip_code]
    return execute_query(query, tuple(params), fetch_mode='commit')

def delete_addr(address_id):
    query = 'DELETE FROM UserAddress WHERE address_id = %s'
    params = [address_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

# Rewards Program Functions
def get_rewards(renter_id):
    query = "SELECT * FROM RewardsProgram WHERE renter_id = %s"
    params = [renter_id]
    return execute_query(query, tuple(params), fetch_mode='one')

def enroll_rewards(renter_id):
    query = "INSERT INTO RewardsProgram (renter_id, points) VALUES (%s, 0)"
    params = [renter_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

def add_rewards_points(renter_id, points):
    query = "UPDATE RewardsProgram SET points = points + %s WHERE renter_id = %s"
    params = [points, renter_id]
    return execute_query(query, tuple(params), fetch_mode='commit')

def redeem_rewards_points(renter_id, points):
    query = "UPDATE RewardsProgram SET points = points - %s WHERE renter_id = %s AND points >= %s"
    params = [points, renter_id, points]
    return execute_query(query, tuple(params), fetch_mode='commit')
