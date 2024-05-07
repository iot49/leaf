from fastapi.encoders import jsonable_encoder
from sqlmodel import SQLModel


def print_model(text: str = "", model: SQLModel | list = []):
    """
    It prints sqlmodel responses for complex relationship models.
    """
    return print(text, jsonable_encoder(model))
