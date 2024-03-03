
from collections import Counter
import json
import random
from typing import List

class Player:
    def __init__(self, hand: list, seat: str, game) -> None:
        self._hand = hand #Would be ideal to ensure the list is sorted, either we can implement it into the constructor at this stage or we can check it at the input stage idk which is better
        self._seat = seat
        self._game = game
        self._dealer = True if seat == "e" else False
    
    def getSeat(self):
        return self._seat
    
    def ron(self):
        latestTile = self._game.discardPiles["total"][-1] #tile in json format ie: 3_char
        self._hand.append(latestTile)
        handScore = self.format_and_score_hand(self._hand)
        self._hand.pop(-1)

        if handScore["shanten"] == -1:
            return handScore
        else:
            return None

    def getHand(self):
        return self._hand
    
    def webFormat(self, handArray):
        dict = {0: 'm',
            1: 's',
            2: 'p',
            3: 'z'
        }

        string = ''
        k=0
        for suit in handArray:
            if sum(suit) == 0:
                k+=1
                continue
            for num in range(len(suit)):
                if suit[num] == 0:
                    continue
                else:
                    string += str(num+1)*suit[num]

            string += dict[k]
            k+=1

        return string

    def discard(self, drawnTile: str): #Eventually will be filled with a method to select a discard, then return new hand and the discard tile

        print()
        print("Current Hand")
        print(self.format_and_score_hand(self._hand))
        print()

        self._hand.append(drawnTile) #append 14th tile to hand

        formatHand = self.format_and_score_hand(self._hand)

        print("Draw Tile: ", drawnTile)
        print(formatHand["displayHand"], formatHand["shanten"])
        print()

        if formatHand["shanten"] == -1:
            return None

        discardPossibilities = []
        for i in range(len(self._hand)): 

            tempHand = self._hand[:i] + self._hand[i+1:]

            tempScore = self.format_and_score_hand(tempHand)
            discardPossibilities.append((self._hand[i] , tempScore))  
        
        discardPossibilities.sort(key=lambda x: (x[1]["shanten"], -x[1]["tileEff"][0]))
        
        # Commented out the discard analysis
        # for item in discardPossibilities:
        #     print(item)
        #     print()

        discardTile = discardPossibilities[0][0]

        self._hand.remove(discardTile)
        
        print("Post discard: ", discardTile)
        print(self.format_and_score_hand(self._hand))
        print()

        return (discardTile)

    def getShanten(self,hand):
        shanten = self.calcShanten(self.format_hand(hand)["calcHand"])
        return shanten
        

    def format_hand(self, hand):

        handDict = {
            "char": [],   # Hopefully this will be useful for calculating shanten and similar operations
            "bamb": [],
            "circ": [],
            "e_wind": 0,
            "s_wind": 0,
            "w_wind": 0,
            "n_wind": 0,
            "w_drag": 0,
            "g_drag": 0,
            "r_drag": 0,
        }

        handArray = [[0 for x in range(9)], [0 for x in range(9)], [0 for x in range(9)], [0 for x in range(7)]]
        
        suitsDict = {
                            "char" : 0,
                            "bamb" : 1,
                            "circ" : 2,
                        }

        honorsDict = {
            "e_wind": 0,
            "s_wind": 1,
            "w_wind": 2,
            "n_wind": 3,
            "w_drag": 4,
            "g_drag": 5,
            "r_drag": 6,
        }
        
        for i in hand:
            for item in handDict:
                if item in i:
                    if item in ["char", "circ", "bamb"]:

                        
                                
                        handDict[item].append((i.split("_")[0]))
                        handDict[item].sort()

                        handArray[suitsDict[item]][int(i[0]) - 1] += 1

                    else:
                        handDict[item] +=1
                        
                        handArray[3][honorsDict[item]] +=1
        
        formattedHand = {
            "hand" : hand,
            "displayHand" : handDict,
            "calcHand" : handArray, #Note the arrays are in the following order: [Characters, Bamboos, Circles, Honours]
            "webFormat" : self.webFormat(handArray),
        }

        return formattedHand


    def format_and_score_hand(self, hand) : #The intent is to separate the raw hand into sublists with integer values for each suit and an integer count of the honour tiles
        
        formattedHand = self.format_hand(hand)

        handScore = {
            "hand" : hand,
            "displayHand" : formattedHand["displayHand"],
            "webFormat" : formattedHand["webFormat"],
            "shanten" : self.calcShanten(formattedHand["calcHand"]),
            "tileEff" : self.calcTileEff(hand, self._game.discardPiles["total"]),
            "discardPile" : dict(Counter(self._game.discardPiles["total"])),
            "dora": self._game.dora
        }

        return handScore

    def calcShanten(self, handArray: list):

        def pairs(suit_arr):
            possible_pairs=[]

            for i in range(9):
                if suit_arr[i]>1:
                    out = [0]*9
                    out[i] = 2
                    possible_pairs.append(out)
            return possible_pairs
        
        def triplets(suit_arr):
            possible_triplets=[]

            for i in range(9):
                if suit_arr[i]>2:
                    out = [0]*9
                    out[i] = 3
                    possible_triplets.append(out)
            return possible_triplets
        
        def complete_sequences(suit_arr):
            possible_sequences=[]
            for i in range(2,9):
                if suit_arr[i]>0 and suit_arr[i-1]>0 and suit_arr[i-2]>0:
                    out = [0]*9
                    out[i]=1
                    out[i-1]=1
                    out[i-2]=1
                    possible_sequences.append(out)
            return possible_sequences
        
        def incomplete_sequences(suit_arr):
            possible_insequences=[]
            if suit_arr[0]>0 and suit_arr[1]>0:
                out = [0]*9
                out[0]=1
                out[1]=1
                possible_insequences.append(out)
            for i in range(2,9):
                if suit_arr[i]>0 and suit_arr[i-1]>0:
                    out = [0]*9
                    out[i]=1
                    out[i-1]=1
                    possible_insequences.append(out)
                if suit_arr[i]>0 and suit_arr[i-2]>0:
                    out = [0]*9
                    out[i]=1
                    out[i-2]=1
                    possible_insequences.append(out)
            return possible_insequences
        
        def resulting_hand(arr1,arr2):
            out=[0]*9
            for i in range(9):
                out[i] = arr1[i] - arr2[i]
            return out
        

        def splits_nogroups(hand):
            set_insequences = incomplete_sequences(hand)
            current_shan=0
            set_pairs = pairs(hand)
            pair_bool = False

            for i in set_pairs:
                current = splits_nogroups(resulting_hand(hand, i))[0]+1
                if current>current_shan:
                    current_shan = current
                    pair_bool = True

            for i in set_insequences:
                current = splits_nogroups(resulting_hand(hand, i))[0]+1
                if current > current_shan:
                    current_shan = current
                    pair_bool = splits_nogroups(resulting_hand(hand, i))[1]

            return current_shan, pair_bool


        def splits(g, hand):                  #******
            current_g_n = g                   #number of groups
            current_i_n = 0                   #number of taatsu
            pair_presance = False             #used for an edge case(s?)                            
            set_seq = complete_sequences(hand)
            set_triplets = triplets(hand)

            for j in set_seq:
                current_split = splits(g+1, resulting_hand(hand,j))   
                current = current_split[0]
                if current>current_g_n:
                    current_g_n = current
                    current_i_n = current_split[1]
                    pair_presance = current_split[2]   #*
                elif current == current_g_n:
                    if current_split[1] > current_i_n:
                        current_i_n = current_split[1]
                        pair_presance = current_split[2]   #*

            for j in set_triplets:
                current_split = splits(g+1, resulting_hand(hand,j))
                current = current_split[0]
                if current>current_g_n:
                    current_g_n = current
                    current_i_n = current_split[1]
                    pair_presance = current_split[2]   #*
                elif current == current_g_n:
                    if current_split[1] > current_i_n:
                        current_i_n = current_split[1]
                        pair_presance = current_split[2]   #*
                        
            if (not set_seq) and (not set_triplets):     #if no more groups then counts maximum of taatsu    
                s=splits_nogroups(hand)
                return g, s[0], s[1]

            return current_g_n,current_i_n,pair_presance
        

        def splits_fullhand(hand):
            current_split = [0,0,False]
            for i in hand[:3]:
                current_arr = splits(0, i)
                current_split[0] += current_arr[0]
                current_split[1] += current_arr[1]
                if current_arr[2] == True:
                    current_split[2] = True

            for i in hand[3]:
                if i == 3:
                    current_split[0] += 1
                elif i == 2:
                    current_split[1] +=1
                    current_split[2] = True
            return current_split


        def general_shanten(handArray):
            split_arr = splits_fullhand(handArray)
            i = split_arr[1]
            g = split_arr[0]
            pair_presence = split_arr[2]
            p=0

            #checking for the edge cases:
            if i >= 5-g and pair_presence == False:
                p=1
            return 8 - 2*g - min(i, 4-g) - min(1, max(0,i+g-4)) + p

        
        def chiitoistu_shanten(handArray):
            pairs = 0
            for suit in handArray:
                for num in suit:
                    pairs += num//2      #counts number of pairs, 4 of the same tile are treated as 2 pairs
            return 6 - pairs
        
        def orphanSource_shanten(handArray):
            diffTerminals = 0
            pairsTerminals = 0
            pair_const = 0
            for i in (0,8):                  #iterates over numbered suits
                for suit in handArray[:3]:
                    pairsTerminals += min(1, suit[i]//2)
                    diffTerminals += min(1, suit[i]//1)


            for num in handArray[3]:        #iterates over honours
                    pairsTerminals += min(1, num//2)
                    diffTerminals += min(1, num//1)
            if pairsTerminals > 0:
                pair_const=1
            return 13 - diffTerminals - pair_const

       
        return min(general_shanten(handArray), chiitoistu_shanten(handArray), orphanSource_shanten(handArray))
    
    
    def calcTileEff(self, hand, discardPile):
        count = 0
        kinds = 0
        tilesInHand = 0
        tilesInDiscard = 0
        tilesInDora = 0

        initial_shanten = self.getShanten(hand)

        if initial_shanten == -1:
            return (0, 0)
        
        with open('tiles_unique.json', 'r') as file:
            start_tiles = json.load(file)

        for tile in start_tiles:
            handCopy = list(hand)
            discardPileCopy = list(discardPile)
            
            discardTile, sh2 = self.simulateDiscard(handCopy, tile)

            if sh2 < initial_shanten:
                
                tileInHand = self.countInList(hand, tile)
                tileInDiscard = self.countInList(self._game.discardPiles["total"], tile)
                tileInDora = self.countInList(self._game.dora, tile)
                count+= max((4 - tileInDora -  tilesInDiscard - tileInHand ), 0)
                kinds+=1
                tilesInHand += tileInHand
                tileInDiscard += tileInDiscard
                tilesInDora += tileInDora



        return count, kinds, tilesInHand, tilesInDiscard, tilesInDora
    
    def countInList(self, lis, elem):
        count = 0 
        dic = Counter(lis)
        if elem in dic:
            count = dic[elem]
        return count

    def simulateDiscard(self, hand, drawnTile: str): #Eventually will be filled with a method to select a discard, then return new hand and the discard tile

        # print()
        # print("Current Hand")
        # print(self.format_and_score_hand(hand))
        # print()

        hand.append(drawnTile) #append 14th tile to hand

        drawnShanten = self.getShanten(hand)

        # print("Draw Tile: ", drawnTile)
        # print(formatHand)
        # print()

        if drawnShanten == -1:
            return (None, -1)

        discardPossibilities = []
        for i in range(len(hand)): 

            if hand[i] == drawnTile: continue

            tempHand = hand[:i] + hand[i+1:]

            tempScore = self.getShanten(tempHand)
            discardPossibilities.append((hand[i] , tempScore))  
        
        discardPossibilities.sort(key=lambda x: (x[1]))
        
        # Commented out the discard analysis
        # for item in discardPossibilities:
        #     print(item)
        #     print()

        discardTile = discardPossibilities[0][0]
        shanten  = discardPossibilities[0][1]
        hand.remove(discardTile)
        

        return (discardTile, shanten)

    def checkForSideWait(self, tenpaiHandStrArray: List[str], winTile: str):

        #Duplicate code below

        def splits_nogroups(hand):
            set_insequences = incomplete_sequences(hand)
            current_shan=0
            set_pairs = pairs(hand)
            pair_bool = False

            for i in set_pairs:
                current = splits_nogroups(resulting_hand(hand, i))[0]+1
                if current>current_shan:
                    current_shan = current
                    pair_bool = True

            for i in set_insequences:
                current = splits_nogroups(resulting_hand(hand, i))[0]+1
                if current > current_shan:
                    current_shan = current
                    pair_bool = splits_nogroups(resulting_hand(hand, i))[1]

            return current_shan, pair_bool

        def splits(g, hand):                  #******
            current_g_n = g                   #number of groups
            current_i_n = 0                   #number of taatsu
            pair_presance = False             #used for an edge case(s?)                            
            set_seq = complete_sequences(hand)
            set_triplets = triplets(hand)

            for j in set_seq:
                current_split = splits(g+1, resulting_hand(hand,j))   
                current = current_split[0]
                if current>current_g_n:
                    current_g_n = current
                    current_i_n = current_split[1]
                    pair_presance = current_split[2]   #*
                elif current == current_g_n:
                    if current_split[1] > current_i_n:
                        current_i_n = current_split[1]
                        pair_presance = current_split[2]   #*

            for j in set_triplets:
                current_split = splits(g+1, resulting_hand(hand,j))
                current = current_split[0]
                if current>current_g_n:
                    current_g_n = current
                    current_i_n = current_split[1]
                    pair_presance = current_split[2]   #*
                elif current == current_g_n:
                    if current_split[1] > current_i_n:
                        current_i_n = current_split[1]
                        pair_presance = current_split[2]   #*
                        
            if (not set_seq) and (not set_triplets):     #if no more groups then counts maximum of taatsu    
                s=splits_nogroups(hand)
                return g, s[0], s[1]

            return current_g_n,current_i_n,pair_presance

        def pairs(suit_arr):
            possible_pairs=[]

            for i in range(9):
                if suit_arr[i]>1:
                    out = [0]*9
                    out[i] = 2
                    possible_pairs.append(out)
            return possible_pairs
        
        def triplets(suit_arr):
            possible_triplets=[]

            for i in range(9):
                if suit_arr[i]>2:
                    out = [0]*9
                    out[i] = 3
                    possible_triplets.append(out)
            return possible_triplets
        
        def complete_sequences(suit_arr):
            possible_sequences=[]
            for i in range(2,9):
                if suit_arr[i]>0 and suit_arr[i-1]>0 and suit_arr[i-2]>0:
                    out = [0]*9
                    out[i]=1
                    out[i-1]=1
                    out[i-2]=1
                    possible_sequences.append(out)
            return possible_sequences
        
        def incomplete_sequences(suit_arr):
            possible_insequences=[]
            if suit_arr[0]>0 and suit_arr[1]>0:
                out = [0]*9
                out[0]=1
                out[1]=1
                possible_insequences.append(out)
            for i in range(2,9):
                if suit_arr[i]>0 and suit_arr[i-1]>0:
                    out = [0]*9
                    out[i]=1
                    out[i-1]=1
                    possible_insequences.append(out)
                if suit_arr[i]>0 and suit_arr[i-2]>0:
                    out = [0]*9
                    out[i]=1
                    out[i-2]=1
                    possible_insequences.append(out)
            return possible_insequences
        
        def resulting_hand(arr1,arr2):
            out=[0]*9
            for i in range(9):
                out[i] = arr1[i] - arr2[i]
            return out
        
        #Non-duplicate code begins below

        def calcHand_addition(arr1,arr2): #Slight variation on resulting_hand function to add instead of subtract
            out=[0]*9
            for i in range(9):
                out[i] = arr1[i] + arr2[i]
            return out

        winTileRawNum = int(winTile[0]) #Converts the winning tile to an integer
        winTileArrPosition = winTileRawNum - 1
        winTileSuit = -1
        if "char" in winTile: #Gets array position of the suit containing winning tile
            winTileSuit = 0
        elif "bamb" in winTile:
            winTileSuit = 1
        elif "circ" in winTile:
            winTileSuit = 2
        else:
            return(False)
        
        winTileCalcHand = self.format_hand([winTile])["calcHand"] #Get data in required format
        tenpaiCalcHand = self.format_hand(tenpaiHandStrArray)["calcHand"]
        combinedWinSuitArray = calcHand_addition(tenpaiCalcHand[winTileSuit], winTileCalcHand[winTileSuit]) #The hand including the winning tile
        
        def checkAbove(_combinedWinSuitArray: List[int], _winTileArrPosition: int): #Checks for a valid protorun above the winning tile
            maxSplits = splits(0, _combinedWinSuitArray)
            if _combinedWinSuitArray[_winTileArrPosition + 1] > 0 and _combinedWinSuitArray[_winTileArrPosition + 2] > 0: #Checks tiles for a protorun exist
                copyArray = _combinedWinSuitArray[:]
                for i in range(3): #Subtract the run, including the winning tile and protorun, from the suit
                    copyArray[_winTileArrPosition + i] = copyArray[_winTileArrPosition + i] - 1
                newSplits = splits(0, copyArray)
                if maxSplits[0] - newSplits[0] == 1 and maxSplits[2] == newSplits[2]: #Check that there is only one less group when removing the run from the final hand, and that pair presence stays unchanged
                    return(True)
                else:
                    return(False)
        
        def checkBelow(_combinedWinSuitArray: List[int], _winTileArrPosition: int): #Same as checkAbove, but checks below
            maxSplits = splits(0, _combinedWinSuitArray)
            if _combinedWinSuitArray[_winTileArrPosition - 1] > 0 and _combinedWinSuitArray[_winTileArrPosition - 2] > 0:
                copyArray = _combinedWinSuitArray[:]
                for i in range(3):
                    copyArray[_winTileArrPosition - i] = copyArray[_winTileArrPosition - i] - 1
                newSplits = splits(0, copyArray)
                if maxSplits[0] - newSplits[0] == 1 and maxSplits[2] == newSplits[2]:
                    return(True)
                else:
                    return(False)
            else:
                return(False)

        if winTileRawNum <= 3:
            return(checkAbove(combinedWinSuitArray, winTileArrPosition))
        elif winTileRawNum >= 7: 
            return(checkBelow(combinedWinSuitArray, winTileArrPosition))
        else:
            return(checkAbove(combinedWinSuitArray, winTileArrPosition) or checkBelow(combinedWinSuitArray, winTileArrPosition))