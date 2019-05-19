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



# qTable = np.array(     [[19,    0,  0,  0,  0,  0,  0,  0,  0,  0, 0],                         # home
#                         [0, 1,  2,  3,  4,  10, -99,7,  8,  9,  7.5],                  # common
#                         [0, 1,  2,  3,  4,  10, -99,3,  -10,12,  7.5],                # safe
#                         [0, 1,  2,  1,  4,  10, -99,7,  2,  11,  7.5],                  # riskySafe
#                         [0, 0.1,-1, 0.1,0.1,10, -99,0.1,0.1,0.1,7.5],     # goalStretch
#                         [0, 1,  2,  3,  4,  10, -99,6,  8,  5,7.5],                # vulnerable
#                         [0, 1,  2,  3,  4,  10, -99,6,  -1, 6,  7.5],                 # baricade
#                         [0, 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]])                       # goal

qTable = np.zeros([8,11])

inf = 9999999999999

preState = -1
preAct = [-1]

alpha = 0.2
gamma = 0.5

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
actGoalStretch = 10



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
    """" Learns to play the game via Q-learning """

    name = 'qLeaner'


    @staticmethod
    def play(state, dice_roll, next_states):

        def getReward(action, currentState):
            reward = 0.0
            global preAct
            global preState

            if actOutHome in preAct:
                reward += 70

            if actCommon in preAct:
                reward += 15

            if actSafe in preAct:
                reward += 50

            if actRiskySafe  in preAct:
                reward += 20

            if actStar in preAct:
                reward += 60
            
            if actGoal in preAct:
                reward += 100

            if actSuicide in preAct:
                reward += -150

            if actBaricade in preAct:
                reward += 50
            
            if actBecomeVulnerable in preAct:
                reward += -10
            
            if actKill in preAct:
                reward += 80
            
            if actGoalStretch in preAct:
                reward += 40



            # Update qTable
            if reward and len(preAct):
                reward = reward/len(preAct)
                for i in preAct:
                    for j in action:
                        qTable[preState][i] += alpha * (reward + gamma * qTable[currentState][j]) - qTable[preState][i]

            
            preState = currentState
            preAct = action


        def getActions(state, next_states):
            actionsArr = [[], [], [], []]
            #print("\n\nchoosing action")
            for i in range(len(next_states)):

                #print(next_states[i])
                if type(next_states[i]) != bool:

                    #print("i",next_states[i][0][i],next_states[i][0][i] // 13)
                    nextQState = getState(next_states[i])
                    if nextQState[i] == common:
                        actionsArr[i].append(actCommon)
                    
                    if will_send_opponent_home(state, next_states[i]):
                        actionsArr[i].append(actKill)

                    if will_send_self_home(state, next_states[i]):
                        actionsArr[i].append(actSuicide)

                    if nextQState[i] == baricade:
                        actionsArr[i].append(actBaricade)

                    if nextQState[i] == vulnerable:
                        actionsArr[i].append(actBecomeVulnerable)

                    if next_states[i][0][i] == 1:    # Token moved out of home
                        actionsArr[i].append(actOutHome)

                    if nextQState[i] == safe:
                        actionsArr[i].append(actSafe)

                    if star_jump(next_states[i][0][i]):
                        actionsArr[i].append(actStar)

                    if nextQState == common:
                        if next_states[i][0][i] % 13 == 1 and np.sum(state[next_states[i][0][i] // 13] == -1) != 0: # token standing infront of not empty enemy home
                            actionsArr[i].append(actRiskySafe)

                    if nextQState[i] == goal:
                        actionsArr[i].append(actGoal)

                    if nextQState[i] == goalStretch:
                        actionsArr[i].append(actGoalStretch)
                else:
                    actionsArr[i] = [None]
                                          
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
            #print("-qState",qState,"\nactionArr",actionArr)
            for i in range(len(actionArr)):
                #print("len(actionArr)", actionArr)
                if actionArr[i] != [None]:    
                    jReward = 0
                    #print(actionArr[i])
                    for j in range(len(actionArr[i])):  # Summing the score of all actions in move
                        jReward += qTable[qState[i]][actionArr[i][j]]

                    if jReward > highestReward: 
                        highestIdx = i
                        highestReward = jReward

            return highestIdx, actionArr
        
        q_state = getState(state)
        move, actions = chooseAction(state,next_states)
        
        # training
        getReward(actions[move],q_state[move])
        return move

