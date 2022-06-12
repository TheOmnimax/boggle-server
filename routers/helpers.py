import logging

from pydantic import BaseModel
from game.room import GameRoom
from game.boggle import BoggleGame
from tools.json_tools import JsonConverter
import threading

from fastapi import HTTPException
import json
from enum import Enum

send_headers = {
  'Access-Control-Allow-Origin': '*'
  }

class GameError(Enum):
  room_not_found = 0

# TODO: Set up concurrency through locks
class MemoryStorage:
  def __init__(self):
    self._lock = threading.Lock()
    self._data = dict()
    self._json_converter = JsonConverter(skipped_keys=['word_index'])
  
  def exists(self, room_code):
    if room_code in self._data:
      return True
    else:
      raise HTTPException(status_code=404, detail='Game room not found!')

  def set(self, game_room: GameRoom):
    self._lock.acquire()
    try:
      room_code = game_room.room_code
      self._data[room_code] = json.dumps(self._json_converter.objToJson(game_room))
      logging.info(f'Set with room code {room_code}')
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
  def getAndSet(self, room_code, predicate=None, new_val_func=None):
    self._lock.acquire()
    try:
      if (predicate == None) or (predicate(room_code)):
        game_room = self.get(room_code)
        if new_val_func == None:
          return 'No action given'
        else:
          data = new_val_func(game_room)
          logging.info('Dumping data')
          self._data[room_code] = json.dumps(self._json_converter.objToJson(game_room))
          logging.info('Dump complete')
          return data
      else:
        logging.info(f'Game room {room_code} not found')
        return GameError.room_not_found
    except:
      logging.exception('Error')
      return {'error': 'Game room not found'}
    finally:
      self._lock.release()

room_storage = MemoryStorage()

def roomExists(room_code):
  if room_storage.exists(room_code):
    return True
  else:
    return False

def checkIfHost():
  pass

# Parameters for the game, so the blank board can be generated
def getGameParameters(boggle_game: BoggleGame):
  return {
      'height': boggle_game.width,
      'width': boggle_game.height,
      'time': boggle_game.getGameTime()
  }

class PlayerCommand(BaseModel):
  room_code: str
  player_id: str

