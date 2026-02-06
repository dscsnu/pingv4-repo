from pingv4 import AbstractBot, ConnectFourBoard, CellState

ROWS = 6
COLS = 7
INF = 10**9
DEPTH = 5
MOVE_ORDER = [3, 2, 4, 1, 5, 0, 6]


class Bot(AbstractBot):
    """
    Rename this class to your NetID before submission.
    """

    @property
    def strategy_name(self) -> str:
        return "AlphaBeta-Minimax"

    @property
    def author_name(self) -> str:
        return "Your Name"

    @property
    def author_netid(self) -> str:
        return "your_netid"

    # ================== MAIN ENTRY ==================

    def get_move(self, board: ConnectFourBoard) -> int:
        ME = board.current_player
        OPP = CellState.Red if ME == CellState.Yellow else CellState.Yellow

        valid_moves = board.get_valid_moves()

        # 1. Instant win
        for col in valid_moves:
            if self._winning_after_move(board, col, ME):
                return col

        # 2. Instant block
        for col in valid_moves:
            if self._winning_after_move(board, col, OPP):
                return col

        # 3. Minimax
        best_score = -INF
        best_move = valid_moves[0]

        for col in MOVE_ORDER:
            if col in valid_moves:
                new_board = board.make_move(col)
                score = self._minimax(
                    new_board, DEPTH - 1, -INF, INF,
                    maximizing=False, ME=ME, OPP=OPP
                )
                if score > best_score:
                    best_score = score
                    best_move = col

        return best_move

    # ================== MINIMAX ==================

    def _minimax(self, board, depth, alpha, beta, maximizing, ME, OPP):
        if depth == 0 or not board.is_in_progress:
            if board.is_victory:
                if board.winner == ME:
                    return INF
                elif board.winner == OPP:
                    return -INF
            return self._evaluate(board, ME, OPP)

        valid_moves = board.get_valid_moves()

        if maximizing:
            value = -INF
            for col in MOVE_ORDER:
                if col in valid_moves:
                    value = max(
                        value,
                        self._minimax(
                            board.make_move(col),
                            depth - 1, alpha, beta, False, ME, OPP
                        )
                    )
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break
            return value

        else:
            value = INF
            for col in MOVE_ORDER:
                if col in valid_moves:
                    value = min(
                        value,
                        self._minimax(
                            board.make_move(col),
                            depth - 1, alpha, beta, True, ME, OPP
                        )
                    )
                    beta = min(beta, value)
                    if alpha >= beta:
                        break
            return value

    # ================== EVALUATION ==================

    def _evaluate(self, board, ME, OPP):
        score = 0

        # Center column control
        center_col = 3
        for r in range(ROWS):
            if board[center_col, r] == ME:
                score += 6
            elif board[center_col, r] == OPP:
                score -= 6

        # Score all windows
        for window in self._all_windows(board):
            score += self._score_window(window, ME)
            score -= int(1.2 * self._score_window(window, OPP))

        return score

    def _score_window(self, window, piece):
        opp = CellState.Red if piece == CellState.Yellow else CellState.Yellow
        piece_count = window.count(piece)
        empty_count = window.count(None)

        if piece_count == 4:
            return 100000
        if piece_count == 3 and empty_count == 1:
            return 100
        if piece_count == 2 and empty_count == 2:
            return 10
        return 0

    # ================== HELPERS ==================

    def _winning_after_move(self, board, col, player):
        new_board = board.make_move(col)
        return new_board.is_victory and new_board.winner == player

    def _all_windows(self, board):
        windows = []

        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                windows.append([board[c + i, r] for i in range(4)])

        # Vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                windows.append([board[c, r + i] for i in range(4)])

        # Diagonal /
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                windows.append([board[c + i, r + i] for i in range(4)])

        # Diagonal \
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                windows.append([board[c + i, r - i] for i in range(4)])

        return windows
