"""
A test runner.

HOW TO USE:
1. Create your bot in submissions/yourname_yournetid.py
2. Change the import line to import YOUR bot
3. Run python main.py
"""

from pingv4 import Connect4Game, MinimaxBot, RandomBot
from submissions import template_bot.py # Change this line to import yourname_yournetid.py

def main():
  bot = Bot
  print("=" * 50)
  print(f"Testing Bot: {bot.strategy_name}")
  print(f"Author: {bot.author_name} {bot.author_netid}")
  print("=" * 50)
  print()

  # Test 1: Human vs Your Bot
  print("Test: Human vs Your Bot")
  input("Press Enter to start")
  game = Connect4Game(player1=None, player2=Bot)
  game.run()

  # Uncomment additional tests

  # Test 3: Your Bot vs Random Bot
  # print("Test: Your Bot vs Random Bot")
  # input("Press Enter to start")
  # game = Connect4Game(player1=Bot, player2=RandomBot")
  # game.run()

  # Test 34: Your Bot vs Minimax Bot
  # print("Test: Your Bot vs Minimax Bot")
  # input("Press Enter to start")
  # game = Connect4Game(player1=Bot, player2=MinimaxBot")
  # game.run()

  # Test 3: Your Bot vs Your Bot
  # print("Test: Your Bot vs Your Bot")
  # input("Press Enter to start")
  # game = Connect4Game(player1=Bot, player2=Bot")
  # game.run()

if __name__ == "__main__":
  main()
