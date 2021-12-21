import cv2
import numpy as np
import logging

logger = logging.getLogger('card_processor')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class Card:
    def __init__(self, vertical, belongs, pattern, confidence, pair, pair_centroid, estimated_bbox):
        self.is_vertical = vertical # false: horizontal
        self.belongs = belongs # false: banker
        self.pattern = pattern
        self.confidence = confidence
        self.pair = pair
        self.pair_centroid = pair_centroid
        self.estimated_bbox = estimated_bbox # TODO: this is just for debug
        self.value = self._get_value(pattern)

    def __str__(self):
        vertical = 'v' if self.is_vertical else 'h'
        belongs = 'player' if self.belongs else 'banker'
        return f'{self.pattern} {self.value}: {vertical} {belongs} {self.confidence} {self.pair} {self.estimated_bbox}'

    def _get_value(self, pattern):
        if len(pattern) == 3: # rank is 10
            return 0
        try:
            return int(pattern[0])
        except:
            if pattern[0] == 'A':
                return 1
            else: # rank is J Q K
                return 0


class raw_pattern:
    def __init__(self, cls, score, bbox):
        self.cls = cls
        self.score = score
        self.bbox = bbox # x, y, w, h
        self.is_vertical = bbox[2] < bbox[3]

def get_centroid(bbox):
    return (
        int(bbox[0] + bbox[2]/2),
        int(bbox[1] + bbox[3]/2)
        )

def get_diagnal_bbox_list(bbox):
    # specify vertical or horizontal (w < h: vertical)
    is_vertical = True if bbox[2] < bbox[3] else False 
    # TODO: find a better way to estimate diagnal bbox instead of fix value
    if is_vertical: # estimate (125, -75)
        dx_offset, dy_offset = 65, 60
        dw, dh = 70, 80

    else:
        dx_offset, dy_offset = 100, -110
        dw, dh = 70, 60

    return [
        [bbox[0]+dx_offset, bbox[1]+dy_offset],
        [bbox[0]+dx_offset+dw, bbox[1]+dy_offset],
        [bbox[0]+dx_offset+dw, bbox[1]+dy_offset+dh],
        [bbox[0]+dx_offset, bbox[1]+dy_offset+dh],
    ]


def get_diagnal_bbox_contour(bbox):
    # specify vertical or horizontal (w < h: vertical)
    is_vertical = True if bbox[2] < bbox[3] else False 
    # TODO: find a better way to estimate diagnal bbox instead of fix value
    if is_vertical: # estimate (125, -75)
        dx_offset, dy_offset = 65, 60
        dw, dh = 70, 80

    else:
        dx_offset, dy_offset = 80, -110
        dw, dh = 80, 70

    return np.array([
        [bbox[0]+dx_offset, bbox[1]+dy_offset],
        [bbox[0]+dx_offset+dw, bbox[1]+dy_offset],
        [bbox[0]+dx_offset+dw, bbox[1]+dy_offset+dh],
        [bbox[0]+dx_offset, bbox[1]+dy_offset+dh],
    ], dtype=np.int32)

def at_diagnal(bbox1, bbox2):
    b2_centroid = get_centroid(bbox2)
    logger.debug(f'b2 centroid: {b2_centroid}')
    b2_estimated_bbox = get_diagnal_bbox_contour(bbox1)
    logger.debug(f'b2 estimate bbox: {b2_estimated_bbox}')
    # pointPolygonTest return -1 means centriod outside of estimated bbox
    return False if cv2.pointPolygonTest(
        b2_estimated_bbox, 
        b2_centroid,
        False
        ) == -1 else True

def process_cards_info(raw):
    cards = []

    # sort by x value
    raw.sort(key=lambda x: x[2][0])
    logger.debug(raw)

    # find pair
    while raw:
        r = raw.pop(0)
        logger.debug(f'** current card {r}')
        # check if next bbox is at diagnal of this bbox
        # if yes, specify next bbox is on same card
        if raw:
            found_pair = False
            pair_centroid = None
            estimated_bbox = None
            # x is on left or right side of table
            belongs = False if r[2][0] > 960 else True
            if at_diagnal(r[2], raw[0][2]):
                dia = raw.pop(0)
                # TODO: check if these two patterns are same
                
                logger.debug(f'{r} found pair {dia}')
                found_pair = True
                # get centriod of two patterns
                print(r, dia)
                pair_centroid = (
                    (r[2][0] + dia[2][0] + dia[2][2])/2,
                    (r[2][1] + dia[2][1] + dia[2][3])/2
                )
                # TODO: just for visualize estimated bbox, remove in the future
                estimated_bbox = get_diagnal_bbox_list(r[2])
            card = Card(
                r[2][2]<r[2][3], # vertical
                belongs, # belongs
                r[0], # pattern
                r[1], # score
                found_pair, # pair
                pair_centroid,
                estimated_bbox
                )
            cards.append(card)
    return cards

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

    cards = process_cards_info(raw)
    logger.debug(cards)
