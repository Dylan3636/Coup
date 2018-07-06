from enum import Enum


class StateType(Enum):
    START_OF_TURN = 0
    SUCCESSFUL_ACTION = 1
    REQUESTING_BLOCK = 2
    BLOCKING = 3
    REQUESTING_CHALLENGE = 4
    CHALLENGE_SUCCESSFUL = 5
    CHALLENGE_FAILED = 6
    REQUESTING_CARD_FLIP = 7
    REQUESTING_EXCHANGE = 8
    END_OF_TURN = 9

