-- DDL for a social media travel application
-- Supports reviews, images, and a wishlits of places to travel to
-- Supports social media connections

DROP TABLE IF EXISTS connections;
DROP TABLE IF EXISTS pictures;
DROP TABLE IF EXISTS visits;
DROP TABLE IF EXISTS wishlist;
DROP TABLE IF EXISTS city_info;
DROP TABLE IF EXISTS user_info;


CREATE TABLE user_info (
    user_id INT AUTO_INCREMENT,

    -- username are up to 20 characters.
    username VARCHAR(20) NOT NULL UNIQUE, 
    email VARCHAR(100) NOT NULL UNIQUE,
    profile_pic VARCHAR(100),

    -- salt will be 8 characters all the time, so we can make this 8
    salt CHAR(8) NOT NULL, 

    -- We use SHA-2 with the 256-bit hasehs. MySQL returns the hash
    -- value as a hexadecimal string, which means that each byte is
    -- represented as 2 characters.  Thus, 256 / 8 * 2 = 64.
    -- We can use BINARY or CHAR here; BINARY simply has a different
    -- definition for comparison/sorting than CHAR.
    password_hash BINARY(64) NOT NULL,

    PRIMARY KEY (user_id)
);

-- Entity set
-- Table to store information about the each city in the country.
-- User to represent cities that are stored in the database. 
CREATE TABLE city_info (
    city_id INT AUTO_INCREMENT,
    city_name VARCHAR(50) NOT NULL,
    state_name VARCHAR(30), 
    country_name VARCHAR(60) NOT NULL,
    population INT NOT NULL,
    fun_fact VARCHAR(300),

    PRIMARY KEY (city_id)
);

-- Relationship set
-- Table to store each user's wishlist of places that they want to go to.
CREATE TABLE wishlist (
    user_id INT, 
    city_id INT,

    -- Time inputted for the use of sorting by most recent for social media
    -- purposes 
    time_inputted TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (user_id, city_id), 

    FOREIGN KEY (user_id) REFERENCES user_info(user_id)
    ON DELETE CASCADE,

    FOREIGN KEY (city_id) REFERENCES city_info (city_id)
    ON DELETE CASCADE
);

-- Entity set
-- Table to store the connection of users with others. Right now, we are
-- thinking about only storing one combination of the connection in the table.
-- e.g: a friendship between user1 and user2 would show up as (user1, user2) or 
-- (user2, user1), but not both.
CREATE TABLE connections (
    user_id1 INT,
    user_id2 INT, 

    PRIMARY KEY (user_id1, user_id2),

    FOREIGN KEY (user_id1) REFERENCES user_info (user_id)
    ON DELETE CASCADE,

    FOREIGN KEY (user_id2) REFERENCES user_info (user_id)
    ON DELETE CASCADE
);

-- Entity set
-- Table to store all of the visits that people have gone on. 
-- Holds information about where a user went and for how long, and a review and
-- rating that ranges from 0.0 - 10.0. 
CREATE TABLE visits (

    -- primary key for visited, is unique to each visit
    visit_id INT AUTO_INCREMENT, 

    -- foreign key that references user_info
    user_id INT NOT NULL,

    -- foreign key that references city_info
    city_id INT NOT NULL,

    review_text VARCHAR(300),
    rating NUMERIC(10,2) NOT NULL,

    -- start and end date that can be used to calculate who you've overlapped
    -- with on visits, how long your stay was, etc. 
    start_date DATE NOT NULL, 
    end_date DATE NOT NULL,

    -- can be used to sort for the most recent posts when turned into a social
    -- media page
    time_inputted TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (visit_id),

    FOREIGN KEY (user_id) REFERENCES user_info (user_id)
    ON DELETE CASCADE,

    FOREIGN KEY (city_id) REFERENCES city_info (city_id)
    ON DELETE CASCADE,

    CHECK (rating BETWEEN 0 and 10)
);

-- tables so that there can be multiple pictures per visit
CREATE TABLE pictures (
    visit_id INT, 
    picture VARCHAR(100),

    PRIMARY KEY (visit_id, picture),

    FOREIGN KEY (visit_id) REFERENCES visits(visit_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE    
);

-- for when we want to query all of a user's cities they want to visit
CREATE INDEX idx_user_wishlist ON wishlist(user_id);

-- for when we wantt o query all of the users who have a certain city on their
-- wishlist
CREATE INDEX idx_city_wishlist ON wishlist(city_id);

-- For when we want to see all of the cities in a specific country
CREATE INDEX idx_city_country ON city_info(country_name);
