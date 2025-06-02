from bulletchess import WHITE, Board, Move
from base_engine import BaseEngine
from typing import Tuple, List
from pathlib import Path


class Game:

    @staticmethod
    def play_match(engine_white: BaseEngine, engine_black: BaseEngine, start_board: Board = None) -> Tuple[Board, List[Move]]:
        board = start_board or Board()
        move_history = []

        while True:
            engine = engine_white if board.turn == WHITE else engine_black
            move = engine.select_move(board)
            board.apply(move)
            
            if board.turn == WHITE:
                engine.get_html_board(board)
            
            
            move_history.append(move)
            print(board.fullmove_number)
            is_terminal, _ = engine_white.terminal(board)  # or engine_black.terminal(board)
            if is_terminal:
                engine_white.get_html_board(board)
                break

        return board, move_history
    
    @staticmethod
    def export_pgn(move_history: List[Move], filename: str = "game.pgn", start_board: Board = None):
        board = start_board or Board()
        pgn_moves = []
        move_number = 1

        for i, move in enumerate(move_history):
            if board.turn == WHITE:
                pgn_moves.append(f"{move_number}. {move.san(board)}")
            else:
                pgn_moves[-1] += f" {move.san(board)}"
                move_number += 1
            board.apply(move)

        with open(filename, "w") as file:
            file.write(" ".join(pgn_moves))