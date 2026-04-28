from fastapi import APIRouter

from app.models import Recipe
from app.services import RecipeServiceDep

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.post("/suggest_tags")
async def suggest_tags(recipe: Recipe, recipe_service: RecipeServiceDep):
    result = await recipe_service.suggest_tags(recipe)
    return result

@router.post("/suggest_substitutions")
async def suggest_substitutions(recipe: Recipe, ingredient_name: str, recipe_service: RecipeServiceDep):
    result = await recipe_service.suggest_substitutions(recipe, ingredient_name)
    return result