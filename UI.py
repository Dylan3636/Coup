import re
from Action import Action
from Game import Game

class UI:
    def __init__(self, default_type=0):
        self.default_type = default_type

    def request_input(self, s, player):
        if self.default_type == 0:
            return input(s)

    def print_things(self, s, recipient=None):
        if self.default_type == 0:
            print(s)

    def request_card_flip(self, player):
        num_hiddens = len(player.hidden_cards)
        if num_hiddens == 1:
            return Action.FLIP_CARD_1S
        else:
            answer = self.request_input('Please choose influence to reveal ({}/0 or {}/1)'.format(player.hidden_cards[0], player.hidden_cards[1]), player)
            answer = answer.strip().lower()
            while True:
                if answer in [player.hidden_cards[0].name, '0']:
                    return Action.FLIP_CARD_1
                elif answer in [player.hidden_cards[0].name, '0']:
                    return Action.FLIP_CARD_2
                else:
                    self.typo_check(answer, player)

    def request_exchange(self, player, state):
        options = state['Exchange Options']
        num_options = len(options)
        if num_options == 3:
            while True:
                answer = self.request_input(
                    'Please choose the card you want to keep from these options {}, ({}/0, {}/1, {}/2)'.format(options, options[0], options[1], options[2]), player)
                answer = answer.strip().lower()
                for index, option in enumerate(options):
                    if answer in [index, option]:
                        return [Action.CHOOSE_CARD_1, Action.CHOOSE_CARD_2, Action.CHOOSE_CARD_3][index]
                self.typo_check(answer, player)

        else:
            typo=True
            first = None
            while typo:
                answer = self.request_input(
                    'Please choose the first card you want to keep from these options {}, ({}/0, {}/1, {}/2, {}/3)'.format(
                        options, options[0], options[1], options[2], options[3]), player)
                answer = answer.strip().lower()
                for index, option in enumerate(options):
                    if answer in [index, option]:
                        first = index
                        typo = False
                        break
                if typo:
                    self.typo_check(answer, player)
            options.pop(first)

            typo=True
            second=None
            while typo:
                answer = self.request_input(
                    'Please choose the second card you want to keep from these options {}, ({}/0, {}/1, {}/2)'.format(
                        options, options[0], options[1], options[2]), player)
                answer = answer.strip().lower()
                for index, option in enumerate(options):
                    if answer in [index, option]:
                        second = index if index<first else index + 1
                        typo = False
                        break
                if typo:
                    self.typo_check(answer, player)

            if 1 in [first, second]:
                if 2 in [first, second]:
                    return Action.CHOOSE_CARDS_1_AND_2
                elif 3 in [first, second]:
                    return Action.CHOOSE_CARDS_1_AND_3
                elif 4 in [first, second]:
                    return Action.CHOOSE_CARDS_1_AND_4
            elif 2 in [first, second]:
                if 3 in [first, second]:
                    return Action.CHOOSE_CARDS_2_AND_3
                elif 4 in [first, second]:
                    return Action.CHOOSE_CARDS_2_AND_4
            elif 3 in [first, second]:
                if 4 in [first, second]:
                    return Action.CHOOSE_CARDS_3_AND_4

    def request_card(self, s, player):
        if self.default_type == 0:
            answer = input(s)
            cards = re.split('\W+', answer)
            return cards

    def request_action(self, player, state):
        action = self.request_only_action('{} it is your turn. What action would you like to take? '.format(player),
                                        player)
        if action in [Action.INCOME, Action.TAX, Action.EXCHANGE, Action.FOREIGN_AID]:
            return action, None
        target = self.request_target(player, state)
        return action, target

    def request_target(self, player, state):
        while True:
            target = self.request_input('Who would you like to take this action against? ', self)
            target = target.strip()
            try:
                target = Game.get_player(state, target)
                return target
            except:
                self.typo_check(target, player)

    def request_only_action(self, s, player):
        while True:
            answer = self.request_input(s, player)
            answer = answer.strip().upper()
            try:
                action = Action.get_action(answer)
                return action
            except:
                self.typo_check(answer, player)

    def request_block(self, player, state):
        action, p1_id, p2_id = state['Pending Action']
        p1 = state['Players'][p1_id]

        while True:
            answer = self.request_input(
                'Player {} has just used {}. {} would you like to block? (yes or no)'.format(p1.name,
                                                                                                           action.name,
                                                                                                           player.name.
                                                                                                           capitalize())
                , player)
            answer = answer.strip().lower()

            if answer in ['yes', 'y']:
                if action is Action.STEAL:
                    answer = self.request_input(
                        'Which influence will you use to block the steal, Ambassador or Captain? (Ambassador/0 or Captain/1)'.format(player.name.
                                                                                                     capitalize()), player)
                    answer = answer.strip().lower()
                    while True:
                        if answer in ['ambassador', '0']:
                            return Action.BLOCK_STEAL_AMBASSADOR
                        elif answer in ['captain', '1']:
                            return Action.BLOCK_STEAL_CAPTAIN
                        else:
                            self.typo_check(answer, player)
                else:
                    return action.get_block()
            elif answer in ['no', 'n']:
                return Action.EMPTY_ACTION
            else:
                self.typo_check(answer, player)



    def request_challenge(self, player, state):
        action, p1_id, _ = state['Pending Action']
        p1 = state['Players'][p1_id]
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
                self.typo_check(answer, player)


    def typo_check(self, answer, player):
        self.print_things('I believe {} was a typo. Try again.'.format(answer), player)
