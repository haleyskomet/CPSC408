from flask import Flask, render_template, request, redirect, url_for, flash, Response
from db_operations import db_operations
from helper import helper
import csv
import io

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
        return redirect(url_for('action', user_id=user_id))
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

@app.route('/action/<user_id>')
def action(user_id):
    return render_template('action.html', user_id=user_id)

@app.route('/dashboard/<user_id>')
def dashboard(user_id):
    query = "SELECT name FROM User WHERE user_id = %s"
    result = db.single_record_params(query, (user_id,))
    query = '''
        SELECT *
        FROM v_complete_post_stats
        WHERE user_id = %s;
    '''
    values = (user_id,)
    posts = db.select_query_params(query, values)
    return render_template('dashboard.html', user_id=user_id, user=result, posts=posts)

@app.route('/createPost/<user_id>', methods=['GET', 'POST'])
def createPost(user_id):
    if request.method == 'POST':
        score = request.form['score']
        winner = request.form['winner']
        loser = request.form['loser']
        date = request.form['date']
        sport = request.form['sport']
        league = request.form['league']
        rating = request.form['rating']
        comment = request.form['comment']

    # Now insert to DB or process post logic
        performCreatePost(user_id, score, winner, loser, date, sport, league, rating, comment)
        return redirect(url_for('action', user_id=user_id))  # or wherever appropriate
    else:
        return render_template('createPost.html', user_id=user_id)


@app.route('/cancelPost/<user_id>', methods=['POST'])
def cancelPost(user_id):
    try:
        # Optional: roll back any changes, or delete uncommitted draft records
        db.rollback_transaction()
        flash("Post creation cancelled.")
    except Exception as e:
        flash("Failed to cancel post.")
    return render_template('action.html', user_id=user_id)


@app.route('/export_csv/<user_id>')
def export_csv(user_id):
    query = '''
        SELECT * FROM v_complete_post_stats WHERE user_id = %s;
    '''
    values = (user_id,)
    posts = db.select_query_params(query, values)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Winner', 'Loser', 'Score', 'Date', 'Sport', 'League', 'Rating', 'Comment', 'UserID'])
    writer.writerows(posts)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=posts_user_{user_id}.csv'}
    )


def performCreatePost(user_id, score, winner, loser, date, sport, league, rating, comment):
    global db
    db.destructor()  # close old connection
    db = db_operations()  # open new connection

    date = date.strip().split("/")
    queryDate = date[2] + "-" + date[0] + "-" + date[1]

    try:
        db.begin_transaction()

        # Check sport
        selectSportQuery = '''
            SELECT sport_id FROM Sport WHERE name = %s;
        '''
        sport_id = db.single_record_params(selectSportQuery, (sport,))
        if sport_id is None:
            insertSportQuery = '''
                INSERT INTO Sport(name) VALUES (%s);
            '''
            db.modify_query_params(insertSportQuery, (sport,))
            sport_id = db.single_record_params(selectSportQuery, (sport,))

        # Check league with sport_id
        selectLeagueQuery = '''
            SELECT league_id FROM League WHERE name = %s AND sport_id = %s;
        '''
        league_id = db.single_record_params(selectLeagueQuery, (league, sport_id))
        if league_id is None:
            insertLeagueQuery = '''
                INSERT INTO League(name, sport_id) VALUES (%s, %s);
            '''
            db.modify_query_params(insertLeagueQuery, (league, sport_id))
            league_id = db.single_record_params(selectLeagueQuery, (league, sport_id))

        # Insert game
        insertGameQuery = '''
            INSERT INTO Game(winner_team, loser_team, score, date, league_id)
            VALUES (%s, %s, %s, %s, %s);
        '''
        db.modify_query_params(insertGameQuery, (winner, loser, score, queryDate, league_id))

        # Retrieve game_id
        selectGameQuery = '''
            SELECT game_id FROM Game
            WHERE winner_team = %s AND loser_team = %s AND score = %s
            ORDER BY date DESC LIMIT 1;
        '''
        game_id = db.single_record_params(selectGameQuery, (winner, loser, score))

        # Insert post
        insertPostQuery = '''
            INSERT INTO Post(rating, comment, game_id, user_id)
            VALUES (%s, %s, %s, %s);
        '''
        db.modify_query_params(insertPostQuery, (rating, comment, game_id, user_id))

        db.commit_transaction()
        flash("Post created successfully.")

    except Exception as e:
        db.rollback_transaction()
        flash("Failed to create post. Please try again.")

if __name__ == '__main__':
    app.run(debug=True)
