import logging
from enum import Enum

import Card_processor as cardp
from Gamer import Player, Banker

logger = logging.getLogger('baccarat')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class Desk():
    def __init__(self):
        self.cards = []
        self.banker = Banker()
        self.player = Player()

    def scan_desk(self, cards):
        p_cards = []
        b_cards = []
        for c in cards:
            if c.belongs: #player
                p_cards.append(c)
            else:
                b_cards.append(c)
        self.player.scan_hand(p_cards)
        self.banker.scan_hand(b_cards)

    def reset(self):
        pass

class Status(Enum):
    END = 0
    ONGOING = 1
    OUTCOME = 2

class Baccarat:
    def __init__(self):
        self.status = Status(0)
        self.frame = 0
        self.desk = Desk()

    def get_result(self):
        if self.desk.player.total_value > self.desk.banker.total_value:
            logger.debug('player won!')
        elif self.desk.player.total_value < self.desk.banker.total_value:
            logger.debug('banker won')
        else:
            logger.debug('Tie')

    def reset(self):
        pass

    def __str__(self):
        print(self.status)


if __name__ == '__main__':
    raw = [
    ['Jd', 94.02, (821, 567, 31, 38)],
    ['Jh', 94.25, (724, 469, 31, 38)],
    ['8s', 98.35, (1165, 808, 36, 49)],
    ['4d', 99.84, (1196, 708, 35, 45)],
    ['4d', 99.84, (1299, 805, 34, 44)],
    ['Ac', 99.87, (539, 459, 57, 22)],
    ['Ac', 99.94, (413, 534, 56, 26)]
    ]

    cards = cardp.process_cards_info(raw)
    for c in cards:
        logger.debug(c)

    baccarat = Baccarat()
    baccarat.desk.scan_desk(cards)
