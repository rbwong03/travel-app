CREATE USER IF NOT EXISTS 'appadmin'@'localhost' IDENTIFIED BY 'adminpw';
CREATE USER IF NOT EXISTS 'appclient'@'localhost' IDENTIFIED BY 'userpw';
-- Can add more users or refine permissions
GRANT ALL PRIVILEGES ON traveldb.* TO 'appadmin'@'localhost';
GRANT SELECT ON traveldb.* TO 'appclient'@'localhost';
FLUSH PRIVILEGES;
