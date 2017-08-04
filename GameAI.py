import os
import sys
import itertools
sys.path.insert(0, os.path.dirname(('..\ReinforcementLearning')))

from Game import *
from ReinforcementLearning.MarkovDecisionProcess import MDP


class agent:
    def __init__(self):
        self.mdp = MDP()
        tmp = []
        for j in xrange(11):
            for i in xrange(3):
                tmp2 = np.concatenate((Action.get_actions(), Action.get_blocks())).tolist()
                tmp2.append(Action.EMPTY_ACTION)
                for action1 in tmp2:
                    for k in xrange(11):
                        for h in xrange(3):
                            tmp2 = np.concatenate((Action.get_actions(), Action.get_blocks())).tolist()
                            tmp2.append(Action.EMPTY_ACTION)
                            for action2 in tmp2:
                                if action1 is Action.EMPTY_ACTION or action2 is Action.EMPTY_ACTION:
                                    tmp.append([i, j, action1, h, k, action2])
        self.states_map = dict(zip(tmp, xrange(len(tmp))))

    def set_game(self, game):
        self.game = game

    def get_transition_model(self, action):
        for k,v in self.states_map.iteritems():
            for action in self.actions
                poss_states =

