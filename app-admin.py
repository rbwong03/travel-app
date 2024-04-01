"""
This program acts as the interface from which admin users can interact with
the database through specified actions.
"""
import sys
import mysql.connector
import mysql.connector.errorcode as errorcode
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
          port='3306',
          password='adminpw',
          database='traveldb'
        )
        print('Successfully connected.')
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR and DEBUG:
            sys.stderr('Incorrect username or password when connecting to DB.')
        elif err.errno == errorcode.ER_BAD_DB_ERROR and DEBUG:
            sys.stderr('Database does not exist.')
        elif DEBUG:
            sys.stderr(err)
        else:
            sys.stderr('An error occurred, please contact the administrator.')
        sys.exit(1)

# ----------------------------------------------------------------------
# Functions for Command-Line Options/Query Execution
# ----------------------------------------------------------------------
def get_all_users():
    """
    Prints all users and their info in the database.
    """
    sql = 'SELECT * FROM user_info;'
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            if row:
                print(row)

    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to get all users')


def delete_user(user_id):
    """
    Deletes a user specified by their user_id from the database
    """

    sql = 'DELETE FROM user_info WHERE user_id = \'%s\';' % (user_id)
    try:
        cursor.execute(sql)
        conn.commit()

        print("User deleted successfully")
    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to delete_user')

def delete_review(visit_id):
    """
    Updates the review of a given visit_id to be a redacted message
    Does not actually delete the review or the visit from the database
    """
    redacted = '*THIS REVIEW HAS BEEN REMOVED FOR VIOLATING COMMUNITY GUIDELINES*'
    cursor = conn.cursor()

    sql = 'UPDATE visits SET review_text = \'%s\' WHERE visit_id = \'%s\';' % (redacted, visit_id)
    try:
        cursor.execute(sql)
        conn.commit()

        print("Review successfully redacted")
    except mysql.connector.Error as err:

        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to delete review')

def add_city(city_name, country_name, population, state_name=None, fun_fact=None):
    """
    Adds a city to the database with the given parameters
    """

    if not fun_fact:
        fun_fact = 'NULL'
    else:
        fun_fact = "\'" + fun_fact + "\'"
    if not state_name:
        state_name = 'NULL'
    else:
        state_name = "\'" + state_name + "\'"

    sql = 'CALL sp_add_city(\'%s\', %s, \'%s\', %s, %s);' % (city_name, state_name, country_name, population, fun_fact)
    try:
        cursor.execute(sql)
        conn.commit()
        print('City added successfully!')
    except mysql.connector.Error as err:

        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to add city')

def remove_city(city_id):
    """
    removes a city from the database with the given city_id
    """
    sql = 'DELETE FROM city_info WHERE city_id = %s;' % (city_id)
    try:
        cursor.execute(sql)
        conn.commit()

    except mysql.connector.Error as err:
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('Failed to remove city')

# ----------------------------------------------------------------------
# Functions for Logging Users In
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
            sys.exit(1)

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

def show_admin_options():
    """
    Displays options specific for admins, such as adding new data <x>,
    modifying <x> based on a given id, removing <x>, etc.
    """
    while True:
        print('\n What would you like to do? ')
        print('  (showall) - display list of all users')
        print('  (deleteuser) - delete a user from the app')
        print('  (deletereview) - delete a user\'s review of a visit')
        print('  (addcity) - add a city to the list of available cities')
        print('  (removecity) - remove a city from the list of available cities')
        print('  (q) - quit')
        print()
        ans = input('Enter an option: ').lower()
        if ans == 'q':
            quit_ui()

        elif ans == 'showall':
            get_all_users()

        elif ans == "deleteuser":
            user_id = input('what is the user_id of the user you would like to delete? ')
            delete_user(user_id)

        elif ans == "deletereview":
            review_id = input('What is the visit_id of the review you would like to delete? ')
            delete_review(review_id)

        elif ans == "addcity":
            city_name = input('What is the name of the city you would like to add? ')
            country_name = input('What country is the city in? ')
            population = input('What is the population of the city? ')
            state_name = input('What state is the city in? (ENTER if N/A) ')
            fun_fact = input('What is a fun_fact about this city? (ENTER if N/A) ')
            add_city(city_name, country_name, population, state_name, fun_fact)

        elif ans == "removecity":
            city_id = input('What is the id of the city you would like to remove? ')
            remove_city(city_id)


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
    show_login_options()
    show_admin_options()


if __name__ == '__main__':
    conn = get_conn()
    cursor = conn.cursor()
    main()
