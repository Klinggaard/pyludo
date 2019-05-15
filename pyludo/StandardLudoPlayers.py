import random
import numpy as np
from .utils import token_vulnerability, token_barricade, star_jump, will_send_self_home, will_send_opponent_home 

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


qTable = np.array(     [[10,0,0,0,0,0,0,0,0,0], # home
                        [0,1,2,3,4,10,-100,7,8,9],  # common
                        [0,1,2,3,4,10,-100,3,-10,5],  # safe
                        [0,1,2,1,4,10,-100,7,2,0],  # riskySafe
                        [0,0,-1,0,0,10,-100,0,0,0],  # goalStretch
                        [0,1,2,3,4,10,-100,6,8,0],  # vulnerable
                        [0,1,2,3,4,10,6,-200,-1,3],  # baricade
                        [0,0,0,0,0,0,0,0,0,0]]) # goal

inf = 9999999999999

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
actRiskySafe = 3
actStar = 4
actGoal = 5
actSuicide = 6
actBaricade = 7
actBecomeVulnerable = 8
actKill = 9
actGoalStretch = 3



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

    name = 'qLeaner'

    @staticmethod
    def play(state, dice_roll, next_states):

        def getActions(state, next_states):
            actionsArr = [goal, goal, goal, goal]
            for nextState in next_states:
                qState = getState(state)
                #print(qState)
                nextQState = getState(nextState)
                # if nextState:
                #    print("\nnext_state",nextState[:],"\nnextQState",nextQState)
                # else:
                #     print("\nnext_state",nextState,"\nnextQState",nextQState)
                    
                #print(nextQState)
                if nextQState:
                   for i in range(len(nextQState)): # nextState[0] is player 0
                    '''
                    Use the previous state, qState
                    '''
                    if qState[i] != nextQState:
                        if qState[i] == home:
                            if nextQState[i]:
                                actionsArr[i] = actOutHome
                            
                        elif qState[i] != goal:
                            if nextQState[i] == common:
                                actionsArr[i] = actCommon
                            if will_send_opponent_home(state,nextState):
                                actionsArr[i] = actKill
                            elif not token_vulnerability(nextState, i):
                                actionsArr[i] = actSafe
                            elif nextQState[i] % 13 == 1:
                                actionsArr[i] = actRiskySafe
                            elif star_jump(nextQState[i]):
                                actionsArr[i] = actStar
                            elif nextQState[i] == goal:
                                actionsArr[i] = actGoal
                            elif nextQState[i] == goalStretch:
                                actionsArr[i] = actGoalStretch
                            elif  will_send_self_home(state, nextState):
                                actionsArr[i] = actSuicide
                            elif nextQState[i] == baricade:
                                actionsArr[i] = actBaricade
                            elif nextQState[i] == vulnerable:
                                actionsArr[i] = actBecomeVulnerable
                            elif nextQState[i] == goalStretch:
                                actionsArr[i] = actGoalStretch
                                            
            return actionsArr

        def getState(state):
            stateArr = [-1,-1,-1,-1]
            if state:
                for i in range(len(state[0])):
                    position = state[0][i]
                    if position == -1:
                        stateArr[i] = home

                    if position > -1 and position < 52:
                        stateArr[i] = common

                    if position == 1:
                        stateArr[i] = safe

                    if token_barricade(state, i):
                        stateArr[i] = baricade
                    
                    if position % 13 == 1:
                        stateArr[i] = riskySafe

                    if position > 51:
                        stateArr[i] = goalStretch

                    if token_vulnerability(state, i) == 1 or token_vulnerability(state, i) == 2:
                        stateArr[i] = vulnerable
                    
                    if position == 99:
                        stateArr[i] = goal

                return stateArr
            return False

        def chooseAction(state, next_states):
            actionArr = getActions(state,next_states)
            qState = getState(state)
            highestReward = -inf
            highestIdx = -1
            '''
            The index here does not fit. make sure to move the correct token 
            '''
            for i in range(len(actionArr)):
                #print("len(actionArr)", actionArr, qState, qTable[qState[i]])
                if qTable[qState[i]][actionArr[i]] > highestReward: 
                    highestIdx = i
                    highestReward = qTable[qState[i]][actionArr[i]]
            return highestIdx
            
        move = chooseAction(state,next_states)
        # print("move\t", move)
        return move

