from fastapi import APIRouter, Depends, HTTPException
from pydantic_ai import ModelHTTPError

from app.auth import auth
from app.models import RecipeDTO, SuggestionDTO
from app.services import NoFamilyException, NotFoundException, RecipeServiceDep

router = APIRouter(
    prefix="/recipes", dependencies=[Depends(auth.implicit_scheme)], tags=["recipes"]
)


@router.post("/")
async def create_recipe(recipe: RecipeDTO, recipe_service: RecipeServiceDep):
    try:
        result = await recipe_service.create_recipe(recipe)
        return result
    except NoFamilyException as e:
        raise HTTPException(status_code=403, detail=e.message)


@router.get("/{recipe_id}")
async def get_recipe(recipe_id: int, recipe_service: RecipeServiceDep):
    result = await recipe_service.get_recipe(recipe_id)
    return result


@router.post("/{recipe_id}/suggested_tags", response_model=list[SuggestionDTO])
async def suggest_tags(recipe_id: int, recipe_service: RecipeServiceDep):
    try:
        result = await recipe_service.suggest_tags(recipe_id)
        return result
    except ModelHTTPError:
        raise HTTPException(
            status_code=503, detail="Tag suggestion service is unavailable."
        )


@router.post("/{recipe_id}/suggested_substitutions", response_model=list[SuggestionDTO])
async def suggest_substitutions(
    recipe_id: int, ingredient_id: int, recipe_service: RecipeServiceDep
):
    try:
        result = await recipe_service.suggest_substitutions(recipe_id, ingredient_id)
        return result
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ModelHTTPError:
        raise HTTPException(
            status_code=503,
            detail="Substitution suggestion service is temporarily unavailable.",
        )
