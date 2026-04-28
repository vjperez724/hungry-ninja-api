from typing import Annotated

from fastapi import Depends
from fastapi_auth0 import Auth0, Auth0User
import os

auth = Auth0(domain=os.getenv("AUTH0_DOMAIN"), api_audience=os.getenv("AUTH0_AUDIENCE"))

AuthUserDep = Annotated[Auth0User, Depends(auth.get_user)]

__all__ = ["auth", "AuthUserDep"]