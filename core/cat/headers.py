import fnmatch

from typing import Annotated
from cat.log import log

from fastapi import (
    WebSocket,
    Request,
)
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

from cat.looking_glass.stray_cat import StrayCat
from cat.env import get_env


api_key_header = APIKeyHeader(name="access_token", auto_error=False)

def ws_auth(
    websocket: WebSocket,
    ) -> None | str:
    """Authenticate websocket connection.

    Parameters
    ----------
    websocket : WebSocket
        Websocket connection.

    Returns
    -------
    None
        Does not raise an exception if the message is allowed.

    Raises
    ------
    HTTPException
        Error with status code `403` if the message is not allowed. # TODOAUTH: ws has no status code

    """

    # internal auth system for the admin panel
    # TODOAUTH

    # custom auth
    authorizator = websocket.app.state.ccat.authorizator
    if not authorizator.is_ws_allowed(websocket):
        raise HTTPException( # TODOAUTH: ws has no status code?
            status_code=403,
            detail={"error": "Invalid Credentials"}
        )
    
def http_auth(request: Request) -> bool:
    """Authenticate endpoint.

    Check the provided key is available in API keys list.

    Parameters
    ----------
    request : Request
        HTTP request.

    Returns
    -------
    None
        Does not raise an exception if the request is allowed.

    Raises
    ------
    HTTPException
        Error with status code `403` if the request is not allowed.

    """

    # internal auth system for the admin panel
    # TODOAUTH

    authorizator = request.app.state.ccat.authorizator
    if authorizator.is_http_allowed(request):
        return None
    else:
        raise HTTPException(
            status_code=403,
            detail={"error": "Invalid Credentials"}
        )


# get or create session (StrayCat)
def session(request: Request) -> StrayCat:

    strays = request.app.state.strays
    user_id = request.headers.get("user_id", "user")
    event_loop = request.app.state.event_loop
    
    if user_id not in strays.keys():
        strays[user_id] = StrayCat(user_id=user_id, main_loop=event_loop)
    return strays[user_id]