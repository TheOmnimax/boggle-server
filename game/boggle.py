from .board import BoardSpace, Board
from .dice import DiceBag
from .player import Player
from .room import Game, GameRoom
from collections import OrderedDict
from enum import Enum
from tools.randomization import genCode

import logging

class BoggleBag(DiceBag):
  boggle_dice = ['AAEEGN', 'ABBJOO', 'ACHOPS', 'AFFKPS',
    'AOOTTW', 'CIMOTU', 'DEILRX', 'DELRVY',
    'DISTTY', 'EEGHNW', 'EEINSU', 'EHRTVW',
    'EIOSST', 'ELRTTY',
    ['H', 'I', 'M', 'N', 'Qu', 'U'],
    'HLNNRZ'] # https://stanford.edu/class/archive/cs/cs106x/cs106x.1132/handouts/17-Assignment-3-Boggle.pdf
  
  def collectDice(self, num_dice: int):
    for d in range(num_dice, 0, -16):
      self.dice.extend(self.boggle_dice)
    
    if (d > 0):
      extra_bag = BoggleBag(self.boggle_dice)
      extra_bag.shuffle()
      for e in range(0, d):
        self.dice.append(extra_bag.dice[e])

class BoggleSpace(BoardSpace):
  def __init__(self, letter: str, id):
    self.letter = letter.lower()
    self.adjacent = []
    self.id = id

  # TODO: QUESTION: How can I make the "space" argument of type "BoggleSpace"?
  def addAdjacent(self, space_id: str):
    self.adjacent.append(space_id)


class BoggleBoard(Board):
  def __init__(self, width: int, height: int):
    self.width = width
    self.height = height
    self._spaces = dict() # This will be a list of all spaces, with the keys being IDs so they can easily be retrieved, and identify which spaces are adjacent
    self.space_id_list = list()
  
  def getSpace(self, id: str) -> BoggleSpace:
    return self._spaces[id]
  
  def addSpace(self, new_space: BoggleSpace) -> str:
    space_code = None
    while (space_code == None) or (space_code in self._spaces):
      # It is extrememely unlikely that a space code will already exist, but it is good to check, just in case!
      space_code = genCode(4)
    self._spaces[space_code] = new_space
    self.space_id_list.append(space_code)
    return space_code

  def genDiceBag(self):
    self.dice_bag = BoggleBag()
    self.dice_bag.collectDice(self.width * self.height)
  
  def genBoard(self):
    """Generate board, and record which spaces are adjacent to each other
    """
    self.dice_bag.shuffle()
    on_dice = 0
    self.board = []
    self.basic_board = [] # Just the letters as Strings
    roll_results = self.dice_bag.rollDice()
    for w in range(self.width):
      board_row = []
      basic_row = []
      for h in range(self.height):
        try:
          letter = roll_results[on_dice]
          new_space = BoggleSpace(letter, on_dice)
          space_id = self.addSpace(new_space)
          board_row.append(space_id) # Will store the space IDs, and reference them using the getSpace() method
          basic_row.append(letter)
          
          on_dice += 1
        except IndexError:
          return on_dice*-1
      self.board.append(board_row)
      self.basic_board.append(basic_row)
    
    for w in range(self.width):
      for h in range(self.height):
        working_space_id = self.board[w][h]
        working_space = self.getSpace(working_space_id)
        if h > 0:
          if w > 0:
            working_space.addAdjacent(self.board[w-1][h-1])
          working_space.addAdjacent(self.board[w][h-1])
          if w < self.height - 1:
            working_space.addAdjacent(self.board[w+1][h-1])
        
        
        if w > 0:
          working_space.addAdjacent(self.board[w-1][h])
        if w < self.height - 1:
          working_space.addAdjacent(self.board[w+1][h])
        
        
        if h < self.height - 1:
          if w > 0:
            working_space.addAdjacent(self.board[w-1][h+1])
          working_space.addAdjacent(self.board[w][h+1])
          if w < self.height - 1:
            working_space.addAdjacent(self.board[w+1][h+1])
  
  
  def getWords(self, word_data: str):
    boggle_word_finder = _BoggleWordFinder(word_data, self)
    self.word_list = boggle_word_finder.findWords()
    self.all_words = word_data.split(',')[1:-1]
    return self.word_list

  def genGame(self, word_data: str):
    self.genDiceBag()
    self.genBoard()
    self.getWords(word_data)

  

class _BoggleWordFinder:
  def __init__(self, word_data: str, boggle_board: BoggleBoard):
    self.word_data = word_data
    self._word_list = []
    self._board = boggle_board
  
  def _buildWord(self, working_space: BoggleSpace, word_so_far: str = '', used_space_ids: list[int] = []):
    space_letter = working_space.letter
    word_so_far = word_so_far + space_letter
    used_space_ids.append(working_space.id)

    
    if ',' + word_so_far in self.word_data: # Stop checks if start of word can't be found at all
      if (word_so_far not in self._word_list) and (',' + word_so_far + ',' in self.word_data): # Add to found words if not in word list and is a full word
        self._word_list.append(word_so_far)

      # Already confirmed at least start of word can be found, so now will add new letters and check them
      adjacent_spaces = working_space.adjacent
      for adj_id in adjacent_spaces:
        if adj_id not in used_space_ids: # Skip if already used that space
          adj_space = self._board.getSpace(adj_id)
          self._buildWord(adj_space, word_so_far, used_space_ids)
  
  def findWords(self):
    self._word_list = []
    for space_code in self._board.space_id_list:
      self._buildWord(self._board.getSpace(space_code))
    return self._word_list

