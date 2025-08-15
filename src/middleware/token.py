import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi.exceptions import HTTPException
from fastapi import Request, Response, FastAPI

logger = logging.getLogger(__name__)

class TokenMiddleware(BaseHTTPMiddleware):

    slots = ('app', 'header_name', 'bypass_rules')

    def __init__(self, app: FastAPI, header_name: str = 'Authorization',
                 bypass: list[tuple[str,str]] = []):
        self.app = app
        self.header_name = header_name
        self.bypass_rules = bypass
        super().__init__(app)

    async def _get_token(self, request: Request) -> str:
        """
        Retrieve the token from the request headers.
        """
        token_text: str | None = request.headers.get(self.header_name, None)
        if not token_text:
            logger.error(f"Token not found in request headers: {self.header_name}")
            raise HTTPException(status_code=401, detail="Authorization token not found")
        else:
            logger.debug(f"Token found in request headers: {self.header_name}")
            if not token_text.startswith("Bearer "):
                logger.error(f"Token does not start with 'Bearer ': {token_text}")
                raise HTTPException(status_code=401, detail="Authorization token not found")

        return token_text.split()[1].strip()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token: str = request.app.state.token
        logger.debug(f"Token from header: {self.header_name}")
        if not request.headers.get(self.header_name) or request.headers.get(self.header_name) != token:
            logging.error(f'Correct API key not supplied ({token})')
            raise HTTPException(status_code=401, detail={"unauthorized": "Authorization token not found"})
        response = await call_next(request)
        return response

