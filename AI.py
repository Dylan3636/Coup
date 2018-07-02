from enum import Enum
import numpy as np

from State import StateType
from Player import Player
from Action import Action
from UI import UI


class AiType(Enum):
    HUMAN = -1
    RANDOM = 0


class AutoPlayer(Player):
    def __init__(self, player_id, turn=0,actionTree=[], cards=None, ui=UI()):
        Player.__init__(self, player_id, turn, cards, ui)
        self.index = 0
        self.actionTree = actionTree

    def request_action(self, state):
        server = state['Server']
        return server.request_action(state, self)#self.actionTree[self.index]
        # if self == player:
        #     return action, target
        # else:
        #     self.index += 1
class Server:
    def __init__(self, GameTree, ActionTree):
        self.GameTree   = GameTree
        self.ActionTree = ActionTree
        self.pointer    = 0

    def request_action(self, state, player):
        actions = self.ActionTree[self.pointer]
        type    = state['Type']

        if type == StateType.START_OF_TURN:
            if player != actions[1]:
                raise Exception("%s /= %s", player, actions[1])
            return actions[0], actions[2]

        if type == StateType.REQUESTING_BLOCK:
            if player != actions[1]:
                return Action.EMPTY_ACTION, None
            else:
                return actions[0], actions[2]

        if type == StateType.REQUESTING_CHALLENGE:
            if player != actions[1]:
                return Action.EMPTY_ACTION, None
            else:
                return actions[0], actions[2]

        if type == StateType.REQUESTING_CARD_FLIP:
            for p in self.GameTree[self.pointer+1]['Players']:
                if p == player:
                    if player.hidden_cards[0] == p.flipped_cards[0]:
                        return Action.FLIP_CARD_1, None
                    else:
                        return Action.FLIP_CARD_2, None


    def increase_pointer(self):
        self.pointer += 1



class ConstantAI(Player):
    def __init__(self, player_id, turn=0, cards=None, ui=UI(), constant_action=None):
        self.constant_action = constant_action
        Player.__init__(self, player_id, turn, cards, ui)

    def request_action(self, state):
        return self.constant_action

class RandomAI(Player):
    def __init__(self, player_id, turn=0, cards=None, ui=UI()):
        Player.__init__(self, player_id, turn, cards, ui)

    def request_action(self, state):
        legal_actions,  target = self.get_legal_actions(state)
        action = np.random.choice(legal_actions)
        if target:
            if action in [Action.STEAL, Action.ASSASSINATE, Action.COUP]:
                opponents = state['Players'][:]
                opponents.remove(self)
                target = np.random.choice(opponents)
            else:
                target = None
        else:
            target = None
        return action, target
