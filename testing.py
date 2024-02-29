import json
import random

from player import Player
from game import Game

testGame = Game()
testHand = ["2_circ", "3_circ", "4_circ", "6_circ", "6_circ", "6_circ", "5_bamb", "5_bamb", "7_bamb", "8_bamb", "w_drag", "w_drag",	"w_drag"]
player = Player(testHand, "e", testGame)

print(player.checkForSideWait(player._hand, "6_bamb"))