import json
import random

from player import Player


with open('tiles.json', 'r') as file:
    start_tiles = json.load(file) #Creates a dictionary containing an entire set of tiles

class Game:
    def __init__(self, logs: bool=False, prevWind: str="e") -> None:
        self.tilePool = start_tiles
        self.turn = 0
        self.dora = []
        self.prevWind = prevWind
        self.logs = logs
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

    def writeLogs(self, txt: str):
        with open("logs.txt", "a") as file:
            txt += "\n\n\n"
            file.write(txt)

    def main(self):
        logsOutput = ""
        while not self.over:
            self.turn+=1
            for player in self.players:
                if not self.over:
                    draw = self.drawTile()

                    if not draw:
                        self.over = True
                        break
                    

                    print(self.windDict[player.getSeat()] , "Player's turn, Turn: ", self.turn)
                    
                    logsOutput += f"{self.windDict[player.getSeat()]} , Player's turn, Turn: {self.turn}\n"
                    logsOutput += f"Drawn tile: {draw}, Current hand: {player.format_hand(player.getHand())['displayHand']}\n"

                    discard = player.discard(draw)


                    if not discard:
                        print(self.windDict[player.getSeat()], "Says: TSUMO!, on turn", self.turn)
                        hand = player.getHand()
                        handScore = player.format_hand(hand)
                        winningTile = hand[-1]
                        print(("t", winningTile, handScore))
                        print()

                        self.over=True
                        
                        tenpaiHand = player.getHand()[:]
                        tenpaiHand.remove(winningTile)
                        logsOutput += f"{self.windDict[player.getSeat()]} wins by Tsumo, with winning tile {winningTile}. Side wait: {player.checkForSideWait(tenpaiHand, winningTile)}\n"
                        logsOutput += f"Final hand: {player.format_hand(hand)['displayHand']}\n"
                        
                        break
                        
                    logsOutput += f"Discarded tile: {discard}. Post discard hand: {player.format_hand(player.getHand())['displayHand']}\n\n"

                    self.discardPiles[player.getSeat()].append(discard)
                    self.discardPiles["total"].append(discard)

                    for ronningPlayer in self.players:
                        handScore = ronningPlayer.ron()
                        if handScore != None:
                            print(self.windDict[ronningPlayer.getSeat()], "Says: RON! on Turn: ", self.turn)
                            winningTile = self.discardPiles["total"][-1]
                            print(("r", winningTile, handScore))
                            print()
                            self.over = True
                            
                            logsOutput += f"{self.windDict[ronningPlayer.getSeat()]} wins by Ron, with winning tile {winningTile}. Side wait: {ronningPlayer.checkForSideWait(ronningPlayer.getHand(), winningTile)}\n"
                            logsOutput += f"Final hand: {handScore['displayHand']}\n"
                            
                            break
        if self.logs:
            self.writeLogs(logsOutput)
        
        

            