from pingv4 import Connect4Game, RandomBot, MinimaxBot
from submissions.mukesh_mp282 import MP282

def main():
    print("Connect Four: RandomBot vs MP282")
    input("Press Enter to start")

    game = Connect4Game(
        player1=RandomBot,
        player2=MP282
    )

    game.run()

if __name__ == "__main__":
    main()
