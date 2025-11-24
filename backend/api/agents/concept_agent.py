"""Concept stage agent for brainstorming and logline refinement"""
from typing import Dict, Any, Optional
from api.agents.base_agent import BaseAgent
from api.agents.tools.firestore_tool import get_project_data, create_project_artifact

class ConceptAgent(BaseAgent):
    """Agent specialized for concept development stage"""

    def __init__(self):
        super().__init__(
            agent_name="Concept Agent",
            model_name="gemini-1.5-pro",  # Use Pro for creative tasks
        )

    def _get_system_instruction(self) -> str:
        return """You are a creative film concept development assistant for the Cinefilm Platform.
Your role is to help filmmakers:
- Brainstorm story ideas and concepts
- Refine loglines and pitches
- Suggest themes and genres
- Develop character concepts
- Explore narrative possibilities

Be creative, encouraging, and provide actionable suggestions."""

    async def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Chat with concept agent"""
        # Load project context if available
        if context and "project_id" in context:
            project_data = get_project_data(context["project_id"])
            if project_data:
                context["project"] = project_data

        return await super().chat(message, context, session_id)

    async def suggest_logline(self, project_id: str, concept: str) -> Dict[str, Any]:
        """Suggest loglines for a concept"""
        prompt = f"""Based on this concept: {concept}

Generate 3-5 compelling loglines (one sentence each) that capture the essence of the story.
Make them engaging, clear, and marketable."""

        response = await self.chat(prompt, {"project_id": project_id})

        # Save as artifact
        if "response" in response:
            artifact_id = create_project_artifact(
                project_id,
                "logline_suggestions",
                {"concept": concept, "loglines": response["response"]},
            )
            response["artifact_id"] = artifact_id

        return response

    async def brainstorm_themes(self, project_id: str, genre: Optional[str] = None) -> Dict[str, Any]:
        """Brainstorm themes for a project"""
        prompt = f"""Generate thematic ideas for a film project"""
        if genre:
            prompt += f" in the {genre} genre"

        prompt += """
Consider:
- Universal themes (love, loss, redemption, etc.)
- Social themes
- Psychological themes
- Philosophical themes

Provide 5-7 theme suggestions with brief explanations."""

        response = await self.chat(prompt, {"project_id": project_id})

        if "response" in response:
            artifact_id = create_project_artifact(
                project_id,
                "theme_brainstorm",
                {"genre": genre, "themes": response["response"]},
            )
            response["artifact_id"] = artifact_id

        return response

