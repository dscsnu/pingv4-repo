from pingv4 import AbstractBot, ConnectFourBoard, CellState
import random
import math
import time

class ss637(AbstractBot):
    """
    Shukhashini's final Bot (Time-Optimized)
    
    STRATEGY:
    1. TIME-AWARE SEARCH: Uses Iterative Deepening to search deep (7-8+ moves) within 7.5s.
    2. PARITY KILLER: Exploits Odd/Even row mathematics (The weakness of vm119 & ac653).
    3. TRAP GUARD: Prevents "suicide moves" that give the opponent an instant win.
    """

    @property
    def strategy_name(self) -> str:
        return "shukhashini unreal bot"

    @property
    def author_name(self) -> str:
        return "Shukhashini Sivakumar Indupriya"

    @property
    def author_netid(self) -> str:
        return "ss637"

    def get_move(self, board: ConnectFourBoard) -> int:
        # 1. Start the Timer
        self.start_time = time.time()
        self.time_limit = 7.5  # Strict 7.5s limit (leaves buffer for safety)

        me = board.current_player
        opp = CellState.Yellow if me == CellState.Red else CellState.Red
        valid_moves = board.get_valid_moves()
        
        if not valid_moves: return 0

        # --- PHASE 1: INSTANT KILL ---
        # If we can win right now, do it.
        for col in valid_moves:
            if board.make_move(col).is_victory:
                return col

        # --- PHASE 2: FORCED SURVIVAL ---
        # If opponent can win on their next turn, we MUST block immediately.
        for col in valid_moves:
            if self.is_winning_spot_for_opponent(board, col, opp):
                return col

        # --- PHASE 3: THE TRAP GUARD ---
        # Filter out moves that act as a "platform" for the opponent to win immediately.
        # This keeps us safe against aggressive bots like ac653.
        safe_moves = []
        for col in valid_moves:
            temp_board = board.make_move(col)
            opponent_can_kill = False
            # Check if this move lets the opponent win immediately
            for opp_col in temp_board.get_valid_moves():
                if temp_board.make_move(opp_col).is_victory:
                    opponent_can_kill = True
                    break
            if not opponent_can_kill:
                safe_moves.append(col)

        # If all moves are bad, we are forced to pick one. Otherwise, strictly use safe moves.
        candidates = safe_moves if safe_moves else valid_moves
        
        # Sort candidates by Center Priority (Critical for Alpha-Beta pruning speed)
        candidates.sort(key=lambda c: -abs(c - 3))

        # --- PHASE 4: TIME-AWARE BRAIN (Iterative Deepening) ---
        best_move_so_far = candidates[0]
        
        try:
            # Start at Depth 1 and go deeper until time runs out.
            # ac653 is fixed at Depth 6. We will try to beat that.
            for depth in range(1, 42):
                if time.time() - self.start_time > self.time_limit:
                    break
                
                # Search this depth
                move, score = self.minimax(board, depth, -math.inf, math.inf, True, me, opp, candidates)
                
                best_move_so_far = move
                
                # Optimization: If we found a guaranteed win, stop searching and play it.
                if score > 900000:
                    return move

        except TimeoutError:
            # If time runs out inside minimax, we catch it here and use the best move found so far.
            pass

        return best_move_so_far

    def is_winning_spot_for_opponent(self, board, col, opp):
        # Quick check: if opponent plays 'col', do they win?
        row = board.column_heights[col]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dc, dr in directions:
            count = 0
            for sign in [1, -1]:
                for i in range(1, 4):
                    c, r = col + (dc * i * sign), row + (dr * i * sign)
                    if 0 <= c < 7 and 0 <= r < 6 and board[c, r] == opp:
                        count += 1
                    else:
                        break
            if count >= 3: return True
        return False

    def minimax(self, board, depth, alpha, beta, maximizing, me, opp, allowed_moves=None):
        # TIME CHECK: Stop immediately if we are out of time
        if (time.time() - self.start_time) > self.time_limit:
            raise TimeoutError()

        valid_moves = allowed_moves if allowed_moves is not None else board.get_valid_moves()
        
        if board.is_victory:
            # Win fast (Higher score), Lose slow (Lower penalty)
            return (None, -10000000 - depth if maximizing else 10000000 + depth)
        if board.is_draw:
            return (None, 0)
        if depth == 0 or not valid_moves:
            return (None, self.evaluate_board(board, me, opp))

        # Move Ordering: Sort Center-Outwards for speed
        valid_moves.sort(key=lambda c: -abs(c - 3))

        if maximizing:
            value = -math.inf
            best_col = valid_moves[0]
            for col in valid_moves:
                next_board = board.make_move(col)
                _, new_score = self.minimax(next_board, depth - 1, alpha, beta, False, me, opp)
                if new_score > value:
                    value = new_score
                    best_col = col
                alpha = max(alpha, value)
                if alpha >= beta: break
            return best_col, value
        else:
            value = math.inf
            best_col = valid_moves[0]
            for col in valid_moves:
                next_board = board.make_move(col)
                _, new_score = self.minimax(next_board, depth - 1, alpha, beta, True, me, opp)
                if new_score < value:
                    value = new_score
                    best_col = col
                beta = min(beta, value)
                if alpha >= beta: break
            return best_col, value

    def evaluate_board(self, board, me, opp):
        score = 0
        
        # FEATURE 1: Center Control
        # vm119 values center at 3. ac653 values it at 6.
        # We value it at 12 to physically dominate the board.
        center_col = [board[3, r] for r in range(6)]
        score += center_col.count(me) * 12
        score -= center_col.count(opp) * 12

        # FEATURE 2: Parity (The "God Slayer")
        # If I am Red (Player 1), I want threats on EVEN rows (0, 2, 4).
        # If I am Yellow (Player 2), I want threats on ODD rows (1, 3, 5).
        # This breaks the opponent's endgame logic.
        parity_target = 0 if me == CellState.Red else 1
        
        for col in range(7):
            row = board.column_heights[col]
            if row < 6:
                # If the next playable spot matches my parity, it is highly valuable
                if row % 2 == parity_target:
                    score += 25 

        # FEATURE 3: Window Scoring
        score += self.scan_board(board, me, opp)

        return score

    def scan_board(self, board, me, opp):
        total_score = 0
        # Horizontal
        for r in range(6):
            for c in range(4):
                total_score += self.evaluate_window([board[c+i, r] for i in range(4)], me, opp)
        # Vertical
        for c in range(7):
            for r in range(3):
                total_score += self.evaluate_window([board[c, r+i] for i in range(4)], me, opp)
        # Diagonals
        for c in range(4):
            for r in range(3):
                total_score += self.evaluate_window([board[c+i, r+i] for i in range(4)], me, opp)
                total_score += self.evaluate_window([board[c+i, r+3-i] for i in range(4)], me, opp)
        return total_score

    def evaluate_window(self, window, me, opp):
        score = 0
        my_count = window.count(me)
        opp_count = window.count(opp)
        empty = window.count(None)

        # OFFENSE
        if my_count == 4: return 1000000
        elif my_count == 3 and empty == 1: score += 200  # Strong threat
        elif my_count == 2 and empty == 2: score += 15

        # DEFENSE (Heavier penalty than ac653)
        # ac653 only penalizes -500. We penalize -9000 to GUARANTEE a block.
        if opp_count == 3 and empty == 1: score -= 9000
        elif opp_count == 2 and empty == 2: score -= 100

        return score