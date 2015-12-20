-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
CREATE DATABASE tournament;
\c tournament;

CREATE SEQUENCE player_id START WITH 1;

CREATE TABLE players (
    p_id    varchar(3),
    p_name  text
);

CREATE TABLE match_record (
    p_id    varchar(3),
    m_record text
);