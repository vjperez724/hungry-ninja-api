import os

import logfire
from fastapi import Depends
from pydantic_ai import Agent, RunContext, Tool
from sqlalchemy.orm import joinedload
from sqlmodel import desc, select

from app.auth import AuthUserDep
from app.data import (
    Ingredient,
    Instruction,
    Recipe,
    RecipeIngredient,
    RecipePartGroup,
    SessionDep,
    SuggestedTagHistory,
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
    def __init__(
        self,
        user: AuthUserDep,
        session: SessionDep,
        family_service: FamilyService = Depends(FamilyService),
    ):
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
            .where(Recipe.id == recipe_id, Recipe.family_id == family.id)
            .options(*_get_recipe_options())
        ).first()
        if not recipe:
            raise NotFoundException("Recipe not found")

        recipe_dto = to_recipe_dto(recipe)
        return recipe_dto

    async def _get_tags_by_acceptance(
        self, family_member_id: int, descending: bool
    ) -> list[str]:
        acceptance_ratio = SuggestedTagHistory.times_accepted / (
            SuggestedTagHistory.times_accepted + SuggestedTagHistory.times_rejected
        )
        tags = self.session.exec(
            select(SuggestedTagHistory)
            .where(
                SuggestedTagHistory.family_member_id == family_member_id,
            )
            .limit(5)
            .order_by(
                desc(acceptance_ratio) if descending else acceptance_ratio,  # pyright: ignore[reportArgumentType]
                SuggestedTagHistory.times_suggested  # pyright: ignore[reportArgumentType]
                if descending
                else desc(SuggestedTagHistory.times_suggested),  # pyright: ignore[reportArgumentType]
            )
        ).all()
        return [tag.tag for tag in tags]

    async def _get_top_tags(self, family_member_id: int) -> list[str]:
        return await self._get_tags_by_acceptance(family_member_id, descending=True)

    async def _get_bottom_tags(self, family_member_id: int) -> list[str]:
        return await self._get_tags_by_acceptance(family_member_id, descending=False)

    async def _save_tag_suggestions(
        self, suggestions: list[SuggestionDTO], family_member_id: int
    ):
        # Get existing tags from db
        suggested_tags = {tag.suggestion for tag in suggestions}
        existing_tags = self.session.exec(
            select(SuggestedTagHistory).where(
                SuggestedTagHistory.tag.in_(suggested_tags),
                SuggestedTagHistory.family_member_id == family_member_id,
            )
        ).all()

        # For existing tags, increment times_suggested and attach id
        # For new tags, save to database and attach id
        for tag in suggestions:
            for existing_tag in existing_tags:
                if tag.suggestion == existing_tag.tag:
                    tag.id = existing_tag.id
                    existing_tag.times_suggested += 1
                    break
            else:
                new_tag_history = SuggestedTagHistory(
                    tag=tag.suggestion,
                    family_member_id=family_member_id,
                    created_by=self.user.id,
                )
                self.session.add(new_tag_history)
                self.session.flush()
                tag.id = new_tag_history.id

        self.session.commit()
        return suggestions

    async def suggest_tags(self, recipe_id: int) -> list[SuggestionDTO]:
        family_member = await self.family_service.get_family_by_auth_id()
        if not family_member:
            raise UnauthorizedException("User does not belong to a family.")
        recipe = await self.get_recipe(recipe_id)
        top_tags = ", ".join(await self._get_top_tags(family_member.id))
        bottom_tags = ", ".join(await self._get_bottom_tags(family_member.id))
        prompt = f"""
        Recipe:
        {recipe}

        Frequently accepted tags:
        {top_tags}

        Frequently rejected tags:
        {bottom_tags}
        """
        result = await tag_suggestion_agent.run(prompt)
        await self._save_tag_suggestions(result.output, family_member.id)
        return result.output

    async def suggest_substitutions(
        self, recipe_id: int, ingredient_id: int
    ) -> list[SuggestionDTO]:
        result = await substitution_agent.run(
            f"Suggest substitutions for ingredient id: {ingredient_id} in recipe_id: {recipe_id}",
            deps=self,
        )
        return result.output


async def _get_recipe_tool(ctx: RunContext[RecipeService], recipe_id: int) -> RecipeDTO:
    """Look up a recipe by id, scoped to the requesting user's family."""
    return await ctx.deps.get_recipe(recipe_id)


tag_suggestion_agent: Agent[None, list[SuggestionDTO]] = Agent(
    os.environ.get("LLM_MODEL"),
    system_prompt=(
        """
        You are a recipe tagging assistant.  Your job is to analyze recipes and generate accurate, useful recipe tags.
        Users may accept, reject, or just ignore your suggestions.

        Rules:
        - Return only relevant tags.
        - Suggest up to 5 tags.
        - Prefer common cooking terminology.
        - Avoid duplicate or redundant tags.
        - Try to use tags that are similar to top tags used by the user
        - Try to avoid tags that are similar to bottom tags used by the user
        - Consider recipe name, ingredients, and instructions.
        - Give reasons for each tag suggestion, such as key ingredients or cooking techniques that justify the tag.
        """
    ),
    output_type=list[SuggestionDTO],
)

substitution_agent: Agent[RecipeService, list[SuggestionDTO]] = Agent(
    os.environ.get("LLM_MODEL"),
    deps_type=RecipeService,
    system_prompt=(
        "Suggest ingredient substitutions for recipes."
        "Given a recipe and an ingredient name, return a list of suitable substitutions for that ingredient."
        "Consider the flavor profile, texture, and cooking properties of the original ingredient when suggesting substitutions."
        "Limit substitutions to a maximum of 5, and ensure they are relevant to the recipe.  You do not have to return all 5 suggestions."
        "If a substitution is requested for an ingredient that is not a part of the recipe's ingredients, return an empty list."
    ),
    output_type=list[SuggestionDTO],
    tools=[Tool(_get_recipe_tool, takes_ctx=True)],
)

logfire.instrument_pydantic_ai(tag_suggestion_agent)
logfire.instrument_pydantic_ai(substitution_agent)
