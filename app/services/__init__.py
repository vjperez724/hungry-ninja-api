from fastapi import Depends
from typing import Annotated

from .family_service import FamilyService
from .recipe_service import RecipeService

FamilyServiceDep = Annotated[FamilyService, Depends(FamilyService)]
RecipeServiceDep = Annotated[RecipeService, Depends(RecipeService)]

__all__ = ["FamilyServiceDep", "RecipeServiceDep"]