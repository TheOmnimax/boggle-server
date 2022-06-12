import logging
logging.getLogger().addHandler(logging.StreamHandler()) # For testing

from os import environ

# environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\boggle-347503-b3513065ff13.json' # TESTING ONLY

import google.cloud.logging
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Request, APIRouter
from routers import creation, preparation, playing, results, test

# TODO: Set up memory to work with datastore, test with emulator
# TODO: Find memory leaks

client = google.cloud.logging.Client()
client.setup_logging()

app = FastAPI()

router = APIRouter()

origins = [
    'http://localhost',
    'http://localhost:8080',
    'http://localhost:61508',
    'https://localhost:61508',
    'https://boggle-663ae.web.app',
    'http://boggle-663ae.web.app',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.middleware('http')
# async def mw(request: Request, call_next):
#   logging.info('In middleware')
#   getHeapSize('Middleware')
#   return await call_next(request)


app.include_router(creation.router)

app.include_router(preparation.router)
app.include_router(playing.router)
app.include_router(results.router)
app.include_router(test.router)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
