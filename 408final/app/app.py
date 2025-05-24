from flask import Flask, render_template, request, redirect, url_for, flash
from db_operations import db_operations
from helper import helper

db = db_operations()
help = helper()
app = Flask(__name__)
app.secret_key = 'secret_key'

# Route for the homepage
@app.route('/')
def startingPage():
    return render_template('startingPage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['uname']
        password = request.form['pword']

        selectQuery = '''
            SELECT user_id
            FROM User
            WHERE name = %s AND password = %s;
        '''
        values = (name, password)
        id = db.single_record_params(selectQuery, values)

        if id is None:
            flash("Username or password incorrect. Please try again")
            return render_template('login.html')

        user_id = help.convert(id)
        return redirect(url_for('dashboard', user_id=user_id))
    else:
        return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pword']

        # Check if username exists
        selectQuery = '''
            SELECT COUNT(*)
            FROM User
            WHERE name = %s;
        '''
        values = (username,)
        exists = db.single_record_params(selectQuery, values)
        if exists > 0:
            flash('Username already exists. Please choose another.')
            return redirect(url_for('create'))

        # Insert new user (make sure your User table has a password column)
        insertQuery = '''
            INSERT INTO User (name, password) VALUES (%s, %s);
        '''
        db.modify_query_params(insertQuery, (username, password))

        # Get the new user id
        selectUserId = '''
            SELECT user_id
            FROM User
            WHERE name = %s;
        '''
        user_id = db.single_record_params(selectUserId, (username,))

        # Redirect or render a page after successful creation
        return redirect(url_for('login'))
    else:
        return render_template('create.html')

@app.route('/dashboard/<user_id>')
def dashboard(user_id):
    return render_template('action.html', user_id=user_id)

def ratingConversionToInt(rating):
    rating = rating.lower().strip()
    numbers = {
        "zero": 0, "one": 1, "two": 2, "three": 3, 
        "four": 4, "five": 5
    }
    try:
        rating = int(rating)
        if (rating >= 1 and rating <= 5):
            return rating
    except:
        pass

    value = 0
    if rating in numbers:
        value = numbers[rating]
        return value
    else:
        return -1

if __name__ == '__main__':
    app.run(debug=True)