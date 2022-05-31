import logging
from fastapi import APIRouter

from os.path import dirname, join, realpath
from pydantic import BaseModel
from typing import Optional

from .helpers import room_storage, getGameParameters

from game.room import GameRoom
from game.boggle import BoggleGame, BogglePlayer

from tools.randomization import genCode

import json

router = APIRouter()


ROOT_FOLDER = dirname(dirname(realpath(__file__)))

class NoData(BaseModel):
  pass

# Creates a new game, sends back the room code
@router.post('/create-room')
async def createRoom(data: NoData):
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
  name: str

# Receives the room code, creates a new boggle game. Sends back the game parameters to create a blank board, as well as the player ID
@router.post('/create-game')
async def createGame(game_config: CreateGame):
  global room_storage
  room_code = game_config.room_code
  width = game_config.width
  height = game_config.height
  time = game_config.time
  host_name = game_config.name
  boggle_game = BoggleGame(width=width, height=height, game_time=time)

  def cg(game_room: GameRoom):
    game_room.addGame(boggle_game)
    with open(join(ROOT_FOLDER, 'data', 'word_list.txt')) as f:
      word_data = f.read()
    word_list = word_data.split(',')
    
    
    with open(join(ROOT_FOLDER, 'data', 'word_index.json')) as f:
      word_index = json.loads(f.read()) 
    boggle_game.genGame(word_index=word_index, word_list=word_list, game_time=game_config.time)
    # TODO: Update game time to be customized by user

    player_id = genCode(6)
    host_data = BogglePlayer(id=player_id, name=host_name)
    game_room.addPlayer(host_data, True)
    
    content = getGameParameters(boggle_game)
    content['player_id'] = player_id
    return content

  content = room_storage.getAndSet(room_code, new_val_func=cg)
  return content
