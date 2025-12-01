from scripts.db import execute_query
from flask import session

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
    """desc"""

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
    """Get user_id, name, and agency from user."""
    
    query = "SELECT user_id, name, agency FROM Users LEFT JOIN Agent ON agent_id=user_id WHERE user_id=%s"
    return execute_query(query, tuple([user_id]), fetch_mode='one')


def get_agency(agent_id):
    query = "SELECT agency FROM agent"
    params = [agent_id]
    return execute_query(query, tuple(params), fetch_mode='one')