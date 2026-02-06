import time
import math
from pingv4 import AbstractBot, ConnectFourBoard, CellState

class dp449(AbstractBot):
    def __init__(self, player: CellState):
        super().__init__(player)
        # Transposition Table (Caches millions of board states)
        self.tt = {} 
        self.start_time = 0
        self.nodes = 0
        # MAX THINKING TIME: 9.5s (Safe buffer for 10s limit)
        # This allows the bot to reach Depth 20+ in endgame
        self.time_limit = 9.5 
        
        # Move Ordering: Center -> Outwards (Best for Alpha-Beta pruning)
        self.column_order = [3, 2, 4, 1, 5, 0, 6]

    @property
    def strategy_name(self) -> str:
        return "The Annihilator"

    @property
    def author_name(self) -> str:
        return "Divyansh"

    @property
    def author_netid(self) -> str:
        return "dp449"

    def get_move(self, board: ConnectFourBoard) -> int:
        self.start_time = time.time()
        self.nodes = 0
        
        # 1. Memory Management (Prevent crash on long games)
        if len(self.tt) > 5_000_000: self.tt = {}

        # 2. Parse Board to High-Speed Integers (Bitboard)
        # position = my pieces (1s)
        # mask = all pieces (1s)
        position, mask = self.parse_board(board)
        
        # 3. Reflex Layer: Instant Win Check
        # Before searching, check if we can win RIGHT NOW.
        valid_moves = self.get_valid_moves_bits(mask)
        for col in valid_moves:
             if self.can_win(position, mask, col):
                 return col
        
        # 4. Iterative Deepening Search
        # Search Depth 1, then 2, then 3... until time runs out.
        # This ensures we always have a valid move ready.
        best_move = valid_moves[0] if valid_moves else 0
        
        # Max theoretical depth is 42. We will likely hit ~18-22.
        for depth in range(1, 43):
            try:
                # Call the Bitboard Negamax Solver
                score, move = self.negamax(position, mask, depth, -math.inf, math.inf)
                
                # Update best move if we completed the search level
                if move != -1:
                    best_move = move
                
                # Time Check
                if time.time() - self.start_time > self.time_limit:
                    break
                
                # If we found a Forced Win (Mate), stop searching to save CPU.
                if score > 5000:
                    break
                    
            except TimeoutError:
                break
        
        return best_move

    # -------------------------------------------------------------------------
    # BITBOARD ENGINE (Runs ~1000x faster than standard Python bots)
    # -------------------------------------------------------------------------
    
    def negamax(self, position, mask, depth, alpha, beta):
        # Optimization: Check time every 8192 nodes (fast bitwise AND)
        self.nodes += 1
        if (self.nodes & 0x1FFF) == 0:
            if time.time() - self.start_time > self.time_limit:
                raise TimeoutError

        # 1. Transposition Table Lookup
        tt_entry = self.tt.get((position, mask))
        if tt_entry:
            tt_depth, tt_flag, tt_val = tt_entry
            # Only use cached result if it was searched deeper or equal to current requirement
            if tt_depth >= depth:
                if tt_flag == 0: return tt_val, -1        # EXACT SCORE
                elif tt_flag == 1: alpha = max(alpha, tt_val) # LOWERBOUND
                elif tt_flag == 2: beta = min(beta, tt_val)   # UPPERBOUND
                if alpha >= beta: return tt_val, -1

        # 2. Draw Check (Board Full)
        if mask == 0b111111011111101111110111111011111101111110111111:
            return 0, -1

        # 3. Leaf Node (Max Depth Reached)
        if depth == 0:
            return self.score_position(position, mask), -1

        # 4. Move Generation
        best_score = -math.inf
        best_move = -1
        
        # Opponent's position for the next recursive step is (mask ^ position)
        opp_position = position ^ mask
        
        # Search center columns first to maximize Alpha-Beta pruning
        for col in [3, 2, 4, 1, 5, 0, 6]:
            # Check if column is valid (Top bit must be 0)
            if (mask & (1 << (col * 7 + 5))) == 0:
                
                # Calculate Move Bit (First 0 bit in the column)
                idx = col * 7
                while (mask >> idx) & 1:
                    idx += 1
                
                move_bit = 1 << idx
                new_position = position | move_bit
                
                # Check Win *Before* Recursion
                # This is a huge speedup. If this move wins, we don't need to search deeper.
                if self.is_win(new_position):
                    self.tt[(position, mask)] = (depth, 0, 10000 + depth)
                    return 10000 + depth, col
                
                # Recursive Step
                # Swap roles: Pass opp_position as 'me', and -beta, -alpha
                score, _ = self.negamax(opp_position, mask | move_bit, depth - 1, -beta, -alpha)
                score = -score
                
                if score > best_score:
                    best_score = score
                    best_move = col
                
                alpha = max(alpha, score)
                if alpha >= beta:
                    break # Pruning (Beta Cutoff)

        # 5. Store in TT
        flag = 0 # Exact
        if best_score <= alpha: flag = 2 # Upperbound
        elif best_score >= beta: flag = 1 # Lowerbound
        
        self.tt[(position, mask)] = (depth, flag, best_score)
        return best_score, best_move

    def score_position(self, position, mask):
        """
        Hyper-Aggressive Evaluation.
        1. Heavily rewards Center Control.
        2. "The Punisher" logic: Penalizes opponent's 3-in-a-row threats implicitly via search.
        """
        score = 0
        opp = position ^ mask
        
        # Center Column (Col 3: Bits 21-26)
        # We reward pieces here heavily because they control the board.
        my_center = bin(position & 0x7E00000).count('1')
        opp_center = bin(opp & 0x7E00000).count('1')
        score += (my_center * 8) - (opp_center * 8)
        
        # Inner Columns (Cols 2,4: Bits 14-19, 28-33)
        inner_mask = 0x3F000FC000
        my_inner = bin(position & inner_mask).count('1')
        opp_inner = bin(opp & inner_mask).count('1')
        score += (my_inner * 4) - (opp_inner * 4)
        
        return score

    # -------------------------------------------------------------------------
    # BITWISE UTILITIES
    # -------------------------------------------------------------------------

    def parse_board(self, board):
        """Converts slow object board to fast integers."""
        position = 0
        mask = 0
        for c in range(7):
            for r in range(6):
                cell = board[c, r]
                if cell is not None:
                    idx = c * 7 + r
                    mask |= (1 << idx)
                    if cell == self.player:
                        position |= (1 << idx)
        return position, mask

    def get_valid_moves_bits(self, mask):
        return [c for c in [3, 2, 4, 1, 5, 0, 6] if (mask & (1 << (c * 7 + 5))) == 0]

    def can_win(self, position, mask, col):
        idx = col * 7
        while (mask >> idx) & 1: idx += 1
        return self.is_win(position | (1 << idx))

    def is_win(self, pos):
        """
        Bitwise Win Check (O(1) complexity).
        Checks horizontal, vertical, and diagonal alignments in parallel.
        """
        # 
        # Horizontal (Shift 7)
        m = pos & (pos >> 7)
        if m & (m >> 14): return True
        # Vertical (Shift 1)
        m = pos & (pos >> 1)
        if m & (m >> 2): return True
        # Diagonal / (Shift 8)
        m = pos & (pos >> 8)
        if m & (m >> 16): return True
        # Diagonal \ (Shift 6)
        m = pos & (pos >> 6)
        if m & (m >> 12): return True
        return False