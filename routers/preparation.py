from sqlite3 import Timestamp
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from typing import Optional

from game.room import GameRoom

from .helpers import send_headers, room_storage, getGameParameters, getBody, roomExists

from tools.randomization import genCode

router = APIRouter()

class HostCommand(BaseModel):
  room_code: str
  player_id: Optional[str] = None

# For guests, not hosts Receives the room code, generates anew player ID, adds that player ID to the room and the game. Sends back the player ID, as well as the game parameters for the game to create tehe blank board 
@router.post('/join-game')
async def joinGame(body: HostCommand):
  global room_storage
  room_code = body.room_code
  host_id = body.player_id

  def jg(game_room: GameRoom):
    boggle_game = game_room.game
    if host_id == game_room.host_id:
      boggle_game.addPlayer(host_id, host=True)
      player_id = host_id
    else:
      player_id = genCode(8)
      boggle_game.addPlayer(player_id)
    content = getGameParameters(boggle_game)
    content['player_id'] = player_id
    return content

  content = room_storage.getAndSet(room_code, roomExists, jg)
  response = JSONResponse(
    content,
    headers=send_headers
    )
  response.status_code = 201
  return response


# Sent by the host to start the game
@router.post('/start-game')
async def startGame(body: HostCommand):
  global room_storage
  
  room_code = body.room_code
  player_id = body.player_id
  
  room_code = body['room_code']
  player_id = body['player_id']
  print(f'Player ID: {player_id}')
  def sg(game_room: GameRoom):
    boggle_game = game_room.game
    print(f'Host ID: {game_room.host_id}')
    if game_room.host_id == player_id:
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

  return response

@router.post('/is-started')
async def isStarted(request: Request):
  global room_storage
  headers = request.headers
  body = await getBody(request)
  room_code = body['room_code']

  game_room = room_storage.get(room_code)
  game_running = game_room.game.running

  response = JSONResponse(
    {
    'running': game_running,
    },
    headers=send_headers
    )
  
  return response

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
    player = game_room.players[player_id] # Return BogglePlayer
    player.playerStarted(timestamp)
    pass

  room_storage.getAndSet(room_code, roomExists, ps)

