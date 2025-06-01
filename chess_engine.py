import math
import random
from bulletchess import *
from dataclasses import dataclass

from base_engine import BaseEngine

@dataclass
class EngineConfig:
    max_depth: int = 4
    use_alpha_beta: bool = True
    eval_scaling: int = 1000
    log: bool = False

class ChessEngine(BaseEngine):
    def __init__(self, player: str, config: EngineConfig = EngineConfig()):
        super().__init__(player)
        self.config = config
        self.counter = 0
        self.limit = 500
            
    def terminal(self, board: Board):
        if board in CHECKMATE:
            winner = board.turn.opposite
            utility = self.config.eval_scaling if winner == self.max_player else -self.config.eval_scaling
            return True, utility
        if board in DRAW:
            return True, 0
        
        if board in STALEMATE:
            return True, 0
        
        if board in THREEFOLD_REPETITION:
            return True, 0
        
        if board in INSUFFICIENT_MATERIAL:
            return True, 0
        
        if board in FIFTY_MOVE_TIMEOUT:
            return True, 0
        
        if board in FIVEFOLD_REPETITION:
            return True, 0
        
        if board in SEVENTY_FIVE_MOVE_TIMEOUT:
            return True, 0
        
        return False, None
    
    
    def evaluate(self, board:Board):
        score = 0
        is_terminal, utility = self.terminal(board)
        if is_terminal:
            return utility
        
        score += self.material_score(board)
        score += self.center_control(board)
        score += self.mobility_score(board)
        score += self.development_score(board)
        score += self.king_safety(board)
        # score += self.pawn_structure_score(board)
        score += self.threat_score(board)
        return score 
        
    
    def minimax(self, board:Board, depth:int, alpha:float, beta:float):
        
        if depth == self.config.max_depth:
            return self.evaluate(board)
        
        is_terminal, _ = self.terminal(board)
        if is_terminal:
            return self.evaluate(board)
        
        legal_moves = board.legal_moves()
        
        if not legal_moves:
            return self.evaluate(board)
        
        is_max_player = self.max_player == board.turn
        best_score = -math.inf if is_max_player else math.inf
        
        for move in legal_moves:
            board_copy = board.copy()
            board_copy.apply(move)
            child_score = self.minimax(board_copy, depth + 1, alpha, beta)
        
            if is_max_player:
                best_score = max(best_score, child_score)
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break
            else:
                best_score = min(best_score, child_score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
                
        return best_score
    
        
    def select_move(self, board: Board):
        best_score = -math.inf
        best_move = None

        for move in board.legal_moves():
            board_copy = board.copy()
            board_copy.apply(move)
            score = self.minimax(board_copy, 1, -math.inf, math.inf)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move
        
    
    def material_score(self, board:Board) -> int:
        piece_values = {
            'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0  # lowercase for black
        }
        score = 0
        for char in board.fen().split()[0]:
            if char.isalpha():
                val = piece_values[char.lower()]
                if char.isupper():
                    score += val  # white piece
                else:
                    score -= val  # black piece
        return score if self.max_player == WHITE else -score

    def mobility_score(self, board: Board) -> int:
        my_moves = len(board.legal_moves())
        
        board.turn = board.turn.opposite  # Flip temporarily
        opponent_moves = len(board.legal_moves())
        board.turn = board.turn.opposite  # Flip back

        return (my_moves - opponent_moves) * 0.1  # weight as needed
    
    def center_control(self, board:Board):
        center_squares = ['D4', 'D5', 'E4', 'E5']
        bonus = 0
        for sq in center_squares:
            piece = board[Square.from_str(sq)]
            if piece:
                if (str(piece).isupper() and self.max_player == WHITE) or (str(piece).islower() and self.max_player == BLACK):
                    bonus += 0.3
                else:
                    bonus -= 0.3
        return bonus
    
    def development_score(self, board: Board) -> float:
        dev_bonus = 0
        initial_squares_white = ["B1", "G1", "C1", "F1"]  # Knights and bishops
        initial_squares_black = ["B8", "G8", "C8", "F8"]
        
        dev_squares = initial_squares_white if self.max_player == WHITE else initial_squares_black

        for sq in dev_squares:
            piece = board[Square.from_str(sq)]
            if piece:
                if ((str(piece).lower() in ['n', 'b']) and
                ((piece.color == WHITE and self.max_player == WHITE) or
                    (piece.color == BLACK and self.max_player == BLACK))):
                    dev_bonus -= 0.25  # Undeveloped
        return dev_bonus
    
    def king_safety(self, board: Board) -> float:
        king_square = board[KING]
        files = ['C', 'D', 'E', 'F', 'G']
        rank = '1' if self.max_player == WHITE else '8'
        
        safe_zone = [Square.from_str(f + rank) for f in files]
        
        if king_square in safe_zone:
            return 0.5  # Reward being castled or centralized
        
        return -0.5  # Penalize exposed king
    
    # def pawn_structure_score(self, board: Board) -> float:
    #     pawn_files = {f: 0 for f in 'abcdefgh'}
    #     for sq in Square:
    #         piece = board[sq]
    #         if piece and piece.name == 'p':
    #             file = sq.file
    #             is_mine = (piece.color == WHITE and self.max_player == WHITE) or \
    #                     (piece.color == BLACK and self.max_player == BLACK)
    #             if is_mine:
    #                 pawn_files[file] += 1
                    
    #     score = 0
    #     for count in pawn_files.values():
    #         if count > 1:
    #             score -= 0.2 * (count - 1)  # Penalize doubled pawns
    #         if count == 0:
    #             score -= 0.1  # Penalize isolated files

    #     return score
    
    def threat_score(self, board: Board) -> float:
        score = 0
        for move in board.legal_moves():
            if move.is_capture(board):
                captured_piece = board[move.destination]
                if captured_piece:
                    value = self.material_value(str(captured_piece))
                    score += value * 0.3
            
        return score
    
    def material_value(self, piece: str) -> float:
        return {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}.get(piece.lower(), 0)

