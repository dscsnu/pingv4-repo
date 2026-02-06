"""
Test runner for pingv4 bots
"""

from pingv4 import Connect4Game, RandomBot, MinimaxBot
from submissions.ae990 import Ae990 as Bot
game = Connect4Game(player1=Bot, player2=MinimaxBot)
game.run()


def main():
  bot = Bot
  print("=" * 50)
  print(f"Testing Bot: {bot.strategy_name}")
  print(f"Author: {bot.author_name} {bot.author_netid}")
  print("=" * 50)
  print()
    # Test 1: Human vs Your Bot
  print("Test: Human vs Your Bot")
  game = Connect4Game(player1=None, player2=Bot)
  game.run()

    # Uncomment if needed

    # Test 2: Your Bot vs Random Bot
    # game = Connect4Game(player1=Bot, player2=RandomBot)
    # game.run()

    # Test 3: Your Bot vs Minimax Bot
    # game = Connect4Game(player1=Bot, player2=MinimaxBot)
    # game.run()


if __name__ == "__main__":
    main()
