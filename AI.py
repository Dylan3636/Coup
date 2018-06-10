from enum import Enum
from Player import Player
from Action import Action
import numpy as np


class AiType(Enum):
    HUMAN = -1
    RANDOM = 0


class AI(Player):
    def __init__(self, type=AiType.RANDOM):
        self.type = type

    def request_action(self, state):
        legal_actions,  target = Action.get_legal_actions(state)
        if self.type is AiType.RANDOM:
            action = np.random.choice(legal_actions)
            if target:
                if action in [Action.STEAL, Action.ASSASSINATE, Action.COUP]:
                    opponents = state['Players'].copy()
                    opponents.remove(self)
                    target = np.random.choice(opponents)
                else:
                    target = None
            else:
                target=None
            return action, target
