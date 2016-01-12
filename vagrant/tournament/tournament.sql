-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

--use this sequence,thus players' id could restart with 1 after deleting all players
CREATE SEQUENCE player_id IF NOT EXISTS START WITH 1;

CREATE TABLE players (
    id    INTEGER PRIMARY KEY, --player's id
    name  text NOT NULL,       --player's name
    score INTEGER,
    rounds INTEGER
);

CREATE TABLE matches (
    id    SERIAL PRIMARY KEY,  --automatically increase
    winner INTEGER REFERENCES players(id) ON DELETE CASCADE ON UPDATE CASCADE,
    loser INTEGER REFERENCES players(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CHECK (winner <> loser)
);