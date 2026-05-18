# Data package for SQLModel models
import os
from typing import Annotated, Generator

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .family import Family
from .family_member import FamilyMember
from .ingredient import Ingredient
from .instruction import Instruction
from .recipe import Recipe
from .recipe_ingredient import RecipeIngredient
from .recipe_part_group import RecipePartGroup
from .recipe_tag import RecipeTag
from .tag import Tag

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
    "RecipePartGroup",
    "Instruction",
    "RecipeIngredient",
    "Tag",
    "RecipeTag",
]
