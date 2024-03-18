DROP FUNCTION IF EXISTS make_salt;
DROP PROCEDURE IF EXISTS sp_add_user;
DROP PROCEDURE IF EXISTS sp_change_password;
DROP FUNCTION IF EXISTS authenticate;


-- This function generates a specified number of characters for using
-- as a salt in passwords.
DELIMITER !
CREATE FUNCTION make_salt(num_chars INT)
RETURNS VARCHAR(20) DETERMINISTIC
BEGIN
    DECLARE salt VARCHAR(20) DEFAULT '';

    -- Don't want to generate more than 20 characters of salt.
    SET num_chars = LEAST(20, num_chars);

    -- Generate the salt!  Characters used are ASCII code 32 (space)
    -- through 126 ('z').
    WHILE num_chars > 0 DO
        SET salt = CONCAT(salt, CHAR(32 + FLOOR(RAND() * 95)));
        SET num_chars = num_chars - 1;
    END WHILE;

    RETURN salt;
END !
DELIMITER ;


-- Adds a new user to the users table, using the specified password (max
-- of 20 characters). Salts the password with a newly-generated salt value,
-- and then the salt and hash values are both stored in the table.
DELIMITER !
CREATE PROCEDURE sp_add_user(new_username VARCHAR(20), new_email VARCHAR(100), 
  password VARCHAR(20))
BEGIN
  DECLARE salt VARCHAR(8);
  DECLARE salted_password VARCHAR(40);

  -- creates salt value
  SET salt = make_salt(8);
  SET salted_password = CONCAT(salt, password);

  -- inserts into table
  INSERT INTO user_info(username, email, salt, password_hash)
  VALUES (new_username, new_email, salt, SHA2(salted_password, 256));
END !
DELIMITER ;

-- Authenticates the specified username and password against the data
-- in the users table.  Returns 1 if the user appears in the table, and the
-- specified password hashes to the value for the user. Otherwise returns 0.
DELIMITER !
CREATE FUNCTION authenticate(username VARCHAR(20), password VARCHAR(20))
RETURNS TINYINT DETERMINISTIC
BEGIN
  
  DECLARE authenticated INT;
  DECLARE user_salt VARCHAR(8);
  
  SET authenticated = 0;
  SET user_salt = '';
 
  -- gets the salt from users into user_salt
  SELECT salt INTO user_salt
  FROM user_info
  WHERE user_info.username = username;

  -- only 1 user should have a matching username and password hash
  SELECT COUNT(*) INTO authenticated
  FROM user_info
  WHERE user_info.username = username
  AND SHA2(CONCAT(user_salt, password), 256) = user_info.password_hash;

  IF authenticated = 1 THEN
    return get_user_id(username);
  ELSE
    return 0;
  END IF;

END !
DELIMITER ;

-- Add at least two users into your users table so that when we run this 
-- file, we will have examples users in the database.

CALL sp_add_user('rb', 'ryan@gmail.com', 'password');


-- Create a procedure sp_change_password to generate a new salt and change the 
-- given user's password to the given password (after salting and hashing)
DELIMITER !
CREATE PROCEDURE sp_change_password(username VARCHAR(20), password VARCHAR(20))
BEGIN
  
  DECLARE salt VARCHAR(8);
  DECLARE salted_password VARCHAR(40);

  SET salt = make_salt(8);
  SET salted_password = CONCAT(salt, password);

  UPDATE users
  SET users.salt = salt, users.password_hash = SHA2(salted_password,
  256)
  WHERE username = users.username;

END !
DELIMITER ;

