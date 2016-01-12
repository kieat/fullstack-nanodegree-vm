#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import re

def connect(db_name='tournament'):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    db = psycopg2.connect("dbname={}".format(db_name))
    cursor = db.cursor()
    return db,cursor

def is_select(q):
    if q.upper().find('SELECT',0,6) == 0:
      return True
    else:
      return False

def query(q,v=''):
    """To execute SQL query of (C)INSERT,(U)UPDATE,(D)DELETE, as these just return that is if successful or not, and number of affected row(s)."""
    """To execute SQL query of (R)SELECT, and returns list of fetched records."""
    db,cursor = connect()
    
    if is_select(q) == True:
      result,row_count = [],0
    else:
      result,row_count = False,0
    
    try:
      cursor.execute(q,v)
      row_count = cursor.rowcount
      
      if is_select(q) == True:
        result = cursor.fetchall()
      else:
        if row_count > 0:
          result = True
    except psycopg2.Error as e:
      print e.pgerror
    except:
      print('<unexpected error>',q,v,result,row_count,)
    finally:
      cursor.connection.commit()
      db.close()
      return result,row_count
    
def deleteMatches():
    """Remove all the match records from the database."""
    query('DELETE FROM matches;')

def deletePlayers():
    """Remove all the player records from the database."""
    query('DELETE FROM players;')
    query('ALTER SEQUENCE player_id RESTART WITH 1;')

def countPlayers():
    """Returns the number of players currently registered."""
    result = query('SELECT count(*) FROM players;')[0]
    
    return result[0][0]
    
def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    result = query("SELECT nextval('player_id');")[0]
    max_id = result[0][0]
    
    q = 'INSERT INTO players (id,name,score,rounds) VALUES (%s,%s,%s,%s);'
    v = (max_id,name,0,0)
    query(q,v)
    
def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    players = query('SELECT id,name,score,rounds FROM players ORDER BY score DESC,id;')[0]
    standings = []
    
    if players == []:
      return []
    
    for player in players:
      standings.append((player[0],player[1],player[2],player[3],))
    
    return standings
    
def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    row_count = query('INSERT INTO matches (winner,loser) values (%s,%s)',(winner,loser))[1]
    assert(row_count == 1),'failed to insert result of this match'
    
    #To pre-select players' score and number of rounds
    players = query('SELECT id,score,rounds FROM players WHERE id = %s or id = %s;',(winner,loser,))[0]
    #To define scores for winner and loser
    scores = {winner:1,loser:0}
    
    for player in players:
      #column(score)  -add 1 to winner,otherwise 0
      #column(rounds) -add 1 to both players
      query('UPDATE players SET score = %s , rounds = %s WHERE id = %s;',(player[1] + scores[player[0]], player[2] + 1, player[0],))
    
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    pairings = []
    
    standings = playerStandings()
    assert(len(standings) % 2 == 0),'number of players is not even.'
    
    #append tuples
    i = 0
    while i < len(standings):
      pairings.append((standings[i][0],standings[i][1],standings[i+1][0],standings[i+1][1],))
      i += 2
    
    return pairings