from pingv4 import Connect4Game, RandomBot, MinimaxBot
from submissions.mukesh_mp282 import MP282

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

    game = Connect4Game(
        player1=RandomBot,
        player2=MP282
    )

    game.run()

if __name__ == "__main__":
    main()
