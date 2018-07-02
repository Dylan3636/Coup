from unittest import TestCase
import numpy as np
from Game import Game, Action, ConstantAI
from State import StateType

class TestGame(TestCase):

    @staticmethod
    def generate_random_state( num_players, stateType, PlayerAI, **kwargs):
        players, deck = Game.generate_random_players(num_players, PlayerAI, kwargs)
        turn = np.random.choice(num_players)
        action = np.random.choice([Action.EXCHANGE, Action.TAX, Action.ASSASSINATE, Action.FOREIGN_AID, Action.STEAL,
                                   Action.BLOCK_ASSASSINATE, Action.BLOCK_STEAL_CAPTAIN, Action.BLOCK_STEAL_AMBASSADOR,
                                   Action.BLOCK_STEAL_AMBASSADOR])
        if action in [Action.EXCHANGE, Action.TAX]:
            target_id = None
        else:
            target_id = np.random.choice(num_players)
            if target_id == turn:
                target_id = (target_id+1) % num_players

        state = {'Players': players, 'Turn': turn, 'Type': stateType, 'Pending Action': (action, turn, target_id), 'Exchange Options': [], 'Finished': False, 'Winner': None, 'Deck': deck}
        return state


    def test_challenger(self):
        num_players = np.random.choice(6)
        state = self.generate_random_state(num_players, StateType.REQUESTING_CHALLENGE, ConstantAI, constant_action=Action.CHALLENGE)
        game = Game(state['Players'])
        next_state = game.continue_turn(state)
