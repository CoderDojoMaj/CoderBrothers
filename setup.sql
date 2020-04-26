CREATE USER IF NOT EXISTS 'coderbrothers'@'localhost' IDENTIFIED BY 'coderbrothers';
DROP DATABASE IF EXISTS coderbrothers;
CREATE DATABASE coderbrothers;

CREATE TABLE coderbrothers.users(
   id INT NOT NULL AUTO_INCREMENT,
   passwd INT NOT NULL,
   nombre VARCHAR(40) NOT NULL,
   foto LONGBLOB,
   perms INT NOT NULL DEFAULT 0,
   PRIMARY KEY ( id )
);

CREATE TABLE coderbrothers.posts(
   id INT NOT NULL AUTO_INCREMENT,
   file VARCHAR(100) NOT NULL,
   author INT NOT NULL,
   PRIMARY KEY ( id ),
   FOREIGN KEY ( author ) REFERENCES coderbrothers.users(id) 
);

CREATE TABLE coderbrothers.comments(
   id INT NOT NULL AUTO_INCREMENT,
   userid INT NOT NULL,
   postid INT NOT NULL,
   content TEXT NOT NULL,
   timestamp TIMESTAMP NOT NULL,
   PRIMARY KEY ( id ),
   FOREIGN KEY ( userid ) REFERENCES coderbrothers.users(id),
   FOREIGN KEY ( postid ) REFERENCES coderbrothers.posts(id)
);

GRANT ALL PRIVILEGES ON coderbrothers.* TO 'coderbrothers'@'localhost' WITH GRANT OPTION;
