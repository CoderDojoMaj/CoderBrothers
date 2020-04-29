CREATE USER IF NOT EXISTS 'coderbrothers'@'localhost' IDENTIFIED BY 'coderbrothers';
DROP DATABASE IF EXISTS coderbrothers;
CREATE DATABASE coderbrothers;

CREATE TABLE coderbrothers.users(
   uuid CHAR(36) NOT NULL UNIQUE,
   passwd BINARY(32) NOT NULL,
   name VARCHAR(40) NOT NULL UNIQUE,
   name_low VARCHAR(40) NOT NULL UNIQUE,
   img LONGBLOB,
   perms INT NOT NULL DEFAULT 0,
   PRIMARY KEY ( uuid )
);

CREATE TABLE coderbrothers.posts(
   uuid CHAR(36) NOT NULL UNIQUE,
   author CHAR(36) NOT NULL,
   title TEXT NOT NULL,
   content TEXT NOT NULL,
   timestamp TIMESTAMP NOT NULL,
   PRIMARY KEY ( uuid ),
   FOREIGN KEY ( author ) REFERENCES coderbrothers.users(uuid) 
);

CREATE TABLE coderbrothers.comments(
   uuid CHAR(36) NOT NULL UNIQUE,
   userid CHAR(36) NOT NULL,
   postid CHAR(36) NOT NULL,
   content TEXT NOT NULL,
   timestamp TIMESTAMP NOT NULL,
   PRIMARY KEY ( uuid ),
   FOREIGN KEY ( userid ) REFERENCES coderbrothers.users(uuid),
   FOREIGN KEY ( postid ) REFERENCES coderbrothers.posts(uuid)
);

CREATE TABLE coderbrothers.sessions(
   uuid CHAR(36) NOT NULL UNIQUE,
   userid CHAR(36) NOT NULL,
   expiry TIMESTAMP NOT NULL,
   PRIMARY KEY ( uuid ),
   FOREIGN KEY ( userid ) REFERENCES coderbrothers.users(uuid)
);

GRANT ALL PRIVILEGES ON coderbrothers.* TO 'coderbrothers'@'localhost' WITH GRANT OPTION;
