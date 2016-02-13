# Subject 'Swiss Tournament System' from Udacity

### Last test is to assume that we have 16 players and the result is:

* 1 player with 4 points - the winner!
* 4 players with 3 points - tied for second place
* 6 players with 2 points
* 4 players with 1 point
* 1 player with 0 points

### How to run this

1. Clone repository from the Github.
2. Run command and go to 'tournament' folder.
3. Make sure you have installed vagrant and virtualBox.
4. Run 'vagrant up', then run 'vagrant ssh'.
5. Run 'psql' on command line, then run '\i tournament.sql' to create database schema.
6. Run '\q' to exit psql mode.
7. Run 'python tournament_test.py'.