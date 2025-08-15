import logging
import json
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response
from fastapi import FastAPI


logger = logging.getLogger(__name__)

class AuthNZMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, authorizer: object):
        self.app = app
        # Authorizer should be an instance of a class that has a verify method
        # verify should return a dict
        self.auth = authorizer
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logging.debug("Running AuthNZMiddleware")
        try:
            request.state.user_auth: dict[str, str | int] = await self.auth.verify(request.cookies.get("X-Authorization"), {}) # type: ignore
            privileges: dict[str, str|int] = json.loads(request.state.user_auth.get("privileges", {})) # type: ignore
            if privileges:
                request.state.admin = privileges.get("admin")
        except Exception:
            logging.exception("AuthNZ error")
            request.state.user_auth = None
            request.state.admin = False

        logging.debug("User Auth: %s", request.state.user_auth) # type: ignore
        response = await call_next(request)
        return response
