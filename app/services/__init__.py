from fastapi import Depends
from typing import Annotated

from .family_service import FamilyService
from .recipe_service import RecipeService
from .exceptions import (
    NoFamilyException,
    DuplicateException,
    UnauthorizedException,
    NotFoundException,
)

FamilyServiceDep = Annotated[FamilyService, Depends(FamilyService)]
RecipeServiceDep = Annotated[RecipeService, Depends(RecipeService)]

__all__ = [
    "FamilyServiceDep",
    "RecipeServiceDep",
    "NoFamilyException",
    "DuplicateException",
    "UnauthorizedException",
    "NotFoundException",
]
