import logging
from logging.handlers import QueueHandler, QueueListener
import sys
import os
import queue
from queue import Queue
from contextlib import asynccontextmanager

# Import general dependencies
from dotenv import dotenv_values
from box import Box

# Import FastAPI and dependencies
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import local dependencies
import routers # noqa: F401

# using box for dot notation because I'm lazy
config: Box = Box({
    **dotenv_values("../.env.local"),  # load shared development variables
    **dotenv_values("../.env.secret"),  # load sensitive variables
    **os.environ,  # override loaded values with environment variables
})

# Logging config - we don't want to block io for logs

# extracted from the logging cookbook, mostly
# https://docs.python.org/3/howto/logging-cookbook.html

que: Queue[int] = queue.Queue(-1)
queue_handler: QueueHandler = logging.handlers.QueueHandler(que) # type: ignore
listener: QueueListener = logging.handlers.QueueListener(que, logging.StreamHandler())  # type: ignore
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(queue_handler) # type: ignore


origins: list[str] = []
# default to development environment
environment: str = config.get("ENVIRONMENT", "development") # type: ignore

if environment != "production":
    origins = [
        "http://localhost",
        "http://localhost:8000",
        "https://localhost:5443",
        "http://localhost:8080",
        "http://localhost:8081"
        ]
else:
    origins = [
        # include list of production origins
    ]

# uncomment below for JWT authorization
#authorizer: Authorizer = Authorizer(
#    public_key=pathlib.Path("../secrets/public.pem"),
#    private_key=pathlib.Path("../secrets/private.pem"),
#    default_claims={"iss": config.JWT_ISSUER, "aud": config.JWT_AUDIENCE})

@asynccontextmanager
async def lifespan(app: FastAPI):
    listener.start()
    try:
        # uncomment for access to JWT authorization
        # app.state.authorizer = authorizer
        app.state.app_name = config.get("APP_NAME", "FastAPI Skeleton") # type: ignore
        yield
    except Exception:
        logger.exception()
        sys.exit(1)
    finally:
        listener.stop()

# Create FastAPI app with token authentication dependency
app: FastAPI = FastAPI(lifespan=lifespan, debug=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bypass rules for token authentication
# rule format: (method, path) (tuple)
#bypass_rules = [("POST","/contact"),("GET","/contact/all"),("GET","/status")]

# Add token and authnz middleware
# uncomment for token/psk enforcement
# app.add_middleware(TokenMiddleware, bypass=bypass_rules)
# uncomment for authorization middleware to set up for validation in routes
# app.add_middleware(AuthNZMiddleware)

@app.get("/")
async def root():
    return {"message": "OK"}

# ensure routers are included
# app.include_router(routers.xxx.router)
