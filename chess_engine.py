import random
from bulletchess import *
from time import sleep

class ChessEngine:
    def __init__(self, board:Board, player:str):
        self.board = board
        self.oppositeMap = {WHITE:BLACK, BLACK:WHITE}
        self.counter=0
        self.limit=500
        self.max_player = player
            
    def terminal(self, b:Board) -> bool:
        if b in CHECKMATE:
            print(f"game finished and winner was: {self.oppositeMap[b.turn]}")
            return True
        if b in DRAW:
            print(f"game ended in a draw")
            return True
    
    def evaluate(self, board:Board):
        pass
    
    def minimax(self, board:Board):
        pass

    def select_move(self, board):
        best_move = self.minimax(board)
        return best_move
        
    def random_game(self):
        with open("fen_strings.txt", "w") as file:
            while True:
                legal_moves = self.board.legal_moves()
                self.board.apply(random.choice(legal_moves))
                file.write(f"{self.board.fen()}\n")
                if self.terminal(self.board):
                    break
                if self.counter >= self.limit:
                    print("REACHED LIMIT ITERATIONS")
                    print(f"CURRENT BOARD: {self.board.fen()}")
                    break
                self.counter += 1