DROP DATABASE IF EXISTS hephaestus;
CREATE DATABASE hephaestus;
\c hephaestus;

CREATE TABLE member
(
    UserID SERIAL NOT NULL,
    Username VARCHAR(20) NOT NULL,
    Email VARCHAR(60),
    DispEmail BOOLEAN DEFAULT False,
    PRIMARY KEY (UserID)
);

CREATE TABLE world
(
    WorldID SERIAL NOT NULL,
    CreatorID SERIAL NOT NULL,
    Name VARCHAR(30) DEFAULT 'Unnamed',
    Private BOOLEAN DEFAULT False,
    PRIMARY KEY (WorldID),
    FOREIGN KEY (CreatorID) REFERENCES member(UserID)
);

CREATE TABLE genre
(
    WorldID SERIAL NOT NULL,
    Genre VARCHAR(20),
    FOREIGN KEY (WorldID) REFERENCES world(WorldID)
);

CREATE TABLE userworlds
(
    WorldID SERIAL NOT NULL,
    UserID SERIAL NOT NULL,
    Role VARCHAR(15) DEFAULT 'Editor',
    FOREIGN KEY (WorldID) REFERENCES world(WorldID)
);

CREATE TABLE article
(
    RecordID SERIAL NOT NULL,
    WorldID SERIAL NOT NULL,
    Name VARCHAR(50) DEFAULT 'Unnamed',
    Body TEXT,
    PRIMARY KEY (RecordID),
    FOREIGN KEY (WorldID) REFERENCES world(WorldID)
);

CREATE TABLE password
(
    PassID SERIAL NOT NULL,
    Salt VARCHAR(128) NOT NULL,
    Password TEXT NOT NULL,
    FOREIGN KEY (PassID) REFERENCES member(UserID)
);

CREATE USER heph WITH PASSWORD '4SrGY9gPFU72aJxh';
GRANT SELECT, INSERT, UPDATE ON member, world, genre, userworlds, article, password TO heph;