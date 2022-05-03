from .player import Player

class Game:
  def __init__(self):
    self.players = dict()
    self.host_id = None
    self.running = False
  
  def addPlayer(self, id, name: str = '', host: bool = False):
    self.players[id] = Player(id, name)
    if host:
      self.host_id = id
  
  def startGame(self):
    self.running = True

class GameRoom:
  def __init__(self, room_code):
    self.room_code = room_code
    self.players = dict()
    self.game = None
    self.host_id = None
  
  def addPlayer(self, player: Player, host: bool = False):
    self.players[player.id] = player
    if self.game != None:
      self.game.addPlayer(player.id, player, host)
    
    if host:
      self.host_id = player.id
  
  def addGame(self, game: Game):
    self.game = game
    for player_code in self.players:
      self.game.addPlayer(player_code, self.players[player_code])
  
  def startGame(self, player_id):
    if player_id == self.host_id:
      self.game.startGame()
      return True
    else:
      return False