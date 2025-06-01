from abc import ABC, abstractmethod
from bulletchess import Board

class BaseEngine(ABC):
    def __init__(self, player: str):
        self.max_player = player

    @abstractmethod
    def select_move(self, board: Board):
        """Selects the next move to make."""
        pass