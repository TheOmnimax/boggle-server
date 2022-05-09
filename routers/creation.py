import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from os.path import dirname, join, realpath
from pydantic import BaseModel
from typing import Optional

from .helpers import send_headers, room_storage, getGameParameters

from game.room import GameRoom
from game.boggle import BoggleGame, BogglePlayer

from tools.randomization import genCode

router = APIRouter()

# Creates a new game, sends back the room code
@router.post('/create-room')
async def createRoom(request: Request):
  logging.info('About to get room storage...')
  global room_storage
  logging.info('Creating room...')

  room_code = genCode(6)
  game_room = GameRoom(room_code)
  room_storage.set(game_room)
  response = JSONResponse(
    {
    'room_code': room_code,
    },
    headers=send_headers
    )
  response.status_code = 201
  logging.info('Room created!')
  return {
    'room_code': room_code,
    }

class GameConfig(BaseModel):
  room_code: Optional[str] = None
  width: Optional[int] = None
  height: Optional[int] = None
  time: Optional[int] = None

# Receives the room code, creates a new boggle game. Sends back the game parameters to create a blank board, as well as the player ID
@router.post('/create-game')
async def createGame(game_config: GameConfig):
  logging.info('Python log: Preparing to create game...')
  global room_storage
  logging.info('Python log: Got global var')
  room_code = game_config.room_code
  width = game_config.width
  height = game_config.height
  time = game_config.time
  logging.info('Python log: Got needed data.')
  boggle_game = BoggleGame(width=width, height=height, game_time=time)
  logging.info('Python log: Game created.')

  def cg(game_room: GameRoom):
    logging.info('Python log: Starting val function')
    game_room.addGame(boggle_game)
    logging.info('Python log: Game added to game room')
    current_folder = dirname(realpath(__file__))
    with open(join(current_folder, 'data', 'word_list.txt')) as f:
      word_data = f.read()
      boggle_game.genGame(word_data)
    
    logging.info('Python log: Got and applied word list')

    player_id = genCode(6)
    host_data = BogglePlayer(player_id)
    logging.info('Python log: Preparing to add player')
    game_room.addPlayer(host_data, True)
    logging.info('Python log: Player added')
    
    content = getGameParameters(boggle_game)
    content['player_id'] = player_id
    print(game_room.game)
    return content

  
  content = room_storage.getAndSet(room_code, new_val_func=cg)

  response = JSONResponse(
    content,
    headers=send_headers
    )
  print('Content:')
  print(content)
  return content
