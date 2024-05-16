from fastapi import FastAPI
from langserve import add_routes
import os
from fastapi.middleware.cors import CORSMiddleware

from sunholo.utils import load_config
from sunholo.logging import setup_logging
from sunholo.langfuse.callback import add_langfuse_tracing

from eduvac import chain as eduvac_chain

log = setup_logging("one_generic_app")

config, filename = load_config('config/cloud_run_urls.json')

origin = config.get('webapp', None)

if origin is None:
    log.warning('Could not find reactapp URL in config for origin, setting to *')
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
add_routes(app, eduvac_chain, path="/eduvac",
           config_keys=["configurable"],
           per_req_config_modifier=add_langfuse_tracing)

if __name__ == "__main__":
    import uvicorn
    import os

    uvicorn.run(app, port=int(os.environ.get("PORT", 8080)), host="0.0.0.0")
