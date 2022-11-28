from fastapi import APIRouter
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from typing import Optional
from game.boggle import BogglePlayer

from game.room import GameRoom

from .helpers import send_headers, room_storage, getGameParameters, roomExists

from tools.randomization import genCode

router = APIRouter()

class AddPlayer(BaseModel):
  room_code: str
  name: str

@router.post('/add-player')
async def addPlayer(data: AddPlayer):

  def ap(game_room: GameRoom):
    boggle_game = game_room.game
    player_id = genCode(8)
    player = BogglePlayer(name=data.name, id=player_id)
    boggle_game.addPlayer(player=player)
    return {'player_id': player_id}
  
  content = room_storage.getAndSet(data.room_code, predicate=roomExists, new_val_func=ap)
  return content

class JoinGame(BaseModel):
  room_code: str
  player_id: Optional[str] = None

# This should be called after the player has been added to the game. This sends the game data to the user
@router.post('/join-game')
async def joinGame(join_data: JoinGame):
  room_code = join_data.room_code

  def jg(game_room: GameRoom):
    boggle_game = game_room.game
    content = getGameParameters(boggle_game)
    content['is_host'] = game_room.isHost(player_id=join_data.player_id)
    return content

  content = room_storage.getAndSet(room_code, predicate=roomExists, new_val_func=jg)
  return content

class HostCommand(BaseModel):
  room_code: str
  player_id: str

# Sent by the host to start the game
@router.post('/start-game')
async def startGame(body: HostCommand):
  global room_storage
  
  room_code = body.room_code
  player_id = body.player_id
  
  room_code = body.room_code
  player_id = body.player_id
  def sg(game_room: GameRoom):
    boggle_game = game_room.game
    if game_room.isHost(player_id):
      boggle_game.startGame()
      return {
        'started': True,
        'board': boggle_game.getBasicBoard()
      }
    else:
      return {
        'started': False,
      }

  content = room_storage.getAndSet(room_code, roomExists, sg)

  game_started = content['started']
  if (game_started):
    status_code = 201
  else:
    status_code = 403
  response = JSONResponse(
    content,
    headers=send_headers
  )
  response.status_code = status_code

  return content

class RoomData(BaseModel):
  room_code: str

@router.post('/is-started')
async def isStarted(body: RoomData):
  room_code = body.room_code

  game_room = room_storage.get(room_code)
  if game_room == None:
    return {
      'running': False
    }
  try:
    game_running = game_room.game.running
  except:
    return {
      'running': False
    }

  return {
    'running': game_running,
    }

@router.post('/get-game-data')
async def isStarted(body: RoomData):
  room_code = body.room_code
  game_room = room_storage.get(room_code)
  game = game_room.game
  game_running = game.running
  
  if game_running:
    basic_board = game.getBasicBoard()
    return {
      'running': True,
      'board': basic_board
    }
  else:
    return {
      'running': False
    }
  
class PlayerStart(BaseModel):
  room_code: str
  player_id: str
  timestamp: int

# Stores the timestamp of when the player started the game. This is used to determine when they are no longer allowed to submit words because time ran out, while accounting for slower internet
@router.post('/player-start')
async def playerStart(body: PlayerStart):
  global room_storage
  room_code = body.room_code
  player_id = body.player_id
  timestamp = body.timestamp

  def ps(game_room: GameRoom):
    game = game_room.game
    game_running = game.running

    if game_running:
      pass
    else:
      return {
        'running': False
      }

    player = game.players[player_id] # Return BogglePlayer
    game_time = game.getGameTime() * 1000
    player.playerStarted(timestamp, game_time)

  room_storage.getAndSet(room_code, roomExists, ps)

