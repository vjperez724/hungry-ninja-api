from pydantic_ai import Agent

from app.models import RecipeDTO, SuggestionDTO
from app.services.exceptions import NotFoundException


class RecipeService:
    tag_suggestion_agent: Agent[RecipeDTO, list[SuggestionDTO]]
    substitution_agent: Agent[tuple[RecipeDTO, str], list[SuggestionDTO]]

    def __init__(self):
        self.tag_suggestion_agent = Agent(
            "google-gla:gemini-3.1-flash-lite-preview",
            system_prompt=(
                "You are a helpful cooking assistant.  The recipe will be provided in the context."
                "Return a list of relevant tags based on included recipe's name, ingredients, and instructions."
                "Limit tags to a maximum of 5, and ensure they are concise and relevant to the recipe.  You do not have to return all 5 tags."
                "Give reasons for each tag suggestion, such as key ingredients or cooking techniques that justify the tag."
                "Avoid returning similar tags, such as both 'quick and easy' and 'simple'."
                "Avoid possibly controversial tags, such as using vegetarian on eggs."
            ),
            deps_type=RecipeDTO,
            output_type=list[SuggestionDTO],
        )
        self.substitution_agent = Agent(
            "google-gla:gemini-3.1-flash-lite-preview",
            system_prompt=(
                "Suggest ingredient substitutions for recipes.  The recipe will be provided in the context."
                "Given a recipe and an ingredient name, return a list of suitable substitutions for that ingredient."
                "Consider the flavor profile, texture, and cooking properties of the original ingredient when suggesting substitutions."
                "Limit substitutions to a maximum of 5, and ensure they are relevant to the recipe.  You do not have to return all 5 suggestions."
                "If a substitution is requested for an ingredient that is not a part of the recipe's ingredients, do not suggest anything."
            ),
            deps_type=tuple[RecipeDTO, str],
            output_type=list[SuggestionDTO],
        )

    async def suggest_recipe_tags(self, recipe: RecipeDTO) -> list[SuggestionDTO]:
        result = await self.tag_suggestion_agent.run(
            f"Suggest tags for recipe: {recipe.name}", deps=recipe
        )
        return result.output

    async def suggest_recipe_substitutions(
        self, recipe: RecipeDTO, ingredient_name: str
    ) -> list[SuggestionDTO]:
        # Validate that ingredient_name exists in the recipe's ingredients
        ingredient_found = False
        for ingredients_list in recipe.ingredients.values():
            for ingredient in ingredients_list:
                if ingredient.name.lower() == ingredient_name.lower():
                    ingredient_found = True
                    break
            if ingredient_found:
                break

        if not ingredient_found:
            raise NotFoundException(
                f"Ingredient '{ingredient_name}' not found in recipe '{recipe.name}'"
            )

        result = await self.substitution_agent.run(
            f"Suggest substitutions for {ingredient_name} in the following recipe: {recipe.name}",
            deps=(recipe, ingredient_name),
        )
        return result.output
