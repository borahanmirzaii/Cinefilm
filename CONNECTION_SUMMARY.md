# Studio → Backend → ADK Connection Summary

## ✅ Complete Connection Chain

### 1. Studio (Frontend) → Backend
**Status**: ✅ **CONNECTED**

**Connection Points**:
- `web-app/src/components/AgentUI.tsx` → `web-app/src/lib/agent_api.ts` → `POST /api/agents/{stage}/chat`
- Firebase authentication token automatically injected
- Project context passed with each request

**Files**:
- `web-app/src/components/AgentUI.tsx` - Main agent UI component
- `web-app/src/lib/agent_api.ts` - Agent API client
- `web-app/src/hooks/useAgents.ts` - React Query hooks

**Integration**:
- Integrated into project detail page (`web-app/src/app/(studio)/projects/[id]/page.tsx`)
- Stage-aware: switches agents based on selected stage
- Real-time chat interface with session history

---

### 2. Backend → ADK (Agent Development Kit)
**Status**: ✅ **CONNECTED**

**Connection Points**:
- `backend/api/routers/agents.py` → `backend/api/agents/{stage}_agent.py` → `BaseAgent._generate_response()`
- Uses Vertex AI SDK (`vertexai.generative_models.GenerativeModel`)
- Connects to Google Cloud via `aiplatform.init()`

**Files**:
- `backend/api/routers/agents.py` - Agent API endpoints
- `backend/api/agents/base_agent.py` - Base agent with ADK integration
- `backend/api/agents/concept_agent.py` - Concept stage agent
- `backend/api/agents/script_agent.py` - Script stage agent
- `backend/api/agents/preproduction_agent.py` - Pre-production agent

**Configuration**:
- Project: `cinefilm-platform`
- Location: `us-central1`
- Model: `gemini-1.5-pro` (configurable)

**Session Storage**:
- Conversations stored in Firestore: `projects/{project_id}/agent_sessions/{session_id}`
- Artifacts stored in Firestore: `projects/{project_id}/artifacts/{artifact_id}`

---

### 3. Agent UI (AG-UI) in Studio
**Status**: ✅ **IMPLEMENTED**

**Features**:
- **Chat Tab**: Real-time conversation with stage-specific agent
- **History Tab**: View past agent sessions
- **Artifacts Tab**: Browse agent-generated content (loglines, analyses, shot lists)

**Location**: 
- Accessible from project detail page
- Floating button: "Agent Studio"
- Stage-aware: Automatically uses correct agent for selected stage

**Connection Flow**:
```
Studio Page
  ↓ User clicks "Agent Studio"
AgentUI Component
  ↓ User sends message
agentApi.chat()
  ↓ HTTP POST
Backend /api/agents/{stage}/chat
  ↓ Routes to agent
{Stage}Agent.chat()
  ↓ Calls ADK
BaseAgent._generate_response()
  ↓ Vertex AI SDK
Gemini Model (via ADK)
  ↓ Response
Stored in Firestore
  ↓ Returned to Studio
Displayed in AgentUI
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    STUDIO (Frontend)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AgentUI Component                                    │  │
│  │  - Chat Interface                                    │  │
│  │  - Session History                                   │  │
│  │  - Artifacts Browser                                 │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │ HTTP POST /api/agents/{stage}/chat    │
│                      │ + Firebase Token                      │
│                      │ + Project Context                     │
└──────────────────────┼───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  /api/agents/{stage}/chat                            │  │
│  │  - Authenticates user                                │  │
│  │  - Routes to stage-specific agent                    │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │  {Stage}Agent (Concept/Script/PreProduction)          │  │
│  │  - Loads project context                              │  │
│  │  - Builds prompt                                      │  │
│  │  - Calls BaseAgent.chat()                            │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │  BaseAgent._generate_response()                        │  │
│  │  - Uses Vertex AI SDK                                 │  │
│  │  - Calls GenerativeModel.generate_content()           │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │  Session Storage                                      │  │
│  │  - Stores in Firestore                                │  │
│  │  - Creates/updates agent_sessions                     │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              GOOGLE ADK / VERTEX AI                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  aiplatform.init()                                   │  │
│  │  - Project: cinefilm-platform                        │  │
│  │  - Location: us-central1                             │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                       │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │  GenerativeModel (gemini-1.5-pro)                    │  │
│  │  - Processes prompt                                   │  │
│  │  - Generates response                                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Integration Points

### Studio → Backend
1. **Authentication**: Firebase token automatically injected via `apiClient` interceptor
2. **Stage Mapping**: Frontend maps UI stages to backend agent endpoints
3. **Context Passing**: Project ID and user ID included in requests
4. **Error Handling**: Graceful error display in UI

### Backend → ADK
1. **Initialization**: Vertex AI SDK initialized in `BaseAgent.__init__()`
2. **Model Selection**: Configurable via `GEMINI_MODEL` environment variable
3. **Prompt Building**: Agent-specific system instructions + context
4. **Response Generation**: Synchronous call to `GenerativeModel.generate_content()`
5. **Session Tracking**: Conversations stored in Firestore for continuity

### Agent UI Features
1. **Multi-tab Interface**: Chat, History, Artifacts
2. **Real-time Updates**: React Query for automatic refetching
3. **Stage Awareness**: Automatically uses correct agent
4. **Session Continuity**: Sessions tracked per project/stage
5. **Artifact Management**: View agent-generated content

---

## Testing the Connection

### 1. Start Services
```bash
docker-compose up
```

### 2. Open Studio
- Navigate to: `http://localhost:3000/projects/{project_id}`
- Click "Agent Studio" button (bottom right)

### 3. Test Chat
- Select a stage (Concept, Script, Pre-Production)
- Type a message
- Verify response appears
- Check browser DevTools → Network tab for API calls

### 4. Verify Backend
```bash
docker-compose logs -f backend-api | grep -i "agent\|vertex\|gemini"
```

### 5. Verify ADK Connection
- Check backend logs for "Generating response with gemini-1.5-pro"
- Verify no "SDK_NOT_AVAILABLE" errors
- Check Firestore for new `agent_sessions` documents

---

## Configuration Checklist

- [x] Frontend API client configured (`web-app/src/lib/api.ts`)
- [x] Agent API client created (`web-app/src/lib/agent_api.ts`)
- [x] Agent UI component implemented (`web-app/src/components/AgentUI.tsx`)
- [x] Backend agent endpoints created (`backend/api/routers/agents.py`)
- [x] Base agent class with ADK integration (`backend/api/agents/base_agent.py`)
- [x] Stage-specific agents implemented
- [x] Vertex AI SDK configured
- [x] Session storage in Firestore
- [x] Artifact storage in Firestore
- [x] Stage switching in Studio UI

---

## Next Enhancements

1. **Streaming Responses**: Real-time token streaming from Gemini
2. **Multi-turn Context**: Load previous messages for context
3. **Agent Memory**: Long-term memory across sessions
4. **Tool Calling**: Agents can call backend APIs directly
5. **Agent Analytics**: Track usage and performance metrics

