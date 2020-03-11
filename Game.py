import logging

import numpy as np

from Action import Action
from Card import Card
#from Player import Player
from AI import Player, RandomAI, AutoPlayer, ConstantAI

from State import StateType

'''
@Author=Dylan
'''


class Game:
    FULL_DECK = []
    for card in Card.get_cards():
        FULL_DECK += [card, card, card]

    def __init__(self, players, LOGLEVEL=logging.DEBUG):
        logging.basicConfig(
            format='%(levelname)s: %(message)s', level=LOGLEVEL)
        logging.info("Making new game with players " +
                     str(list(map(str, players))))
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
        self.state = {'Players': players, 'Turn': 0, 'Type': None, 'Pending Action': None,
                      'Exchange Options': [], 'Finished': False, 'Winner': None, 'Deck': deck}
        self.gameTree = [self.state]
        self.playerRank = []
        self.winner = None

    def start_game(self):
        logging.info('Starting game...')
        self.run_game(self.state)

    def end_game(self, state):
        logging.info('Ending game...')
        self.winner = state['Winner']
        logging.info('Winner is %s', self.winner)
        return state

    def run_game(self, state, step=-1, lookahead=np.inf):
        finished = state['Finished']
        if finished or step >= lookahead:
            return self.end_game(state)
        ns = self.run_turn(state)
        step += 1
        return self.run_game(ns, step, lookahead)

    def result_of_action(self, state, action, player, target=None):
        logging.debug(
            "Checking the result of action: %s taken by player %s in state: %s against target %s",
            str(action), str(player), Game.print_state(state), str(target))
        player_id = player.turn
        target_id = None if target is None else target.turn
        new_state = state.copy()
        successful = new_state['Type'] == StateType.SUCCESSFUL_ACTION

        if action is Action.EMPTY_ACTION:  # Accept pending action
            pending_action, _, _ = new_state['Pending Action']
            logging.info('Action accepted!')
            logging.debug("Recursing into pending action: %s", pending_action)
            new_state['Type'] = StateType.SUCCESSFUL_ACTION
            new_state = self.result_of_action(new_state, pending_action, player, target)
            new_state['Type'] = StateType.END_OF_TURN

        elif action is Action.CHALLENGE:  # Challenge
            pending_action, p1_id, p2_id = new_state['Pending Action']
            p1 = new_state['Players'][p1_id]
            p2 = None if p2_id is None else new_state['Players'][p2_id]
            if not p1.bluffing(pending_action):
                logging.info("Challenged Failed!")
                logging.debug(
                    "Recursing into pending action: %s", pending_action)
                new_state['Type'] = StateType.CHALLENGE_FAILED
                new_state['Pending Action'] = (None, player.turn, p1.turn)
                new_state = self.result_of_action(new_state, pending_action, p1, p2)
                new_state['Type'] = StateType.SUCCESSFUL_ACTION
                return self.result_of_action(new_state, pending_action, p1, p2)
                # TODO if challengee won challenge then their revealed card needs to be replaced

            else:
                logging.info("Challenge successful!")
                new_state['Type'] = StateType.CHALLENGE_SUCCESSFUL
                new_state['Pending Action'] = (None, player.turn, p1.turn)

        elif action is Action.INCOME:  # Income
            # new_state = state.copy()
            new_state['Players'][player_id].increase_coins(1)
            new_state['Type'] = StateType.END_OF_TURN

        elif action is Action.COUP:  # Coup
            # new_state = state.copy()
            new_state['Players'][player_id].decrease_coins(7)
            new_state['Type'] = StateType.REQUESTING_CARD_FLIP
            new_state['Pending Action'] = Action.COUP, player_id, target_id

        elif action is Action.STEAL:  # Steal
            if successful:
                net = new_state['Players'][target_id].decrease_coins(2)
                new_state['Players'][player_id].increase_coins(net)
            new_state['Type'] = StateType.END_OF_TURN

        elif action is Action.TAX:  # Tax
            # Do if successful, if not do nothing
            if successful:
                new_state['Players'][player_id].increase_coins(3)
                new_state['Type'] = StateType.END_OF_TURN

        elif action is Action.FOREIGN_AID:  # Foreign Aid
            # Do if successful, if not do nothing
            if successful:
                new_state['Players'][player_id].increase_coins(3)
                new_state['Type'] = StateType.END_OF_TURN

        elif action is Action.ASSASSINATE:  #Assassinate
            new_state['Players'][player_id].decrease_coins(3)
            if successful:
                new_state['Type'] = StateType.REQUESTING_CARD_FLIP
            else:
                new_state['Type'] = StateType.END_OF_TURN

        elif action is Action.EXCHANGE:  # Exchange
            if successful:
                card_choices = list(player.hidden_cards) + \
                    list(self.draw_cards(2, deck=new_state['Deck']))
                new_state['Exchange Options'] = card_choices
                new_state['Type'] = StateType.REQUESTING_EXCHANGE

        elif action.is_choosing_action():  # Choosing cards to keep after exchange
            deck = new_state['Deck']
            card_choices = new_state['Exchange Options']
            new_cards = []

            if action is Action.CHOOSE_CARD_1:
                new_cards.append(card_choices.pop(0))

            elif action is Action.CHOOSE_CARD_2:
                new_cards.append(card_choices.pop(1))

            elif action is Action.CHOOSE_CARD_3:
                new_cards.append(card_choices.pop(2))

            elif action is Action.CHOOSE_CARDS_1_AND_2:
                new_cards.append(card_choices.pop(0))
                new_cards.append(card_choices.pop(0))

            elif action is Action.CHOOSE_CARDS_1_AND_3:
                new_cards.append(card_choices.pop(0))
                new_cards.append(card_choices.pop(1))

            elif action is Action.CHOOSE_CARDS_1_AND_4:

                new_cards.append(card_choices.pop(0))
                new_cards.append(card_choices.pop(2))

            elif action is Action.CHOOSE_CARDS_2_AND_3:
                new_cards.append(card_choices.pop(1))
                new_cards.append(card_choices.pop(1))

            elif action is Action.CHOOSE_CARDS_2_AND_4:
                new_cards.append(card_choices.pop(1))
                new_cards.append(card_choices.pop(2))

            elif action is Action.CHOOSE_CARDS_3_AND_4:
                new_cards.append(card_choices.pop(2))
                new_cards.append(card_choices.pop(2))
            else:
                raise Exception("INVALID ACTION")
            new_state = self.set_player_cards(new_state, player_id, new_cards)
            deck = self.return_cards(deck, card_choices)
            new_state['Deck'] = deck
            new_state['Exchange Options'] = None
            new_state['Type'] = StateType.END_OF_TURN

        elif action.is_flipping_action():  # Flipping cards after challenge
            card = new_state['Players'][player_id].hidden_cards[action.value - 20]
            new_state = self.flip_player_card(player, card, new_state)
            new_state['Type'] = StateType.END_OF_TURN

        elif action.is_block():  # Block Actions
            if not successful:
                logging.info("Block failed!")
                logging.debug("Recursing into action: %s",
                              action.get_non_block())
                return self.result_of_action(new_state, action.get_non_block(), target, player)
            else:
                logging.info("player %s successfully blocked player %s action %s",
                             player, target, action.get_non_block())
                new_state['Type'] = StateType.END_OF_TURN

        logging.debug("Resulting state: %s", Game.print_state(new_state))
        return new_state

    def next_state(self, state, action, player, target=None):
        # if state['Type'] != StateType.START_OF_TURN:
        #     logging.critical('State type should be START_OF_TURN but found %s', state['Type'])
        debugstr = 'Initiating transition from from State: {} using Action: {} played by player {}'.format(
            Game.print_state(state), action, player)
        debugstr += '' if target is None else 'with target {}'.format(target)
        logging.debug(debugstr)
        cpy = state.copy()

        if not player.action_possible(action):
            logging.critical(
                'Action %s could not be taken by player %s', action, player)
            return

        player_id = player.turn
        target_id = None if target is None else target.turn

        if action in [Action.EMPTY_ACTION, Action.INCOME, Action.COUP, Action.CHALLENGE] or action.value >= 11:
            # These actions cannot be blocked or challenged
            cpy = self.result_of_action(cpy, action, player, target)
        else:
            logging.debug("Action %s is now pending", action)
            cpy['Pending Action'] = (action, player_id, target_id)
        return cpy

    def run_turn(self, state):
        ns = self.start_turn(state)
        self.gameTree.append(ns)
        while ns['Type'] is not StateType.END_OF_TURN:
            ns = self.continue_turn(ns)
            self.gameTree.append(ns)
        ns = self.end_turn(ns)
        self.gameTree.append(ns)
        return ns

    def start_turn(self, state):
        player = state['Players'][state['Turn']]
        logging.info("Starting player %s's turn", player)
        state = state.copy()
        state['Type'] = StateType.START_OF_TURN
        action, target = self.request_action(player, state)
        logging.info(
            "Player %s has chosen action %s against player %s", player, action, target)
        next_state = self.next_state(state, action, player, target)
        if next_state is None:
            logging.critical('Action %s failed for player %s', action, player)
            return
        if next_state['Pending Action'] is None:
            logging.info('%s could not be blocked or challenged.', action)
            # The action can not be blocked or challenged
            return next_state

        return next_state

    def continue_turn(self, state):
        state = state.copy()
        player = state['Players'][state['Turn']]
        logging.info("Continuing player %s's turn", player)

        pending_action, player_id, target_id = state['Pending Action']
        player = state['Players'][player_id]
        target = None if target_id is None else state['Players'][target_id]

        if state['Type'] is StateType.START_OF_TURN and state['Pending Action'] is not None:
            action, player_id, target_id = state['Pending Action']
            player = state['Players'][player_id]
            target = None if target_id is None else state['Players'][target_id]
            # Query all players to see if they want to challenge or block
            response_action, responder = self.request_block_or_challenge(
                state, target)
            logging.debug("Response action: %s", response_action)

            if response_action is Action.EMPTY_ACTION:
                # The action was not challenged or blocked
                logging.info('%s was not blocked or challenged', action)
                state['Type'] = StateType.SUCCESSFUL_ACTION
                next_state = self.result_of_action(
                    state, action, player, target)
                return next_state
                #next_state['Type'] = StateType.END_OF_TURN

            elif response_action.is_block():
                # Action was blocked
                logging.info('%s was blocked by %s', action, responder)
                state['Type'] = StateType.BLOCKING
                next_state = self.next_state(state, action, responder)
                return next_state
                # next_state = self.next_state(state, response_action, responder, player)

            elif response_action is Action.CHALLENGE:
                # The action was challenged
                logging.info('%s was challenged by %s', action, responder)
                next_state = self.next_state(
                    state, response_action, responder, player)
                return next_state
            else:
                logging.critical(
                    "Found invalid action: %s with state: %s", response_action, state)

        elif state['Type'] is StateType.BLOCKING:
            challenger = self.request_challenge(player, state)

            if challenger is None:
                # Blocking action was not challenged
                logging.info('%s was not challenged', pending_action)
                next_state = self.next_state(
                    state, Action.EMPTY_ACTION, player, target)
            else:
                # Blocking action was challenged
                logging.info('%s was challenged by %s',
                             pending_action, challenger)
                next_state = self.next_state(
                    state, Action.CHALLENGE, challenger, target)

            next_state['Type'] = StateType.END_OF_TURN

        elif state['Type'] is StateType.CHALLENGE_SUCCESSFUL:
            _, _, player_id = state['Pending Action']
            player = state['Players'][player_id]
            next_state = self.request_card_flip(player, state)
            next_state['Type'] = StateType.END_OF_TURN

        elif state['Type'] is StateType.CHALLENGE_FAILED:
            _, challenger_id, _ = state['Pending Action']
            challenger = state['Players'][challenger_id]
            next_state = self.request_card_flip(challenger, state)
            next_state['Type'] = StateType.END_OF_TURN

        elif state['Type'] is StateType.REQUESTING_CARD_FLIP:
            # In the cases of Assassinations or Coups
            _, _, target_id = state['Pending Action']
            target = state['Players'][target_id]
            next_state = self.request_card_flip(target, state)
            next_state['Type'] = StateType.END_OF_TURN

        elif state['Type'] is StateType.REQUESTING_EXCHANGE:
            _, player_id, _ = state['Pending Action']
            player = state['Players'][player_id]
            next_state = self.request_exchange(player, state)
            next_state['Type'] = StateType.END_OF_TURN

        else:
            logging.critical("Found invalid state: %s", state)
            return None

        return next_state

    def end_turn(self, state):
        if len(state['Players']) < 2:
            state['Winner'] = state['Players'][0]
            state['Finished'] = True
            return state
        try:
            p = state['Players'][state['Turn']]
            logging.info("Ending player %s's turn\n", p)
        except IndexError:
            logging.debug(
                'The player whose turn it was already kicked from the game')
        state['Turn'] = (state['Turn'] + 1) % len(state['Players'])
        state['Pending Action'] = None

        return state

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
        if player is None:
            action, p1_id, _ = state['Pending Action']
            if action is Action.BLOCK_FOREIGN_AID:
                for player in state['Players']:
                    if player.turn == p1_id:
                        continue
                    else:
                        action, _ = self.request_action(player, state)
            else:
                action = Action.EMPTY_ACTION
        else:
            action, _ = self.request_action(player, state)

        if action is Action.EMPTY_ACTION:
            _, player_id, _ = state['Pending Action']
            player = state['Players'][player_id]
            challenger = self.request_challenge(player, state)
            if challenger is None:
                return Action.EMPTY_ACTION, None
            else:
                return Action.CHALLENGE, challenger
        else:
            return action, player

    def request_challenge(self, p1, state):
        state = state.copy()
        logging.info('Requesting players to challenge action')
        players = state['Players']
        state['Type'] = StateType.REQUESTING_CHALLENGE
        for player in players:
            logging.debug('PLAYERS %s %s', str(p1), str(player))
            if player == p1:
                logging.debug('SKIPPING PLAYER %s', str(player))
                continue
            action, _ = player.request_action(state)
            if action is Action.CHALLENGE:
                logging.info("%s has challenged %s's action", player, p1)
                return player
            else:
                logging.info(
                    "%s has chosen not to challenge %s's action", player, p1)
        return None

    def request_card_flip(self, player, state):
        logging.info("Requesting card flip from %s...", player)
        logging.debug("Current available cards %s", player.hidden_cards)
        state['Type'] = StateType.REQUESTING_CARD_FLIP
        action, _ = player.request_action(state)
        logging.info("Player %s chose action %s", player, action)
        return self.result_of_action(state, action, player)

    def request_exchange(self, player, state):
        state['Type'] = StateType.REQUESTING_EXCHANGE
        action, _ = player.request_action(state)
        logging.info("Player %s chose action %s", player, action)
        return self.result_of_action(state, action, player)

    @staticmethod
    def new_deck():
        deck = Game.FULL_DECK
        return Game.shuffle_cards(deck)

    @staticmethod
    def shuffle_cards(cards):
        np.random.shuffle(cards)
        return cards

    @staticmethod
    def draw_cards(num, deck):
        player_cards = np.random.choice(deck, num, replace=False)
        [deck.remove(card) for card in player_cards]
        return player_cards

    @staticmethod
    def return_cards(deck, cards):
        logging.debug('Returning cards %s to deck %s', cards, deck)
        deck += cards
        return Game.shuffle_cards(deck)

    @staticmethod
    def set_player_cards(state, player_id, cards):
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
            state = self.remove_player(player, state)
        return state

    @staticmethod
    def get_player(player_name, state):
        for player in state['Players']:
            if player.name == player_name:
                return player
        raise Exception('Player not found!')

    def remove_player(self, player, state):
        logging.info(
            "Player %s has shown all their influence and has lost.", player.name)
        state['Players'].remove(player)
        for p in state['Players']:
            if p.turn > player.turn:
                p.turn -= 1
        self.playerRank.append((player, len(self.playerRank)+1))
        return state

    @staticmethod
    def generate_random_players(num_players, PlayerAI, **kwargs):
        deck = Game.FULL_DECK
        players = []
        for i in range(num_players):
            name = "p" + i
            cards = Game.draw_cards(2, deck)
            p = PlayerAI(name, kwargs)
            if np.random.uniform() < 0.5:
                card = cards.pop()
                p.hidden_cards = cards
                p.flipped_cards = [card]
            p.hidden_cards = cards
            p.coins = np.random.choice(range(10))

            players.append(p)
        return players, deck

    @staticmethod
    def print_state(state):
        s = 'Turn: {} Type: {} Pending Action: {} \nDeck: {} \nExchange Options: {} \nFinished: {} Winner: {}\n'.format(
            state['Turn'], state['Type'], state['Pending Action'], state['Deck'],
            state['Exchange Options'], state['Finished'], state['Winner']
        )
        for player in state['Players']:
            s += ('Player: {} Coins: {} Turn: {} Hidden Cards: {} Revealed Cards: {}\n'.format(
                player.name, player.coins, player.turn, player.hidden_cards, player.flipped_cards
            ))
        return s


def test():

    p1 = RandomAI('p1')  # Player('p1', cards=[Card.AMBASSADOR, Card.DUKE])
    p2 = RandomAI('p2')  # Player('p2', cards=[Card.AMBASSADOR, Card.DUKE])
    p3 = RandomAI('p3')  # p3 = Player([Card.AMBASSADOR, Card.DUKE], 0, 'p3')
    p4 = RandomAI('p4')
    p5 = RandomAI('p5')
    p6 = RandomAI('p6')

    # p4 = Player([Card.AMBASSADOR, Card.DUKE], 0, 'p4')
    game = Game([p1, p2, p3, p4, p5, p6])
    game.start_game()


if __name__ == '__main__':
    test()
