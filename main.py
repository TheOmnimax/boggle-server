from os import environ
environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:\\Users\\maxshaberman\\Documents\\Coding\\Keys\\boggle-663ae-0633a194a5f2.json' # TESTING ONLY

import logging
logging.getLogger().addHandler(logging.StreamHandler()) # For testing

import google.cloud.logging
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, APIRouter
from routers import creation, preparation, playing, results, test

client = google.cloud.logging.Client()
client.setup_logging()

app = FastAPI()

router = APIRouter()

origins = [
    'http://localhost',
    'http://localhost:8080',
    'http://localhost:65227',
    'https://localhost:65227',
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

app.include_router(creation.router)
app.include_router(preparation.router)
app.include_router(playing.router)
app.include_router(results.router)
app.include_router(test.router)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
