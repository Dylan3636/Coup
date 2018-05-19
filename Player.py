from Card import Card
from Action import Action

class Player:
    def __init__(self, cards, turn, name, player_type=0):
        self.hidden_cards = cards
        self.flipped_cards = []
        self.turn = turn
        self.coins = 0
        self.name = name
        self.player_type = player_type

    def flip_card(self, card):
        self.hidden_cards.remove(card)
        self.flipped_cards.append(card)

    def get_card(self, card_name):
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
            card = self.get_card(card_name)
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

    #  def __eq__(self, other):
    #     return self.turn == other.turn

    def __gt__(self, other):
        return self.turn > other.turn

    def __str__(self):
        return self.name
