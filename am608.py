from pingv4 import AbstractBot, ConnectFourBoard

class Am608(AbstractBot):
  """
  This will be your Connect4 bot.
  CHANGE THE CLASS NAME TO your snu net id.
  """
  
  @property
  def strategy_name(self) -> str:
    return "Your Strategy Name"

  @property
  def author_name(self) -> str:
    return "Your Name"

  @property
  def author_netid(self) -> str:
    return "Your NetID"

  def get_move(self, board: ConnectFourBoard) -> int:
    valid_moves = board.get_valid_moves()
    # This is an example of just picking the first valid move.
    return valid_moves[0] # You should improve this!
  
  # Test against built-in MinimaxBot
from pingv4 import MinimaxBot
game = Connect4Game(player1=Bot, player2=MinimaxBot)
game.run()