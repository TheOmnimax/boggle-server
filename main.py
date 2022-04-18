from turtle import width
from typing import Optional
import logging
# from google.cloud import storage
# import google.cloud.logging
# import google.oauth2.id_token
from game import boggle
import random
import string

from ebooklib import epub

from os.path import dirname, join, realpath
from os import remove, environ

from fastapi import FastAPI, Header, Response, Request
from fastapi.responses import JSONResponse
# from pydantic import BaseModel

app = FastAPI()
code_chars = string.ascii_lowercase + string.digits

boggle_game = boggle.BoggleGame(width=4, height=4)

# @app.middleware('http')
# async def mw(request: Request, call_next):
#   print('Middleware')
#   return await call_next(request)

def addPlayer(game_code: str):
  global boggle_game
  player_id = ''.join(random.choice(code_chars) for i in range(8))
  boggle_game.addPlayer(player_id)
  return player_id

@app.get('/test')
async def test(request: Request):
  return('Success!')

@app.post('/create-room')
async def createRoom(request: Request):
  print('Creating room...')
  headers = request.headers
  game_code = ''.join(random.choice(code_chars) for i in range(6))
  response = JSONResponse({
    'game_code': game_code
    })
  response.status_code = 200
  print(f'Game code: {game_code}')
  return response

@app.post('/create-board')
async def createBoard(request: Request):
  global boggle_game
  headers = request.headers
  game_code = headers['game_code']
  width = int(headers['width'])
  height = int(headers['height'])
  boggle_game = boggle.BoggleGame(width=width, height=height)
  current_folder = dirname(realpath(__file__))
  with open(join(current_folder, 'data', 'word_list.txt')) as f:
    word_data = f.read()
    boggle_game.genGame(word_data)
  
  player_id = addPlayer(game_code)
  response = JSONResponse({
    'board': boggle_game.getBasicBoard(),
    'player_id': player_id
    })
  return response


# TODO: QUESTION: In JSON, is it better to use underscores, or camel case
@app.post('/join-game')
async def getGame(request: Request):
  global boggle_game
  headers = request.headers
  game_code = headers['game_code']
  player_id = addPlayer(game_code)
  response = JSONResponse({
    'board': boggle_game.getBasicBoard(),
    'player_id': player_id
    })
  return response

@app.post('/start-game')
async def startGame(request: Request):
  headers = request.headers
  game_code = headers['game_code']
  response = JSONResponse()
  return response

@app.post('/add-word')
async def addWord(request: Request):
  global boggle_game
  headers = request.headers
  game_code = headers['game_code']
  player_id = headers['player_id']
  word = headers['word']
  add_result = boggle_game.enteredWord(player_id, word)
  content = boggle_game.getPlayerWords(player_id)
  response = JSONResponse(content)
  response.status_code = 200
  return response

# TODO: QUESTION: Is it better to have a post request, or have the game code in the URL?
@app.post('/get-results')
async def getResults(request: Request):
  headers = request.headers
  game_code = headers['game_code']
  response = JSONResponse()
  return response


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)