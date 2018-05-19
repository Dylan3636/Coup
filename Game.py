import numpy as np
import re
from pandas import DataFrame
from Card import Card
from Action import Action
from Player import Player

'''
@Author=Dylan
'''








class UI:

    def __init__(self, default_type):
        self.default_type = default_type

    def request_input(self, s, recipient=None):
        if self.default_type == 0:
            return input(s)

    def print_things(self, s, recipient=None):
        if self.default_type == 0:
            print(s)


class Game:
    def __init__(self, players, ui_type=0):
        self.players = players
        while None in self.players:
            self.players.remove(None)
        self.players.sort()
        self.turn = 0
        self.card_count = {}
        self.ui = UI(ui_type)

        for player in self.players:
            for card in player.hidden_cards:
                if card.name in self.card_count:
                    check = self.card_count[card.name] + 1 > 3
                    skip = False
                    while check:
                        card, = player.shuffle(card.name)
                        if card.name not in self.card_count:
                            check = False
                            self.card_count[card.name] = 1
                            skip = True
                        else:
                            check = (self.card_count[card.name] + 1) > 3
                    if not skip:
                        self.card_count[card.name] = self.card_count[card.name] + 1
                else:
                    self.card_count[card.name] = 1

    def get_state(self, p1=None, hidden=True):
        players = []
        coins = []
        hidden_cards = []
        flipped_cards = []

        for player in self.players:
            if not((p1 is None) or (p1 == player)):
                continue
            players.append(player.name)
            coins.append(player.coins)
            if hidden:
                hidden_cards.append(len(player.hidden_cards))
            else:
                hidden_cards.append([card.name for card in player.hidden_cards])
            flipped_cards.append([card.name for card in player.flipped_cards])

        state = DataFrame()
        state['Player'] = players
        state['Coins'] = coins
        state['Hidden Cards'] = hidden_cards
        state['Flipped Cards'] = flipped_cards

        return state
    def next_state(self, state, action):
        
    def possible_result_states(self, state, action, player, target=None, challenge=0, allow=0):
        if not player.action_possible(action):
            return
        player_id = (state['Player'] == player.name)
        target_id = (state['Player'] == target.name)

        possible_states = []

        if action.value == 5:  # Steal
            cpy = state.copy()
            block_results = self.possible_result_states(cpy, Action.BLOCK_STEAL, player, target)  # block successful/ block challenge fail/ block challenge successful

            successful_challenges = []
            if not player.legal_action(action):
                for challenger in self.players:
                    tmp = cpy.copy()
                    tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
                    successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            cpy.loc[target_id, 'Coins'] -= 2  # no challenge
            cpy.loc[player_id, 'Coins'] += 2  # no challenge
            if allow:
                return possible_states.append(cpy.loc[:,['Coins', 'Hidden Cards']].values.flatten())

            failed_challenges = []
            for challenger in self.players:
                challenger_id = (state['Player'] == challenger.name)
                tmp3 = cpy.copy()
                tmp3.loc[challenger_id, 'Hidden Cards'] -= 1  # challenge failed
                failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            if challenge == 1:
                return np.concatenate((failed_challenges, successful_challenges))

            possible_states.append(cpy.loc[:, ['Coins','Hidden Cards']].values.flatten())
            return np.concatenate((possible_states, failed_challenges, successful_challenges, block_results)).tolist()

        elif action.value == 6:  # Tax
            cpy = state.copy()

            successful_challenges = []
            if not player.legal_action(action):
                for challenger in self.players:
                    tmp = cpy.copy()
                    tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
                    successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            cpy.loc[player_id, 'Coins'] += 3  # no challenge

            failed_challenges = []
            for challenger in self.players:
                challenger_id = (state['Player'] == challenger.name)
                tmp3 = cpy.copy()
                tmp3.loc[target_id, 'Hidden Cards'] -= 1  # challenge failed
                failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            if challenge == 1:
                return np.concatenate((failed_challenges, successful_challenges))

            possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())

            return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()

        elif action.value == 7:  # Income
            cpy = state.copy()
            cpy.loc[player_id, 'Coins'] += 1
            return possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())

        elif action.value == 8:  # Foreign Aid
            cpy = state.copy()
            block_results = self.possible_result_states(cpy, Action.BLOCK_FOREIGN_AID, target, player)

            successful_challenges = []
            if not player.legal_action(action):
                for challenger in self.players:
                    tmp = cpy.copy()
                    tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
                    successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            cpy.loc[player_id, 'Coins'] += 2  # no challenge
            if allow:
                return possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())

            failed_challenges = []
            for challenger in self.players:
                challenger_id = (state['Player'] == challenger.name)
                tmp3 = cpy.copy()
                tmp3.loc[challenger_id, 'Hidden Cards'] -= 1  # challenge failed
                failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            if challenge == 1:
                return np.concatenate((failed_challenges, successful_challenges))

            possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            return np.concatenate((possible_states, failed_challenges, successful_challenges, block_results)).tolist()

        elif action.value == 0:  # Assassinate
            cpy = state.copy()
            if player.action_possible(action):
                cpy.loc[player_id, 'Coins'] -= 3
                block_results = self.possible_result_states(cpy, Action.BLOCK_FOREIGN_AID, target, player)

                successful_challenges = []
                if not player.legal_action(action):
                    for challenger in self.players:
                        tmp = cpy.copy()
                        tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
                        successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

                cpy.loc[target_id, 'Hidden Cards'] -= 1  # no challenge
                if allow:
                    return possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

                failed_challenges = []
                for challenger in self.players:
                    if challenger == target and len(target.hidden_cards)==0:
                        continue
                    challenger_id = (state['Player'] == challenger.name)
                    tmp3 = cpy.copy()
                    tmp3.loc[challenger_id, 'Hidden Cards'] -= 1  # challenge failed
                    failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

                if challenge == 1:
                    return np.concatenate((failed_challenges, successful_challenges))

                possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())

                return np.concatenate((possible_states, failed_challenges, successful_challenges, block_results)).tolist()

        elif action.value == 9:  # Coup
            cpy = state.copy()
            if player.action_possible(action):
                cpy.loc[player_id, 'Coins'] -= 7
                cpy.loc[target_id, 'Hidden Cards'] -=1
                possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

        elif action.value == 1:  # Block Assassinate
            cpy = state.copy()  # no challenge
            possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
            if allow:
                return possible_states

            successful_challenges = []
            failed_challenges = []

            for challenger in self.players:
                challenger_id = (state['Player'] == challenger.name)

                tmp2 = state.copy()
                tmp2.loc[challenger_id, 'Hidden Cards'] -= 1  # block challenge failed
                failed_challenges.append(tmp2.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

                if not player.legal_action(action):
                    tmp = cpy.copy()
                    tmp.loc[player_id, 'Hidden Cards'] -= 1  # block challenge successful
                    if len(tmp.hidden_cards) == 1:
                        tmp[player_id, 'Hidden Cards'] -= 1  # proceeded with assassination
                    successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            if challenge == 1:
                return np.concatenate((failed_challenges, successful_challenges))

            return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()

        elif action.value == 2:  # Block Foreign Aid
            cpy = state.copy()  # no challenge
            possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
            if allow:
                return possible_states

            successful_challenges = []
            failed_challenges = []

            for challenger in self.players:
                challenger_id = (state['Player'] == challenger.name)

                tmp2 = state.copy()
                tmp2.loc[challenger_id, 'Hidden Cards'] -= 1  # block challenge failed
                failed_challenges.append(tmp2.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

                if not player.legal_action(action):
                    tmp = cpy.copy()
                    tmp.loc[player_id, 'Hidden Cards'] -= 1  # block challenge successful
                    tmp[target_id, 'Coins'] += 2  # proceed with foreign aid
                    successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            if challenge == 1:
                return np.concatenate((failed_challenges, successful_challenges))

            return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()

        elif action.value == 3:  # Block Steal
            cpy = state.copy()  # no challenge
            possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())
            if allow:
                return possible_states

            successful_challenges = []
            failed_challenges = []

            for challenger in self.players:
                challenger_id = (state['Player'] == challenger.name)

                tmp2 = state.copy()
                tmp2.loc[challenger_id, 'Hidden Cards'] -= 1  # block challenge failed
                failed_challenges.append(tmp2.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

                if not player.legal_action(action):
                    tmp = cpy.copy()
                    tmp.loc[player_id, 'Hidden Cards'] -= 1  # block challenge successful
                    net = player.decrease_coins(2,set_coins=False)
                    tmp[player_id, 'Coins'] -= net  # proceed with steal
                    tmp[target_id, 'Coins'] += net  # proceed with steal

                    successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            if challenge == 1:
                return np.concatenate((failed_challenges, successful_challenges))

            return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()

        elif action.value == 4:  # Exchange
            cpy = state.copy()

            successful_challenges = []
            if not player.legal_action(action):
                for _ in self.players:
                    tmp = cpy.copy()
                    tmp.loc[player_id, 'Hidden Cards'] -= 1  # challenge successful
                    successful_challenges.append(tmp.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            possible_states.append(cpy.loc[:, ['Coins', 'Hidden Cards']].values.flatten())  # no challenge

            if allow:
                return possible_states.append(cpy.loc[:,['Coins','Hidden Cards']].values.flatten())

            failed_challenges = []
            for challenger in self.players:
                challenger_id = (state['Player'] == challenger.name)
                tmp3 = cpy.copy()
                tmp3.loc[challenger_id, 'Hidden Cards'] -= 1  # challenge failed
                failed_challenges.append(tmp3.loc[:, ['Coins', 'Hidden Cards']].values.flatten())

            if challenge == 1:
                return np.concatenate((failed_challenges, successful_challenges))

            return np.concatenate((possible_states, failed_challenges, successful_challenges)).tolist()

    def begin(self):
        while len(self.players) > 1:
            self.next_turn()
            self.ui.print_things(self.get_state(),0)

    def next_turn(self):
        self.turn = (self.turn + 1) % len(self.players)
        player = self.players[self.turn]
        action, target = self.ask_for_action(player)
        result = self.try_action(action, player, target)

        while result == -1:
            if player.coins == 10:
                self.ui.print_things("You have too many coins! You must commit a coup.")
            else:
                self.ui.print_things("You do not have enough coins to take that action.")
            action, target = self.ask_for_action(player)
            result = self.try_action(action, player, target)

    def ask_for_action(self, player):
        action = input('{} it is your turn. What action would you like to take? '.format(player))
        action = action.strip().upper()
        action = Action.get_action(action)
        if action in [Action.INCOME, Action.TAX, Action.EXCHANGE, Action.FOREIGN_AID]:
            return action, None
        target = input('Who would you like to take this action against? ')
        target = target.strip()
        return action, self.get_player(target)

    def ask_for_challenge_or_block(self, p1, p2, action):
        if action in [Action.INCOME, Action.COUP]:
            return 0, None
        blockable = True
        if action in [Action.TAX, Action.EXCHANGE, Action.BLOCK_STEAL, Action.BLOCK_FOREIGN_AID, Action.BLOCK_ASSASSINATE]:
            blockable = False
        players = self.players[:]
        players.remove(p1)
        for i, player in enumerate(players):
            typo = True
            while typo:
                if blockable:
                    answer = self.ui.request_input(
                        'Player {} has just used {}. {} would you like to challenge or block? (challenge/block/no)'.format(p1.name, action.name, player.name.capitalize()), player)
                else:
                    answer = self.ui.request_input(
                        'Player {} has just used {}. {} would you like to challenge? (challenge/yes or no)'.format(p1.name, action.name, player.name.capitalize()), player)
                tmp = answer.strip()
                challenge_or_block = tmp

                if challenge_or_block == 'challenge':
                    return 1, player, Card.get_card_from_action(action)
                elif challenge_or_block == 'yes' and not blockable:
                    return 1, player, Card.get_card_from_action(action)
                elif challenge_or_block == 'yes' and blockable:
                    self.ui.print_things('Please insert challenge or block', player)
                elif challenge_or_block == 'block':
                    card = self.ui.request_input('Which influence are you using to block the action', player)
                    card = card.strip()
                    return -1, player, card
                elif challenge_or_block == 'no':
                    typo = False
                else:
                    self.ui.print_things('I believe {} was a typo. Try again.'.format(tmp), player)
        return 0, None, None

    def request_card_flip(self, flip_reason, player):
        answer = ''
        if len(player.hidden_cards) == 2:
            if flip_reason == 1:
                answer = self.ui.request_input(
                    'The challenge was successful! {} which influence would you like to reveal?'.format(player.name), player)
            elif flip_reason == 0:
                answer = self.ui.request_input(
                    'The challenge failed! {} which influence would you like to reveal?'.format(player.name), player)
            elif flip_reason == 2:
                answer = self.ui.request_input(
                    'One of your influences have been assassinated! {} which influence would you like to reveal?'.format
                    (player.name), player)
            elif flip_reason == 3:
                answer = self.ui.request_input(
                    'There has been a coup! {} which influence would you like to reveal?'.format(player.name), player)

            answer = answer.strip().upper()
            card = player.get_card(answer)
        else:

            if flip_reason == 1:
                self.ui.print_things(
                    'The challenge was successful!'.format(player.name))
            elif flip_reason == 0:
                self.ui.print_things(
                    'The challenge failed!'.format(player.name))
            elif flip_reason == 2:
                self.ui.print_things(
                    'One of your influences have been assassinated!'.format
                    (player.name))
            elif flip_reason == 3:
                self.ui.print_things(
                    'There has been a coup!'.format(player.name))

            card = player.hidden_cards[0]
        self.flip_player_card(player, card)

    def request_exchange(self, player):
        cards = Card.get_random_cards(len(player.hidden_cards))
        choices = player.hidden_cards
        choices = np.append(choices, cards).tolist()
        decision = self.ui.request_input('{} these are your choices {}. Which would you like to keep?'.format(
            player.name, choices))
        cards = re.split('\W+', decision)
        player.hidden_cards = Card.get_cards(cards)

    def try_action(self, action, player, target=None, card=None):
        result = action.result()
        if not player.action_possible(action):
            return -1
        else:
            if result < 0:
                player.decrease_coins(result)
            if action in [Action.INCOME, Action.COUP]:
                self.do_action(action, player, target)
                return
            challenge_or_block, challenger_or_blocker, block_card = self.ask_for_challenge_or_block(player, target, action)

            if challenge_or_block == 1:

                challenge_success = True

                for card in player.hidden_cards:
                    challenge_success = challenge_success and action not in card.actions()

                self.process_challenge_result(challenge_success, action, player, challenger_or_blocker, card)

            elif challenge_or_block == 0:
                self.ui.print_things('No challenge was attempted')
                self.do_action(action, player, target)

            else:
                block = action.get_block()
                challenge, challenger = self.ask_for_challenge_or_block(target, player, block)

                if challenge == 1:

                    challenge_success = False

                    for card in target.hidden_cards:
                        challenge_success = challenge_success or action in card.actions()

                    self.process_challenge_result(challenge_success, block, target, challenger, card)
                else:
                    self.process_challenge_result(0, block, target, challenger, card)

    def process_challenge_result(self, result, action, p1, p2, card=None):
        """Process the result of p2's challenge of p1's action"""
        if result == 1:
            self.request_card_flip(1, p1)
        else:
            self.request_card_flip(0, p2)
            self.do_action(action, p1, p2)
            p1.shuffle(card.name)

    def do_action(self, action, p1, p2):
        if action is Action.ASSASSINATE:
            self.request_card_flip(2, p2)
        elif action is Action.EXCHANGE:
            self.request_exchange(p1)
        elif action is Action.STEAL:
            net = p2.decrease_coins(action.result())
            p1.increase_coins(net)
        elif action is Action.COUP:
            self.request_card_flip(3, p2)
        else:
            p1.increase_coins(action.result())

    def flip_player_card(self,player,card):
        player.flip_card(card)
        if player.hidden_cards == []:
            self.remove_player(player)

    def get_player(self, player_name):
        for player in self.players:
            if player.name == player_name:
                return player
        raise Exception('Player not found!')

    def remove_player(self, player):
        print("Player {} has shown all their influence and has lost.".format(player.name))
        self.players.remove(player)


def test():

    p1 = Player([Card.AMBASSADOR, Card.DUKE], 0, 'p1')
    p2 = Player([Card.AMBASSADOR, Card.DUKE], 0, 'p2')
    # p3 = Player([Card.AMBASSADOR, Card.DUKE], 0, 'p3')
    # p4 = Player([Card.AMBASSADOR, Card.DUKE], 0, 'p4')

    game = Game(p1, p2)
    print(game.card_count)
    game.begin()

if __name__ == '__main__':
    test()


