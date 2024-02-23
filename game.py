import json
import random

from player import Player


with open('tiles.json', 'r') as file:
    start_tiles = json.load(file) #Creates a dictionary containing an entire set of tiles

class Game:
    def __init__(self, prevWind = "e") -> None:
        self.tilePool = start_tiles
        self.turn = 0
        self.dora = []
        self.prevWind = prevWind
        self.windDict = {
                        "e": "East",
                        "s": "South",
                        "w": "West",
                        "n" : "North"
                    }
        self.seats = ["e", "s", "w", "n"]
        self.discardPiles = {"e": [], "s": [], "w": [], "n" : [], "total" : []}
        self.over=False
        self.deadWall = [[self.drawTile() for i in range(7)] for j in range(2)]

        self.chooseDora()
        self.players = [Player(self.drawHand(), self.chooseSeat(), self) for i in range(4)]

    def chooseDora(self):
        l = len(self.dora)
        self.dora.append(self.deadWall[0][2+l])

    def drawHand(self):
        self.tempHandArray = []
        for i in range(13):
            self.tempHandArray.append(self.drawTile())

        return self.tempHandArray
    
    def drawTile(self):
        keys, weights = zip(*self.tilePool.items())

        if any(weights):
            self.tempRandomElement = random.choices(keys, weights=weights)[0]
            self.tilePool[self.tempRandomElement] -= 1
            return self.tempRandomElement
        
        else:
            return None

    def chooseSeat(self):
        seat = self.seats.pop(0)
        return seat

    def main(self):
        while not self.over:
            self.turn+=1
            for player in self.players:
                if not self.over:
                    draw = self.drawTile()

                    if not draw:
                        self.over = True
                        break
                    

                    print(self.windDict[player.getSeat()] , "Player's turn, Turn: ", self.turn)
                    discard = player.discard(draw)
                    if not discard:
                        print(self.windDict[player.getSeat()], "Says: TSUMO!, on turn", self.turn)
                        self.over=True
                        break

                    self.discardPiles[player.getSeat()].append(discard)
                    self.discardPiles["total"].append(discard)

                    for ronningPlayer in self.players:
                        if ronningPlayer.ron():
                            print(self.windDict[ronningPlayer.getSeat()], "Says: RON! on Turn: ", self.turn)
                            self.over = True
                            break
        
        

            