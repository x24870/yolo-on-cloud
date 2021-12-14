from enum import Enum
import logging

logger = logging.getLogger('Gamer')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class Role(Enum):
    Banker = True
    Player = False

class Hand:
    def __init__(self):
        self.accumulate = 0
        self.card = None

    #TODP: optimize this machanism
    def update(self, new_output):
        if not self.card:
            self.card = new_output
        else:
            if self.card.pair_centroid:
                if abs(self.card.pair_centroid[0] - new_output[0]) > 80:
                    if self.accumulate <= 0:
                        self.card = new_output
                    else:
                        self.accumulate -= 1
                else:
                    self.accumulate += 1
            elif new_output.pair_centroid:
                self.card = new_output


    @property
    def value(self):
        # TODO: tune accumulate value
        if not self.card or self.accumulate < 0:
            return 0
        else:
            return self.card.value

class Gamer:
    def __init__(self):
        self.first = Hand()
        self.second = Hand()
        self.third = Hand()

    def reset(self):
        pass

    @property
    def total_value(self):
        total = sum([self.first.value, self.second.value, self.third.value])
        if total > 9: total = total % 9
        logger.debug(f'total {total}')
        return total

class Player(Gamer):
    def __init__(self):
        super().__init__()
        self.role = Role(True)

    # TODO: optimize the machanism
    def scan_hand(self, cards):
        for idx, card in enumerate(cards):
            if card.is_vertical:
                logger.debug('update player 3rd')
                self.third.update(card)
            else:
                if idx == len(cards)-1:
                    logger.debug('update player 2st')
                    self.second.update(card)
                else:
                    logger.debug('update player 1st')
                    self.first.update(card)

class Banker(Gamer):
    def __init__(self):
        super().__init__()
        self.role = Role(False)

# TODO: optimize the machanism
    def scan_hand(self, cards):
        for idx, card in enumerate(cards):
            if card.is_vertical:
                logger.debug('update player 3rd')
                self.third.update(card)
            else:
                if idx == 0:
                    logger.debug('update player 1st')
                    self.first.update(card)
                else:
                    logger.debug('update player 2st')
                    self.second.update(card)