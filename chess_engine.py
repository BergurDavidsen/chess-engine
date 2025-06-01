import math
import random
from bulletchess import *
from dataclasses import dataclass

from base_engine import BaseEngine

@dataclass
class EngineConfig:
    max_depth: int = 20
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
        return False, None
    
    
    def evaluate(self, board:Board):
        is_terminal, utility = self.terminal(board)
        if is_terminal:
            return utility
        return self.material_score(board.fen())
        
    
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
        
    def random_game(self, board):
        with open("fen_strings.txt", "w") as file:
            while True:
                legal_moves = board.legal_moves()
                board.apply(random.choice(legal_moves))
                file.write(f"{board.fen()}\n")
                if self.terminal(board):
                    return board
                if self.counter >= self.config.limit:
                    print("REACHED LIMIT ITERATIONS")
                    print(f"CURRENT BOARD: {board.fen()}")
                    return board
                self.counter += 1
    
    def material_score(self, fen: str) -> int:
        piece_values = {
            'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0  # lowercase for black
        }
        score = 0
        for char in fen.split()[0]:
            if char.isalpha():
                val = piece_values[char.lower()]
                if char.isupper():
                    score += val  # white piece
                else:
                    score -= val  # black piece
        return score if self.max_player == WHITE else -score

        
    def get_html_board(self, board:Board, filename:str = "board"):
        with open(f"{filename}.html", "w") as file:
            file.write(board._repr_html_())