class WordReason(Enum):
  ACCEPTED = 0
  TOO_SHORT = 1
  NOT_FOUND = 2
  NOT_A_WORD = 3
  SHARED_WORD = 4
  NO_TIME = 5
  ALREADY_ADDED = 6


class BogglePlayer(Player):
  def __init__(self, id, name: str = ''):
    super().__init__(id, name)
    self.approved_words = []
    self.rejected_words = OrderedDict()
    self._start_time = 0
  
  def playerStarted(self, timestamp: int):
    self._start_time = timestamp
  
  def withinTime(self, entered_time: int, game_time: int):
    """Checks if too much time has passed, and if the player is allowed to enter a word or not

    Args:
        entered_time (int): Unix timestamp of when the action was done
        game_time (int): Total time in the game in milliseconds

    Returns:
        bool: Returns True if time has not run out yet, and False if time has run out
    """

    if game_time + self._start_time > entered_time:
      return False
    else:
      return True

  
  # def addWordWithTime(self, word: str, entered_time: int, game_time: int):
  #   """Only adds word to the list if time has not run out yet

  #   Args:
  #       word (str): Word to be added
  #       entered_time (int): Unix time milliseconds when the time was entered
  #       game_time (int): Total amount of time in the game in seconds. Used with self._start_time to determine if the word should be added or not.
    
  #   Returns True of word was added, False if it wasn't
  #   """

  #   if game_time * 1000 + self._start_time > entered_time:
  #     return False
  #   else:
  #     return self.addWord(word)
  
  def addWord(self, word: str):
    if (word in self.approved_words) or (word in self.rejected_words):
      return WordReason.ALREADY_ADDED
    elif len(word) < 3:
      if self.addRejected(word, WordReason.TOO_SHORT):
        return WordReason.TOO_SHORT
      else:
        return WordReason.ALREADY_ADDED
    else:
      self.approved_words.append(word)
      return WordReason.ACCEPTED
  
  def addRejected(self, word: str, reason: WordReason):
    """Adds a word that has been rejected.

    Args:
        word (str): Word to be added
        reason (WordReason): Reason the word has been rejected

    Returns:
        bool: Returns False if the word has already been added to the list, and True if it has not been added yet.
    """
    if word in self.rejected_words:
      return False
    else:
      self.rejected_words[word] = reason
      return True
  
  def scorePlayer(self, shared_words):
    scoring = {
      3: 1,
      4: 1,
      5: 2,
      6: 3,
      7: 5
    }
    self.score = 0
    self.score_list = OrderedDict()
    for word in self.approved_words:
      if word in shared_words:
        self.score_list[word] = 0
      else:
        word_length = len(word)
        if word_length >= 8:
          self.score_list[word] = 11
        else:
          word_score = scoring[word_length]
          self.score_list[word] = word_score
          self.score += word_score
    return self.score

class BoggleGame(Game):
  def __init__(self, width: int, height: int, game_time: int):
    self._board = BoggleBoard(width=width, height=height)
    self.width = width
    self.height = height
    self._game_time = game_time * 1000
    super().__init__()

  def addPlayer(self, id, name: str = '', host: bool = False):
    self.players[id] = BogglePlayer(id, name)
    if host:
      self.host_id = id

  def genGame(self, word_data: str):
    self._board.genGame(word_data=word_data)
  
  def getBasicBoard(self):
    basic_board = self._board.basic_board
    return basic_board
  
  def enteredWord(self, id, word, entered_time) -> WordReason:
    """Adds word to the word list

    Args:
        id (str): Player ID
        word (str): Word to be added
        entered_time (int): Unix time in ms when word was entered
    
    Returns:
      bool: Returns True if word was accepted, False if rejected
    """
    
    player = self.players[id]
    if not player.withinTime(entered_time, self._game_time):
      return WordReason.NO_TIME
    elif word in self._board.word_list: # True if word is in current board
      return self.players[id].addWord(word)
    elif word in self._board.all_words: # It is a real word, but not on the board
      if self.players[id].addRejected(word, WordReason.NOT_FOUND):
        return WordReason.NOT_FOUND
      else:
        return WordReason.ALREADY_ADDED
    else:
      if self.players[id].addRejected(word, WordReason.NOT_A_WORD):
        return WordReason.NOT_A_WORD
      else:
        return WordReason.ALREADY_ADDED
  
  def getPlayerWords(self, id):
    player = self.players[id]
    return {
      'approved': player.approved_words,
      'rejected': player.rejected_words
    }
  
  # TODO: Add scoring based on shared words
