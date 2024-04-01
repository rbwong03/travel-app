"""
This program acts as the interface from which client users can interact with
the database through specified actions.
"""
import sys  
import mysql.connector
import mysql.connector.errorcode as errorcode
import datetime


DEBUG = True


# ----------------------------------------------------------------------
# SQL Utility Functions
# ----------------------------------------------------------------------
def get_conn():
    """"
    Returns a connected MySQL connector instance, if connection is successful.
    If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          user='appadmin',
          # Find port in MAMP or MySQL Workbench GUI or with
          # SHOW VARIABLES WHERE variable_name LIKE 'port';
          port='3306',  # this may change!
          password='adminpw',
          database='traveldb' # replace this with your database name
        )
        print('Successfully connected.')
        return conn
    except mysql.connector.Error as err:
        # Remember that this is specific to _database_ users, not
        # application users. So is probably irrelevant to a client in your
        # simulated program. Their user information would be in a users table
        # specific to your database; hence the DEBUG use.
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR and DEBUG:
            sys.stderr('Incorrect username or password when connecting to DB.')
        elif err.errno == errorcode.ER_BAD_DB_ERROR and DEBUG:
            sys.stderr('Database does not exist.')
        elif DEBUG:
            sys.stderr(err)
        else:
            # A fine catchall client-facing message.
            sys.stderr('An error occurred, please contact the administrator.')
        sys.exit(1)


# ----------------------------------------------------------------------
# Functions for Command-Line Options/Query Execution
# ----------------------------------------------------------------------
        
# User functions
def show_profile(user_id):
    """
    Shows a user's profile information
    """
    param1 = ''
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    sql = 'SELECT * FROM user_info WHERE user_id = \'%s\';' % (user_id)
    try:
         
        cursor.execute(sql)
        row = cursor.fetchone()
        print('\n')
        print('User Profile:')
        if row:
            print(f"    user_id: {row[0]}")
            print(f"    username: {row[1]}")
            print(f"    email: {row[2]}")
            print(f"    profile_pic: {row[3]} \n")
        else:
            print("User not found.")
 
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            # TODO: Please actually replace this :) 
            sys.stderr('An error occurred, give something useful for clients...')


def show_wishlist(user_id):
    """
    Shows a list of all the places that the user wants to visit
    """
    cursor = conn.cursor()

    sql = 'SELECT city_name FROM wishlist w JOIN city_info ci on w.city_id = ci.city_id WHERE user_id = \'%s\';' % (user_id)
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        print('\n')
        print('Wishlist:')
        if rows:  
            for index, row in enumerate(rows, start=1):
                print(f'    {index}: {row[0]}')
        else:
            print("No wishlist found.")  
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to get wishlist')

def show_visited(user_id):
    """
    Shows a list of all the places that the user has visited, ordered with
    most recent visits on top 
    """

    sql = 'SELECT ci.city_name, v.start_date, v.end_date, v.review_text, v.rating FROM visits v JOIN city_info ci ON v.city_id = ci.city_id WHERE v.user_id = %s ORDER BY v.time_inputted DESC;'
    try:
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()

        for row in rows:
            if row:
                city_name, start_date, end_date, review_text, rating = row

                formatted_start_date = start_date.strftime('%Y-%m-%d %H:%M:%S') if start_date else 'N/A'
                formatted_end_date = end_date.strftime('%Y-%m-%d %H:%M:%S') if end_date else 'N/A'
                formatted_rating = "{:.2f}".format(rating) if rating else 'No rating'
                formatted_review = review_text if review_text else 'No review'
                print('\n')
                print(f"City: {city_name}")
                print(f"    Start Date: {formatted_start_date}")
                print(f"    End Date: {formatted_end_date}")
                print(f"    Review: {formatted_review}")
                print(f"    Rating: {formatted_rating} \n")
            else:
                print("No visits found.")

    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to get visited places')


def show_connections(user_id):
    """
    Shows a list of all the user's connections.
    """
    try:

        cursor = conn.cursor()
        cursor.callproc('sp_get_user_connections', [user_id,])
        print('\n')
        print('My Connections:')

        for result in cursor.stored_results():
            if result:
                rows = result.fetchall()
                for index, row in enumerate(rows, start=1):
                    print(f'    {index}: {row[0]}')
            else:
                print("No connections found.")
        

    except mysql.connector.Error as err:
        errorMsg = str(err) + '\n'
        print('Failed to get connections\n')
        print(errorMsg)
    finally:
        if cursor:
            cursor.close()


# City functions
def show_city_reviews(user_id, city_name):
    """
    Shows a list of all the reviews that the user's friends have written about a city.
    """
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.callproc('sp_get_friends_reviews', [user_id, city_name])

        print('\n')
        print(f'{city_name} Reviews:')

        for result in cursor.stored_results():
            rows = result.fetchall()
            for index, row in enumerate(rows, start=1):
                print(f'    {index}: {row[0]} - {row[1]} - Rating: {row[2]}')
        print('\n')

    except mysql.connector.Error as err:
        errorMsg = f"Failed to get city reviews due to an error: {err}\n"
        if DEBUG:
            sys.stderr.write(errorMsg)
            sys.exit(1)
        else:
            sys.stderr.write("Failed to get city reviews\n")
    finally:
        if cursor is not None:
            cursor.close()
    
def average_city_rating(city_name):
    """
    Shows the average rating of a city
    """
    param1 = ''
    cursor = conn.cursor()

    sql = 'SELECT AVG(v.rating) AS average_rating FROM city_info ci JOIN visits v ON ci.city_id = v.city_id WHERE ci.city_name = \'%s\' GROUP BY ci.city_name;' % (city_name)
    try:
        cursor.execute(sql)
        row = cursor.fetchone()
        if row:
            print('\n')
            print(f'Average rating of {city_name}:')
            print(f'    {row[0]}')
        else:
            print("No ratings found.")
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to get average rating of city')

def add_connection(user_id, connection_username):
    """
    adds a connection by username
    """
    cursor = conn.cursor()
    sql = 'CALL sp_add_connection(\'%s\', \'%s\')' % (user_id, connection_username)
    try:
        cursor.execute(sql)
        conn.commit()
        print("Friend added successfully!")
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to add friend')

def add_visit(user_id, city_name, rating, start_date, end_date, picture=None, review_text=None):
    """
    Adds a visit to the database with the given arguments.
    """
    cursor = conn.cursor()
    if not picture:
        picture = 'NULL'
    else:
        picture = "\'" + picture + "\'"
    
    if not review_text:
        review_text = 'NULL'
    else:
        review_text = "\'" + review_text + "\'"

    sql = "CALL sp_add_visit(%s, \'%s\', %s, %s, %s, \'%s\', \'%s\');" % (user_id, city_name, review_text, picture, rating, start_date, end_date)


    try:
        cursor.execute(sql)
        conn.commit()
        print('Visit added successfully!')
    except mysql.connector.Error as err:
        print(f'Failed to add visit due to an error: {err}')
        if DEBUG:
            sys.exit(1)

def add_to_wishlist(user_id, city_name):
    """
    adds a city to the user's wishlist. Is removed
    after the user visits that city
    """
    cursor = conn.cursor()

    sql = 'CALL sp_add_to_wishlist(\'%s\', \'%s\');' % (user_id, city_name)
    print(sql)
    try:
        cursor.execute(sql)
        conn.commit()
        print('City added to wishlist successfully!')
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to add city to wishlist')


# ----------------------------------------------------------------------
# Functions for Logging People in
# ----------------------------------------------------------------------
            
def login():
    """
    Logs in users 
    """
    username = input('Enter username: ')
    password = input('Enter password: ')
    query = "SELECT authenticate('%s', '%s')" % (username, password)
    try:
        cursor.execute(query)
        result = cursor.fetchone()  
        if result and result[0] != 0:
            print("Authentication successful. \n")
            logged_in_userid = result[0]
        else:
            print("No user found or authentication failed.")
            sys.exit(1)
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr.write(str(err) + '\n')
            sys.exit(1)
        else:
            sys.stderr.write('Authentication failed.\n')
    return logged_in_userid

def create_account():
    """
    Creates a new account
    """
    new_username = input('Enter a username: ')
    new_email = input('Enter an email: ')
    password = input('Enter a password: ')
    cursor = conn.cursor()

    sql = 'CALL sp_add_user(\'%s\', \'%s\', \'%s\');' % (new_username, new_email, password)
    try:
        cursor.execute(sql)
        conn.commit()
        print('Account created successfully!')
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to create account')


# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------
            
def show_login_options():
    while True:
        print('What would you like to do? ')
        print('  (login) - Login')
        print('  (createaccount) - Create new account')
        print('  (q) - quit')

        

        ans = input('Enter an option: ').lower()
        if ans == 'login':
            return login()
        elif ans == 'createaccount':
            create_account()
            continue
        elif ans == 'q':
            quit_ui()
        

def show_options(logged_in_userid):
    """
    Displays options users can choose in the application, such as
    viewing <x>, filtering results with a flag (e.g. -s to sort),
    sending a request to do <x>, etc.
    """
    while True:
        print('\n What would you like to do? ')
        print('  (myprofile) - View my profile')
        print('  (myvisits) - View list of places I\'ve visited')
        print('  (mywishlist) - View my wishlist')
        print('  (myconnections) - View my connections')

        print('  (cityreviews) - View all of my friend\'s reviews and ratings for a city')
        print('  (cityrating) - View the average rating of a city')

        print('  (addfriend) - Add a friend')
        print('  (addvisit) - Log a visit for a recent trip')
        print('  (addtowishlist) - Add a city to your wishlist')

        print('  (q) - quit')
        print()
        ans = input('Enter an option: ').lower()
        if ans == 'q':
            quit_ui()
        elif ans == 'myprofile':
            show_profile(logged_in_userid)
        elif ans == 'myvisits':
            show_visited(logged_in_userid)
        elif ans == 'mywishlist':
            show_wishlist(logged_in_userid)
        elif ans == 'myconnections':
            show_connections(logged_in_userid)
        elif ans == 'cityreviews':
            city_name = input('Enter the name of the city you would like to view? ')
            show_city_reviews(logged_in_userid, city_name)
        elif ans == 'cityrating':
            city_name = input('Enter the name of the city you would like to view? ')
            average_city_rating(city_name)
        elif ans == 'addfriend':
            friend_username = input('Enter the username of the person you would like to add as a friend: ')
            add_connection(logged_in_userid, friend_username)
        elif ans == 'addvisit':
            city_name = input('What is the name of the city you visited? ')
            rating = input('What would you rate the city? (0.0-10.0) ')
            start_date = input('What date did your trip begin (YYYY-MM-DD) ')
            end_date = input('What date did you end your trip? (YYYY-MM-DD) ')
            review_text = input('Write a short review of your trip! (ENTER to skip) ')
            picture = input('Enter a filepath for an image: (ENTER to skip)')
            add_visit(logged_in_userid, city_name, rating, start_date, end_date, picture, review_text)
        elif ans == 'addtowishlist':
            city_name = input('Enter the name of the city you would like to put on your wishlist (will be removed after you visit that city)')
            add_to_wishlist(logged_in_userid, city_name)
    

def quit_ui():
    """
    Quits the program, printing a good bye message to the user.
    """
    print('Good bye!')
    exit()


def main():
    """
    Main function for starting things up.
    """
    logged_in_userid = show_login_options()
    show_options(logged_in_userid)


if __name__ == '__main__':
    conn = get_conn()
    cursor = conn.cursor()
    main()
