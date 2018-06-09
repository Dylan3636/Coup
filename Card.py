import numpy as np
from enum import Enum
from Action import Action


class Card(Enum):
    AMBASSADOR = 0
    ASSASSIN = 1
    CAPTAIN = 2
    CONTESSA = 3
    DUKE = 4

    def action_descriptions(self):
        if self.value == 0:
            return 'Exchange this card with another card in the deck. Block another player from stealing from you.'
        elif self.value == 1:
            return 'Pay 3 coins to assassinate another player, revealing one of their character cards.'
        elif self.value == 2:
            return 'Steal 2 coins from another player. Block another player from stealing from you.'
        elif self.value == 3:
            return 'Block a player from assassinating you.'
        else:
            return 'Take 3 coins from the treasure. Block another player from using foreign aid'

    def actions(self, name=0):
        actions = []
        if self.value == 0:  # Ambassador
            actions.append(Action.EXCHANGE)
            actions.append(Action.BLOCK_STEAL)
        elif self.value == 1:  # Assassin
            actions.append(Action.ASSASSINATE)
            actions.append(Action.BLOCK_STEAL)
        elif self.value == 2:  # Captain
            actions.append(Action.STEAL)
            actions.append(Action.BLOCK_STEAL)
        elif self.value == 3:  # Contessa
            actions.append(Action.BLOCK_ASSASSINATE)
        else:  # Duke
            actions.append(Action.TAX)
            actions.append(Action.BLOCK_FOREIGN_AID)
        actions.append(Action.INCOME)
        actions.append(Action.FOREIGN_AID)
        actions.append(Action.COUP)
        if name:
            actions = [action.name for action in actions]
        return actions

    @staticmethod
    def get_cards(card_names=None):
        card_list = [Card.AMBASSADOR, Card.ASSASSIN, Card.CAPTAIN, Card.CONTESSA, Card.DUKE]
        cards = []
        if card_names is None:
            return card_list
        for card_name in card_names:
            for card in card_list:
                if card_name == card.name:
                    cards.append(card)
        return cards

    @staticmethod
    def get_random_cards(num, deck=None):
        if deck is None:
            return np.random.choice(Card.get_cards(), num, replace=True)
        else:
            return np.random.choice(deck, num, replace=False)

    @staticmethod
    def get_card_from_action(action):
        for card in Card.get_cards():
            if action in card.actions():
                return card

    def __eq__(self, other):
        if type(other) is str:
            return self.name == other.upper()
        else:
            return self.name == other.name

    def __str__(self):
        return self.name
