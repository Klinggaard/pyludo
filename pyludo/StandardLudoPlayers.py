import random
import numpy as np
from .utils import token_vulnerability, token_barricade, star_jump, will_send_self_home, will_send_opponent_home, is_globe_pos
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



qTable = np.array(  [[14.89616383287278,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,16.058586480950403,0.0],
[0.0,3.9005414028481455,10.354428449010069,0.0,6.035400785808294,20.82833509994991,-10.145801139457992,-10.145801139457992,-0.7945859715185462,9.527062502561762,10.083606039583591],
[0.0,3.6035400785808296,0.0,0.0,8.961638328727796,20.86004100398958,-28.519197055853553,-8.565538221833082,-0.9599214191706098,10.048344791488601,9.014853616383288],
[0.0,3.590038998785329,0.0,0.0,8.36060395835895,0.0,-8.481671410010996,10.858936473590102,6.060395835895095,9.906548945035833,0.0],
[0.0,0.0,0.0,0.0,0.0,19.838330148154895,0.0,0.0,0.0,0.0,9.98383301481549],
[0.0,10.544544284490101,10.900340848716107,0.0,8.452706250256176,21.508099093910147,-8.541641049051059,-8.541641049051059,-1.6145992141917063,10.544544284490101,8.949906548945036],
[15.080990939101454,2.908610781943924,10.853350494540354,0.0,5.360410288357844,20.90040542008665,-8.959098494896393,-8.959098494896393,-1.646395897116422,15.390159910647336,9.011015083785354],
[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]])


#qTable = np.zeros([8,11])

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

    name = 'qLearner'

    def __init__(self, train):
        self.train = train
    
    #@staticmethod
    def play(self,state, dice_roll, next_states):
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
                reward -= 20

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

                    if is_globe_pos(position):
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
        #print(self.train)
        if self.train:
            getReward(actions[move],q_state[move])
        return move

