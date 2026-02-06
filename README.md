# pingv4 repo!

This repository uses the [pingv4](https://github.com/dscsnu/pingv4) library for Connect Four gameplay.

---

## Instructions

### 1. Fork and Clone
```bash
# Fork this repo on GitHub (click the Fork button), then:
git clone https://github.com/YOUR_USERNAME/pingv4-competition
cd pingv4-competition
```

### 2. Install pingv4
```bash
pip install pingv4
```

### 3. Create Your Bot
```bash
# Copy the template
cp submissions/template_bot.py submissions/yourname_yournetid.py
```

Edit your bot file:
- Change `strategy_name` to describe your approach
- Fill in your `author_name` and `author_netid`
- Write your AI logic in the `get_move()` method

**IMPORTANT: Change the class name as `your snu net id`!**

### 4. Test Your Bot

Edit `main.py`:
```python
# Change this:
from submissions.template_bot import Bot

# To this (with your filename):
from submissions.yourname_yournetid import YourSNUNetID # For eg. DJ141
```

Run the test:
```bash
python main.py
```

### 5. Submit
```bash
git add submissions/yourname_yournetid.py
git add main.py
git commit -m "Add [Your Name]'s bot: [Strategy Name]"
git push origin main
```

Create a **Pull Request** on GitHub!

---

## Submission Rules

### DO:
- Submit exactly ONE bot file in `submissions/`
- Update the import in `main.py` to your bot
- Change the class name to `your snu net id`
- Test locally before submitting
- Use only pingv4 library and Python standard library

### DON'T:
- Modify other files
- Use external libraries or network calls
- Submit multiple bots in one PR

---

## Bot Development Guide

### Available Board Methods
```python
def get_move(self, board: ConnectFourBoard) -> int:
    # Get valid moves
    valid_moves = board.get_valid_moves()  # Returns list like [0,1,2,3,4,5,6]
    
    # Check whose turn it is
    my_color = board.current_player  # CellState.Red or CellState.Yellow
    
    # Access cells (column, row indexing)
    cell = board[3, 0]  # Bottom of center column
    
    # Simulate future moves
    future_board = board.make_move(3)
    if future_board.is_victory:
        return 3  # Winning move!
    
    # Check column heights
    heights = board.column_heights  # [2, 3, 1, 4, 2, 0, 1]
    
    # Get game state
    board.is_in_progress  # True if game ongoing
    board.winner          # CellState.Red, CellState.Yellow, or None
    
    return your_column_choice
```

---

## Testing Against Other Bots

You can test your bot against others by editing `main.py`:
```python
# Test against built-in MinimaxBot
from pingv4 import MinimaxBot
game = Connect4Game(player1=Bot, player2=MinimaxBot)
game.run()
```

---

## Resources

- **pingv4 Documentation:** [GitHub](https://github.com/dscsnu/pingv4)
- **Minimax Algorithm:** [Wikipedia](https://en.wikipedia.org/wiki/Minimax)

---
