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
