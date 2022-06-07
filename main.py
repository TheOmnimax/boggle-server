from testing.tools import resetHeap, getHeapSize
import logging
logging.getLogger().addHandler(logging.StreamHandler()) # For testing

resetHeap()

from os import environ

environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\ereader-341202-cde00806c15f.json'

import google.cloud.logging
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Request, APIRouter
from routers import creation, preparation, playing, results, test

# TODO: Set up memory to work with datastore, test with emulator
# TODO: Find memory leaks

client = google.cloud.logging.Client()
client.setup_logging()
resetHeap()
getHeapSize('Initial')

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


getHeapSize('Got middleware')

app.include_router(creation.router)

app.include_router(preparation.router)
getHeapSize('Got preparation')
app.include_router(playing.router)
getHeapSize('Got playing')
app.include_router(results.router)
getHeapSize('Got results')
app.include_router(test.router)
getHeapSize('Got test')

getHeapSize('After setup data')

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
