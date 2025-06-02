from bulletchess import Board, Move
from stockfish import Stockfish

from base_engine import BaseEngine


class StockfishBot(BaseEngine):
    def __init__(self, player):
        super().__init__(player)
        self.stockfish = Stockfish()
    def select_move(self, board: Board):
        self.stockfish.set_fen_position(board.fen())
        return Move.from_uci(self.stockfish.get_best_move())
        
    
