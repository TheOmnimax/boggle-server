import logging
from fastapi import APIRouter

from os.path import dirname, join, realpath
from pydantic import BaseModel
from typing import Optional

from .helpers import room_storage, getGameParameters

from game.room import GameRoom
from game.boggle import BoggleGame, BogglePlayer

from tools.randomization import genCode

router = APIRouter()


ROOT_FOLDER = dirname(dirname(realpath(__file__)))

# Creates a new game, sends back the room code
@router.post('/create-room')
async def createRoom():
  room_code = genCode(6)
  game_room = GameRoom(room_code)
  room_storage.set(game_room)
  return {
    'room_code': room_code,
    }

class CreateGame(BaseModel):
  room_code: str
  width: int
  height: int
  time: int

# Receives the room code, creates a new boggle game. Sends back the game parameters to create a blank board, as well as the player ID
@router.post('/create-game')
async def createGame(game_config: CreateGame):
  global room_storage
  room_code = game_config.room_code
  width = game_config.width
  height = game_config.height
  time = game_config.time
  boggle_game = BoggleGame(width=width, height=height, game_time=time)

  def cg(game_room: GameRoom):
    game_room.addGame(boggle_game)
    with open(join(ROOT_FOLDER, 'data', 'word_list.txt')) as f:
      word_data = f.read()
      boggle_game.genGame(word_data)

    player_id = genCode(6)
    host_data = BogglePlayer(player_id)
    game_room.addPlayer(host_data, True)
    
    content = getGameParameters(boggle_game)
    content['player_id'] = player_id
    print(game_room.game)
    return content

  
  content = room_storage.getAndSet(room_code, new_val_func=cg)

  print('Content:')
  print(type(content).__name__)
  print(content)
  return content
