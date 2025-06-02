import math
import random
from bulletchess import *
from bulletchess import utils
from dataclasses import dataclass

from base_engine import BaseEngine


@dataclass
class EngineConfig:
    max_depth: int = 4
    use_alpha_beta: bool = True
    eval_scaling: int = 1000000
    log: bool = False


PAWN_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5, -10,  0,  0, -10, -5,  5,
    5, 10, 10, -20, -20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_PST = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,  0,  0,  0,  0, -20, -40,
    -30,  0, 10, 15, 15, 10,  0, -30,
    -30,  5, 15, 20, 20, 15,  5, -30,
    -30,  0, 15, 20, 20, 15,  0, -30,
    -30,  5, 10, 15, 15, 10,  5, -30,
    -40, -20,  0,  5,  5,  0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

BISHOP_PST = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  0,  5, 10, 10,  5,  0, -10,
    -10,  5,  5, 10, 10,  5,  5, -10,
    -10,  0, 10, 10, 10, 10,  0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10,  5,  0,  0,  0,  0,  5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

ROOK_PST = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]
QUEEN_PST = [
    - 20, -10, -10, -5, -5, -10, -10, -20,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  0,  5,  5,  5,  5,  0, -10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0, -10,
    -10,  0,  5,  0,  0,  0,  0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

KING_PST = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20

]


class ChessEngine(BaseEngine):
    def __init__(self, player: str, config: EngineConfig = EngineConfig()):
        super().__init__(player)
        self.config = config
        self.transposition_table = {}
        self.killer_moves = {}

    def terminal(self, board: Board):
        if board in CHECKMATE:
            winner = board.turn.opposite
            utility = self.config.eval_scaling if winner == self.max_player else - \
                self.config.eval_scaling
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

    def evaluate(self, board: Board):
        score = 0.0

        is_terminal, utility = self.terminal(board)
        if is_terminal:
            return utility

        score += utils.evaluate(board)
        # score += self.material_score(board)
        score += self.center_control(board)
        score += self.mobility_score(board)
        score += self.king_safety(board)
        score += self.threat_score(board)
        score += self.positional_score(board)
        return score

    def minimax(self, board: Board, depth: int, alpha: float, beta: float):
        key = hash(board)

        if key in self.transposition_table:
            entry = self.transposition_table[key]
            if entry["depth"] >= self.config.max_depth-depth:
                return entry["score"]

        if depth == self.config.max_depth:
            return self.evaluate(board)

        is_terminal, _ = self.terminal(board)
        if is_terminal:
            return self.evaluate(board)

        legal_moves = self.order_moves(board)

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

        self.transposition_table[key] = {
            "score": best_score,
            "depth": self.config.max_depth-depth,
            "best_move": move  # optional for enhanced ordering
        }
        return best_score

    def select_move(self, board: Board):
        best_score = -math.inf
        best_move = None

        for move in self.order_moves(board):
            board_copy = board.copy()
            board_copy.apply(move)
            score = self.minimax(board_copy, 1, -math.inf, math.inf)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def order_moves(self, board: Board, depth: int = 0):
        key = hash(board)
        tt_entry = self.transposition_table.get(key)
        best_move = tt_entry["best_move"] if tt_entry and "best_move" in tt_entry else None

        killer_moves = self.killer_moves.get(depth, [])
        moves = list(board.legal_moves())

        def move_score(move):
            score = 0
            if move == best_move:
                return 1000
            if move in killer_moves:
                return 900
            if move.is_capture(board):
                captured_piece = board[move.destination]
                if captured_piece:
                    score += self.material_value(str(captured_piece)) * 10
            return score

        return sorted(moves, key=move_score, reverse=True)


    def material_score(self, board: Board) -> int:
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

    def center_control(self, board: Board):
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
                    score += value * 0.7

        return score

    def material_value(self, piece: str) -> float:
        return {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}.get(piece.lower(), 0)

    def positional_score(self, board: Board) -> float:
        score = 0.0
        pst_tables = {
            'p': PAWN_PST,
            'n': KNIGHT_PST,
            'b': BISHOP_PST,
            'r': ROOK_PST,
            'q': QUEEN_PST,
            'k': KING_PST
        }

        for index, sq in enumerate(SQUARES):
            piece = board[sq]
            if piece:
                piece_char = str(piece).lower()
                pst = pst_tables.get(piece_char)
                if pst:
                    
                    if piece.color == BLACK:
                        index = 63 - index  # Flip vertically
                    value = pst[index]
                    if (piece.color == WHITE and self.max_player == WHITE) or (piece.color == BLACK and self.max_player == BLACK):
                        score += value
                    else:
                        score -= value
        return score
    
    def pvs(self, board: Board, depth: int, alpha: float, beta: float, is_max_player: bool):
        key = hash(board)

        if key in self.transposition_table:
            entry = self.transposition_table[key]
            if entry["depth"] >= self.config.max_depth - depth:
                return entry["score"]
        
        
        is_terminal, _ = self.terminal(board)
        if is_terminal or depth==self.config.max_depth:
            return self.evaluate(board)
        


        legal_moves = self.order_moves(board)
        if not legal_moves:
            return self.evaluate(board)

        first = True
        score = -math.inf if is_max_player else math.inf

        for move in legal_moves:
            board_copy = board.copy()
            board_copy.apply(move)

            if first:
                child_score = self.pvs(board_copy, depth + 1, alpha, beta, not is_max_player)
            else:
                # Null window search
                child_score = self.pvs(board_copy, depth + 1, alpha, alpha + 1, not is_max_player)
                if alpha < child_score < beta:
                    # Re-search with full window
                    child_score = self.pvs(board_copy, depth + 1, alpha, beta, not is_max_player)

            if is_max_player:
                score = max(score, child_score)
                alpha = max(alpha, score)
            else:
                score = min(score, child_score)
                beta = min(beta, score)

            if alpha >= beta:
                # Killer move: move caused a beta-cutoff
                if depth not in self.killer_moves:
                    self.killer_moves[depth] = []
                if move not in self.killer_moves[depth]:
                    self.killer_moves[depth].append(move)
                    if len(self.killer_moves[depth]) > 2:  # limit killers
                        self.killer_moves[depth].pop(0)
                break
            
            first = False

        self.transposition_table[key] = {
            "score": score,
            "depth": self.config.max_depth - depth,
            "best_move": move
        }
        return score

