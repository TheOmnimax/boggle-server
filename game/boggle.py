from .board import BoardSpace, Board
from .dice import DiceBag
from .player import TimedPlayer
from .room import Game
from .word_game import word_trie
from collections import OrderedDict
from enum import Enum
from typing import List, Dict

class BoggleBag(DiceBag):
  boggle_dice = ['AAEEGN', 'ABBJOO', 'ACHOPS', 'AFFKPS',
    'AOOTTW', 'CIMOTU', 'DEILRX', 'DELRVY',
    'DISTTY', 'EEGHNW', 'EEINSU', 'EHRTVW',
    'EIOSST', 'ELRTTY',
    ['H', 'I', 'M', 'N', 'Qu', 'U'],
    'HLNNRZ'] # https://stanford.edu/class/archive/cs/cs106x/cs106x.1132/handouts/17-Assignment-3-Boggle.pdf
  
  def collectDice(self, num_dice: int):
    """Add dice to the dice bag. If the number of dice being added is not a multiple of 16, then it will pick the remaining dice randomly.

    Args:
        num_dice (int): Number of dice to add to the bag.
    """
    for d in range(num_dice, 0, -16):
      self.dice.extend(self.boggle_dice)
    
    # If there are still dice to add to the bag, then it will pick the remaining dice at random.
    if (d > 0):
      extra_bag = BoggleBag(self.boggle_dice)
      extra_bag.shuffle()
      for e in range(0, d):
        self.dice.append(extra_bag.dice[e])

class BoggleSpace(BoardSpace):
  """Boggle space on the board, which will contain a dice.
  """
  def __init__(self, letter: str, id):
    self.letter = letter.lower() # Letter assigned to space
    self.adjacent = [] # Which letters are adjacent to that space, creating a graph, which is used later to find all possible words
    self.id = id # ID of the space, used to make sure the same space is not used twice when building a word.

  def addAdjacent(self, space_id: str):
    """Add a space that is adjacent, so know where to look when finding words

    Args:
        space_id (str): ID of the adjacent space.
    """
    self.adjacent.append(space_id)


class BoggleBoard(Board):
  def __init__(self, width: int, height: int):
    self.width = width
    self.height = height
    self._spaces = dict() # This will be a list of all spaces, with the keys being IDs so they can easily be retrieved, and identify which spaces are adjacent
    self.space_id_list = list() # Used by _BoggleWordFinder to cycle through all spaces on the board
  
  def getSpace(self, id: str) -> BoggleSpace:
    return self._spaces[id]
  
  def addSpace(self, new_space: BoggleSpace) -> str:
    space_code = new_space.id
    self._spaces[space_code] = new_space
    self.space_id_list.append(space_code)
    return space_code

  def genDiceBag(self):
    """Generate bag of dice based on number of spaces.
    """
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
  
  
  def getWords(self) -> List[str]:
    """Generate list of all possible words on the board

    Returns:
        List[str]: List of words
    """
    boggle_word_finder = _BoggleWordFinder(self)
    self.word_list = boggle_word_finder.findWords()
    return self.word_list

  def genGame(self):
    """Generate the game using the needed functions
    """
    self.genDiceBag()
    self.genBoard()
    self.getWords()


class _BoggleWordFinder:
  """Used to traverse the Boggle board and find all possible words.
  """
  def __init__(self, boggle_board: BoggleBoard):
    self._word_list = []
    self._board = boggle_board
  
  def _buildWord(self, working_space: BoggleSpace, word_so_far: str = '', used_space_ids: list[int] = [], working_dict: dict = dict()):
    
    space_letter = working_space.letter
    word_so_far = word_so_far + space_letter
    
    if space_letter == 'qu':
      space_letter = 'q'
    
    if space_letter in working_dict:
      working_dict = working_dict[space_letter]
      if space_letter == 'q':
        if 'u' in working_dict:
          working_dict = working_dict['u']
          space_letter = 'u'
        else:
          return

      if ('word' in working_dict) and (len(word_so_far) > 1) and (word_so_far not in self._word_list):
        self._word_list.append(word_so_far)
    
      used_space_ids = used_space_ids.copy()
      used_space_ids.append(working_space.id)
      # Already confirmed at least start of word can be found, so now will add new letters and check them

      adjacent_spaces = working_space.adjacent
      for adj_id in adjacent_spaces:
        if adj_id not in used_space_ids: # Skip if already used that space
          adj_space = self._board.getSpace(adj_id)
          self._buildWord(adj_space, word_so_far, used_space_ids, working_dict=working_dict)
  
  def findWords(self) -> List[str]:
    self._word_list = []
    for space_code in self._board.space_id_list:
      self._buildWord(self._board.getSpace(space_code), working_dict=word_trie.word_index)
    return self._word_list

class WordReason(Enum):
  """Why a word is accepted or rejected by the game.
  """
  ACCEPTED = 0
  TOO_SHORT = 1
  NOT_FOUND = 2
  NOT_A_WORD = 3
  SHARED_WORD = 4
  NO_TIME = 5
  ALREADY_ADDED = 6


