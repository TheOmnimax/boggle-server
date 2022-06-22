from fastapi import APIRouter
from .helpers import room_storage
from .playing import RoomData

router = APIRouter()

# TODO: Update with results
@router.post('/get-results')
async def getResults(body: RoomData):
  boggle_game = room_storage.get(body.room_code).game
  content = boggle_game.getScores()
  return content