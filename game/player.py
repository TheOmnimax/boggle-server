class Player:
  def __init__(self, id, name: str = '', start_score: int = 0):
    self.id = id
    self.name = name
    self.score = start_score