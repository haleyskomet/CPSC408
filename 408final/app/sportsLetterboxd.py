from helper import helper
from db_operations import db_operations
import random


#global variable
db_ops = db_operations()

def createView():
    db_ops.modify_query("DROP VIEW IF EXISTS v_complete_post_stats;")
    query = '''
        CREATE VIEW v_complete_post_stats AS
            SELECT g.winner_team, g.loser_team, g.score, g.date, s.name AS 'sport', l.name AS 'league', p.rating, p.comment, p.user_id
            FROM Post AS p
            INNER JOIN Game AS g
                ON p.game_id = g.game_id
            INNER JOIN League AS l
                ON g.league_id = l.league_id
            INNER JOIN Sport AS s
                ON l.sport_id = s.sport_id;
        '''
    db_ops.modify_query(query)

# first welcome page
def startScreen():
    user_id = -1
    print(''' 
          Welcome to SportsLetterboxd!
          Login or Sign up
          1. Login
          2. Sign up
          ''')
    while (user_id == -1):
        match helper.get_choice([1,2]):
            case 1:
                user_id = login()
            case 2:
                user_id = createAccount()
    return user_id

# login function
def login():
    name = input("What is your username?: ")
    password = input("What is your password?: ")
    selectQuery = '''
        SELECT user_id
        FROM User
        WHERE name = %s AND password = %s;
        '''
    values = (name, password)
    id = db_ops.single_record_params(selectQuery, values)
    if (id is None):
        print("Username not found.")
        id = -1
    return helper.convert(id)
        
# create new account
def createAccount():
    while(True):
        username = input("Enter a username: ")
        selectQuery = '''
            SELECT COUNT(*)
            FROM User
            WHERE name = %s;
         '''
        values = (username,)
        if (db_ops.single_record_params(selectQuery, values) == 0):
            updateQuery = "INSERT INTO User (user_id, name) VALUES (DEFAULT, %s)"
            values = (username,)
            db_ops.modify_query_params(updateQuery, values)
            break
        else:
            print("Username already exists")

    selectQuery = '''
        SELECT user_id
        FROM User
        WHERE name = %s;
        '''
    user_id = db_ops.single_record_params(selectQuery, values)
    return user_id

def displayOptions(user_id):
    option = 0
    while (option != 3):
        print(''' 
        Menu
        ---------
        1. View posts
        2. Create post
        3. Logout
            ''')
        option = helper.get_choice([1,2,3])
        match option:
            case 1:
                viewPosts(user_id)
            case 2:
                createPost(user_id)
    return

def viewPosts(user_id):
    query = '''
        SELECT *
        FROM v_complete_post_stats
        WHERE user_id = %s;
    '''
    values = (user_id,)
    posts = db_ops.select_query_params(query, values)

    for post in posts:
        # Columns in order based on your view:
        # [0] winner_team, [1] loser_team, [2] score, [3] date,
        # [4] sport (from s.name AS sport), [5] league (from l.name AS league),
        # [6] rating, [7] comment, [8] user_id

        print()
        print(f"{post[0]} vs. {post[1]} on {post[3].strftime('%B %d, %Y')}")
        print(f"- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        print(f"Winner: {post[0]}")
        print(f"Score: {post[2]}")
        print(f"Sport: {post[4]}")
        print(f"League: {post[5]}")
        print()
        print(f"Rating: {post[6]}")
        print("Comments: ")
        print(f"{post[7]}")
    return

def createPost(user_id):
    print("Please enter details")
    score = input("Score: ")
    winner = input("Winner: ")
    loser = input("Loser: ")
    date = input("Date (mm/dd/yyyy): ")
    sport = input("Sport: ")
    league = input("League: ")

    ratingValue = -1
    while (ratingValue == -1):
        rating = input("Rating (1-5, whole numbers only): ")
        ratingValue = ratingConversionToInt(rating)

    comment = input("Any comments: ")

    date = date.strip().split("/")
    queryDate = date[2] + "-" + date[0] + "-" + date[1]

    selectQuery = '''
        SELECT league_id
        FROM League
        WHERE name = %s;
        '''
    values = (league,)
    league_id = db_ops.single_record_params(selectQuery, values)

    if (league_id is None):
        query = '''
        INSERT INTO League(name)
        VALUES (%s);
        '''
        db_ops.modify_query_params(query, values)
        selectQuery = '''
        SELECT league_id
        FROM League
        WHERE name = %s;
        '''
        league_id = db_ops.single_record_params(selectQuery, values)
        
        query = '''
        INSERT INTO Sport(name, league_id)
        VALUES (%s, %s);
        '''
        values = (sport, league_id)
        db_ops.modify_query_params(query, values)

    selectQuery = '''
        SELECT sport_id
        FROM Sport
        WHERE league_id = %s;
        '''
    values = (league_id,)
    sport_id = db_ops.single_record_params(selectQuery, values)
     
        
    query = '''
    INSERT INTO Game(winner_team, loser_team, score, date, sport_id)
    VALUES(%s, %s, %s, %s, %s);
    '''
    values = (winner, loser, score, queryDate, sport_id)
    db_ops.modify_query_params(query, values)

    selectQuery = '''
        SELECT game_id
        FROM Game
        WHERE winner_team = %s AND loser_team = %s AND score = %s
        ORDER BY date DESC
        LIMIT 1;
        '''
    values = (winner, loser, score)
    game_id = db_ops.single_record_params(selectQuery, values)

    query = '''
    INSERT INTO Post(rating, comment, game_id, user_id)
    VALUES (%s, %s, %s, %s);
    '''
    values = (ratingValue, comment, game_id, user_id)
    db_ops.modify_query_params(query, values)


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


# main function
createView()
user_id = startScreen()
displayOptions(user_id)