from Card import Card
from Action import Action
from UI import UI
from Game import StateType


class Player:
    def __init__(self, player_id, turn=0, cards=None, ui=UI()):
        self.hidden_cards = []
        self.flipped_cards = []
        self.set_cards(cards)
        self.turn = turn
        self.coins = 0
        self.name = player_id
        self.ui = ui

    def request_action(self, state):
        pass

    def set_cards(self, cards):
        if cards is None:
            return

        self.hidden_cards = cards
        self.flipped_cards = []

    def flip_card(self, card):
        self.hidden_cards.remove(card)
        self.flipped_cards.append(card)

    def get_unflipped_card(self, card_name):
        for card in self.hidden_cards:
            if card.name == card_name.upper():
                return card
        else:
            raise Exception('{} does not have the unflipped card {}'.format(self.name, card_name))

    def increase_coins(self, value):
        self.coins = min(self.coins + value, 10)

    def decrease_coins(self, value, set_coins=True):
        result = self.coins - abs(value)
        if result < 0:
            net = result + abs(value)
            result = 0
        else:
            net = abs(value)
        if set_coins:
            self.coins = result
        return net

    def shuffle(self, card_names):
        cards = []
        if type(card_names) is str:
            card_names = [card_names]

        for card_name in card_names:
            card = self.get_unflipped_card(card_name)
            self.hidden_cards.remove(card)
            card, = Card.get_random_cards(1)
            self.hidden_cards.insert(0, card)
            cards.append(card)
        return cards

    def action_possible(self, action):
        if self.coins == 10:
            return action is Action.COUP
        return self.coins + action.result() >= 0

    def get_legal_actions(self, state):
        state_type = state['Type']
        options = []
        target = False
        if state_type is StateType.START_OF_TURN:
            options = [Action.EXCHANGE, Action.STEAL, Action.TAX, Action.INCOME, Action.FOREIGN_AID]
            if self.coins >= 3:
                options.append(Action.ASSASSINATE)
            if self.coins >= 7:
                options.append(Action.COUP)
            if self.coins == 10:
                options = [Action.COUP]
            target = True

        elif state_type is StateType.REQUESTING_EXCHANGE:
            exchange_options = state['Exchange Options']
            if len(exchange_options) == 4:
                options = [
                    Action.CHOOSE_CARDS_1_AND_2,
                    Action.CHOOSE_CARDS_1_AND_3,
                    Action.CHOOSE_CARDS_1_AND_4,
                    Action.CHOOSE_CARDS_2_AND_3,
                    Action.CHOOSE_CARDS_2_AND_4,
                    Action.CHOOSE_CARDS_3_AND_4
                ]
            else:
                options = [
                    Action.CHOOSE_CARD_1,
                    Action.CHOOSE_CARD_2,
                    Action.CHOOSE_CARD_3,
                ]

        elif state_type is StateType.REQUESTING_BLOCK:
            options = Action.get_blocks() + [Action.CHALLENGE, Action.EMPTY_ACTION]

        elif state_type is StateType.REQUESTING_CHALLENGE:
            options = [Action.CHALLENGE, Action.EMPTY_ACTION]

        elif state_type is StateType.REQUESTING_CARD_FLIP:
            options = [Action.FLIP_CARD_1, Action.FLIP_CARD_2]

        options.sort()
        return options, target

    def bluffing(self, action):
        for card in self.hidden_cards:
            if action in card.actions():
                return True
        return False

    def __lt__(self, other):
        return self.turn < other.turn

    def __eq__(self, other):
        if other is not Player:
            return False
        return self.name == other.name

    def __gt__(self, other):
        return self.turn > other.turn

    def __str__(self):
        return self.name


class Human(Player):

    def __init__(self, player_id, turn=0, cards=None, ui=UI()):
        Player.__init__(self, player_id, turn, cards, ui)

    def request_action(self, state):
        # legal_actions = Action.get_legal_actions(state)
        action = None
        target = None
        state_type = state['Type']
        if state_type is StateType.START_OF_TURN:
            action, target = self.ui.request_action(self, state)
        elif state_type is StateType.REQUESTING_BLOCK:
            action = self.ui.request_block(self, state)
            target = None

        elif state_type is StateType.REQUESTING_CHALLENGE:
            action = self.ui.request_challenge(self, state)  # CHALLENGE or EMPTY_ACTION/ACCEPT
            target = None

        elif state_type is StateType.REQUESTING_CARD_FLIP:
            action = self.ui.request_card_flip(self)

        elif state_type is StateType.REQUESTING_EXCHANGE:
            action = self.ui.request_exchange(self, state)
            target = None
        return action, target

# if action is Action.CHALLENGE:
#     logging.debug('%s has challenged action', player)
#     return player
# else:
#     logging.debug('%s has chosen not to challenge action', player)

    # def request_card_flip(self, state, flip_reason):
    #     if len(self.hidden_cards) == 2:
    #         card = None
    #         if self.player_type == 1:
    #             card = self.request_card_flip(state)
    #         else:
    #             if flip_reason == 1:
    #                 card = self.ui.request_card(
    #                     'The challenge was successful! {} which influence would you like to reveal?'.format(self.name)
    #                     , self)
    #             elif flip_reason == 0:
    #                 card = self.ui.request_card(
    #                     'The challenge failed! {} which influence would you like to reveal?'.format(self.name)
    #                     , self)
    #             elif flip_reason == 2:
    #                 card = self.ui.request_card(
    #                     'One of your influences have been assassinated! {} which influence would you like to reveal?'
    #                     .format(self.name), self)
    #             elif flip_reason == 3:
    #                 card = self.ui.request_card(
    #                     'There has been a coup! {} which influence would you like to reveal?'.format(self.name)
    #                     , self)
    #
    #     else:
    #
    #         if flip_reason == 1:
    #             self.ui.print_things(
    #                 'The challenge was successful!'.format(self.name))
    #         elif flip_reason == 0:
    #             self.ui.print_things(
    #                 'The challenge failed!'.format(self.name))
    #         elif flip_reason == 2:
    #             self.ui.print_things(
    #                 'One of your influences have been assassinated!'.format
    #                 (self.name))
    #         elif flip_reason == 3:
    #             self.ui.print_things(
    #                 'There has been a coup!'.format(self.name))
    #         card = self.hidden_cards[0]
