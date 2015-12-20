1. clone repository from the Github.
2. Run command and go to 'tournament' folder.
3. Make sure you have installed vagrant and virtualBox.
4. Run 'vagrant up', then run 'vagrant ssh'.
5. Run 'psql' on command line, then run '\i tournament.sql' to create database schema.
6. Run '\q' to exit psql mode.
7. Run 'python tournament_test.py'.