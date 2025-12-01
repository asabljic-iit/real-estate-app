import functools
import psycopg2
from flask import Flask, render_template, request, flash, abort, g, session
from flask import redirect, url_for
from scripts.misc import *
from scripts.account import *
from scripts.auth import *
from scripts.book import *
from scripts.property import *

app = Flask(__name__)
app.config.from_mapping(SECRET_KEY='dev')

# Login Functions
def login_required(view): 
    #TODO- maybe have two functions, one for renter one for agent or add another param
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None: #TODO
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

    display_headers = headers
    return render_template('home.html',
                           headers=display_headers, 
                           properties=results)

# User Register Page
# Both agents and prospective renters can register with an email and personal information.
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
            flash("Registration failed: That email address is already registered.")
        except Exception as error:
            flash(f"An unexpected error occurred: {error}")

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
            flash(error)
        except Exception as error:
            flash(f"An unexpected error occurred: {error}")

    return render_template('auth/login.html')

# Renter- Account Page
# TODO- Renters can add, modify, or delete addresses and credit cards. 
# Billing addresses cannot be deleted before deleting the associated credit card.
# TODO Renter- save info, display saved info (if any), and add rewards program
# TODO Agent- check for agent or renter, then show applicable options
#  (for agents, its job title, agency, contact info (phone num))
@app.route('/your-account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        flash('whoopsie')

    return render_template('manage/account.html')

# Agent- Manage Properties Page
# TODO- add, manage, delete properties
@app.route('/manage-properties', methods=['GET', 'POST'])
@login_required
def manage_properties():
    if request.method == 'POST':
        flash('whoopsie')

    return render_template('manage/manage-props.html')

# Search Results Page
# Search by location, TODO- rental/sale type, number of bedrooms, price range,
#  property type, and desired date.
# Only available properties meeting all criteria are shown. (i think this is implemented?)
# TODO- Results display price, bedrooms, property type, and description.
# TODO- Users can sort results by price or number of bedrooms.
@app.route('/search', methods=['GET'])
def search():
    # Get the search criteria from the URL query parameters
    street = request.args.get('street', '')
    city = request.args.get('city', '')
    state = request.args.get('state', '')
    zip_code = request.args.get('zip_code', '')
    
    # Call a new database function to filter the properties
    headers, results = search_properties(street, city, state, zip_code)

    display_headers = headers[1:]
    
    return render_template('prop-results.html', 
                           headers=display_headers, 
                           properties=results, 
                           search_params=request.args)

# TODO- add a property details page and book from there instead of currently booking
#  directly from  the search results?

# Renter- Booking Page
# TODO- Renters select a property, rental period, and payment method.
# TODO- Booking details show rental period, total cost, and payment method.
@app.route('/book/<property_id>', methods=['GET', 'POST'])
@login_required
def book_property(property_id):
    property_details = get_property_details(property_id)
    if request.method == 'POST':
        # flash('whoopsie')
        # success = save_booking(property_id, user_name, ...)
        return render_template('book/confirmation.html', property=property_details)
    else:
        if property_details:
            return render_template('book/create-book.html', property=property_details)
        else:
            abort(404)

# Manage Bookings Page
# TODO- Renters can view and cancel their bookings. Refunds go to the saved
#  payment method, if applicable.
# TODO- Agents can view and cancel bookings for properties under their agency,
#  including renter details, property info, rental period, and payment method
@app.route('/manage-booking', methods=['GET', 'POST'])
@login_required
def manage_booking():
    if request.method == 'POST':
        flash('whoopsie')

    return render_template('manage/manage-books.html')

if __name__ == '__main__':
    app.run(debug=True) # debug=True allows editing w/o having to restart server