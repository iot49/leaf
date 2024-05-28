# https://www.crosstalksolutions.com/cloudflare-tunnel-easy-setup/
# https://developers.cloudflare.com/cloudflare-one/tutorials/fastapi/

import json
import logging

import aiohttp
import jwt
from async_lru import alru_cache
from fastapi import Depends, HTTPException
from fastapi.requests import HTTPConnection
from fastapi.security import APIKeyCookie

from ..env import Environment, env

"""
Checks for CF_Authorization cookie in the request and verifies it with Cloudflare.
If successful, sets request.state.user_email to the email address in the token.

Raises: HTTPException with status 400 if the token is missing or invalid.

Test skipped for config.ENVIRONMENT != config.Environment.production.
"""

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# CF Access team domain
CERTS_URL = "{}/cdn-cgi/access/certs".format(env.CF_TEAM_DOMAIN)

CHECK_USER_DISABLED = False


@alru_cache
async def _get_public_keys():
    """
    Returns:
        List of RSA public keys usable by PyJWT.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(CERTS_URL) as resp:
            jwk_set = await resp.json()
            public_keys = []
            for key_dict in jwk_set["keys"]:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_dict))  # type: ignore
                public_keys.append(public_key)
    return public_keys


cookie_scheme = APIKeyCookie(name="CF_Authorization", auto_error=False, description="Cloudflare Access Token")


async def verify_cloudflare_cookie(request: HTTPConnection, session: str = Depends(cookie_scheme)) -> str:
    """
    Verify the Cloudflare token in the request.
    Set request.state.user_mail to the email address in the token.

    Returns: The email address in the token.
    """
    host = request.url.hostname
    if env.ENVIRONMENT != Environment.production and host in ["localhost", "127.0.0.1", "0.0.0.0"]:
        # Skip verification when running locally
        request.state.user_email = env.FIRST_SUPERUSER_EMAIL
        return env.FIRST_SUPERUSER_EMAIL

    if "CF_Authorization" not in request.cookies:
        logger.debug(f"Missing required Cloudflare cookie; host={host}, env={env.ENVIRONMENT}")
        raise HTTPException(
            status_code=400,
            detail="Missing required Cloudflare authorization token",
        )

    token = request.cookies["CF_Authorization"]
    logger.debug(f"Got CF token '{token}'")
    keys = await _get_public_keys()  # type: ignore

    # Loop through the keys since we can't pass the key set to the decoder
    for key in keys:
        try:
            # decode returns the claims that has the email when needed
            claims = jwt.decode(
                token,
                key=key,
                audience=env.CF_POLICY_AUD,
                algorithms=["RS256"],
            )
            request.state.user_email = claims["email"]
            if CHECK_USER_DISABLED:
                # verify that the user is not disabled in the database
                # TODO: expensive database lookup - cache?
                from .get_current_user import get_current_user

                user = await get_current_user(request)
                if user.disabled:
                    raise HTTPException(status_code=403, detail="Account suspended")
                # we just return the email to keep compatibility with situations where user data is not retrieved
                logger.debug(f"Verified CF token, user = {user.email}")
            return claims["email"]
        except jwt.DecodeError as e:
            logger.debug(f"""Error decoding CF token -> {jwt.decode(
                token,
                key=key,
                audience=env.CF_POLICY_AUD,
                algorithms=["RS256"],
                options={"verify_signature": False},
            )}: {e}""")
            raise HTTPException(status_code=400, detail=f"Error decoding token: {e}")
    raise HTTPException(status_code=400, detail="Invalid Cloudflare token")
