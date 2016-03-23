DROP DATABASE IF EXISTS hephaestus;
CREATE DATABASE hephaestus;
\c hephaestus;

DROP TABLE IF EXISTS member CASCADE;
CREATE TABLE member
(
    UserID SERIAL NOT NULL,
    Username VARCHAR(20) NOT NULL,
    Email VARCHAR(60) NOT NULL,
    DispEmail BOOLEAN DEFAULT False,
    JoinDate DATE NOT NULL,
    PRIMARY KEY (UserID)
);

DROP TABLE IF EXISTS world CASCADE;
CREATE TABLE world
(
    WorldID SERIAL NOT NULL,
    CreatorID SERIAL NOT NULL,
    Name VARCHAR(30) DEFAULT 'Unnamed',
    Private BOOLEAN DEFAULT False,
    PRIMARY KEY (WorldID),
    FOREIGN KEY (CreatorID) REFERENCES member(UserID)
);

DROP TABLE IF EXISTS genre;
CREATE TABLE genre
(
    WorldID SERIAL NOT NULL,
    Genre VARCHAR(20),
    FOREIGN KEY (WorldID) REFERENCES world(WorldID)
);

DROP TABLE IF EXISTS userworlds;
CREATE TABLE userworlds
(
    WorldID SERIAL NOT NULL,
    UserID SERIAL NOT NULL,
    Role VARCHAR(15) DEFAULT 'Editor',
    FOREIGN KEY (WorldID) REFERENCES world(WorldID)
);

DROP TABLE IF EXISTS article;
CREATE TABLE article
(
    RecordID SERIAL NOT NULL,
    WorldID SERIAL NOT NULL,
    Name VARCHAR(50) DEFAULT 'Unnamed',
    Body TEXT,
    PRIMARY KEY (RecordID),
    FOREIGN KEY (WorldID) REFERENCES world(WorldID)
);

DROP TABLE IF EXISTS password;
CREATE TABLE password
(
    PassID SERIAL NOT NULL,
    Salt VARCHAR(128) NOT NULL,
    Password TEXT NOT NULL,
    FOREIGN KEY (PassID) REFERENCES member(UserID)
);

CREATE USER heph WITH PASSWORD '4SrGY9gPFU72aJxh';
GRANT SELECT, INSERT, UPDATE ON member, world, genre, userworlds, article, password TO heph;
GRANT SELECT, USAGE, UPDATE ON SEQUENCE member_userid_seq TO heph;

INSERT INTO member (Username, Email, DispEmail, JoinDate) VALUES ('Marty', 'mmclark317@gmail.com', TRUE, now());
INSERT INTO member (Username, Email, DispEmail, JoinDate) VALUES ('Evan', 'romannumeralii@gmail.com', FALSE, now());