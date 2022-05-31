import logging

from pydantic import BaseModel
from game.room import GameRoom
from game.boggle import BoggleGame
from tools.json_tools import JsonConverter
import threading

from fastapi import Request
import json

send_headers = {
  'Access-Control-Allow-Origin': '*'
  }

# TODO: Set up concurrency through locks
class MemoryStorage:
  def __init__(self):
    self.lock = threading.Lock()
    self.data = dict()
    self.json_converter = JsonConverter()

  def set(self, game_room: GameRoom):
    self.lock.acquire()
    try:
      room_code = game_room.room_code
      self.data[room_code] = json.dumps(self.json_converter.objToJson(game_room))
    except:
      pass
    finally:
      self.lock.release()
        
  def get(self, room_code) -> GameRoom:
    """Given a game code, returns a game room

    Args:
        room_code (str): Game code

    Returns:
        GameRoom: Game room with that code
    """
    try:
      raw_data = self.data[room_code]
    except KeyError:
      logging.warning(f'Room code {room_code} not found')
      for code in self.data:
        logging.info(code)
      return dict()
    try:
      return self.json_converter.jsonToObj(json.loads(raw_data))
    except:
      logging.exception('Unknown error')
      return dict()
  def getAndSet(self, room_code, predicate=None, new_val_func=None):
    self.lock.acquire()
    try:
      if (predicate == None) or (predicate(room_code)):
        game_room = self.get(room_code)
        if new_val_func == None:
          return 'No action given'
        else:
          data = new_val_func(game_room)
          self.data[room_code] = json.dumps(self.json_converter.objToJson(game_room))
          return data
      else:
        logging.info(f'Game room {room_code} not found')
        return 'Game room not found'
    except:
      logging.exception('Error')
      return {'error': 'Game room not found'}
    finally:
      self.lock.release()


def roomExists(room_code):
  global room_storage
  try:
    game_room = room_storage.get(room_code)
  except:
    return False
  return True

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

room_storage = MemoryStorage()
