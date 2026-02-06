from pingv4 import Connect4Game, MinimaxBot, RandomBot
# Make sure your helper file is actually named 'ps950_helper.py'
from ps950_helper import pravin_s 

# Options for players: pravin_s, None (for Human), MinimaxBot, RandomBot
game = Connect4Game(player1=MinimaxBot, player2=pravin_s)

game.run()
