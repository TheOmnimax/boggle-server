import random
from typing import List

class Dice:
  def __init__(self, sides: list):
    self.sides = sides
    self.num_sides = len(sides)
  
  def roll(self):
    side_num = random.randrange(0, self.num_sides)
    return self.sides[side_num]
  

class DiceBag:
  def __init__(self, dice: list[Dice] = []):
    self.dice = dice
  
  def addDice(self, dice: Dice):
    self.dice.append(dice)

  def shuffle(self):
    random.shuffle(self.dice)
  
  def rollDice(self) -> List:
    """Roll the dice, and return a list of the results.

    Returns:
        List: List of results. Usually str, but could be int. For Boggle, it is always str.
    """
    return [r[random.randrange(0, len(r))] for r in self.dice]
