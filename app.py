import functools
import psycopg2
from datetime import datetime, date

from flask import Flask, render_template, request, flash, abort, g, session
from flask import redirect, url_for

from scripts.account import *
from scripts.auth import *
from scripts.book import *
from scripts.property import *

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='dev') # change when deploying
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}


# Miscellanous Functions
def format_currency(value):
    """Formats a number with comma separators (e.g., 350000 -> 350,000)"""
    if value is None:
        return ""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value

app.jinja_env.filters['currency'] = format_currency

def format_credit_card(value):
    """Formats credit card number to last 4 digits."""
    if value is None:
        return ""
    try:
        return f"{value[-4:]}"
    except (ValueError, TypeError):
        return value

app.jinja_env.filters['credit_card'] = format_credit_card

# Login Functions
def login_required(view): 
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("You must log in.", 'info')
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view

def agent_required(view): 
    """View decorator that redirects non-agent users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user['agency'] is None:
            flash("Only agents can access that page.", 'error')
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view

@app.before_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = (get_user(user_id))

@app.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for('home'))


# The application supports the following actions (role in parentheses):
# - Account registration (agents and prospective renters)
# - Add/modify/delete payment and address information (prospective renters)
# - Add/Delete/Modify properties (agents)
# - Search properties (all users)
# - Book properties (prospective renters)


# Home Page
@app.route('/')
def home():
    headers, results = get_random_properties()

    display_headers = headers[1:]
    return render_template('home.html',
                           headers=display_headers, 
                           properties=results)


# User Register Page
# Both agents and prospective renters can register with an email and personal
#  information.
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        agency = request.form['agency']
        email = request.form['email']
        name = request.form['name']
        pswd = request.form['password']

        try:
            register_user(agency, email, name, pswd)
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash("Registration failed: That email address is already registered.", 'error')
        except Exception as error:
            flash(f"An unexpected error occurred: {str(error)}", 'error')

    return render_template('auth/register.html')


# User Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pswd = request.form['password']

        try:
            login_user(email, pswd)
            return redirect(url_for('account'))
        except ValueError as error:
            flash(str(error), 'error')
        except Exception as error:
            flash(f"An unexpected error occurred: {str(error)}", 'error')

    return render_template('auth/login.html')


# Account Page
# Renters can add, modify, or delete addresses and credit cards. 
#  Billing addresses cannot be deleted before deleting the associated credit 
#  card.
# Renters can join a reward program. Reward points are earned equal to the
#  rental price for each booking.
@app.route('/your-account', methods=['GET', 'POST'])
@login_required
def account():
    if not g.user:
        flash("You must be logged in", "error")
    
    if request.method == 'POST':
        action = request.form.get('action')
        if g.user["agency"]:
            agency = request.form.get('agency')
            title = request.form.get('title')
            phone = request.form.get('phone')

            try:
                save_agent_details(g.user["user_id"], agency, title, phone)
            except Exception as e:
                flash(f'Error saving account details: {str(e)}', 'error')

        elif action == "delete":
            card_id = request.form.get("card_id")
            try:
                delete_credit_card(g.user["user_id"], card_id)
            except Exception as e:
                flash(f'Error deleting credit card: {str(e)}', 'error')

        elif action == "edit":
            card_id = request.form.get("card_id")
            newCardnum = request.form.get("new_credit_card_number")
            newExpdate = request.form.get("new_expiration_date")

            try:
                edit_credit_card(g.user["user_id"], card_id, newCardnum, 
                                 newExpdate)
            except Exception as e:
                flash(f'Error editing credit card: {str(e)}', 'error')

        elif action == "create":
            card_number = request.form.get('cardnum')
            expiration_date = request.form.get('expdate')
            street = request.form.get('street')
            city = request.form.get('city')
            state = request.form.get('state')
            zipcode = request.form.get('zipcode')

            try:
                address_id = save_addr(g.user['user_id'], street, city, state, 
                                       zipcode)
                save_credit_card(g.user['user_id'], card_number, address_id, 
                                 expiration_date)
            except Exception as e:
                flash(f'Error saving credit card: {str(e)}', 'error')
            
        elif action == 'preferences':
            movein = request.form.get('movein')
            preferloc = request.form.get("preferloc")
            budget = request.form.get("budget")

            try: 
                save_renter_prefs(g.user["user_id"], movein, preferloc, budget)
            except Exception as e:
                flash(f"Error saving your preferences: {str(e)}", 'error')
            
        elif action == 'rewards':

            try:
                enroll_rewards(g.user["user_id"])
            except Exception as e:
                flash(f"an error has occured please try again later {str(e)}", 'error')
        
        else:
            # Handle other POST requests or missing data
            flash('Invalid action or missing booking or property ID.', 'error')

        

    headers, results = get_credit_cards(g.user['user_id'])
    rewards = get_rewards(g.user['user_id'])
    accountprefs = get_account(g.user['user_id'])
    return render_template('manage/account.html', headers=headers, payment=results, rewards=rewards, accountprefs=accountprefs)


# Agent- Manage Properties Page
# Add, manage, delete properties.
@app.route('/manage-properties', methods=['GET', 'POST'])
@agent_required
def manage_properties():
    if request.method == 'POST':
        action = request.form.get('action')
        property_id = request.form.get('property_id')
        neighborhood_id = request.form.get('neighborhood_id')
        num_rooms = request.form.get('num_rooms')
        description = request.form.get('description')
        sq_footage = request.form.get('sq_footage')
        price = request.form.get('price')
        street = request.form.get('street')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip_code')
        prop_type = request.form.get('prop_type')
        business_type = request.form.get('business_type')
        building_type = request.form.get('building_type')
        zoning_type = request.form.get('zoning_type')
        
        if action == 'delete' and property_id:
            try:
                agency_delete_property(g.user['agency'], property_id)               
                flash(f'{property_id} has been successfully deleted.', 'success')
            except Exception as e:
                flash(f'Error deleting property: {str(e)}', 'error')
            
            return redirect(url_for('manage_properties'))
        
        elif action == 'edit' and property_id:
            try: 
                agency_edit_property(g.user['agency'], property_id, num_rooms, 
                                     description, price)
                flash(f'{property_id} has been successfully edited.', 'success')
            except Exception as e:
                flash(f'Error editing property: {str(e)}', 'error')
        
        elif action == 'add':
            try:
                agency_add_property(g.user['agency'], neighborhood_id, num_rooms,
                                    description, sq_footage, price, street, city, 
                                    state, zip_code, prop_type, building_type, 
                                    business_type, zoning_type)
                flash('Property has been successfully added.', 'success')
            except Exception as e:
                flash(f'Error adding property: {str(e)}', 'error')
        else:
            # Handle other POST requests or missing data
            flash('Invalid action or missing property ID.', 'error')

    headers, results = get_agency_properties(g.user['agency'])

    display_headers = headers

    return render_template('manage/manage-props.html',
                           headers=display_headers, 
                           properties=results)


# Search Results Page
# Search by location, number of bedrooms (num), price range (num min, range max),
#  property type, and desired date.
# Only available properties meeting all criteria are shown.
# Results display price, bedrooms, property type, and description.
# Users can sort results by price or number of bedrooms.
@app.route('/search', methods=['GET'])
def search():
    # Get the search criteria from the URL query parameters
    street = request.args.get('street', '')
    city = request.args.get('city', '')
    state = request.args.get('state', '')
    zip_code = request.args.get('zip_code', '')
    num_rooms = request.args.get('num_rooms', '')
    price_min = request.args.get('price_min', '')
    price_max = request.args.get('price_max', '')
    prop_type = request.args.get('prop_type', '')
    desired_date = request.args.get('desired_date', '')
    sort_by = request.args.get('sort_by', '')

    # Call a new database function to filter the properties
    headers, results = search_properties(street, city, state, zip_code,
                                         num_rooms, price_min, price_max,
                                         prop_type, desired_date, sort_by)

    display_headers = headers[1:]
    
    return render_template('search-results.html', 
                           headers=display_headers, 
                           properties=results, 
                           search_params=request.args)


# Renter- Property Details/Booking Page
# Renters select a property, rental period, and payment method. 
# Add new payment from booking page.
# Booking details show rental period, total cost, and payment method.
@app.route('/property-details/<property_id>', methods=['GET', 'POST'])
def book_property(property_id):
    property_details = get_property_details(property_id)

    if request.method == 'POST':
        is_newcard = request.form['newcard']
        action = request.form['action']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        credit_card = [None, request.form.get('cardnum')]
        expiration_date = request.form.get('expdate')
        street = request.form.get('street')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            if is_newcard=='yes':
                expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format submitted.', 'error')
            return redirect(url_for('booking_form'))

        today = date.today() 

        if start_date < today:
            flash('The booking date cannot be in the past. Please select today or a future date.', 'error')
        else:
            try:
                if is_newcard=='yes':
                    address_id = save_addr(g.user['user_id'], street, city, 
                                           state, zipcode)
                    credit_card[0] = save_credit_card(g.user['user_id'], 
                                                      credit_card[1], address_id, 
                                                      expiration_date)
                else:
                    credit_card = request.form.get('payment').split(',') 
                
                save_booking(g.user['user_id'], property_id, start_date, end_date, 
                             credit_card[0])
        
                if action =='redeem':
                    redeem_rewards_points(g.user['user_id'], property_details['price'])

                elif g.user['activated']:
                    add_rewards_points(g.user['user_id'], property_details['price'])
                
                flash('Sucessfully booked!', 'success')
                return render_template('book/confirmation.html', 
                                       property=property_details,
                                       booking=[start_date, end_date, 
                                                str(credit_card[1])[-4:]])
            except ValueError as error:
                flash(str(error), 'error')
            except Exception as error:
                flash(f"An unexpected error occurred: {str(error)}", 'error')

    if property_details:
        if g.user:
            headers, results = get_credit_cards(g.user['user_id'])
            reward_details= get_rewards(g.user['user_id'])
            return render_template('book/prop-details.html', 
                                property=property_details,
                                headers=headers,
                                credit_cards=results,
                                reward_details=reward_details)
        else:
            return render_template('book/prop-details.html', 
                                property=property_details)
    else:
        abort(404)


# Manage Bookings Page
# Renters can view and cancel their bookings. Refunds go to the saved
#  payment method, if applicable.
# Agents can view and cancel bookings for properties under their agency,
#  including renter details, property info, rental period, and payment method.
@app.route('/manage-bookings', methods=['GET', 'POST'])
@login_required
def manage_bookings():
    if request.method == 'POST':
        action = request.form.get('action')
        booking_id = request.form.get('booking_id')
        property_id = request.form.get('property_id')
        new_start_date = request.form.get('new_start_date')
        new_end_date = request.form.get('new_end_date')

        if action == 'edit' and (booking_id and property_id and new_start_date 
                                 and new_end_date):
            try:
                new_start_date = datetime.strptime(new_start_date, '%Y-%m-%d').date()
                new_end_date = datetime.strptime(new_end_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format submitted.', 'error')
                return redirect(url_for('manage_bookings'))
    
            try:
                edit_booking(g.user['user_id'], booking_id, new_start_date, 
                             new_end_date, g.user['agency'])               
                flash(f'{property_id} has been successfully edited.', 'success')
            except Exception as e:
                flash(f'Error editing booking: {str(e)}', 'error')
            
            return redirect(url_for('manage_bookings'))
        
        elif action == 'cancel' and booking_id and property_id:
            try:
                property_details = get_property_details(property_id)

                cancel_booking(g.user['user_id'], booking_id, property_id, 
                               g.user['agency'])
                
                if g.user['activated']:
                    print("you are removing: ", property_details['price'])
                    add_rewards_points(g.user['user_id'], property_details['price'])
                    
                flash(f'{property_id} has been successfully cancelled.', 'success')
            except Exception as e:
                flash(f'Error cancelling booking: {str(e)}', 'error')
            
            return redirect(url_for('manage_bookings'))

        else:
            # Handle other POST requests or missing data
            flash('Invalid action or missing booking or property ID.', 'error')

    headers, results = get_renter_bookings(g.user['user_id'], g.user['agency'])

    display_headers = headers[2:]
    if g.user['agency']:
        display_headers = headers[1:]

    return render_template('manage/manage-books.html', 
                           headers=display_headers, 
                           bookings=results)


if __name__ == '__main__':
    app.run(debug=True) # debug=True allows editing w/o having to restart server