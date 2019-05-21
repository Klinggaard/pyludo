from pyludo import LudoGame
from pyludo.StandardLudoPlayers import LudoPlayerRandom, LudoPlayerFast, LudoPlayerAggressive, LudoPlayerDefensive, LudoPlayerQ, qTable
import random
import time
import numpy as np
import csv
import progressbar

players = [
    LudoPlayerQ(False),
    LudoPlayerRandom(),
    LudoPlayerAggressive(),
    LudoPlayerDefensive(),
]

scores = {}
for player in players:
    scores[player.name] = 0

    
n = 1
trainIterations = 50
testIterations = 400 

print(qTable)

preTotal = 0

winRates = [[],[],[],[]]
highWR = 0
highN = 0
highWRTable = np.copy(qTable)

for i in range(len(players)):
    winRates[i].append(players[i].name)

bar = progressbar.ProgressBar(maxval=n, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()

start_time = time.time()
for j in range(n):

    # # training
    # for player in players:
    #     if player.name == "qLearner":
    #         player.train = True
    # for i in range(trainIterations):
    #     random.shuffle(players)
    #     ludoGame = LudoGame(players)
    #     winner = ludoGame.play_full_game()
    #     #scores[players[winner].name] += 1
    # #print('Game ', i, ' done')
   

    # Collecting data
    for player in players:
        if player.name == "qLearner":
            player.train = False
    for i in range(testIterations):
        random.shuffle(players)
        ludoGame = LudoGame(players)
        winner = ludoGame.play_full_game()
        scores[players[winner].name] += 1
       
    for player in players:
        if player.name == "qLearner":
            winRates[0].append(scores[player.name])

            if (scores[player.name]-preTotal) / 400 > highWR / 400:
                highN = n
                highWR = scores[player.name] - preTotal
                highWRTable = np.copy(qTable)
            preTotal = scores[player.name]
        elif player.name == "random":
            winRates[1].append(scores[player.name])
        elif player.name == "defensive":
            winRates[2].append(scores[player.name])
        elif player.name == "aggressive":
            winRates[3].append(scores[player.name])

    bar.update(j+1)


duration = time.time() - start_time

print('win distribution:', scores)
print('games per second:', n / duration)


with open('winrates.csv', 'w') as winrateFile:
    writer = csv.writer(winrateFile)
    writer.writerows(winRates)

with open('bestQTable.csv', 'w') as bQTFile:
    writer = csv.writer(bQTFile)
    writer.writerows(highWRTable)

with open('finalQTable.csv', 'w') as fQTFile:
    writer = csv.writer(fQTFile)
    writer.writerows(qTable)

generalData = [["duration","iterations","best win rate","best win rate at n"],[duration,n,highWR,highN]]

with open('genData.csv', 'w') as genDataFile:
    writer = csv.writer(genDataFile)
    writer.writerows(generalData)
