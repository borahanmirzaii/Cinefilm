# Studio → Backend → ADK Connection Architecture

## Overview

This document describes the complete connection flow from the Studio (frontend) through the Backend to Google's Agent Development Kit (ADK).

## Connection Flow

```
Studio (Frontend)
    ↓ HTTP POST /api/agents/{stage}/chat
Backend API (FastAPI)
    ↓ Vertex AI SDK
Google ADK / Vertex AI
    ↓ Gemini Model
AI Response
    ↓ Stored in Firestore
Studio (Display + History)
```

## Components

### 1. Studio Frontend (`web-app/src/components/AgentUI.tsx`)

**Purpose**: User interface for interacting with agents in the studio

**Features**:
- Chat interface for real-time agent conversations
- Session history viewer
- Artifacts browser (agent-generated content)
- Stage-specific agent selection

**Connection**:
- Uses `agentApi` client (`web-app/src/lib/agent_api.ts`)
- Sends requests to `/api/agents/{stage}/chat`
- Includes Firebase auth token automatically
- Passes `project_id` for context

**Key Files**:
- `web-app/src/components/AgentUI.tsx` - Main agent UI component
- `web-app/src/lib/agent_api.ts` - API client for agents
- `web-app/src/hooks/useAgents.ts` - React Query hooks

### 2. Backend API (`backend/api/routers/agents.py`)

**Purpose**: RESTful API endpoints for agent interactions

**Endpoints**:
- `POST /api/agents/{stage}/chat` - Chat with stage-specific agent
- `POST /api/agents/{stage}/execute` - Execute agent tasks
- `GET /api/agents/{stage}/sessions` - List agent sessions
- `GET /api/agents/{stage}/artifacts` - List agent artifacts

**Connection**:
- Receives requests from Studio
- Authenticates via Firebase token
- Routes to appropriate agent instance
- Returns agent responses

**Key Files**:
- `backend/api/routers/agents.py` - Agent API routes
- `backend/api/middleware/auth.py` - Authentication middleware

### 3. Agent Layer (`backend/api/agents/`)

**Purpose**: Stage-specific AI agents using Google ADK/Vertex AI

**Agents**:
- **ConceptAgent** (`concept_agent.py`) - Concept development, loglines, themes
- **ScriptAgent** (`script_agent.py`) - Script analysis, dialogue, structure
- **PreProductionAgent** (`preproduction_agent.py`) - Shot lists, storyboards, scheduling

**Connection**:
- Uses `BaseAgent` class (`base_agent.py`)
- Initializes Vertex AI/Gemini models
- Connects to Google Cloud via `aiplatform.init()`
- Uses `GenerativeModel` for chat completion

**Key Files**:
- `backend/api/agents/base_agent.py` - Base agent with ADK integration
- `backend/api/agents/concept_agent.py` - Concept stage agent
- `backend/api/agents/script_agent.py` - Script stage agent
- `backend/api/agents/preproduction_agent.py` - Pre-production agent
- `backend/api/agents/tools/firestore_tool.py` - Firestore tools for agents

### 4. ADK / Vertex AI Integration

**Purpose**: Google's Agent Development Kit for AI agent execution

**Configuration**:
- Project ID: `cinefilm-platform`
- Location: `us-central1`
- Model: `gemini-1.5-pro` (configurable)

**Connection**:
- Backend agents initialize Vertex AI SDK
- Use `aiplatform.init()` for authentication
- Call `GenerativeModel.generate_content()` for responses
- Store conversations in Firestore for memory

**Key Configuration**:
- `backend/api/config.py` - Vertex AI settings
- `backend/api/agents/base_agent.py` - ADK initialization

## Data Flow Example

### User sends message in Studio:

1. **Studio** → User types message in `AgentUI` component
2. **Frontend** → `agentApi.chat()` called with stage, message, projectId
3. **HTTP Request** → `POST /api/agents/concept/chat` with Firebase token
4. **Backend** → `agents.py` router receives request
5. **Authentication** → `get_current_user()` verifies Firebase token
6. **Agent Selection** → Router gets `ConceptAgent` instance
7. **Agent Processing** → `ConceptAgent.chat()` called
8. **ADK Connection** → `BaseAgent._generate_response()` uses Vertex AI
9. **Vertex AI** → Calls Gemini model via `GenerativeModel.generate_content()`
10. **Response** → Agent receives AI response
11. **Session Storage** → Response stored in Firestore `agent_sessions` collection
12. **HTTP Response** → Backend returns response to Studio
13. **Studio** → `AgentUI` displays response in chat interface

## Session Management

### Firestore Structure

```
projects/{project_id}/
  agent_sessions/{session_id}
    - project_id: string
    - stage: string (concept|script|preproduction)
    - agent: string (agent name)
    - messages: array[{role, content, timestamp}]
    - created_at: timestamp
    - updated_at: timestamp

  artifacts/{artifact_id}
    - project_id: string
    - type: string (logline_suggestions|script_analysis|shot_list|...)
    - content: object
    - created_at: timestamp
```

## Artifact Creation

Agents can create artifacts (saved outputs) that are stored in Firestore:

- **Concept Agent**: `logline_suggestions`, `theme_brainstorm`
- **Script Agent**: `script_analysis`, `dialogue_suggestion`
- **Pre-Production Agent**: `shot_list`, `storyboard_suggestion`

Artifacts are accessible via:
- Studio UI: `AgentUI` → Artifacts tab
- API: `GET /api/agents/{stage}/artifacts?project_id={id}`

## Configuration

### Environment Variables

```env
# Vertex AI / ADK
VERTEX_AI_PROJECT_ID=cinefilm-platform
VERTEX_AI_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-pro
```

### Frontend Environment

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing the Connection

1. **Start services**:
   ```bash
   docker-compose up
   ```

2. **Open Studio**:
   - Navigate to a project: `http://localhost:3000/projects/{id}`
   - Click "Agent Studio" button

3. **Test Chat**:
   - Type a message in the chat
   - Verify response appears
   - Check browser console for API calls

4. **Verify Backend**:
   - Check backend logs: `docker-compose logs backend-api`
   - Should see agent initialization and API calls

5. **Verify ADK**:
   - Check Vertex AI logs in Google Cloud Console
   - Verify model calls are being made

## Troubleshooting

### Studio → Backend Connection Issues

- **401 Unauthorized**: Check Firebase token is being sent
- **404 Not Found**: Verify agent endpoint path matches stage
- **Network Error**: Check `NEXT_PUBLIC_API_URL` is correct

### Backend → ADK Connection Issues

- **SDK_NOT_AVAILABLE**: Vertex AI SDK not initialized
  - Check `GOOGLE_APPLICATION_CREDENTIALS` is set
  - Verify service account has Vertex AI permissions
- **Model Error**: Check `GEMINI_MODEL` name is correct
- **Authentication Error**: Verify GCP project ID and credentials

### Agent Not Responding

- Check backend logs for errors
- Verify Vertex AI API is enabled in GCP
- Check service account permissions
- Verify model name is available in your region

## Next Steps

1. **Enhanced Agent Memory**: Implement conversation context retrieval
2. **Multi-turn Conversations**: Support follow-up questions with context
3. **Agent Tools**: Expand tool library for agents
4. **Streaming Responses**: Implement streaming for real-time responses
5. **Agent Analytics**: Track agent usage and performance

