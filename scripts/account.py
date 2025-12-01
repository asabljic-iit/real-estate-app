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

# Rewards Program Functions
def get_rewards(renter_id):
    pass