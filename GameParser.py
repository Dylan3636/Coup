import ijson
# class CoupParser:
#
#     def __init__(self):
#         pass
#
#     def parse_file(self, filename):
import logging
from Game import Game, Player
from State import StateType
from Action import Action
from Card import Card
LOGLEVEL=logging.DEBUG
logging.basicConfig(format='%(levelname)s: %(message)s', level=LOGLEVEL)

with open('db/games.json') as json_file:
    parser = ijson.parse(json_file)
    game_events = False
    players = []
    index = 0
    ai_count = None
    turn = None
    GameTrees = []
    ActionTrees = []
    num_games = 0
    skip = False
    accepted=False
    for i, tup in enumerate(parser):
        prefix, event, value = tup
        if num_games == 98:
            print(prefix, event, value)

        if num_games >= 5:
            break

        if skip or prefix == 'item.gameType':
            if prefix == 'item.gameType':
                skip = value == 'inquisitors'
                if skip:
                    state = None
                    logging.warning('SKIPPING INQUISITOR GAME')
            else:
                continue

        if prefix == 'item' and event == 'start_map':
            logging.debug('STARTING NEW GAME')
            num_games += 1
            GameTree = []
            id = 0

        if prefix == 'item' and event == 'end_map':
            logging.debug('FINISHED GAME\n')
            num_games += 1
            print(num_games)
            GameTrees.append(GameTree)
            #ActionTrees.append(ActionTree)


        if prefix == 'item.playerIds' and event == 'start_array':
            logging.debug('Entering playerIds')
            players = []
            ai_count = 0
            turn = 0

        if prefix == 'item.playerIds.item':
            if value == 'ai':
                player = Player(str(value)+str(ai_count), turn)
                ai_count += 1
            else:
                player = Player(value, turn)
            logging.debug("Adding player %s", player)
            turn += 1
            players.append(player)

        if prefix == 'item.playerIds' and event == 'end_array':
            logging.debug('Exiting playerIds')

        if prefix == 'item.events' and event == 'start_array':
            logging.debug('Entering events')
            game_events = True
            state = {'Players': [], 'Turn': 0, 'Type': None, 'Pending Action': None, 'Exchange Options': [], 'Finished': False, 'Winner': None, 'Deck': None, 'id': id}
            id += 1
            ActionTree = []
        if prefix == 'item.events':
            print (prefix, event, value)

        if prefix == 'item.events' and event == 'end_array':
            logging.debug('Exiting events')
            #logging.debug('Adding to Game Tree: %s', state)
            game_events = False

        if prefix == 'item.events.item.type':
            logging.debug('Dealing with game state %s', value)
            action = None
            if value == 'START_OF_TURN':
                state['Type'] = StateType.START_OF_TURN
                state['Pending Action'] = None
                if accepted:
                    ActionTree.append((Action.EMPTY_ACTION, target, None))
                    accepted = False
                ActionTrees.append(ActionTree)
                ActionTree = []

            if value == 'ACTION':
                player = state['Players'][turn]
                accepted = True

            if value == 'BLOCK':
                player = state['Players'][turn]
                # TODO Adding action tree. A list of actions, synced up with the states so that the auto players know how to respond.
                # state['Type'] = StateType.REQUESTING_BLOCK
                # logging.debug('Adding to Game Tree: %s', state)
                # GameTree.append(state)
                # state = state.copy()

            if value == 'CHALLENGE_SUCCESS':
                pass

            if value == 'CHALLENGE_FAILED':
                pass
            if value == 'PLAYER_LEFT':
                pass
            if value == 'GAME_OVER':
                pass

        if prefix == 'item.events.item.action':
            logging.debug('Pending action: %s', value)
            act = Action.get_action(value)
            action = (act, player, None)
            if act in [Action.EMPTY_ACTION, Action.INCOME, Action.COUP, Action.CHALLENGE]:
                accepted = False
            else:
                accepted = True


        if prefix == 'item.events.item.target':
            target = state['Players'][value]
            logging.debug('Target %s', target)
            action = (act, player, target)

        if prefix == 'item.events.item.blockingPlayer':
            blocking_player = state['Players'][value]
            logging.debug('Blocking player: %s', blocking_player)

        if prefix == 'item.events.item.blockingRole':
            logging.debug('Blocking role: %s', value)
            blocking_role = Card.get_cards(str(value))
            blocking_action = blocking_role.get_block()
            action = (blocking_action, blocking_player, player)
            accepted = True

        if prefix == 'item.events.item.challenger':
            challenger = state['Players'][value]
            logging.debug('Challenger: %s', challenger)

        if prefix == 'item.events.item.challenged':
            challengee = state['Players'][value]
            logging.debug('Challenger: %s', challengee)
            action = (Action.CHALLENGE, challenger, challengee)
            accepted = False

        if prefix == 'item.events.item' and event == 'start_map':
            action = None

        if prefix == 'item.events.item' and event == 'end_map':
            #logging.debug('Adding to Game Tree: %s', state)
            #GameTree.append(state)
            if action is not None:
                logging.debug('Adding to Action Tree: %s', action)
                ActionTree.append(action)

            state = state.copy()
            # TODO Do stuff with gameType

        if prefix == 'item.events.item.playerStates' and event == 'start_array':
            player_states = True
            state['Players'] = []
            deck = Game.new_deck()[:]
            index = 0

        # TODO Store player states
        if prefix == 'item.events.item.playerStates' and event == 'end_array':
            player_states = False
            logging.debug('Adding to Game Tree: %s', state)
            GameTree.append(state)

        if prefix == 'item.events.item.playerStates.item' and event == 'start_map':
            filling_player = True
            player = players[index].__copy__()
            flipped_cards = []
            hidden_cards = []
            logging.debug("Start filling player %s state", player)

        if prefix == 'item.events.item.playerStates.item' and event == 'end_map':
            player.hidden_cards = hidden_cards
            player.flipped_cards = flipped_cards
            state['Players'].append(player)
            state['Deck'] = deck
            logging.debug("Finished filling player %s state", player)
            index += 1

        if prefix == 'item.events.item.playerStates.item.cash':
            logging.debug("Entering coin value of {} ".format(int(value)))
            if value > 10:
                skip = True
            player.coins = int(value)

        if prefix == 'item.events.item.whoseTurn':
            logging.debug("Entering value for turn: {} ".format(value))
            turn = value
            state['Turn'] = turn

        if prefix == 'item.events.item.playerStates.item.influence.item.role':
            influence = Card.get_cards(str(value))
            logging.debug("Influence {} has been removed from the deck".format(influence))
            try:
                deck.remove(influence)
            except ValueError:
                pass # TODO game simulation apparently allows for more than three copies of each card. This may need to be addressed in the future.
            if (revealed):
                logging.debug("Influence {} has been added to player's flipped cards ".format(influence))
                flipped_cards.append(influence)
            else:
                logging.debug("Influence {} has been added to player's hidden cards ".format(influence))
                hidden_cards.append(influence)

        if prefix == 'item.events.item.playerStates.item.influence.item.revealed':
            revealed = value

        if prefix == 'item.events.item.playerStates.item.influence' and event == 'end_array':
            if flipped_cards == [] and hidden_cards == []:
                skip = True

        if prefix == 'item.events.item.playerStates' and event == 'end_array':
            player_states = False

    for i, state in enumerate(GameTrees[0]):
        print(state)
        for action in ActionTrees[i]:
            print(action)
        print



