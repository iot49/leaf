from fastapi import APIRouter

router = APIRouter()


@router.get("/new_config")
def update_config():
    return {"msg": "Hello World"}
