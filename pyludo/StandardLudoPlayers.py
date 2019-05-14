import random
import numpy as np
from .utils import token_vulnerability
from .utils import token_barricade

"""
def play(self, state, dice_roll, next_states):
    :param state:
        current state relative to this player
    :param dice_roll:
        [1, 6]
    :param next_states:
        np array of length 4 with each entry being the next state moving the corresponding token.
        False indicates an invalid move. 'play' won't be called, if there are no valid moves.
    :return:
        index of the token that is wished to be moved. If it is invalid, the first valid token will be chosen.
"""

# q-Table states 
home = 0
common = 1
safe = 2
riskySafe = 3
goalStretch = 4
vulnerable = 5
baricade = 6
goal = 7

# actions
actOutHome = 0
actCommon = 1
actSafe = 2
actGoalStretch = 3
actStar = 4
actGoal = 5
actSuicide = 6
actBaricade = 7
actBecomeVulnerable = 8
actKill = 9




class LudoPlayerRandom:
    """ takes a random valid action """
    name = 'random'

    @staticmethod
    def play(state, dice_roll, next_states):
        return random.choice(np.argwhere(next_states != False))


class LudoPlayerFast:
    """ moves the furthest token that can be moved """
    name = 'fast'

    @staticmethod
    def play(state, _, next_states):
        for token_id in np.argsort(state[0]):
            if next_states[token_id] is not False:
                return token_id


class LudoPlayerAggressive:
    """ tries to send the opponent home, else random valid move """
    name = 'aggressive'

    @staticmethod
    def play(state, dice_roll, next_states):
        for token_id, next_state in enumerate(next_states):
            if next_state is False:
                continue
            if np.sum(next_state[1:] == -1) > np.sum(state[1:] == -1):
                return token_id
        return LudoPlayerRandom.play(None, None, next_states)


class LudoPlayerDefensive:
    """ moves the token that can be hit by most opponents """
    name = 'defensive'

    @staticmethod
    def play(state, dice_roll, next_states):
        hit_rates = np.empty(4)
        hit_rates.fill(-1)
        for token_id, next_state in enumerate(next_states):
            if next_state is False:
                continue
            hit_rates[token_id] = token_vulnerability(state, token_id)
        return random.choice(np.argwhere(hit_rates == np.max(hit_rates)))


class LudoPlayerQ:
    """" Learns to play the game via Q-learning"""
    
    def __init__(self):
        self.qTable = np.array(    [[10,0,0,0,0,0,0,0],
                                    [0,1,2,3,4,5,6,7],
                                    [0,1,2,3,4,5,6,7],
                                    [0,1,2,3,4,5,6,7],
                                    [0,1,2,3,4,5,6,7],
                                    [0,1,2,3,4,5,6,7],
                                    [0,1,2,3,4,5,6,7],
                                    [0,1,2,3,4,5,6,7],
                                    [0,1,2,3,4,5,6,7],
                                    [0,1,2,3,4,5,6,7]])

    name = 'qLeaner'

    @staticmethod
    def play(self, state, dice_roll, next_states):

        def getActions(state, dice_roll):
            print("here")

        def getState(state):
            stateArr = np.zeros(4)
            for i in range(len(state[0])):
                position = state[i]
                
                if position == -1:
                    stateArr[i] = home

                if position > -1 and position < 52:
                    stateArr[i] = common

                if position == 1:
                    stateArr[i] = safe
                
                if position > 51:
                    stateArr[i] = goalStretch

                if position % 13 == 1:
                    stateArr[i] = riskySafe

                if token_barricade(state, i):
                    stateArr = baricade

                if token_vulnerability(state,i) == 1 or token_vulnerability(state,i) == 2:
                    stateArr[i] = vulnerable
                
                if position == 99:
                    stateArr[i] = goal

            
            return stateArr

        def chooseAction(state, dice_roll):
        
            return "action"
    
        print(self.qTable)
