from fastapi import FastAPI
from langserve import add_routes
import logging, os
from fastapi.middleware.cors import CORSMiddleware

from sunholo.utils import load_config

logging.basicConfig(level=logging.INFO)
logging.info(f"langserve app started with port: {int(os.environ.get('PORT', 8080))}")

from pirate_speak.chain import chain as pirate_speak_chain
from csv_agent import agent_executor as csv_agent_chain
from rag_lance import chain as rag_lance_chain
from image_talk import chain as image_talk_chain

config, filename = load_config('config/cloud_run_urls.json')

origin = config.get('webapp', None)

if origin is None:
    logging.warning('Could not find reactapp URL in config for origin, setting to *')
    origin = '*'

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin], 
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# the path marries up to the {vector_name} e.g. vector_name=pirate_speak
add_routes(app, pirate_speak_chain, path="/pirate_speak")

add_routes(app, csv_agent_chain, path="/csv_agent")

add_routes(app, rag_lance_chain, path="/rag_lance")

add_routes(app, image_talk_chain, path="/image_talk")

if __name__ == "__main__":
    import uvicorn
    import os

    uvicorn.run(app, port=int(os.environ.get("PORT", 8080)), host="0.0.0.0")
