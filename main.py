from base_engine import BaseEngine
from chess_engine import ChessEngine, EngineConfig
from bulletchess import Board, WHITE, BLACK

from game import Game
from random_bot import RandomBot

config = EngineConfig(max_depth=4)
minimax_bot = ChessEngine(WHITE, config)

random_bot = RandomBot(BLACK)
board, move_history = Game.play_match(minimax_bot, random_bot, Board())
print(board.fen())
Game.export_pgn(move_history)

    