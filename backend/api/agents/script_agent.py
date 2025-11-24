"""Script stage agent for script analysis and development"""
from typing import Dict, Any, Optional
from api.agents.base_agent import BaseAgent
from api.agents.tools.firestore_tool import get_project_data, create_project_artifact

class ScriptAgent(BaseAgent):
    """Agent specialized for script development stage"""

    def __init__(self):
        super().__init__(
            agent_name="Script Agent",
            model_name="gemini-1.5-pro",
        )

    def _get_system_instruction(self) -> str:
        return """You are a script development assistant for the Cinefilm Platform.
Your role is to help filmmakers:
- Analyze scripts for structure, pacing, and character development
- Suggest dialogue improvements
- Identify plot holes and inconsistencies
- Develop character arcs
- Refine scenes and sequences
- Provide feedback on script elements

Be constructive, specific, and provide actionable feedback."""

    async def analyze_script(self, project_id: str, script_content: str) -> Dict[str, Any]:
        """Analyze a script"""
        prompt = f"""Analyze this script:

{script_content}

Provide analysis on:
1. Structure (three-act, hero's journey, etc.)
2. Character development
3. Dialogue quality
4. Pacing
5. Strengths and areas for improvement"""

        response = await self.chat(prompt, {"project_id": project_id})

        if "response" in response:
            artifact_id = create_project_artifact(
                project_id,
                "script_analysis",
                {"script_content": script_content[:500], "analysis": response["response"]},
            )
            response["artifact_id"] = artifact_id

        return response

    async def suggest_dialogue(self, project_id: str, scene_context: str, character: str) -> Dict[str, Any]:
        """Suggest dialogue for a scene"""
        prompt = f"""Based on this scene context:
{scene_context}

Suggest dialogue for the character: {character}

Make it natural, character-appropriate, and serve the story."""

        response = await self.chat(prompt, {"project_id": project_id})

        if "response" in response:
            artifact_id = create_project_artifact(
                project_id,
                "dialogue_suggestion",
                {"scene": scene_context, "character": character, "dialogue": response["response"]},
            )
            response["artifact_id"] = artifact_id

        return response

