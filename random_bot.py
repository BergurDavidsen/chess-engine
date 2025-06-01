import random

from bulletchess import Board

from base_engine import BaseEngine

class RandomBot(BaseEngine):
    def select_move(self, board: Board):
        legal_moves = board.legal_moves()
        return random.choice(legal_moves)
