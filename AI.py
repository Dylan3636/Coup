from enum import Enum
import numpy as np


from Player import Player
from Action import Action
from UI import UI

class AiType(Enum):
    HUMAN = -1
    RANDOM = 0


class RandomAI(Player):
    def __init__(self, player_id, turn=0, cards=None, ui=UI()):
        Player.__init__(self, player_id, turn, cards, ui)

    def request_action(self, state):
        legal_actions,  target = Action.get_legal_actions(state)
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
