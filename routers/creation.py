from testing.tools import getHeapSize

import logging
from fastapi import APIRouter

from pydantic import BaseModel

from .helpers import room_storage, getGameParameters

from game.room import GameRoom
from game.boggle import BoggleGame, BogglePlayer

from tools.randomization import genCode

router = APIRouter()

class NoData(BaseModel):
  pass

# Creates a new game, sends back the room code
@router.post('/create-room')
async def createRoom(data: NoData):
  getHeapSize('Function: create-room')
  room_code = genCode(6)
  game_room = GameRoom(room_code)
  room_storage.set(game_room)
  logging.info(f'Created room code {room_code}')
  getHeapSize('After size')
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
  
  getHeapSize('Function: create-game')
  global room_storage
  room_code = game_config.room_code
  width = game_config.width
  height = game_config.height
  time = game_config.time
  host_name = game_config.name
  getHeapSize('About to create game')
  boggle_game = BoggleGame(width=width, height=height, game_time=time)

  def cg(game_room: GameRoom):
    getHeapSize('About to add game')
    game_room.addGame(boggle_game)
    
    getHeapSize('Generating game')
    boggle_game.genGame(game_time=game_config.time)
    # TODO: Update game time to be customized by user

    
    getHeapSize('About to create player')
    player_id = genCode(6)
    host_data = BogglePlayer(id=player_id, name=host_name)
    
    getHeapSize('About to add player to game')
    game_room.addPlayer(host_data, True)
    logging.info('Added player')
    
    content = getGameParameters(boggle_game)
    content['player_id'] = player_id
    logging.info('Got content')
    return content

  logging.info('Getting and setting')
  content = room_storage.getAndSet(room_code, new_val_func=cg)
  logging.info('Complete!')
  return content
