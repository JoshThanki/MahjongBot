import json
import random
from typing import List

total_tiles = {}
with open('tiles.json', 'r') as file:
    data = json.load(file)

    
class Game:
    def __init__(self) -> None:
        with open('tiles.json', 'r') as file:
            self.tilePool = json.load(file)  # Load the tile pool from a JSON file

    def chooseDora(self):
        keys, weights = zip(*self.tilePool.items())
        tempRandomElement = random.choices(keys, weights=weights)[0]
        self.tilePool[tempRandomElement] -= 1
        return tempRandomElement

    def drawHand(self):
        tempHandArray = []
        for _ in range(13):
            keys, weights = zip(*self.tilePool.items())
            tempRandomElement = random.choices(keys, weights=weights)[0]
            self.tilePool[tempRandomElement] -= 1
            tempHandArray.append(tempRandomElement)
        return tempHandArray

class Player:

    def __init__(self, hand: list) -> None:
        """
        Initializes a Player object with the given hand.

        Parameters:
            hand (list): The initial hand of the player.
        """
        self._hand = hand
        self.total_tiles = total_tiles  # Assign the total_tiles attribute
        self.sort_hand()

    def sort_hand(self) -> None:
        """
        Sorts the player's hand.
        """
        self._hand.sort()

    def discard(self, drawnTile: str) -> None:
        """
        Discards a tile from the player's hand.

        Parameters:
            drawnTile (str): The tile to be discarded.
        """
        # Append the drawn tile to the hand
        self._hand.append(drawnTile)

        # Initialize list to store discard possibilities
        discardPossibilities = []

        # Generate all possible discard possibilities and their scores
        for i, tile in enumerate(self._hand):
            # Simulate removing the current tile from the hand
            tempHand = self._hand[:i] + self._hand[i+1:]
            # Calculate the score difference between the current hand and the hand after discarding the tile
            tempScore = self.format_hand(tempHand)
            if "discarded_tiles" in tempScore:
                score_difference = tempScore["discarded_tiles"] - self.format_hand(self._hand)["discarded_tiles"]
            else:
                score_difference = 0
            # Get the shanten value of the hand or set default to 0 if missing
            shanten = tempScore.get("shanten", 0)
            # Append the tile and its score difference to the discard possibilities list
            discardPossibilities.append((tile, (score_difference, shanten)))

        # Sort discard possibilities based on score difference and shanten value
        discardPossibilities.sort(key=lambda x: (x[1][0], -x[1][1] if x[1][1] is not None else 0))

        # Remove the tile with the lowest score (first element after sorting)
        self._hand.remove(discardPossibilities[0][0])

    def format_hand(self, hand) -> dict:
        """
        Formats the player's hand into a structured dictionary.

        Parameters:
            hand (list): The player's hand.

        Returns:
            dict: A dictionary containing the formatted hand information.
            """
        # Initialize dictionaries and arrays to store hand information
        handDict = {
            "char": [],
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
        handArray = [[0 for _ in range(9)] for _ in range(4)]

        # Iterate through the hand and update dictionaries and arrays
        for item in handDict:
            for i in hand:
                if item in i:
                    if item in ["char", "circ", "bamb"]:
                        suitsDict = {"char": 0, "bamb": 1, "circ": 2}
                        suit = i.split("_")[0]
                        value = int(i[1:]) - 1
                        handDict[item].append((suit, value))
                        handDict[item].sort()
                        handArray[suitsDict[suit]][value] += 1
                    else:
                        handDict[item] += 1

        # Count discarded tiles and update hand representation
        discarded_tiles = len(self._hand) - len(hand)
        handDict["discarded_tiles"] = discarded_tiles

        # Calculate hand score and return formatted hand information
        handScore = {
            "displayHand": handDict,
            "calcHand": handArray,
            "shanten": self.calcShanten(handArray),
            "tileEff": self.calcTileEff(handDict)
        }
        return handScore

    def calcShanten(self, hand) -> int:
        """
        Calculates the shanten value of the player's hand.

        Parameters:
            hand (list): The formatted hand information.

        Returns:
            int: The shanten value.
        """
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
        
        def shanten_nogroups(hand):
            set_insequences = incomplete_sequences(hand)
            current_shan=0
            set_pairs = pairs(hand)

            for i in set_insequences:
                current = shanten_nogroups(resulting_hand(hand, i))
                if current > current_shan:
                    current_shan = current

            for i in set_pairs:
                current = shanten_nogroups(resulting_hand(hand, i))+1

                if current>current_shan:
                    current_shan = current
            return current_shan
        
        def shanten(hand):
            current_shanten=0
            set_pairs = pairs(hand)
            set_seq = complete_sequences(hand)
            set_triplets = triplets(hand)

            if len(set_seq) == 0  and len(set_triplets) == 0:
                current_shanten += shanten_nogroups(hand)

            for j in set_seq:
                current = shanten(resulting_hand(hand, j))+2
                if current>current_shanten:
                    current_shanten = current

            for j in set_triplets:
                current = shanten(resulting_hand(hand, j))+2
                if current>current_shanten:
                    current_shanten = current
            return current_shanten
        def shanten_honours(hand):
            current_shanten=0
            for i in hand:
                if i > 2:
                    current_shanten += 2
                if i == 2:
                    current_shanten += 1
            return current_shanten
        return 8 -(shanten(hand[0]) + shanten(hand[1]) + shanten(hand[2]) + shanten_honours(hand[3]))

    def calcTileEff(self, handDict) -> int:
        """
        Calculates the tile efficiency of the player's hand.

        Parameters:
            handDict (dict): The formatted hand information.

        Returns:
            int: The tile efficiency value.
        """
        return random.randint(1, 30)
    
    def draw_tile(self):
        """
        Simulates drawing a tile from the player's hand.

        Returns:
            str or None: The drawn tile if there are tiles remaining in the hand,
                        None if the hand is empty.
        """
        if self._hand:
            # Draw a random tile from the deck
            drawn_tile = random.choice(self._hand)
            # Remove the drawn tile from the deck
            self._hand.remove(drawn_tile)
            # Return the drawn tile
            return drawn_tile
        else:
            # If the deck is empty, return None
            return None
        
    def discard_tile(self):
        """
        Simulates discarding a tile from the player's hand.

        Returns:
            str or None: The discarded tile if there are tiles remaining in the hand,
                        None if the hand is empty.
        """
        if self._hand:
            # For now, let's discard the last tile in the hand
            discarded_tile = self._hand.pop()
            return discarded_tile
        else:
            return None

# Example usage
player = Player(["2_char", "3_char", "5aka_char", "2_circ", "3_circ", "6_circ", "6_circ", "6_bamb", "7_bamb", "7_bamb", "w_drag", "w_drag", "w_drag"])
player.discard("1_char")

    
# The dictionary definition resulted in a syntax error because there was no closing brace. Fixed it. 
# Added a missing key-value separator ":" in the dictionary definition
seq = {
    "1,2,3": ""
}

# Added a missing key-value separator ":" in the dictionary definition
trip = {
    "1,1,1": ""
}

player = Player(["2_char", "3_char",	"5aka_char",	"2_circ",	"3_circ",	"6_circ",	"6_circ",	"6_bamb",	"7_bamb",	"7_bamb",	"w_drag",	"w_drag",	"w_drag"])
player.discard("1_char")

# Example usage:
testGame = Game()
player_hand = testGame.drawHand()
player = Player(player_hand)
player.discard("1_char")
print(testGame.chooseDora())
