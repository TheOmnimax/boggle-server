import random

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
  
  def rollDice(self):
    return [r[random.randrange(0, len(r))] for r in self.dice]
