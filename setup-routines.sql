DROP PROCEDURE IF EXISTS sp_add_visit;
DROP PROCEDURE IF EXISTS sp_add_city;
DROP PROCEDURE IF EXISTS sp_get_user_connections;
DROP PROCEDURE IF EXISTS sp_add_connection;
DROP PROCEDURE IF EXISTS sp_get_friends_reviews;
DROP PROCEDURE IF EXISTS sp_add_to_wishlist;
DROP FUNCTION IF EXISTS get_user_id;
DROP FUNCTION IF EXISTS get_city_id;
DROP TRIGGER IF EXISTS tr_delete_from_wishlist_after_visit; 


-- UDFS:

-- gets the user_id given the username of a user.
DELIMITER !
CREATE FUNCTION get_user_id (user_username VARCHAR(20))
RETURNS INT DETERMINISTIC
BEGIN
    DECLARE id INT;

    SELECT user_id INTO id
    FROM user_info
    WHERE username = user_username;

    RETURN id;
END !
DELIMITER ;

-- gets the city_id given the name of a city.
DELIMITER !
CREATE FUNCTION get_city_id (inputted_city_name VARCHAR(50))
RETURNS INT DETERMINISTIC
BEGIN
    DECLARE id INT;

    SELECT city_id INTO id
    FROM city_info
    WHERE city_name = inputted_city_name;

    RETURN id;
END !
DELIMITER ;


-- PROCEDURES: 

-- procedure that gets the connections of a givn user_id
DELIMITER !

CREATE PROCEDURE sp_get_user_connections(given_user_id INT)
BEGIN
    SELECT user_info.username
    FROM connections
    JOIN user_info ON connections.user_id2 = user_info.user_id
    WHERE connections.user_id1 = given_user_id
    UNION
    SELECT user_info.username
    FROM connections
    JOIN user_info ON connections.user_id1 = user_info.user_id
    WHERE connections.user_id2 = given_user_id;
END !

DELIMITER ;

-- procedure that returns all reviews of a given user_ids friends for a given city

DELIMITER !

CREATE PROCEDURE sp_get_friends_reviews(
    given_user_id INT, 
    given_city_name VARCHAR(50))
BEGIN

    CREATE TEMPORARY TABLE friends AS (
        SELECT user_info.user_id
        FROM connections
        JOIN user_info ON connections.user_id2 = user_info.user_id
        WHERE connections.user_id1 = given_user_id
        UNION
        SELECT user_info.user_id
        FROM connections
        JOIN user_info ON connections.user_id1 = user_info.user_id
        WHERE connections.user_id2 = given_user_id
    );

    SELECT user_info.username, visits.review_text, visits.rating
    FROM friends JOIN visits ON friends.user_id = visits.user_id
    JOIN user_info ON visits.user_id = user_info.user_id
    WHERE visits.city_id = get_city_id(given_city_name);

    DROP TABLE IF EXISTS friends_reviews;
END !

DELIMITER ;


-- procedure that adds an instance to the visits table.
DELIMITER !
CREATE PROCEDURE sp_add_visit(
    user_id VARCHAR(20),
    city_name VARCHAR(50),
    given_text VARCHAR(300),
    given_picture VARCHAR(100),
    given_rating NUMERIC(10,2),
    first_day DATE,
    last_day DATE)
BEGIN
    DECLARE city_no INT;
    
    SET city_no = get_city_id(city_name);

    INSERT INTO visits(
        user_id,
        city_id,
        review_text,
        picture,
        rating,
        start_date,
        end_date,
        time_inputted)
    VALUES (
        user_id,
        city_no,
        given_text,
        given_picture,

        given_rating,
        first_day,
        last_day,
        NOW());
END !
DELIMITER ;


-- procedure that adds an instance to the city table.
DELIMITER !
CREATE PROCEDURE sp_add_city(
    given_name VARCHAR(50), 
    given_state VARCHAR(30), 
    given_country VARCHAR(60), 
    given_population INT, 
    given_fun_fact VARCHAR(300)
)
BEGIN
    INSERT INTO city_info(city_name, state_name, country_name, population, fun_fact)
    VALUES (given_name, given_state, given_country, given_population,
        given_fun_fact);
END !
DELIMITER ;

-- procedure that adds a connection to the connections table
-- user_id1 is stored as a global variable when the user logs in
-- but we still need to convert username2 into user_id2 because
-- users dont know user_ids, only usernames

DELIMITER !
CREATE PROCEDURE sp_add_connection(
    user_id1 INT,
    username2 VARCHAR(20)
)
BEGIN
    DECLARE user_id2 INT;
    SET user_id2 = get_user_id(username2);
    INSERT INTO connections VALUES (user_id1, user_id2);
END !
DELIMITER ;

DELIMITER !
CREATE PROCEDURE sp_add_to_wishlist(
    user_id1 INT,
    city_name VARCHAR(50)
)
BEGIN
    DECLARE city_id INT;
    SET city_id = get_city_id(city_name);
    INSERT INTO wishlist (user_id, city_id, time_inputted) VALUES (user_id1, city_id, NOW());
END !
DELIMITER ;



call sp_add_visit('rb', 'New York', 'This place is amazing', 'path/to/picture', 7, '2024-01-15', '2024-01-17');
call sp_add_visit('rb', 'Chicago', 'This place is the best place in the world', '/pictures/pic',  9.99, '2024-01-18', '2024-01-22');

call sp_add_connection(4, 'rb');
call sp_add_connection(5, 'rb');
call sp_add_connection(6, 'rb');
call sp_add_connection(7, 'rb');
call sp_add_connection(8, 'rb');
call sp_add_connection(9, 'rb');
call sp_add_connection(1, 'rb');
call sp_add_connection(2, 'rb');


INSERT INTO wishlist (user_id, city_id, time_inputted)
            VALUES (21, 49, '2018-06-25 09:11:47');
INSERT INTO wishlist (user_id, city_id, time_inputted)
            VALUES (21, 88, '2006-03-12 16:11:11');
INSERT INTO wishlist (user_id, city_id, time_inputted)
            VALUES (21, 61, '2008-02-18 17:29:08');
INSERT INTO wishlist (user_id, city_id, time_inputted)
            VALUES (21, 31, '2020-06-10 18:59:32');
INSERT INTO wishlist (user_id, city_id, time_inputted)
            VALUES (21, 8, '2011-01-01 17:19:25');
INSERT INTO wishlist (user_id, city_id, time_inputted)
            VALUES (21, 44, '2019-05-28 07:30:08');
INSERT INTO wishlist (user_id, city_id, time_inputted)
            VALUES (21, 21, '2004-11-20 00:26:44');

call sp_add_city('Peoria', 'Illinois', 'United States', 234233, 'My cousins used to live there'); 
call sp_add_city('Madrid', NULL, 'Spain', 234233, 'This is where liv is for the semester'); 

-- TRIGGERS:
DELIMITER !

CREATE TRIGGER tr_delete_from_wishlist_after_visit
AFTER INSERT ON visits
FOR EACH ROW
BEGIN
    DELETE FROM wishlist
    WHERE wishlist.user_id = NEW.user_id
    AND wishlist.city_id = NEW.city_id;
END!

DELIMITER ;
