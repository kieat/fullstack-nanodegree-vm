#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import re

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")
def exeQ(q,v = ''):
    """Execute SQL query
    
    Args:
      q: SQL query string.
    Returns:
      If fetch nothing, returns None. Otherwise, returns fetched data.
    """
    conn = connect()
    c = conn.cursor()
    result = None
    
    pattern = r"; *$"
    if not re.search(pattern,q):
      q+= ";"
    
    try:
      c.execute(q,v)
    except psycopg2.Error as e:
      print e.pgerror
    except psycopg2.Warning as w:
      print w
    except:
      print 'error'
    
    #print '--> ' + 'running:' + c.mogrify(q,v)
    #print '---> ' + 'rowcount:' + str(c.rowcount) + ' ' + 'rownumber:' + str(c.rownumber)

    try:
      result = c.fetchall()
    except psycopg2.ProgrammingError as pe:
      result = None
    
    #print '----> ' + str(result)
    
    c.connection.commit()
    c.close()
    conn.close()

    return result
    
def deleteMatches():
    """Remove all the match records from the database."""
    exeQ('DELETE FROM match_record;')

def deletePlayers():
    """Remove all the player records from the database."""
    exeQ('DELETE FROM players;')

def countPlayers():
    """Returns the number of players currently registered."""
    p_count = exeQ('SELECT count(*) FROM players;')
    
    p_count = p_count[0][0]
    
    return p_count

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    max_id = exeQ("SELECT nextval('player_id');")
    max_id = str(max_id[0][0])
    
    q = 'INSERT INTO Players (p_id,p_name) VALUES (%s,%s);'
    v = (max_id, name,)
    
    exeQ(q,v)
    
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
    records = exeQ('SELECT p_id,m_record FROM match_record ORDER BY m_record DESC, p_id;')
    players = exeQ('SELECT p_id,p_name FROM players ORDER BY p_id;')
    standings = []
    dict_players = {}
    
    if players == []:
      return []
    
    #convert list to dictionary
    for player in players:
      dict_players[player[0]] = player[1]
    
    #if no records exist, assign 0 to wins,matches
    if records == []:
      for player in players:
        standings.append((player[0],player[1],0,0,))
    #if records exist, count '1' for wins and count all length for matches
    else:
      for record in records:
        standings.append((record[0],dict_players[record[0]],record[1].count('1'),len(record[1]),))

    return standings
    
def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    records = exeQ('SELECT p_id,m_record FROM match_record WHERE p_id = %s or p_id = %s;',(winner,loser,))
    if records == None:
      return
    
    players = [winner,loser]
    scores = {winner:'1',loser:'0'}
    
    #if no records exist, insert new record into database
    if records == []:
      for player in players:
        exeQ('INSERT INTO match_record (p_id,m_record) values (%s,%s);',(player,scores[player],))
    #if records exist, update old record using new one
    else:
      for record in records:
        #update record, if win, concatenate with '1', but with '0'
        #for example, if first and third one are win, '1','1','0','0' => '11','10','01','00'
        exeQ('UPDATE match_record SET m_record = %s WHERE p_id = %s;',(record[1] + scores[record[0]],record[0],))
    
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
    
    #append tuples
    i = 0
    while i < len(standings):
      pairings.append((standings[i][0],standings[i][1],standings[i+1][0],standings[i+1][1],))
      i += 2
    
    return pairings