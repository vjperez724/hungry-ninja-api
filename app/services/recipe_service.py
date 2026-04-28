from pydantic_ai import Agent

from app.models import Recipe, Suggestion

class RecipeService:
    tag_suggestion_agent: Agent
    substitution_agent: Agent

    def __init__(self):
        self.tag_suggestion_agent = Agent(
            "google-gla:gemini-3.1-flash-lite-preview",
            system_prompt=(
                "Suggest tags for recipes."
                "Return a list of relevant tags based on the recipe's name, ingredients, and instructions."
                "Limit tags to a maximum of 5, and ensure they are concise and relevant to the recipe."
                "Give reasons for each tag suggestion, such as key ingredients or cooking techniques that justify the tag."
            ),
            output_type=list[Suggestion],
        )
        self.substitution_agent = Agent(
            "google-gla:gemini-3.1-flash-lite-preview",
            system_prompt=(
                "Suggest ingredient substitutions for recipes."
                "Given a recipe and an ingredient name, return a list of suitable substitutions for that ingredient."
                "Consider the flavor profile, texture, and cooking properties of the original ingredient when suggesting substitutions."
                "Limit substitutions to a maximum of 5, and ensure they are relevant to the recipe."
            ),
            output_type=list[Suggestion],
        )

    async def suggest_tags(self, recipe: Recipe) -> list[Suggestion]:
        prompt = f"Suggest tags for the following recipe: {recipe}"
        result = await self.tag_suggestion_agent.run(prompt)
        return result.output

    async def suggest_substitutions(self, recipe: Recipe, ingredient_name: str) -> list[Suggestion]:
        prompt = f"Suggest substitutions for {ingredient_name} in the following recipe: {recipe}"
        result = await self.substitution_agent.run(prompt)
        return result.output