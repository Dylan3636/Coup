from enum import Enum
class Action(Enum):
    ASSASSINATE = 0
    BLOCK_ASSASSINATE = 1
    BLOCK_FOREIGN_AID = 2
    BLOCK_STEAL = 3
    EXCHANGE = 4
    STEAL = 5
    TAX = 6
    INCOME = 7
    FOREIGN_AID = 8
    COUP = 9
    EMPTY_ACTION = -1

    def result(self):
        """Result of actions in terms of coins gained or lost"""
        if self.value == 5:  # Steal
            return 2
        elif self.value == 6:  # Tax
            return 3
        elif self.value == 7:  # Income
            return 1
        elif self.value == 8:  # Foreign Aid
            return 2
        elif self.value == 0:  # Assassinate
            return -3
        elif self.value == 9:  # Coup
            return -7
        else:
            return 0

    def get_block(self):
        """ Function to retrieve corresponding block for the action if it exists else return -1"""
        if self.value == 1:
            return Action.BLOCK_ASSASSINATE
        elif self.value == 2:
            return Action.BLOCK_FOREIGN_AID
        elif self.value == 3:
            return Action.BLOCK_STEAL
        else:
            return -1

    @staticmethod
    def get_blocks(read=0):

        blocks = [Action.BLOCK_ASSASSINATE, Action.BLOCK_FOREIGN_AID, Action.BLOCK_STEAL]
        if read:
            blocks = [block.name for block in blocks]
        return blocks

    @staticmethod
    def get_action(action_name):
        actions = [Action.ASSASSINATE, Action.EXCHANGE, Action.STEAL, Action.TAX, Action.INCOME, Action.FOREIGN_AID,
                   Action.COUP]
        for action in actions:
            if action.name == action_name:
                return action
        raise Exception('Action not found!')

    @staticmethod
    def get_actions():
        actions = [Action.ASSASSINATE, Action.EXCHANGE, Action.STEAL, Action.TAX, Action.INCOME, Action.FOREIGN_AID,
                   Action.COUP]
        return actions

    def __str__(self):
        return self.name
