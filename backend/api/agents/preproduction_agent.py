"""Pre-production stage agent for shot lists and scheduling"""
from typing import Dict, Any, Optional
from api.agents.base_agent import BaseAgent
from api.agents.tools.firestore_tool import get_project_data, create_project_artifact

class PreProductionAgent(BaseAgent):
    """Agent specialized for pre-production stage"""

    def __init__(self):
        super().__init__(
            agent_name="Pre-Production Agent",
            model_name="gemini-1.5-pro",
        )

    def _get_system_instruction(self) -> str:
        return """You are a pre-production assistant for the Cinefilm Platform.
Your role is to help filmmakers:
- Create shot lists from scripts
- Suggest storyboard ideas
- Plan shooting schedules
- Identify locations and props needed
- Estimate production requirements
- Organize production logistics

Be practical, detailed, and production-focused."""

    async def generate_shot_list(self, project_id: str, script_content: str) -> Dict[str, Any]:
        """Generate shot list from script"""
        prompt = f"""Based on this script content:

{script_content[:2000]}  # Limit to avoid token limits

Generate a detailed shot list with:
- Scene number
- Shot description
- Camera angle/shot type
- Location
- Props/equipment needed
- Estimated duration"""

        response = await self.chat(prompt, {"project_id": project_id})

        if "response" in response:
            artifact_id = create_project_artifact(
                project_id,
                "shot_list",
                {"script_preview": script_content[:500], "shot_list": response["response"]},
            )
            response["artifact_id"] = artifact_id

        return response

    async def suggest_storyboard(self, project_id: str, scene_description: str) -> Dict[str, Any]:
        """Suggest storyboard ideas for a scene"""
        prompt = f"""For this scene:
{scene_description}

Suggest storyboard frames with:
- Frame descriptions
- Camera angles
- Composition notes
- Visual style suggestions"""

        response = await self.chat(prompt, {"project_id": project_id})

        if "response" in response:
            artifact_id = create_project_artifact(
                project_id,
                "storyboard_suggestion",
                {"scene": scene_description, "storyboard": response["response"]},
            )
            response["artifact_id"] = artifact_id

        return response

