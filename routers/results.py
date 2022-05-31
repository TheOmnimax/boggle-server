from fastapi import APIRouter
from .helpers import send_headers, room_storage, roomExists
from .playing import RoomData

router = APIRouter()

# TODO: Update with results
@router.post('/get-results')
async def getResults(body: RoomData):
  boggle_game = room_storage.get(body.room_code).game
  content = dict()
  return boggle_game.getScores()