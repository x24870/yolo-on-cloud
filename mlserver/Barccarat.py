import Card_processor as cardp
import logging
from enum import Enum

logger = logging.getLogger('baccarat')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

raw = [
    ['Jd', 94.02, (821, 567, 31, 38)],
    ['Jh', 94.25, (724, 469, 31, 38)],
    ['8s', 98.35, (1165, 808, 36, 49)],
    ['4d', 99.84, (1196, 708, 35, 45)],
    ['4d', 99.84, (1299, 805, 34, 44)],
    ['Ac', 99.87, (539, 459, 57, 22)],
    ['Ac', 99.94, (413, 534, 56, 26)]
]

class Gamer:
    def __init__(self, is_player):
        self.is_play = is_player
        self.points = 0
        self.cards = []

    @property
    def total_value(self):
        total = sum(c.value for c in self.cards)
        if total > 9: total = total % 9
        return total

class Status(Enum):
    END = 0
    ONGOING = 1
    OUTCOME = 2

class Baccarat:
    def __init__(self):
        self.status = Status(0)
        self.desk = {}
        self.frame = 0
        self.banker = Gamer(False)
        self.player = Gamer(True)

    def deal_cards(self, cards):
        self.banker.cards = []
        self.player.cards = []
        for c in cards:
            if c.belongs_to: # player
                self.player.cards.append(c)
            else: # banker
                self.banker.cards.append(c)

    def get_result(self):
        if self.player.total_value > self.banker.total_value:
            logger.debug('player won!')
        elif self.player.total_value < self.banker.total_value:
            logger.debug('banker won')
        else:
            logger.debug('Tie')

    def __str__(self):
        print(self.status)


cards = cardp.process_cards_info(raw)
for c in cards:
    logger.debug(c)

baccarat = Baccarat()
baccarat.deal_cards(cards)
print(baccarat)
res = baccarat.get_result()
print(res)