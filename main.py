import logging
from google.cloud import storage
from game import room
from game.room import GameRoom
import google.cloud.logging
# import google.oauth2.id_token
from game.boggle import BoggleGame, BogglePlayer
import random
import string
import threading

from os.path import dirname, join, realpath

from fastapi import FastAPI, Header, Response, Request
from fastapi.responses import JSONResponse
# from pydantic import BaseModel
import json

logging.getLogger().addHandler(logging.StreamHandler()) # For testing

client = google.cloud.logging.Client()
client.setup_logging()

app = FastAPI()
code_chars = string.ascii_lowercase + string.digits

send_headers = {
  'Access-Control-Allow-Origin': '*'
  }

# @app.middleware('http')
# async def mw(request: Request, call_next):
#   return await call_next(request)


# TODO: Set up concurrency through locks
class MemoryStorage:
  def __init__(self):
    self.lock = threading.Lock()
    self.data = dict()

  def set(self, room_code, boggle_game):
    self.lock.acquire()
    try:
      self.data[room_code] = json.dumps(boggle_game)
    finally:
      self.lock.release()

  def get(self, room_code):
     return json.loads(self.data[room_code])

  def getAndSet(self, room_code, bool_func, new_val_func):
    self.lock.acquire()
    try:
      data = json.loads(self.data[room_code])
      if (bool_func(data)):
        self.data[room_code] = json.dumps(new_val_func(data))
    finally:
      self.lock.release()


room_storage = MemoryStorage()

# Takes a room code, generates a new player ID, and adds that player to the room and the game. Returns the player ID, so the player can use that to send new commands
def addPlayer(room_code: str):
  global room_storage
  game_room = room_storage.data[room_code]
  player_id = ''.join(random.choice(code_chars) for i in range(8))
  game_room.addPlayer(player_id)
  return player_id

def genCode(length: int):
  return ''.join(random.choice(code_chars) for i in range(length))

def getGame(room_code: str):
  game_room = room_storage.data[room_code]
  return game_room.game

@app.get('/')
async def test(request: Request):
  return 'Welcome!'

@app.get('/test')
async def test(request: Request):
  return 'Success!'

# Creates a new game, sends back the room code
@app.post('/create-room')
async def createRoom(request: Request):
  global room_storage
  print('Creating room...')
  headers = request.headers
  # logging.info('Headers:')
  # logging.info(str(headers))
  room_code = ''.join(random.choice(code_chars) for i in range(6))
  room_storage.data[room_code] = GameRoom(room_code)
  response = JSONResponse(
    {
    'room_code': room_code,
    },
    headers=send_headers
    )
  response.status_code = 200
  return response

# Parameters for the game, so the blank board can be generated
def getGameParameters(boggle_game: BoggleGame):
  return {
      'height': boggle_game.width,
      'width': boggle_game.height,
      'time': 90
  }


# Receives the room code, creates a new boggle game. Sends back the game parameters to create a blank board, as well as the player ID
@app.post('/create-game')
async def createGame(request: Request):
  global room_storage
  headers = request.headers
  room_code = headers['room_code']
  width = int(headers['width'])
  height = int(headers['height'])
  boggle_game = BoggleGame(width=width, height=height)
  game_room = room_storage.data[room_code]
  game_room.addGame(boggle_game)
  current_folder = dirname(realpath(__file__))
  with open(join(current_folder, 'data', 'word_list.txt')) as f:
    word_data = f.read()
    boggle_game.genGame(word_data)
  
  player_id = genCode(6)
  host_data = BogglePlayer(player_id)
  game_room.addPlayer(host_data, True)
  
  content = getGameParameters(boggle_game)
  content['player_id'] = player_id

  response = JSONResponse(
    content,
    headers=send_headers
    )
  return response


# TODO: QUESTION: In JSON, is it better to use underscores, or camel case
# For guests, not hosts Receives the room code, generates anew player ID, adds that player ID to the room and the game. Sends back the player ID, as well as the game parameters for the game to create tehe blank board 
@app.post('/join-game')
async def getGame(request: Request):
  global room_storage
  boggle_game = getGame(room_code)
  headers = request.headers
  room_code = headers['room_code']
  player_id = addPlayer(room_code)
  content = getGameParameters(boggle_game)
  content['player_id'] = player_id
  response = JSONResponse(
    content,
    headers=send_headers
    )
  response.status_code = 200
  return response

# Currently not used
@app.post('/get-game-parameters')
async def getPar(request: Request):
  global room_storage
  headers = request.headers
  room_code = headers['room_code']
  boggle_game = getGame(room_code)
  content = getGameParameters(boggle_game)
  response = JSONResponse(
    content,
    headers=send_headers
    )
  response.status_code = 200
  return response

# Sent by the host to start the game
@app.post('/start-game')
async def startGame(request: Request):
  global room_storage
  headers = request.headers
  room_code = headers['room_code']
  player_id = headers['player_id']
  game_room = room_storage.data['room_code']
  # boggle_game = getGame(room_code)
  # player_data = game_room[player_id]
  host_id = game_room.host_id

  if (player_id == host_id):
    game_room.startGame(host_id)
    response = JSONResponse(
      {
        'result': 'Game started',
      },
      headers=send_headers
    )
    response.status_code = 201
  else:
    response = JSONResponse(
      {

      },
      headers=send_headers
    )
    response.status_code = 403

  return response

@app.post('/is-started')
async def isStarted(request: Request):
  global room_storage
  headers = request.headers
  room_code = headers['room_code']
  game_room = room_storage.data[room_code]
  game_running = game_room.game.running

  response = JSONResponse(
    {
    'running': game_running,
    },
    headers=send_headers
    )
  
  return response



@app.post('/add-word')
async def addWord(request: Request):
  global room_storage
  headers = request.headers
  room_code = headers['room_code']
  player_id = headers['player_id']
  boggle_game = getGame(room_code)
  word = headers['word']
  add_result = boggle_game.enteredWord(player_id, word)
  content = boggle_game.getPlayerWords(player_id)
  response = JSONResponse(
    content,
    headers=send_headers
  )
  response.status_code = 201
  return response

# TODO: QUESTION: Is it better to have a post request, or have the game code in the URL?
@app.post('/get-results')
async def getResults(request: Request):
  global room_storage
  headers = request.headers
  room_code = headers['room_code']
  boggle_game = getGame(room_code)
  response = JSONResponse({},
    headers=send_headers)
  return response


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
