from enum import Enum

class Role(Enum):
    Banker = True
    Player = False

class Hand:
    def __init__(self):
        self.first = None
        self.second = None
        self.third = None

class Gamer:
    def __init__(self):
        self.cards = []

    def reset(self):
        pass

    @property
    def total_value(self):
        total = sum(c.value for c in self.cards)
        if total > 9: total = total % 9
        return total

class Player(Gamer):
    def __init__(self):
        self.role = Role(True)

    def scan_hand(self, cards):
        for card in cards:
            if card.belongs_to:
                pass

class Banker(Gamer):
    def __init__(self):
        self.role = Role(False)

    def scan_hand(self, cards):
        pass