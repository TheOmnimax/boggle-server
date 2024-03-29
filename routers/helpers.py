import logging

from pydantic import BaseModel
from game.room import GameRoom
from game.boggle import BoggleGame
from tools.json_tools import JsonConverter
import threading

from fastapi import HTTPException
import json
from enum import Enum
from typing import Dict

class GameError(Enum):
  room_not_found = 0

class MemoryStorage:
  """Used to manage active game rooms and games. (Used instead of Redis to save on costs.)
  """
  def __init__(self):
    self._lock = threading.Lock()
    self._data = dict()
    self._json_converter = JsonConverter(skipped_keys=['word_index'])
  
  def exists(self, room_code: str) -> bool:
    """Check if a room with that room code exists.

    Args:
        room_code (str): Room code

    Raises:
        HTTPException: Raised if room cannot be found.

    Returns:
        bool: True if room is found
    """
    if room_code in self._data:
      return True
    else:
      message = f'Game room {room_code} not found!'
      logging.info(message)
      raise HTTPException(status_code=404, detail=message)

  def set(self, game_room: GameRoom):
    """Used to generate a new room

    Args:
        game_room (GameRoom): New game room data
    """
    self._lock.acquire()
    try:
      room_code = game_room.room_code
      self._data[room_code] = json.dumps(self._json_converter.objToJson(game_room))
    except:
      pass
    finally:
      self._lock.release()
        
  def get(self, room_code) -> GameRoom:
    """Given a game code, returns a game room

    Args:
        room_code (str): Game code

    Returns:
        GameRoom: Game room with that code
    """
    try:
      raw_data = self._data[room_code]
    except KeyError:
      logging.warning(f'Room code {room_code} not found')
      for code in self._data:
        logging.info(code)
      return dict()
    try:
      return self._json_converter.jsonToObj(json.loads(raw_data))
    except:
      logging.exception('Unknown error')
      return dict()

  def getAndSet(self, room_code: str, predicate=None, new_val_func=None):
    """Update existing game room with new data

    Args:
        room_code (str): Room code
        predicate (function, optional): Predicate that should be true before running the get-and-set. Should take one parameter, a str, the room code. Defaults to None.
        new_val_func (function, optional): Function that will manipulate the data before it is written to the memory. Should take one parameter with type "GameRoom". Defaults to None.

    Returns:
        _type_: _description_
    """

    self._lock.acquire()
    try:
      if (predicate == None) or (predicate(room_code)):
        game_room = self.get(room_code)
        if new_val_func == None:
          return 'No action given'
        else:
          data = new_val_func(game_room)
          self._data[room_code] = json.dumps(self._json_converter.objToJson(game_room))
          return data
      else:
        logging.info(f'Game room {room_code} not found')
        return {'error': 'Game room not found'}
    except:
      logging.exception('Error')
      return {'error': 'Game room not found'}
    finally:
      self._lock.release()

room_storage = MemoryStorage()

def roomExists(room_code):
  try:
    if room_storage.exists(room_code):
      return True
    else:
      return False
  except HTTPException:
    return False

# Parameters for the game, so the blank board can be generated
def getGameParameters(boggle_game: BoggleGame) -> Dict[str, int]:
  """Parameters for the game, so the blank board can be generated by the client, displayed to the player.

  Args:
      boggle_game (BoggleGame): Boggle game data

  Returns:
      Dict[str, int]: Data about the Boggle game
  """
  return {
      'height': boggle_game.width,
      'width': boggle_game.height,
      'time': boggle_game.getGameTime()
  }
