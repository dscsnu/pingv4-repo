"""
Test your bot against different opponents
"""

from pingv4 import Connect4Game, MinimaxBot, RandomBot
from unbeatable_bot import UnbeatableBot

def main():
    print("=" * 60)
    print("TESTING YOUR UNBEATABLE BOT")
    print("=" * 60)
    
    # Test 1: Your bot vs Random Bot (should win easily)
    print("\n🎮 Test 1: Your Bot (Red) vs Random Bot (Yellow)")
    print("-" * 60)
    game = Connect4Game(player1=UnbeatableBot, player2=RandomBot)
    game.run()
    
    # Test 2: Your bot vs Built-in Minimax Bot
    print("\n🎮 Test 2: Your Bot (Red) vs MinimaxBot (Yellow)")
    print("-" * 60)
    game = Connect4Game(player1=UnbeatableBot, player2=MinimaxBot)
    game.run()
    
    # Test 3: Your bot vs Yourself (Human)
    print("\n🎮 Test 3: Human (Red) vs Your Bot (Yellow)")
    print("-" * 60)
    game = Connect4Game(player1=None, player2=UnbeatableBot)
    game.run()

if __name__ == "__main__":
    main()
