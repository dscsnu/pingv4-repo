from pingv4 import Connect4Game, MinimaxBot, RandomBot

from la390_algorithm import lokkesh



# Options for players: MyBot, None (for Human), MinimaxBot, RandomBot

game = Connect4Game(player1=lokkesh, player2=RandomBot)



game.run()
