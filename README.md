# travel-app
This application enables users to share ratings and reviews of cities they've 
visited with their friends, as well as to create wish lists of cities 
they want to visit.

The data was self generated using a python script in order to populate the 
tables. To run our project, ensure you are in 
the correct directory, then launch MYSQL and run the following:

## Project Setup

mysql> source setup.sql;

mysql> source load-data.sql;

mysql> source setup-passwords.sql;

mysql> source setup-routines.sql;

mysql> source grant-permissions.sql;

Alternatively, you can also run:
mysql> source quick.sql

Then, quit out of MYSQL with 
mysql> quit;

Next, if you are an adiministrator, run:
$ python3 app-admin.py

If you are a user, run:
$ python3 app-client.py

You will be presented with a login and registration page. If you have not made 
an account before, follow the commands in the menu to do so.
Once you have made in account, you can follow the directions to log in. 
Once you have logged in, you will be presented with the main menu page, 
giving you different options depending on whether you are a client or an admin.
Follow the directions to perform the action you would like, and after
completing that action, you will be brough back to the same menu page.
You can continue taking more actions, or you can quit and end the program.