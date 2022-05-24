from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

import logging

from game.room import GameRoom
from game.boggle import WordReason

from pydantic import BaseModel
from typing import Optional

from .helpers import send_headers, room_storage, roomExists

router = APIRouter()

class AddWord(BaseModel):
  room_code: str
  player_id: str
  timestamp: int
  word: str

@router.post('/add-word')
async def addWord(body: AddWord):
  def aw(game_room: GameRoom) -> WordReason:
    boggle_game = game_room.game
    return boggle_game.enteredWord(body.player_id, body.word, body.timestamp)
  
  word_reason = room_storage.getAndSet(body.room_code, roomExists, aw)
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

  return content

class PlayerCheckIn(BaseModel):
  room_code: str
  player_id: str
  timestamp: int

@router.post('/check-in')
async def checkIn(body: PlayerCheckIn):
  player_id = body.player_id
  logging.info(f'Check in at {body.timestamp}')

  def ci(game_room: GameRoom):
    content = dict()
    boggle_game = game_room.game
    player = boggle_game.players[player_id]
    player.withinTime(body.timestamp)
    game_ended = boggle_game.checkGameEnded()
    content['ended'] = game_ended
    return content
  
  content = room_storage.getAndSet(body.room_code, roomExists, ci)
  print(content)
  return content


class RoomData(BaseModel):
  room_code: str

@router.post('/check-ended')
async def checkEnded(body: RoomData):

  def ce(game_room: GameRoom):
    content = dict()
    boggle_game = game_room.game
    game_ended = boggle_game.checkGameEnded()
    content['ended'] = game_ended
    return content
  
  content = room_storage.getAndSet(body.room_code, roomExists, ce)
  return content

# TODO: Update with results
@router.post('/get-results')
async def getResults(body: RoomData):
  boggle_game = room_storage.get(body.room_code).game
  content = dict()
  return content

