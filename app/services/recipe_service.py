from fastapi import Depends
from pydantic_ai import Agent, Tool
from sqlalchemy.orm import joinedload
from sqlmodel import select

from app.auth import AuthUserDep
from app.data import (
    Ingredient,
    Instruction,
    Recipe,
    RecipeIngredient,
    RecipePartGroup,
    SessionDep,
)
from app.mapping import to_recipe_dto
from app.models import IngredientDTO, RecipeDTO, SuggestionDTO
from app.services.exceptions import (
    NoFamilyException,
    NotFoundException,
    UnauthorizedException,
)

from .family_service import FamilyService


def _get_recipe_options():
    """Build joinedload options for Recipe query."""
    return [
        joinedload(Recipe.recipe_part_groups).joinedload(RecipePartGroup.instructions),  # type: ignore
        joinedload(Recipe.recipe_part_groups)  # type: ignore
        .joinedload(RecipePartGroup.recipe_ingredients)  # type: ignore
        .joinedload(RecipeIngredient.ingredient),  # type: ignore
    ]


class RecipeService:
    tag_suggestion_agent: Agent[None, list[SuggestionDTO]]
    substitution_agent: Agent[None, list[SuggestionDTO]]

    def __init__(
        self,
        user: AuthUserDep,
        session: SessionDep,
        family_service: FamilyService = Depends(FamilyService),
    ):
        self.tag_suggestion_agent = Agent(
            "google-gla:gemini-3.1-flash-lite-preview",
            system_prompt=(
                "You are a helpful cooking assistant."
                "Return a list of relevant tags based on included recipe's name, ingredients, and instructions."
                "Limit tags to a maximum of 5, and ensure they are concise and relevant to the recipe.  You do not have to return all 5 tags."
                "Give reasons for each tag suggestion, such as key ingredients or cooking techniques that justify the tag."
                "Avoid returning similar tags, such as both 'quick and easy' and 'simple'."
                "Avoid possibly controversial tags, such as using vegetarian on eggs."
            ),
            output_type=list[SuggestionDTO],
            tools=[Tool(self.get_recipe, takes_ctx=False)],
        )
        self.substitution_agent = Agent(
            "google-gla:gemini-3.1-flash-lite-preview",
            system_prompt=(
                "Suggest ingredient substitutions for recipes."
                "Given a recipe and an ingredient name, return a list of suitable substitutions for that ingredient."
                "Consider the flavor profile, texture, and cooking properties of the original ingredient when suggesting substitutions."
                "Limit substitutions to a maximum of 5, and ensure they are relevant to the recipe.  You do not have to return all 5 suggestions."
                "If a substitution is requested for an ingredient that is not a part of the recipe's ingredients, return an empty list."
            ),
            output_type=list[SuggestionDTO],
            tools=[Tool(self.get_recipe, takes_ctx=False)],
        )
        self.family_service = family_service
        self.session = session
        self.user = user

    async def create_recipe(self, new_recipe: RecipeDTO) -> RecipeDTO:
        # This needs improvement
        # Get family for user
        family = await self.family_service.get_family_by_auth_id()
        if not family:
            raise NoFamilyException("User must be part of a family to create a recipe")

        # Create Recipe
        recipe = Recipe(
            name=new_recipe.name, created_by=self.user.id, family_id=family.id
        )
        self.session.add(recipe)
        self.session.flush()
        self.session.refresh(recipe)

        # Create groups for ingredients and instructions
        group_names = set((new_recipe.ingredients or {}).keys()) | set(
            (new_recipe.instructions or {}).keys()
        )
        groups = {}
        for group_name in group_names:
            group = RecipePartGroup(
                name=group_name,
                created_by=self.user.id,
                recipe_id=recipe.id,  # type: ignore
            )
            self.session.add(group)
            self.session.flush()
            self.session.refresh(group)
            groups[group_name] = group.id

        # Create instructions
        recipe_instructions = {}
        for group_name, instructions in (new_recipe.instructions or {}).items():
            recipe_instructions[group_name] = []
            for i, instruction in enumerate(instructions):
                inst = Instruction(
                    order=i,
                    created_by=self.user.id,
                    description=instruction,
                    group_id=groups[group_name],
                )
                self.session.add(inst)
                self.session.flush()
                self.session.refresh(inst)
                recipe_instructions[group_name].append(inst.description)

        # Save ingredients
        recipe_ingredients = {}
        for group_name, ingredients in (new_recipe.ingredients or {}).items():
            recipe_ingredients[group_name] = []
            for i, ingredient in enumerate(ingredients):
                ing = Ingredient(
                    name=ingredient.name, family_id=family.id, created_by=self.user.id
                )
                self.session.add(ing)
                self.session.flush()
                self.session.refresh(ing)
                recipe_ingredient = RecipeIngredient(
                    order=i,
                    created_by=self.user.id,
                    amount=ingredient.amount,
                    unit=ingredient.unit,
                    group_id=groups[group_name],
                    ingredient_id=ing.id,
                )
                self.session.add(recipe_ingredient)
                self.session.flush()
                self.session.refresh(recipe_ingredient)
                recipe_ingredients[group_name].append(
                    IngredientDTO(
                        id=ing.id,
                        name=ing.name,
                        amount=recipe_ingredient.amount,
                        unit=recipe_ingredient.unit,
                    )
                )

        # Commit everything
        self.session.commit()

        return RecipeDTO(
            id=recipe.id,
            name=recipe.name,
            ingredients=recipe_ingredients,
            instructions=recipe_instructions,
        )

    async def get_recipe(self, recipe_id: int) -> RecipeDTO:
        family = await self.family_service.get_family_by_auth_id()
        if not family:
            raise UnauthorizedException("User does not belong to a family.")

        recipe = self.session.exec(
            select(Recipe)
            .where(Recipe.id == recipe_id and Recipe.family_id == family.id)
            .options(*_get_recipe_options())
        ).first()
        if not recipe:
            raise NotFoundException("Recipe not found")

        recipe_dto = to_recipe_dto(recipe)
        return recipe_dto

    async def suggest_tags(self, recipe_id: int) -> list[SuggestionDTO]:
        result = await self.tag_suggestion_agent.run(
            f"Suggest tags for recipe id: {recipe_id}"
        )
        return result.output

    async def suggest_substitutions(
        self, recipe_id: int, ingredient_id: int
    ) -> list[SuggestionDTO]:
        result = await self.substitution_agent.run(
            f"Suggest substitutions for ingredient id: {ingredient_id} in recipe_id: {recipe_id}"
        )
        return result.output
