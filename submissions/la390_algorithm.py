from pingv4 import AbstractBot, ConnectFourBoard, CellState
import random

# --- TOURNAMENT CONFIGURATION ---
# We stick to Depth 5 for speed, but our smarter scoring will beat Depth 6.
MAX_DEPTH = 5


class lokkesh(AbstractBot):
    def __init__(self, color):
        super().__init__(color)
        self.transposition_table = {}

    @property
    def strategy_name(self) -> str:
        return "Grandmaster-Paranoid-v6"

    @property
    def author_name(self) -> str:
        return "lokkesh"

    @property
    def author_netid(self) -> str:
        return "lokkesh"

    def get_move(self, board: ConnectFourBoard) -> int:
        me = board.current_player
        # Clear cache every move if memory is an issue, but usually keep it.
        # self.transposition_table = {}

        best_col, score = self.minimax(board, MAX_DEPTH, -float('inf'), float('inf'), True, me)
        return best_col

    def minimax(self, board, depth, alpha, beta, is_maximizing, my_color):
        state_id = board.hash
        if state_id in self.transposition_table:
            stored_depth, stored_score, stored_col = self.transposition_table[state_id]
            if stored_depth >= depth:
                return stored_col, stored_score

        valid_moves = board.get_valid_moves()

        # Check for Immediate Win/Loss
        if board.is_victory:
            if board.winner == my_color:
                return None, 1000000 + depth
            else:
                return None, -1000000 - depth

        if not valid_moves or depth == 0:
            return None, self.score_position(board, my_color)

        # Move Ordering: Check Center First
        center_order = [3, 2, 4, 1, 5, 0, 6]
        ordered_moves = [c for c in center_order if c in valid_moves]

        best_col = ordered_moves[0]

        if is_maximizing:
            max_eval = -float('inf')
            for col in ordered_moves:
                new_board = board.make_move(col)
                _, eval_score = self.minimax(new_board, depth - 1, alpha, beta, False, my_color)

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_col = col
                alpha = max(alpha, eval_score)
                if beta <= alpha: break

            self.transposition_table[state_id] = (depth, max_eval, best_col)
            return best_col, max_eval

        else:
            min_eval = float('inf')
            for col in ordered_moves:
                new_board = board.make_move(col)
                _, eval_score = self.minimax(new_board, depth - 1, alpha, beta, True, my_color)

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_col = col
                beta = min(beta, eval_score)
                if beta <= alpha: break

            self.transposition_table[state_id] = (depth, min_eval, best_col)
            return best_col, min_eval

    def score_position(self, board, piece):
        score = 0

        # 1. Center Control (Bonus)
        center_array = [board[3, i] for i in range(6)]
        center_count = center_array.count(piece)
        score += center_count * 3

        # 2. Horizontal
        for r in range(6):
            row_array = [board[c, r] for c in range(7)]
            for c in range(4):
                window = row_array[c:c + 4]
                score += self.evaluate_window(window, piece)

        # 3. Vertical
        for c in range(7):
            col_array = [board[c, r] for r in range(6)]
            for r in range(3):
                window = col_array[r:r + 4]
                score += self.evaluate_window(window, piece)

        # 4. Diagonal /
        for r in range(3):
            for c in range(4):
                window = [board[c + i, r + i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        # 5. Diagonal \
        for r in range(3, 6):
            for c in range(4):
                window = [board[c + i, r - i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = CellState.Yellow if piece == CellState.Red else CellState.Red

        # --- OFFENSE (My Points) ---
        if window.count(piece) == 4:
            score += 10000  # Win
        elif window.count(piece) == 3 and window.count(None) == 1:
            score += 5  # Good setup
        elif window.count(piece) == 2 and window.count(None) == 2:
            score += 2  # Decent

        # --- DEFENSE (Block Enemy) ---
        # FIX: Massive penalty so we NEVER ignore a threat
        if window.count(opp_piece) == 3 and window.count(None) == 1:
            score -= 80  # CRITICAL DANGER! Must block!

        return score