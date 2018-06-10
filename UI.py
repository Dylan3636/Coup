import re
from Action import Action

class UI:

    def __init__(self, default_type):
        self.default_type = default_type

    def request_input(self, s, player):
        if self.default_type == 0:
            return input(s)

    def request_card(self, s, player):
        if self.default_type == 0:
            answer = input(s)
            cards = re.split('\W+', answer)
            return cards

    def request_action(self, s, player):
        if self.default_type == 0:
            answer = input(s)
            answer = answer.strip().upper()
            return Action.get_action(answer)

    def request_challenge(self, player, state):
        action, p1_id, _ = state['Pending Action']
        p1 = state['Players'][p1_id]
        if player.player_type == 1:
            return player.request_challenge(player, state)
        while True:
            answer = self.request_input(
                'Player {} has just used {}. {} would you like to challenge? (challenge/yes or no)'.format(p1.name,
                                                                                                           action.name,
                                                                                                           player.name.
                                                                                                           capitalize())
                , player)
            challenge = answer.strip().lower()

            if challenge in ['challenge','yes', 'y']:
                return Action.CHALLENGE
            elif challenge in ['no', 'n']:
                return None
            else:
                self.print_things('I believe {} was a typo. Try again.'.format(challenge), player)

    def print_things(self, s, recipient=None):
        if self.default_type == 0:
            print(s)
