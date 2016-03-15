DROP DATABASE IF EXISTS hephaestus;
CREATE DATABASE hephaestus;
\c hephaestus;

CREATE TABLE user
(
    UserID INT NOT NULL,
    Username VARCHAR(20) NOT NULL,
    Email VARCHAR(60),
    DispEmail BOOLEAN DEFAULT False,
    PRIMARY KEY (UserID),
);

/* ???
CREATE TABLE username
(
    UserID INT NOT NULL,
    
    FOREIGN KEY UserID REFERENCES user(UserID)
);
*/

CREATE TABLE world
(
    WorldID INT NOT NULL,
    CreatorID INT NOT NULL,
    Name VARCHAR(30) DEFAULT "Unnamed",
    Private BOOLEAN DEFAULT False,
    PRIMARY KEY (WorldID),
    FOREIGN KEY CreatorID REFERENCES user(UserID)
);

CREATE TABLE userworlds
(
    WorldID INT NOT NULL,
    UserID INT NOT NULL,
    Role VARCHAR(15) DEFAULT "Editor",
    FOREIGN KEY WorldID REFERENCES world(WorldID)
);

CREATE TABLE article
(
    RecordID INT NOT NULL,
    WorldID INT NOT NULL,
    Name VARCHAR(50) DEFAULT "Unnamed",
    Body TEXT,
    PRIMARY KEY (RecordID),
    FOREIGN KEY (WorldID) REFERENCES world(WorldID)
);

CREATE TABLE password
(
    ID INT NOT NULL,
    Salt VARCHAR(128) NOT NULL,
    Password TEXT NOT NULL,
    FOREIGN KEY ID REFERENCES user(UserID)
);