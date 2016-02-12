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

CREATE TABLE players (
    id    SERIAL PRIMARY KEY, --player's id
    name  text NOT NULL       --player's name
);

CREATE TABLE matches (
    id    SERIAL PRIMARY KEY,  --automatically increase
    winner INTEGER REFERENCES players(id) ON DELETE CASCADE ON UPDATE CASCADE,
    loser INTEGER REFERENCES players(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CHECK (winner <> loser)
);

CREATE VIEW win_tracker
AS
  SELECT players.id,
         players.name,
         count(matches) AS wins
  FROM players
       LEFT JOIN matches
              ON players.id = matches.winner
  GROUP BY players.id;

CREATE VIEW match_tracker
AS
  SELECT players.id,
         players.name,
         count(matches) AS matches_played
  FROM players
       LEFT JOIN matches
              ON players.id = matches.winner
                 OR players.id = matches.loser
  GROUP BY players.id;

CREATE VIEW standings
AS
  SELECT win_tracker.id,
         win_tracker.name,
         win_tracker.wins,
         match_tracker.matches_played
  FROM win_tracker
       LEFT JOIN match_tracker
              ON win_tracker.id = match_tracker.id
  ORDER BY win_tracker.wins DESC;