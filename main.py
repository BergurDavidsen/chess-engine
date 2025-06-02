from base_engine import BaseEngine
from chess_engine import ChessEngine, EngineConfig
from bulletchess import Board, WHITE, BLACK

from game import Game
from random_bot import RandomBot
from stockfish_bot import StockfishBot

config = EngineConfig(max_depth=7)
bot1 = ChessEngine(WHITE, config)
bot2 = StockfishBot(BLACK)

board_start = Board()

board_copy = board_start.copy()

# Run the live match
board, move_history = Game.play_match(bot1, bot2, board_start)
Game.export_pgn(move_history, start_board=board_copy)
print(board.fen())



