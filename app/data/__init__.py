# Data package for SQLModel models
from fastapi import Depends
import os
from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated, Generator

from .family_member import FamilyMember
from .family import Family
from .ingredient import Ingredient
from .recipe import Recipe
from .instruction import Instruction
from .recipe_ingredient import RecipeIngredient
from .tag import Tag
from .recipe_tag import RecipeTag


engine = create_engine(os.environ.get("DATABASE_URL"))


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

__all__ = [
    "init_db",
    "get_session",
    "SessionDep",
    "FamilyMember",
    "Family",
    "Ingredient",
    "Recipe",
    "Instruction",
    "RecipeIngredient",
    "Tag",
    "RecipeTag",
]
