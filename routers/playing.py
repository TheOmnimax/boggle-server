from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


from game.room import GameRoom
from game.boggle import WordReason

from .helpers import send_headers, room_storage, getBody, roomExists

router = APIRouter()

@router.post('/add-word')
async def addWord(request: Request):
  global room_storage
  headers = request.headers
  body = await getBody(request)
  room_code = body['room_code']
  player_id = body['player_id']
  timestamp = body['timestamp']
  word = body['word']

  def aw(game_room: GameRoom) -> WordReason:
    boggle_game = game_room.game
    return boggle_game.enteredWord(player_id, word, timestamp)
  
  word_reason = room_storage.getAndSet(room_code, roomExists, aw)
  content = dict()

  if word_reason is WordReason.ACCEPTED:
    content['reason'] = 'ACCEPTED'
    status_code = 201
  elif word_reason is WordReason.TOO_SHORT:
    content['reason'] = 'TOO_SHORT'
    status_code = 406
  elif word_reason is WordReason.NOT_FOUND:
    content['reason'] = 'NOT_FOUND'
    status_code = 404
  elif word_reason is WordReason.NOT_A_WORD:
    content['reason'] = 'NOT_A_WORD'
    status_code = 404
  elif word_reason is WordReason.SHARED_WORD:
    content['reason'] = 'SHARED_WORD'
    status_code = 406
  elif word_reason is WordReason.NO_TIME:
    content['reason'] = 'NO_TIME'
    status_code = 406
  elif word_reason is WordReason.ALREADY_ADDED:
    content['reason'] = 'ALREADY_ADDED'
    status_code = 406
  else:
    content['reason'] = 'UNKNOWN'

  response = JSONResponse(
    content,
    headers=send_headers
  )
  response.status_code = status_code
  return response

@router.post('/get-results')
async def getResults(request: Request):
  global room_storage
  body = await getBody(request)
  headers = request.headers
  room_code = headers['room_code']
  # boggle_game = getGame(room_code)
  response = JSONResponse({},
    headers=send_headers)
  return response

