from Card import Card
from Action import Action


class Player:
    def __init__(self, player_id, turn=0, cards=None, player_type=0):
        self.set_cards(cards)
        self.turn = turn
        self.coins = 0
        self.name = player_id
        self.player_type = player_type
        #self.ai = AI(player_type)

    def request_action(self, state):
        if self.player_type == 1:
            action, target = self.request_action(state)
        else:
            action = self.ui.request_action('{} it is your turn. What action would you like to take? '.format(self),
                                            self)
            if action in [Action.INCOME, Action.TAX, Action.EXCHANGE, Action.FOREIGN_AID]:
                return action, None
            target = self.ui.request_input('Who would you like to take this action against? ', self)
            target = target.strip()
            target = self.get_player(target, self)
        return action, target

    def request_challenge(self, state):
            if player is p1:
                continue
            if player.player_type == 1:
                action = player.request_challenge(state)
            else:
                action = self.ui.request_challenge(player, state)  # CHALLENGE or EMPTY_ACTION/ACCEPT
            if action is Action.CHALLENGE:
                logging.debug('%s has challenged action', player)
                return player
            else:
                logging.debug('%s has chosen not to challenge action', player)
        return None

    def request_card_flip(self, state, flip_reason):
        if len(self.hidden_cards) == 2:
            card = None
            if self.player_type == 1:
                card = self.request_card_flip(state)
            else:
                if flip_reason == 1:
                    card = self.ui.request_card(
                        'The challenge was successful! {} which influence would you like to reveal?'.format(self.name)
                        , self)
                elif flip_reason == 0:
                    card = self.ui.request_card(
                        'The challenge failed! {} which influence would you like to reveal?'.format(self.name)
                        , self)
                elif flip_reason == 2:
                    card = self.ui.request_card(
                        'One of your influences have been assassinated! {} which influence would you like to reveal?'
                        .format(self.name), self)
                elif flip_reason == 3:
                    card = self.ui.request_card(
                        'There has been a coup! {} which influence would you like to reveal?'.format(self.name)
                        , self)

        else:

            if flip_reason == 1:
                self.ui.print_things(
                    'The challenge was successful!'.format(self.name))
            elif flip_reason == 0:
                self.ui.print_things(
                    'The challenge failed!'.format(self.name))
            elif flip_reason == 2:
                self.ui.print_things(
                    'One of your influences have been assassinated!'.format
                    (self.name))
            elif flip_reason == 3:
                self.ui.print_things(
                    'There has been a coup!'.format(self.name))
            card = self.hidden_cards[0]

    def set_cards(self, cards):
        if cards is None:
            return
        self.hidden_cards = cards
        self.flipped_cards = []
        self.cards = zip(cards, [False, False])

    def flip_card(self, card):
        # for i, tup in enumerate(self.cards):
        #     if tup[0] == card:
        #         self.cards[i][1] = True
        self.hidden_cards.remove(card)
        self.flipped_cards.append(card)

    def get_unflipped_card(self, card_name):
        # for tup in self.cards:
        #     card = tup[0]
        #     if card.name == card_name.upper():
        #         return card
        # else:
        #     raise Exception('{} does not have the unflipped card {}'.format(self.name, card_name))
        for card in self.hidden_cards:
            if card.name == card_name.upper():
                return card
        else:
            raise Exception('{} does not have the unflipped card {}'.format(self.name, card_name))

    def increase_coins(self, value):
        self.coins = min(self.coins + value, 10)

    def decrease_coins(self, value, set_coins=True):
        tmp = self.coins - abs(value)
        if tmp < 0:
            net = tmp - abs(value)
            tmp = 0
        else:
            net = abs(value)
        if set_coins:
            self.coins = tmp
        return net

    def shuffle(self, card_names):
        cards = []
        if type(card_names) is str:
            card_names = [card_names]

        for card_name in card_names:
            card = self.get_unflipped_card(card_name)
            self.hidden_cards.remove(card)
            card, = Card.get_random_cards(1)
            self.hidden_cards.insert(0,card)
            cards.append(card)
        return cards

    def action_possible(self, action):
        if self.coins == 10:
            return action is Action.COUP
        return self.coins + action.result() >= 0

    def legal_action(self, action, discriminate=True):
        if discriminate:
            if self.player_type == 0:
                return False
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
