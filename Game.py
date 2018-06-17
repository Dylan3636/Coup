import numpy as np
import logging
from enum import Enum
from Card import Card
from Action import Action
from Player import Player

'''
@Author=Dylan
'''
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


class Game:
    FULL_DECK = []
    for card in Card.get_cards():
        FULL_DECK += [card, card, card]

    def __init__(self, players, LOGLEVEL=logging.DEBUG):
        logging.basicConfig(format='%(levelname)s: %(message)s', level=LOGLEVEL)
        logging.info("Making new game with players " + str(list(map(str, players))))

        deck = self.new_deck()

        turn_order = list(range(len(players)))
        np.random.shuffle(turn_order)

        while None in players:
            players.remove(None)

        for i, player in enumerate(players):
            player.turn = turn_order[i]
            player_cards = self.draw_cards(2, deck=deck)
            player.set_cards(player_cards)
        players.sort()
        self.state = {'Players': players, 'Turn': 0, 'Type': None, 'Pending Action': None, 'Exchange Options': [], 'Finished': False, 'Winner': None, 'Deck': deck}

    def start_game(self):
        logging.info('Starting game...')
        self.run_game(self.state)

    def end_game(self, state):
        logging.info('Ending game...')
        return state

    def run_game(self, state, step=-1, lookahead=np.inf):
        finished = state['Finished']
        if finished or step >= lookahead:
            return self.end_game(state)
        ns = self.run_turn(state)
        step += 1
        return self.run_game(ns, step, lookahead)

        # while next_state is None:
        #     turn = state['Turn']
        #     player = state['Players'][turn]
        #     if player.coins == 10:
        #         self.ui.print_things("You have too many coins! You must commit a coup.")
        #     else:
        #         self.ui.print_things("You do not have enough coins to take that action.")
        #     next_state = self.start_turn(state)
        #
        # while not finished and step< lookahead:
        #     next_state = self.start_turn(state)
        #     while next_state is None:
        #         turn = state['Turn']
        #         player = state['Players'][turn]
        #         if player.coins == 10:
        #             self.ui.print_things("You have too many coins! You must commit a coup.")
        #         else:
        #             self.ui.print_things("You do not have enough coins to take that action.")
        #         next_state = self.start_turn(state)
        #     state = self.end_turn(next_state)

    def result_of_action(self, state, action, player, target=None):
        logging.debug("Checking the result of action: %s take by player %s in state: %s against target %s", str(action), str(player), str(state), str(target))
        player_id = player.turn
        target_id = None if target is None else target.turn
        cpy = state.copy()
        successful = cpy['Type'] == StateType.SUCCESSFUL_ACTION

        if action is Action.EMPTY_ACTION:  # Accept pending action
            pending_action, _, _ = cpy['Pending Action']
            logging.debug("Action accepted! Recursing into pending action: %s", pending_action)
            cpy['Type'] = StateType.SUCCESSFUL_ACTION
            cpy = self.result_of_action(cpy, pending_action, player, target)
            cpy['Type'] = StateType.END_OF_TURN

        if action is Action.CHALLENGE:  # Challenge
            pending_action, p1, p2 = cpy['Pending Action']
            if not target.bluffing(pending_action):
                logging.debug("Challenged Failed! Recursing into pending action: %s", pending_action)
                cpy['Type'] = StateType.SUCCESSFUL_ACTION
                cpy = self.result_of_action(cpy, pending_action, player, target)
                cpy['Type'] = StateType.CHALLENGE_FAILED
                cpy['Pending Action'] = (None, p1, p2)

            else:
                logging.debug("Challenge successful!")
                cpy['Type'] = StateType.CHALLENGE_SUCCESSFUL

            # TODO if challengee won challenge then their revealed card needs to be replaced

        if 16 < action.value < 19: # Flipping cards after challenge
            card = cpy['Players'][player_id].hidden_cards[action.value-17]
            cpy = self.flip_player_card(player, card, cpy)

        elif action.value == 7:  # Income
            cpy = state.copy()
            cpy['Players'][player_id].increase_coins(1)

        elif action.value == 9:  # Coup
            cpy = state.copy()
            if player.action_possible(action):
                cpy['Players'][player_id].decrease_coins(7)
                cpy['Type'] = StateType.REQUESTING_CARD_FLIP

        elif action.value == 5:  # Steal
            if successful:
                net = cpy['Players'][target_id].decrease_coins(2)
                cpy['Players'][player_id].increase_coins(net)

        elif action.value == 6:  # Tax
            if successful:
                cpy['Players'][player_id].increase_coins(3)

        elif action.value == 8:  # Foreign Aid
            if successful:
                cpy['Players'][player_id].increase_coins(3)

        elif action.value == 0:  # Assassinate
            cpy['Players'][player_id].decrease_coins(3)
            if successful:
                cpy['Type'] = StateType.REQUESTING_CARD_FLIP

        elif action.value == 4:  # Exchange
            if successful:
                card_choices = player.hidden_cards + self.draw_cards(2, deck=cpy['Deck'])
                cpy['Exchange Options'] = card_choices
                cpy['Type'] = StateType.REQUESTING_EXCHANGE

        elif 10 < action.value < 20: # Choosing cards to keep after exchange
            deck = cpy['Deck']
            card_choices = cpy['Exchange Options']
            new_cards = []

            if action is Action.CHOOSE_CARD_1:
                new_cards += card_choices.pop(0)

            if action is Action.CHOOSE_CARD_2:
                new_cards += card_choices.pop(1)

            if action is Action.CHOOSE_CARD_3:
                new_cards += card_choices.pop(2)

            if action is Action.CHOOSE_CARDS_1_AND_2:
                new_cards += card_choices.pop(0)
                new_cards += card_choices.pop(0)

            elif action is Action.CHOOSE_CARDS_1_AND_3:
                new_cards += card_choices.pop(0)
                new_cards += card_choices.pop(1)

            elif action is Action.CHOOSE_CARDS_1_AND_4:

                new_cards += card_choices.pop(0)
                new_cards += card_choices.pop(2)

            elif action is Action.CHOOSE_CARDS_2_AND_3:
                new_cards += card_choices.pop(1)
                new_cards += card_choices.pop(1)

            elif action is Action.CHOOSE_CARDS_2_AND_4:
                new_cards += card_choices.pop(1)
                new_cards += card_choices.pop(2)

            elif action is Action.CHOOSE_CARDS_3_AND_4:
                new_cards += card_choices.pop(2)
                new_cards += card_choices.pop(2)
            cpy = self.set_player_cards(cpy, player_id, new_cards)
            deck = self.return_cards(deck, card_choices)
            cpy['Deck'] = deck

        elif action.is_block():  # Block Actions
            if not successful:
                logging.info("Block failed!")
                logging.debug("Recursing into action: %s", action.get_non_block())
                return self.result_of_action(cpy, action.get_non_block(), target, player)
            else:
                logging.info("player %s successfully blocked player %s action %s", player, target, action.get_non_block())

        logging.debug("Resulting state: %s", cpy)
        return cpy

    def next_state(self, state, action, player, target=None):
        debugstr = 'Initiating transition from from State: {} using Action: {} played by player {}'.format(state, action, player)
        debugstr += '' if target is None else 'with target {}'.format(target)
        logging.debug(debugstr)
        cpy = state.copy()

        if not player.action_possible(action):
            logging.critical('Action %s could not be taken by player %s', action, player)
            return

        player_id = player.turn
        target_id = None if target is None else target.turn

        if action in [Action.EMPTY_ACTION, Action.INCOME, Action.COUP, Action.CHALLENGE] and action.value >= 11:
            # These actions cannot be blocked or challenged
            cpy = self.result_of_action(cpy, action, player, target)
        else:
            logging.debug("Action %s is now pending", action)
            cpy['Pending Action'] = (action, player_id, target_id)

        return cpy

    def run_turn(self, state):
        ns = self.start_turn(state)
        while ns['Type'] is not StateType.END_OF_TURN:
            ns = self.continue_turn(ns)
        ns = self.end_turn(ns)
        return ns

    def start_turn(self, state):
        player = state['Players'][state['Turn']]
        logging.info("Starting player %s's turn", player)
        state = state.copy()
        state['Type'] = StateType.START_OF_TURN
        action, target = self.request_action(player, state)
        next_state = self.next_state(state, action, player, target)

        if next_state is None:
            logging.critical('Action %s failed for player %s', action, player)
            return

        if next_state['Pending Action'] is None:
            logging.debug('%s could not be blocked or challenged, so moving on', action)
            # The action can not be blocked or challenged
            next_state['Type'] = StateType.END_OF_TURN
            return next_state
        else:
            # Query all players to see if they want to challenge
            response_action, responder = self.request_block_or_challenge(player, next_state)

            if action is Action.EMPTY_ACTION:
                # The action was not challenged or blocked
                logging.debug('%s was not blocked or challenged', response_action)
                next_state = self.next_state(next_state, action, target)
                next_state['Type'] = StateType.END_OF_TURN

            elif action.is_block():
                # Action was blocked
                logging.debug('%s was blocked by %s', action, responder)
                next_state['Type'] = StateType.BLOCKING
                next_state = self.next_state(next_state, response_action, responder, player)

            elif response_action is Action.CHALLENGE:
                # The action was challenged
                logging.debug('%s was challenged by %s', action, responder)
                next_state = self.next_state(next_state, response_action, responder, player)

        return next_state

    def continue_turn(self, state):
        state = state.copy()
        player = state['Players'][state['Turn']]
        logging.info("Continuing player %s's turn", player)

        pending_action, player_id, target_id = state['Pending Action']
        player = state['Players'][player_id]
        target = None if target_id is None else state['Players'][target_id]

        if state['Type'] is StateType.BLOCKING:
            challenger = self.request_challenge(player, state)

            if challenger is None:
                # Blocking action was not challenged
                logging.debug('%s was not challenged', pending_action)
                next_state = self.next_state(state, Action.EMPTY_ACTION, player, target)
            else:
                # Blocking action was challenged
                logging.debug('%s was challenged by %s', pending_action, challenger)
                next_state = self.next_state(state, Action.CHALLENGE, challenger, target)

            next_state['Type'] = StateType.END_OF_TURN

        if state['Type'] is StateType.CHALLENGE_SUCCESSFUL:
            _, player, target = pending_action
            next_state = self.request_card_flip(player, state)
            next_state['Type'] = StateType.END_OF_TURN

        elif state['Type'] is StateType.CHALLENGE_FAILED:
            _, player, target = pending_action
            next_state = self.request_card_flip(target, state)
            next_state['Type'] = StateType.END_OF_TURN

        elif state['Type'] is StateType.REQUESTING_CARD_FLIP:
            _, player, target = pending_action
            next_state = self.request_card_flip(target, state)
            next_state['Type'] = StateType.END_OF_TURN

        else:
            return None

        return next_state

    def end_turn(self, state):
        p = state['Players'][state['Turn']]
        logging.info("Ending player %s's turn", p)
        state['Turn'] = (state['Turn'] + 1) % len(state['Players'])
        if len(state['Players']) < 2:
            state['Winner'] = state['Players'][0]
            state['Finished'] = True
        return state

    # def possible_result_states(self, state, action, player, target=None, challenge=0, allow=0):
    #     if not player.action_possible(action):
    #         return
    #     player_id = (state['Player'] == player.name)
    #     target_id = (state['Player'] == target.name)
    #
    #     possible_states = []
    #
    #     if action.value == 5:  # Steal
    #         cpy = state.copy()
    #         block_results = self.possible_result_states(cpy, Action.BLOCK_STEAL, player, target)
    #         # block successful/ block challenge fail/ block challenge successful
    #
    #         successful_challenges = []
    #         if not player.legal_action(action):
    #             for challenger in self.players:
    #                 tmp = cpy.copy()
    #                 tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
    #                 successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         cpy.loc[target_id, 'Coins'] -= 2  # no challenge
    #         cpy.loc[player_id, 'Coins'] += 2  # no challenge
    #         if allow:
    #             return possible_states.append(cpy.loc[:,['Coins', 'Hidden Cards']].values.flatten())
    #
    #         failed_challenges = []
    #         for challenger in self.players:
    #             challenger_id = (state['Player'] == challenger.name)
    #             tmp3 = cpy.copy()
    #             tmp3.loc[challenger_id, 'Hidden Cards'] -= 1  # challenge failed
    #             failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         if challenge == 1:
    #             return np.concatenate((failed_challenges, successful_challenges))
    #
    #         possible_states.append(cpy.loc[:, ['Coins','Hidden Cards']].values.flatten())
    #         return np.concatenate((possible_states, failed_challenges, successful_challenges, block_results)).tolist()
    #
    #     elif action.value == 6:  # Tax
    #         cpy = state.copy()
    #
    #         successful_challenges = []
    #         if not player.legal_action(action):
    #             for challenger in self.players:
    #                 tmp = cpy.copy()
    #                 tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
    #                 successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         cpy.loc[player_id, 'Coins'] += 3  # no challenge
    #
    #         failed_challenges = []
    #         for challenger in self.players:
    #             challenger_id = (state['Player'] == challenger.name)
    #             tmp3 = cpy.copy()
    #             tmp3.loc[target_id, 'Hidden Cards'] -= 1  # challenge failed
    #             failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         if challenge == 1:
    #             return np.concatenate((failed_challenges, successful_challenges))
    #
    #         possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())
    #
    #         return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()
    #
    #     elif action.value == 7:  # Income
    #         cpy = state.copy()
    #         cpy.loc[player_id, 'Coins'] += 1
    #         return possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())
    #
    #     elif action.value == 8:  # Foreign Aid
    #         cpy = state.copy()
    #         block_results = self.possible_result_states(cpy, Action.BLOCK_FOREIGN_AID, target, player)
    #
    #         successful_challenges = []
    #         if not player.legal_action(action):
    #             for challenger in self.players:
    #                 tmp = cpy.copy()
    #                 tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
    #                 successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         cpy.loc[player_id, 'Coins'] += 2  # no challenge
    #         if allow:
    #             return possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())
    #
    #         failed_challenges = []
    #         for challenger in self.players:
    #             challenger_id = (state['Player'] == challenger.name)
    #             tmp3 = cpy.copy()
    #             tmp3.loc[challenger_id, 'Hidden Cards'] -= 1  # challenge failed
    #             failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         if challenge == 1:
    #             return np.concatenate((failed_challenges, successful_challenges))
    #
    #         possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         return np.concatenate((possible_states, failed_challenges, successful_challenges, block_results)).tolist()
    #
    #     elif action.value == 0:  # Assassinate
    #         cpy = state.copy()
    #         if player.action_possible(action):
    #             cpy.loc[player_id, 'Coins'] -= 3
    #             block_results = self.possible_result_states(cpy, Action.BLOCK_FOREIGN_AID, target, player)
    #
    #             successful_challenges = []
    #             if not player.legal_action(action):
    #                 for challenger in self.players:
    #                     tmp = cpy.copy()
    #                     tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
    #                     successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #             cpy.loc[target_id, 'Hidden Cards'] -= 1  # no challenge
    #             if allow:
    #                 return possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #             failed_challenges = []
    #             for challenger in self.players:
    #                 if challenger == target and len(target.hidden_cards)==0:
    #                     continue
    #                 challenger_id = (state['Player'] == challenger.name)
    #                 tmp3 = cpy.copy()
    #                 tmp3.loc[challenger_id, 'Hidden Cards'] -= 1  # challenge failed
    #                 failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #             if challenge == 1:
    #                 return np.concatenate((failed_challenges, successful_challenges))
    #
    #             possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())
    #
    #             return np.concatenate((possible_states, failed_challenges, successful_challenges,
    # block_results)).tolist()
    #
    #     elif action.value == 9:  # Coup
    #         cpy = state.copy()
    #         if player.action_possible(action):
    #             cpy.loc[player_id, 'Coins'] -= 7
    #             cpy.loc[target_id, 'Hidden Cards'] -=1
    #             possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #     elif action.value == 1:  # Block Assassinate
    #         cpy = state.copy()  # no challenge
    #         possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #         if allow:
    #             return possible_states
    #
    #         successful_challenges = []
    #         failed_challenges = []
    #
    #         for challenger in self.players:
    #             challenger_id = (state['Player'] == challenger.name)
    #
    #             tmp2 = state.copy()
    #             tmp2.loc[challenger_id, 'Hidden Cards'] -= 1  # block challenge failed
    #             failed_challenges.append(tmp2.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #             if not player.legal_action(action):
    #                 tmp = cpy.copy()
    #                 tmp.loc[player_id, 'Hidden Cards'] -= 1  # block challenge successful
    #                 if len(tmp.hidden_cards) == 1:
    #                     tmp[player_id, 'Hidden Cards'] -= 1  # proceeded with assassination
    #                 successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         if challenge == 1:
    #             return np.concatenate((failed_challenges, successful_challenges))
    #
    #         return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()
    #
    #     elif action.value == 2:  # Block Foreign Aid
    #         cpy = state.copy()  # no challenge
    #         possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #         if allow:
    #             return possible_states
    #
    #         successful_challenges = []
    #         failed_challenges = []
    #
    #         for challenger in self.players:
    #             challenger_id = (state['Player'] == challenger.name)
    #
    #             tmp2 = state.copy()
    #             tmp2.loc[challenger_id, 'Hidden Cards'] -= 1  # block challenge failed
    #             failed_challenges.append(tmp2.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #             if not player.legal_action(action):
    #                 tmp = cpy.copy()
    #                 tmp.loc[player_id, 'Hidden Cards'] -= 1  # block challenge successful
    #                 tmp[target_id, 'Coins'] += 2  # proceed with foreign aid
    #                 successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         if challenge == 1:
    #             return np.concatenate((failed_challenges, successful_challenges))
    #
    #         return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()
    #
    #     elif action.value == 3:  # Block Steal
    #         cpy = state.copy()  # no challenge
    #         possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #         if allow:
    #             return possible_states
    #
    #         successful_challenges = []
    #         failed_challenges = []
    #
    #         for challenger in self.players:
    #             challenger_id = (state['Player'] == challenger.name)
    #
    #             tmp2 = state.copy()
    #             tmp2.loc[challenger_id, 'Hidden Cards'] -= 1  # block challenge failed
    #             failed_challenges.append(tmp2.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #             if not player.legal_action(action):
    #                 tmp = cpy.copy()
    #                 tmp.loc[player_id, 'Hidden Cards'] -= 1  # block challenge successful
    #                 net = player.decrease_coins(2,set_coins=False)
    #                 tmp[player_id, 'Coins'] -= net  # proceed with steal
    #                 tmp[target_id, 'Coins'] += net  # proceed with steal
    #
    #                 successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         if challenge == 1:
    #             return np.concatenate((failed_challenges, successful_challenges))
    #
    #         return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()
    #
    #     elif action.value == 4:  # Exchange
    #         cpy = state.copy()
    #
    #         successful_challenges = []
    #         if not player.legal_action(action):
    #             for _ in self.players:
    #                 tmp = cpy.copy()
    #                 tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
    #                 successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())  # no challenge
    #
    #         if allow:
    #             return possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())
    #
    #         failed_challenges = []
    #         for challenger in self.players:
    #             challenger_id = (state['Player'] == challenger.name)
    #             tmp3 = cpy.copy()
    #             tmp3.loc[challenger_id, 'Hidden Cards'] -= 1  # challenge failed
    #             failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
    #
    #         if challenge == 1:
    #             return np.concatenate((failed_challenges, successful_challenges))
    #
    #         return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()

    def request_action(self, player, state):
        if player is None:
            # Edge case of Foreign Aid that has no target but can be blocked.
            for p in state['Players']:
                if p.player_type == 1:
                    action, _ = player.request_action(state)
        action, target = player.request_action(state)
        return action, target

    def request_block_or_challenge(self, state, player):
        state = state.copy()
        state['Type'] = StateType.REQUESTING_BLOCK
        action, _ = self.request_action(player, state)
        if action is Action.EMPTY_ACTION:
            _, player, _ = state['Pending Action']
            challenger = self.request_challenge(player, state)
            if challenger is None:
                return Action.EMPTY_ACTION, None
            else:
                return Action.CHALLENGE, challenger
        else:
            return action, player

    def request_challenge(self, p1, state):
        state = state.copy()
        logging.debug('Requesting players to challenge action')
        players = state['Players']
        state['Type'] = StateType.REQUESTING_CHALLENGE
        for player in players:
            if player is p1:
                continue
            action, _ = player.request_action(state)
            if action is Action.CHALLENGE:
                logging.debug('%s has challenged action', player)
                return player
            else:
                logging.debug('%s has chosen not to challenge action', player)
        return None

    def request_block(self, p1, state):
        state['Type'] = StateType.REQUESTING_BLOCK
        action, _ = self.request_action(p1, state)
        return action

    def request_card_flip(self, player, state):
        logging.info("Requesting card flip from %s...", player)
        logging.debug("Current available cards %s", player.hidden_cards)
        action = player.request_card_flip(state)
        return self.result_of_action(state, action, player)

    # def request_exchange(self, player, state):
    #     cards = self.draw_cards(1)
    #     choices = player.hidden_cards
    #     choices = np.append(choices, cards).tolist()
    #     action = player.request_exchange(choices, state)
    #     state['Players'][player.name].set_cards(Card.get_cards(cards))
    #     return state


    def new_deck(self):
        deck = self.FULL_DECK
        return self.shuffle_cards(deck)

    def shuffle_cards(self, cards):
        np.random.shuffle(cards)
        return cards

    def draw_cards(self, num, deck):
        player_cards = np.random.choice(deck, num, replace=False)
        [deck.remove(card) for card in player_cards]
        return player_cards

    def return_cards(self, deck, cards):
        deck += cards
        return self.shuffle_cards(deck)

    def set_player_cards(self, state, player_id, cards):
        state['Players'][player_id].set_cards(cards)
        return state

    # def try_action(self, action, player, target=None, card=None):
    #     result = action.result_of_action()
    #
    #     # Check if player has enough coins to complete action
    #     if not player.action_possible(action):
    #         return -1
    #     else:
    #         #if result < 0:
    #         #    player.decrease_coins(result)
    #         if action in [Action.INCOME, Action.COUP]:
    #             self.do_action(action, player, target)
    #             return
    #         challenge_or_block, challenger_or_blocker, block_card = self.request_challenge(player, target, action)
    #
    #         if challenge_or_block == 1:
    #
    #             challenge_success = True
    #
    #             for card in player.hidden_cards:
    #                 challenge_success = challenge_success and action not in card.actions()
    #
    #             self.process_challenge_result(challenge_success, action, player, challenger_or_blocker, card)
    #
    #         elif challenge_or_block == 0:
    #             self.ui.print_things('No challenge was attempted')
    #             self.do_action(action, player, target)
    #
    #         else:
    #             block = action.get_block()
    #             challenge, challenger = self.request_challenge(target, player, block)
    #
    #             if challenge == 1:
    #
    #                 challenge_success = False
    #
    #                 for card in target.hidden_cards:
    #                     challenge_success = challenge_success or action in card.actions()
    #
    #                 self.process_challenge_result(challenge_success, block, target, challenger, card)
    #             else:
    #                 self.process_challenge_result(0, block, target, challenger, card)

    # def process_challenge_result(self, result, action, p1, p2, card=None):
    #     """Process the result of p2's challenge of p1's action"""
    #     if result == 1:
    #         self.request_card_flip(1, p1)
    #     else:
    #         self.request_card_flip(0, p2)
    #         self.do_action(action, p1, p2)
    #         p1.shuffle(card.name)

    # def do_action(self, action, p1, p2):
    #     if action is Action.ASSASSINATE:
    #         self.request_card_flip(2, p2)
    #     elif action is Action.EXCHANGE:
    #         self.request_exchange(p1)
    #     elif action is Action.STEAL:
    #         net = p2.decrease_coins(action.result_of_action())
    #         p1.increase_coins(net)
    #     elif action is Action.COUP:
    #         self.request_card_flip(3, p2)
    #     else:
    #         p1.increase_coins(action.result_of_action())

    def flip_player_card(self, player, card, state):
        state['Players'][player.turn].flip_card(card)
        if state['Players'][player.turn].hidden_cards == []:
            self.remove_player(player, state)

    @staticmethod
    def get_player(player_name, state):
        for player in state['Players']:
            if player.name == player_name:
                return player
        raise Exception('Player not found!')

    @staticmethod
    def remove_player(player, state):
        logging.info("Player {} has shown all their influence and has lost.".format(player.name), player)
        state['Players'].remove(player)


def test():

    p1 = Player('p1', cards=[Card.AMBASSADOR, Card.DUKE], player_type=0)
    p2 = Player('p2', cards=[Card.AMBASSADOR, Card.DUKE], player_type=0)
    # p3 = Player([Card.AMBASSADOR, Card.DUKE], 0, 'p3')
    # p4 = Player([Card.AMBASSADOR, Card.DUKE], 0, 'p4')
    game = Game([p1, p2])
    game.start_game()

if __name__ == '__main__':
    test()
