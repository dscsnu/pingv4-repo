"""
Connect Four Game - Test Your Bot
Author: Aarnav Arya (aa557)
"""

from pingv4 import Connect4Game
from submissions.aarnav_aa557 import aa557

def main():
    """
    Run the Connect Four game.
    Player 1 (Red): Your Bot (aa557)
    Player 2 (Yellow): Human Player
    """
    game = Connect4Game(player1=aa557, player2=None)
    game.run()

if __name__ == "__main__":
    main()
