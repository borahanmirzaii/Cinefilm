"""Base agent class using Google ADK"""
import logging
from typing import Dict, Any, Optional, List
from api.config import settings

logger = logging.getLogger(__name__)

# Note: ADK integration will use Vertex AI directly for now
# Full ADK SDK integration can be added when package is available
try:
    from google.cloud import aiplatform
    # Use google-cloud-aiplatform for GenerativeModel
    try:
        from vertexai.preview.generative_models import GenerativeModel
    except ImportError:
        try:
            from vertexai.generative_models import GenerativeModel
        except ImportError:
            # Fallback: Use google-cloud-aiplatform directly
            logger.warning("vertexai module not available, using google-cloud-aiplatform")
            GenerativeModel = None
            ADK_AVAILABLE = False
    if GenerativeModel:
        ADK_AVAILABLE = True
    else:
        ADK_AVAILABLE = False
except ImportError:
    ADK_AVAILABLE = False
    GenerativeModel = None
    logger.warning("Vertex AI SDK not available. ADK features will be limited.")


class BaseAgent:
    """Base agent class for ADK agents"""

    def __init__(
        self,
        agent_name: str,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        """
        Initialize base agent.

        Args:
            agent_name: Name of the agent
            project_id: GCP project ID (defaults to settings)
            location: GCP location (defaults to settings)
            model_name: Gemini model name (defaults to settings)
        """
        self.agent_name = agent_name
        self.project_id = project_id or settings.vertex_ai_project_id
        self.location = location or settings.vertex_ai_location
        self.model_name = model_name or settings.gemini_model

        # Initialize Vertex AI
        if ADK_AVAILABLE:
            try:
                aiplatform.init(project=self.project_id, location=self.location)
                self.model = GenerativeModel(self.model_name)
                logger.info(f"Initialized {agent_name} agent with model {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Vertex AI: {e}")
                self.model = None
        else:
            self.model = None

    async def chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Chat with the agent.

        Args:
            message: User message
            context: Additional context (project data, etc.)
            session_id: Session ID for conversation continuity

        Returns:
            Agent response with session tracking
        """
        if not self.model:
            return {
                "response": "Agent is not available. Vertex AI SDK not initialized.",
                "error": "SDK_NOT_AVAILABLE",
                "agent": self.agent_name,
            }

        try:
            # Build prompt with context
            prompt = self._build_prompt(message, context)

            # Generate response using ADK/Vertex AI
            response_text = await self._generate_response(prompt)

            # Store session in Firestore if project_id provided
            if context and "project_id" in context:
                session_id = await self._store_session(
                    context["project_id"],
                    message,
                    response_text,
                    session_id,
                )

            return {
                "response": response_text,
                "session_id": session_id,
                "agent": self.agent_name,
            }
        except Exception as e:
            logger.error(f"Error in agent chat: {e}")
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "error": str(e),
                "agent": self.agent_name,
            }

    async def _store_session(
        self,
        project_id: str,
        user_message: str,
        agent_response: str,
        session_id: Optional[str] = None,
    ) -> str:
        """Store agent session in Firestore"""
        try:
            from firebase_admin import firestore
            from datetime import datetime

            db = firestore.client()
            sessions_ref = (
                db.collection("projects")
                .document(project_id)
                .collection("agent_sessions")
            )

            if session_id:
                # Update existing session
                session_ref = sessions_ref.document(session_id)
                session_data = session_ref.get().to_dict() if session_ref.get().exists else {}
                messages = session_data.get("messages", [])
                messages.append({
                    "role": "user",
                    "content": user_message,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                })
                messages.append({
                    "role": "agent",
                    "content": agent_response,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                })
                session_ref.set({
                    "messages": messages,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                    "stage": self._get_stage(),
                }, merge=True)
                return session_id
            else:
                # Create new session
                new_session_ref = sessions_ref.document()
                new_session_ref.set({
                    "project_id": project_id,
                    "stage": self._get_stage(),
                    "agent": self.agent_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": user_message,
                            "timestamp": firestore.SERVER_TIMESTAMP,
                        },
                        {
                            "role": "agent",
                            "content": agent_response,
                            "timestamp": firestore.SERVER_TIMESTAMP,
                        },
                    ],
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "updated_at": firestore.SERVER_TIMESTAMP,
                })
                return new_session_ref.id
        except Exception as e:
            logger.warning(f"Failed to store session: {e}")
            return session_id or ""

    def _get_stage(self) -> str:
        """Get stage name from agent name"""
        if "Concept" in self.agent_name:
            return "concept"
        elif "Script" in self.agent_name:
            return "script"
        elif "Pre-Production" in self.agent_name:
            return "preproduction"
        return "unknown"

    def _build_prompt(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        """Build prompt with agent-specific instructions and context"""
        prompt_parts = [self._get_system_instruction()]

        if context:
            prompt_parts.append(f"\nContext: {self._format_context(context)}")

        prompt_parts.append(f"\nUser: {message}")
        prompt_parts.append("\nAssistant:")

        return "\n".join(prompt_parts)

    def _get_system_instruction(self) -> str:
        """Get system instruction for this agent (override in subclasses)"""
        return f"You are {self.agent_name}, an AI assistant for the Cinefilm Platform."

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for prompt"""
        import json
        return json.dumps(context, indent=2)

    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Gemini model via Vertex AI/ADK"""
        if not self.model:
            raise RuntimeError("Model not initialized")

        # Generate response using Vertex AI Gemini model
        try:
            logger.debug(f"Generating response with {self.model_name} for {self.agent_name}")
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.warning("Empty response from model")
                return "I apologize, but I couldn't generate a response. Please try again."
            
            logger.debug(f"Response generated successfully ({len(response.text)} chars)")
            return response.text
        except Exception as e:
            logger.error(f"Error generating response with {self.model_name}: {e}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")

    async def execute_task(
        self,
        task: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a specific task.

        Args:
            task: Task description
            parameters: Task parameters

        Returns:
            Task result
        """
        # Override in subclasses for specific tasks
        return await self.chat(f"Execute task: {task}", parameters)

