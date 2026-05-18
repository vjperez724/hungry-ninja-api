from app.data import Recipe
from app.models import IngredientDTO, RecipeDTO


def to_recipe_dto(recipe: Recipe) -> RecipeDTO:
    ingredients_map: dict[str, list[IngredientDTO]] = {}
    instructions_map: dict[str, list[str]] = {}

    for group in recipe.recipe_part_groups:
        # Map ingredients
        if group.recipe_ingredients:
            ingredients_map[group.name] = [
                IngredientDTO(
                    id=recipe_ingredient.ingredient.id,
                    name=recipe_ingredient.ingredient.name,
                    amount=recipe_ingredient.amount,
                    unit=recipe_ingredient.unit,
                )
                for recipe_ingredient in group.recipe_ingredients
            ]

        # Map instructions
        if group.instructions:
            instructions_map[group.name] = [
                instruction.description for instruction in group.instructions
            ]

    return RecipeDTO(
        id=recipe.id,
        name=recipe.name,
        ingredients=ingredients_map,
        instructions=instructions_map,
    )