class BogglePlayer(TimedPlayer):
  def __init__(self, id, name: str = ''):
    super().__init__(id, name)
    self.approved_words = []
    self.rejected_words = OrderedDict()
    self._start_time = 0
  
  
  def addWord(self, word: str) -> WordReason:
    """Word entered by player, add to their list of words.

    Args:
        word (str): Word entered by player.

    Returns:
        WordReason: Reason word was accepted or rejected
    """
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
  
  def addRejected(self, word: str, reason: WordReason) -> bool:
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
  
  def getApprovedWords(self) -> List[str]:
    return self.approved_words
  
  def scorePlayer(self, shared_words: List[str]) -> int:
    """When game is over, take their words, and score them.

    Args:
        shared_words (list[str]): List of words shared by other players, which will be scored as 0.

    Returns:
        int: Final score of player.
    """
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
    self._game_scored = False
    super().__init__()
  
  def getName(self, id) -> str:
    """Get name of player with that ID

    Args:
        id (str): Player ID

    Returns:
        str: Name of player
    """
    return self.players[id].name

  def genGame(self, game_time: int = 90):
    """Generate the game, so it is ready to play.

    Args:
        game_time (int, optional): How long the game should be. Defaults to 90.
    """
    self._board.genGame()
    self._game_time = game_time
  
  def getGameTime(self):
    return self._game_time
  
  def getBasicBoard(self) -> List[List[str]]:
    """Retrtieves a basic version of the Boggle board, just the letters, with no adjacents or IDs.

    Returns:
        List[List[str]]: Basic version of Boggle board.
    """
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
    if not player.withinTime(entered_time):
      return WordReason.NO_TIME
    elif word in self._board.word_list: # True if word is in current board
      return self.players[id].addWord(word)
    else:
      word_exists = word_trie.checkWordExists(word)
      if word_exists:
        if self.players[id].addRejected(word, WordReason.NOT_FOUND):
          return WordReason.NOT_FOUND
        else:
          return WordReason.ALREADY_ADDED
      elif self.players[id].addRejected(word, WordReason.NOT_A_WORD): # True if word is not a real word
        return WordReason.NOT_A_WORD
      else:
        return WordReason.ALREADY_ADDED
  
  def getPlayerWords(self, id):
    player = self.players[id]
    return {
      'approved': player.approved_words,
      'rejected': player.rejected_words
    }
  
  def checkGameEnded(self):
    """Check all players, and see if their time is up. If their time is up, then the game is over.

    Returns:
        bool: True if all player's time is up and game is over, False if there is at least one player left
    """
    for player_id in self.players:
      player = self.players[player_id]
      if player.checkWithinTime():
        return False
    return True

  def scoreGame(self):
    """After game is over, score the game, and store it in object property "score_data", which is retrieved later when requested.
    """
    if self._game_scored: # Ensure game is not scored too many times
      return
    self._game_scored = True

    self.results = dict()
    self.found_words = dict()
    players = self.players

    # Get shared words
    for player_id in players:
      player = players[player_id]
      approved_words = player.getApprovedWords()
      for word in approved_words:
        if word in self.found_words:
          self.found_words[word].append(player.id)
        else:
          self.found_words[word] = [player.id]
    self.shared_words = []
    for word in self.found_words:
      if len(self.found_words[word]) > 1:
        self.shared_words.append(word)

    # Score players
    for player_id in players:
      player = players[player_id]
      player.scorePlayer(self.shared_words)
    
    who_shared_words = dict() # Dict where key is the shared word, and value is a list of player names who shared that word
    for word in self.found_words:
      word_players = self.found_words[word] # IDs of players who found that word
      if len(word_players) > 1:
        player_names = list()
        for player_id in word_players:
          player_names.append(self.getName(player_id))
        who_shared_words[word] = player_names
    
    # Calculated all scores. Now, will put into JSON format so it can be returned in an HTTP request.

    player_data = list()
    winner_names = []
    winning_score = 1

    for player_id in self.players:
      player = self.players[player_id]
      score_list = list(player.score_list.items())
      p_data = {
        'name': player.name,
        'score_list': score_list,
        'score': player.score
      }
      player_data.append(p_data)
      if player.score > winning_score:
        winning_score = player.score
        winner_names = [player.name]
      elif player.score == winning_score:
        winner_names.append(player.name)
    
    if len(winner_names) == 0:
      winning_score = 0

    missed_words = []

    for word in self._board.word_list:
      if (len(word) > 2) and (word not in self.found_words.keys()):
        missed_words.append(word)

    self.score_data = { # Dict that can be returned to users
      'shared_words': who_shared_words,
      'player_data': player_data,
      'winning_score': winning_score,
      'winner_names': winner_names,
      'missed_words': missed_words
    }

  def getScores(self) -> Dict:
    return self.score_data

