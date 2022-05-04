from .board import BoardSpace, Board
from .dice import DiceBag
print('Running...')
from .player import Player
from .room import Game, GameRoom
from collections import OrderedDict
from enum import Enum

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
    self.letter = letter
    self.adjacent = []
    self.id = id

  # TODO: QUESTION: How can I make the "space" argument of type "BoggleSpace"?
  def addAdjacent(self, space):
    self.adjacent.append(space)


class BoggleBoard(Board):
  def __init__(self, width: int, height: int):
    self.width = width
    self.height = height
  
  def genDiceBag(self):
    self.dice_bag = BoggleBag()
    self.dice_bag.collectDice(self.width * self.height)
  
  def genBoard(self):
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
          board_row.append(BoggleSpace(letter, on_dice))
          basic_row.append(letter)
          on_dice += 1
        except IndexError:
          return on_dice*-1
      self.board.append(board_row)
      self.basic_board.append(basic_row)
    
    for w in range(self.width):
      for h in range(self.height):
        working_space = self.board[w][h]
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
    print('Successfully generated board!')
    print(self.basic_board)
    return on_dice
  
  
  def getWords(self, word_data: str):
    boggle_word_finder = _BoggleWordFinder(word_data)
    self.word_list = boggle_word_finder.findWords(self.board)
    self.all_words = word_data.split(',')[1:-1]
    return self.word_list

  def genGame(self, word_data: str):
    self.genDiceBag()
    self.genBoard()
    self.getWords(word_data)

  

class _BoggleWordFinder:
  def __init__(self, word_data: str):
    self.word_data = word_data
    self.word_list = []
  
  def _buildWord(self, working_space: BoggleSpace, word_so_far: str = '', used_space_ids: list[int] = []):
    adjacent_spaces = working_space.adjacent
    for adj in adjacent_spaces:
      if adj.id not in used_space_ids: # Skip if already used that space
        testing_word = word_so_far + adj.letter
        if ',' + testing_word in self.word_data: # Only check if start of word can be found
          if (testing_word not in self.word_list) and (',' + testing_word + ',' in self.word_data): # Add to found words if not in word list and is a full word
            self.word_list.append(testing_word)
          used_space_ids.append(adj.id) # Indicate that that letter has been used, and should not be re-used in this sequence
          self._buildWord(adj, testing_word, used_space_ids)
  
  def findWords(self, boggle_board: BoggleBoard):
    board = boggle_board
    self.word_list = []
    for row in board:
      for space in row:
        self._buildWord(space)
    return self.word_list

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

  def genGame(self, word_data: str):
    self._board.genGame(word_data=word_data)
  
  def getBasicBoard(self):
    print(self._board)
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
