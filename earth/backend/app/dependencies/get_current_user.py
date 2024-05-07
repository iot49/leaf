from fastapi import HTTPException
from fastapi.requests import HTTPConnection
from sqlmodel import select

from ..api.user.model import User
from ..db import SessionLocal


async def get_current_user(request: HTTPConnection):
    """
    Lookup user in the database.

    Args:
        email (str | None): The email address of the user to lookup. Default: request.stat.user_email.

    Returns (User): The user object, also assigned to request.state.user.
    """
    # check if we already retrieved it
    try:
        user = request.state.user
        if user is not None:
            return user
    except AttributeError:
        pass

    # get the user email (set by verify_cloudflare_token)
    try:
        email = request.state.user_email
    except AttributeError:
        raise HTTPException(status_code=400, detail="Not authenticated.")

    # lookup user in the database or create if not found
    async with SessionLocal() as session:
        user = await session.execute(select(User).where(User.email == email))
        user = user.scalars().first()
        if user is None:
            # user does not exist - create
            # guest permission: edit user profile, view trees and branches but no connection to websockets
            user = User(email=email, roles=["guest"])
            session.add(user)
            await session.commit()
            await session.refresh(user)
        request.state.user = user
        return user
