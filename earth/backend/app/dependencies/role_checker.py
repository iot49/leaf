from fastapi import Depends, HTTPException, status

from ..api.user.model import User
from .get_current_user import get_current_user


class RoleChecker:
    def __init__(self, required_roles: list[str]) -> None:
        self.required_roles = required_roles

    def __call__(self, user: User = Depends(get_current_user)) -> bool:
        for role in self.required_roles:
            if role not in user.roles:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized (roles)")
        return True
