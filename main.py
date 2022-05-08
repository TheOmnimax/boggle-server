import logging
# from google.cloud import storage
# from game import room
from game.room import GameRoom
import google.cloud.logging
# import google.oauth2.id_token
from game.boggle import BoggleGame, BogglePlayer, WordReason
from tools.json_tools import JsonConverter
from tools.randomization import genCode
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
    self.json_converter = JsonConverter()

  def set(self, game_room: GameRoom):
    self.lock.acquire()
    try:
      room_code = game_room.room_code
      self.data[room_code] = json.dumps(self.json_converter.objToJson(game_room))
    except:
      pass
    finally:
      self.lock.release()
        
  def get(self, room_code) -> GameRoom:
    """Given a game code, returns a game room

    Args:
        room_code (str): Game code

    Returns:
        GameRoom: Game room with that code
    """
    for key in self.data:
      print(key)
    try:
      return self.json_converter.jsonToObj(json.loads(self.data[room_code]))
    except:
      exit()
  def getAndSet(self, room_code, predicate=None, new_val_func=None):
    self.lock.acquire()
    try:
      if (predicate == None) or (predicate(room_code)):
        logging.info('Python log: About to get game room...')
        game_room = self.get(room_code)
        logging.info('Python log: Game room retrieved!')
        if new_val_func == None:
          return 'No action given'
        else:
          logging.info('Python log: Applying function...')
          data = new_val_func(game_room)
          logging.info('Python log: About to dump data...')
          self.data[room_code] = json.dumps(self.json_converter.objToJson(game_room))
          logging.info('Python log: Dump complete')
          return data
      else:
        print(f'Game room {room_code} not found')
        return 'Game room not found'
    except:
      pass
    finally:
      self.lock.release()

room_storage = MemoryStorage()

def roomExists(room_code):
  global room_storage
  try:
    game_room = room_storage.get(room_code)
  except:
    return False
  return True

def checkIfHost():
  pass

async def getBody(request: Request) -> dict:  
  body_raw = b''
  async for chunk in request.stream():
      body_raw += chunk

  print(body_raw)
  body = json.loads(body_raw)
  return body


# Takes a room code, generates a new player ID, and adds that player to the room and the game. Returns the player ID, so the player can use that to send new commands
# def addPlayer(room_code: str):
#   global room_storage
#   game_room = room_storage.data[room_code]
#   player_id = ''.join(random.choice(code_chars) for i in range(8))
#   new_player = BogglePlayer(player_id)
#   game_room.addPlayer(new_player)
#   return player_id



# def getGame(room_code: str):
#   game_room = room_storage.data[room_code]
#   return game_room.game

@app.middleware('http')
async def mw(request: Request, call_next):
  logging.info('In middleware')
  return await call_next(request)

@app.get('/')
async def test(request: Request):
  return 'Welcome!'

@app.get('/test')
async def test(request: Request):
  return 'Success!'

# Creates a new game, sends back the room code
@app.post('/create-room')
async def createRoom(request: Request):
  logging.info('About to get room storage...')
  global room_storage
  logging.info('Creating room...')
  headers = request.headers
  logging.info('Headers:')
  for header in headers:
    logging.info(header)

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
  logging.info('Python log: Preparing to create game...')
  global room_storage
  logging.info('Python log: Got global var')
  headers = request.headers

  body = await getBody(request)

  # for item in body:
  #   logging.info(f'Header: {item}')
  room_code = body['room_code']
  width = int(body['width'])
  height = int(body['height'])
  time = int(body['time'])
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
  return response

# For guests, not hosts Receives the room code, generates anew player ID, adds that player ID to the room and the game. Sends back the player ID, as well as the game parameters for the game to create tehe blank board 
@app.post('/join-game')
async def joinGame(request: Request):
  global room_storage
  headers = request.headers
  body = await getBody(request)
  room_code = body['room_code']
  host_id = body['host_id']

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

# Currently not used
# @app.post('/get-game-parameters')
# async def getPar(request: Request):
#   global room_storage
#   headers = request.headers
#   room_code = headers['room_code']
#   boggle_game = getGame(room_code)
#   content = getGameParameters(boggle_game)
#   response = JSONResponse(
#     content,
#     headers=send_headers
#     )
#   response.status_code = 200
#   return response

# Sent by the host to start the game
@app.post('/start-game')
async def startGame(request: Request):
  global room_storage
  headers = request.headers
  body = await getBody(request)
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

@app.post('/is-started')
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

# Stores the timestamp of when the player started the game. This is used to determine when they are no longer allowed to submit words because time ran out, while accounting for slower internet
@app.post('/player-start')
async def playerStart(request: Request):
  global room_storage
  headers = request.headers
  body = await getBody(request)
  room_code = body['room_code']
  player_id = body['player_id']
  timestamp = int(body['timestamp'])

  def ps(game_room: GameRoom):
    player = game_room.players[player_id] # Return BogglePlayer
    player.playerStarted(timestamp)
    pass

  room_storage.getAndSet(room_code, roomExists, ps)


@app.post('/add-word')
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

@app.post('/get-results')
async def getResults(request: Request):
  global room_storage
  body = await getBody(request)
  headers = request.headers
  room_code = headers['room_code']
  # boggle_game = getGame(room_code)
  response = JSONResponse({},
    headers=send_headers)
  return response


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
