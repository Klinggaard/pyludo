from pyludo import LudoGame
from pyludo.StandardLudoPlayers import LudoPlayerRandom, LudoPlayerFast, LudoPlayerAggressive, LudoPlayerDefensive, LudoPlayerQ, qTable
import random
import time
ans = input('Train the qLearn? y/n')
players = [
    LudoPlayerQ(),
    LudoPlayerRandom(),
    LudoPlayerAggressive(),
    LudoPlayerDefensive(),
]

scores = {}
for player in players:
    scores[player.name] = 0

n = 1000

start_time = time.time()
for i in range(n):
    random.shuffle(players)
    ludoGame = LudoGame(players)
    winner = ludoGame.play_full_game()
    scores[players[winner].name] += 1
    print('Game ', i, ' done')
duration = time.time() - start_time

if ans == 'y':
    print(qTable)

print('win distribution:', scores)
print('games per second:', n / duration)
