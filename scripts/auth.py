from scripts.db import execute_query
from flask import session

# Register Page Functions
def register_user(agency, email, name, pswd):
    """Register user."""

    if email is None:
        raise ValueError("Email is required.")
    elif pswd is None:
        raise ValueError("Password is required.")
    
    query = """
    INSERT INTO Users (email_address, name, password) VALUES 
    (%s, %s, %s)
    RETURNING user_id
    """
    params = [email, name, pswd]    
    new_user_id = execute_query(query, tuple(params), fetch_mode='return')

    if agency:
        query = """
        INSERT INTO Agent (agent_id, agency) VALUES 
        (%s, %s)
        """
        execute_query(query, tuple([new_user_id, agency]), fetch_mode='commit')
    else:
        query = """INSERT INTO Renter (renter_id) VALUES 
        (%s)
        """
        execute_query(query, tuple([new_user_id]), fetch_mode='commit')
        query = """
        INSERT INTO Rewards (renter_id) VALUES 
        (%s)
        """
        execute_query(query, tuple([new_user_id]), fetch_mode='commit')

    return True


# Login Page Functions
def login_user(email, pswd):
    """Login user."""

    query = """
    SELECT * FROM Users 
    WHERE email_address=%s
    """
    user = execute_query(query, tuple([email]), fetch_mode='one')
    
    if user is None:
        raise ValueError("Incorrect email.")
    elif not user["password"] == pswd:
        raise ValueError("Incorrect email and/or password.")
    
    session.clear()
    session['user_id'] = user['user_id']

    return True

def get_user(user_id):
    """Get user_id, name, agency, activated from user."""
    
    query = """
    SELECT U.user_id, U.name, A.agency, R.activated FROM Users AS U 
    LEFT JOIN Rewards AS R ON U.user_id = R.renter_id
    LEFT JOIN Agent AS A ON U.user_id = A.agent_id
    WHERE U.user_id = %s;
    """
    return execute_query(query, tuple([user_id]), fetch_mode='one')


def get_agency(agent_id):
    """Get agency name from agent."""
    
    query = """
    SELECT agency FROM Agent
    """
    params = [agent_id]
    return execute_query(query, tuple(params), fetch_mode='one')