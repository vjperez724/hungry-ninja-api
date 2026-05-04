from fastapi import Depends
from pydantic_ai import Agent
from sqlmodel import select

from app.auth import AuthUserDep
from app.data import (
    Recipe,
    SessionDep,
    RecipePartGroup,
    Instruction,
    Ingredient,
    RecipeIngredient,
)
from app.models import RecipeDTO, SuggestionDTO, IngredientDTO
from app.services.exceptions import NoFamilyException, UnauthorizedException, NotFoundException
from .family_service import FamilyService


class RecipeService:
    tag_suggestion_agent: Agent
    substitution_agent: Agent

    def __init__(
        self,
        user: AuthUserDep,
        session: SessionDep,
        family_service: FamilyService = Depends(FamilyService),
    ):
        self.tag_suggestion_agent = Agent(
            "google-gla:gemini-3.1-flash-lite-preview",
            system_prompt=(
                "Suggest tags for recipes."
                "Return a list of relevant tags based on the recipe's name, ingredients, and instructions."
                "Limit tags to a maximum of 5, and ensure they are concise and relevant to the recipe."
                "Give reasons for each tag suggestion, such as key ingredients or cooking techniques that justify the tag."
            ),
            output_type=list[SuggestionDTO],
        )
        self.substitution_agent = Agent(
            "google-gla:gemini-3.1-flash-lite-preview",
            system_prompt=(
                "Suggest ingredient substitutions for recipes."
                "Given a recipe and an ingredient name, return a list of suitable substitutions for that ingredient."
                "Consider the flavor profile, texture, and cooking properties of the original ingredient when suggesting substitutions."
                "Limit substitutions to a maximum of 5, and ensure they are relevant to the recipe."
            ),
            output_type=list[SuggestionDTO],
        )
        self.family_service = family_service
        self.session = session
        self.user = user

    async def create_recipe(self, new_recipe: RecipeDTO) -> RecipeDTO:
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
        group_names = set(new_recipe.ingredients.keys()) | set(
            new_recipe.instructions.keys()
        )
        groups = {}
        for group_name in group_names:
            group = RecipePartGroup(
                name=group_name, created_by=self.user.id, recipe_id=recipe.id
            )
            self.session.add(group)
            self.session.flush()
            self.session.refresh(group)
            groups[group_name] = group.id

        # Create instructions
        recipe_instructions = {}
        for group_name, instructions in new_recipe.instructions.items():
            recipe_instructions[group_name] = []
            for i, instruction in enumerate(instructions):
                inst = Instruction(
                    order=i,
                    created_by=self.user.id,
                    description=instruction,
                    group_id=groups.get(group_name),
                )
                self.session.add(inst)
                self.session.flush()
                self.session.refresh(inst)
                recipe_instructions[group_name].append(inst.description)

        # Save ingredients
        recipe_ingredients = {}
        for group_name, ingredients in new_recipe.ingredients.items():
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
                    group_id=groups.get(group_name),
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
        recipe = self.session.get(Recipe, recipe_id)
        if recipe.family_id != family.id:
            raise UnauthorizedException("User does not have access to this recipe")
        if not recipe:
            raise NotFoundException("Recipe not found")

        # Get groups
        groups = self.session.exec(
            select(RecipePartGroup).where(RecipePartGroup.recipe_id == recipe.id)
        ).all()
        group_map = {group.id: group.name for group in groups}

        # Get instructions
        instructions = self.session.exec(
            select(Instruction).where(Instruction.group_id.in_(group_map.keys()))
        ).all()
        instruction_map: dict[str, list[str]] = {}
        for instruction in instructions:
            group_name = group_map.get(instruction.group_id, "Default")
            instruction_map.setdefault(group_name, []).append(instruction.description)

        # Get ingredients
        recipe_ingredients = self.session.exec(
            select(RecipeIngredient).where(
                RecipeIngredient.group_id.in_(group_map.keys())
            )
        ).all()
        ingredient_map: dict[str, list[IngredientDTO]] = {}
        for recipe_ingredient in recipe_ingredients:
            group_name = group_map.get(recipe_ingredient.group_id, "Default")
            ingredient = self.session.get(Ingredient, recipe_ingredient.ingredient_id)
            ingredient_map.setdefault(group_name, []).append(
                IngredientDTO(
                    id=ingredient.id,
                    name=ingredient.name,
                    amount=recipe_ingredient.amount,
                    unit=recipe_ingredient.unit,
                )
            )

        return RecipeDTO(
            id=recipe.id,
            name=recipe.name,
            ingredients=ingredient_map,
            instructions=instruction_map,
        )

    async def suggest_tags(self, recipe_id: int) -> list[SuggestionDTO]:
        recipe = await self.get_recipe(recipe_id)
        prompt = f"Suggest tags for the following recipe: {recipe}"
        result = await self.tag_suggestion_agent.run(prompt)
        return result.output

    async def suggest_substitutions(
        self, recipe_id: int, ingredient_id: int
    ) -> list[SuggestionDTO]:
        recipe = await self.get_recipe(recipe_id)
        ingredient = self.session.get(Ingredient, ingredient_id)
        if ingredient is None:
            raise NotFoundException("Ingredient not found")
        if recipe.ingredients is None:
            raise NotFoundException("Recipe has no ingredients")            
        ingredient_ids = [ing.id for group in recipe.ingredients for ing in recipe.ingredients[group]]
        if ingredient_id not in ingredient_ids:
            raise NotFoundException(f"Ingredient {ingredient.name} is not part of the recipe")
        prompt = f"Suggest substitutions for {ingredient.name} in the following recipe, which is in JSON format: {recipe}"
        result = await self.substitution_agent.run(prompt)
        return result.output
