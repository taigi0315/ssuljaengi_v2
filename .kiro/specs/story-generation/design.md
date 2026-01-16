# Design Document: AI Story Generation (Phase 2)

## Overview

This design describes the implementation of AI-powered story generation using LangChain and LangGraph. The system allows users to select Reddit posts and generate creative stories through an automated workflow that includes writing, evaluation, and conditional rewriting.

**Key Technologies:**
- **Frontend**: Next.js with React hooks for state management
- **Backend**: FastAPI with LangChain and LangGraph
- **LLM**: Google Gemini 2.0 Flash
- **Workflow**: LangGraph for orchestration

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │ Search Page  │────────▶│  Story Page  │                 │
│  │ (Select Post)│         │ (View Story) │                 │
│  └──────────────┘         └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           LangGraph Workflow                         │  │
│  │                                                       │  │
│  │   ┌─────────┐    ┌───────────┐    ┌──────────┐    │  │
│  │   │ Writer  │───▶│ Evaluator │───▶│ Rewriter │    │  │
│  │   └─────────┘    └───────────┘    └──────────┘    │  │
│  │                         │                           │  │
│  │                         │ score >= 7?               │  │
│  │                         ▼                           │  │
│  │                    ┌─────────┐                      │  │
│  │                    │   END   │                      │  │
│  │                    └─────────┘                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │  Gemini 2.5 Flash│
                  │  (Google AI)     │
                  └──────────────────┘
```

### Directory Structure

```
backend/
├── app/
│   ├── models/
│   │   └── story.py              # NEW: Story data models
│   ├── services/
│   │   ├── llm_config.py        # NEW: Gemini configuration
│   │   ├── story_writer.py      # NEW: Writer node
│   │   ├── story_evaluator.py   # NEW: Evaluator node
│   │   └── story_rewriter.py    # NEW: Rewriter node
│   ├── workflows/
│   │   └── story_workflow.py    # NEW: LangGraph workflow
│   ├── routers/
│   │   └── story.py             # NEW: Story API endpoints
│   └── utils/
│       └── story_cache.py       # NEW: Story caching

viral-story-search/
├── src/
│   ├── app/
│   │   ├── page.tsx             # MODIFY: Add selection state
│   │   └── story/
│   │       └── generate/
│   │           └── page.tsx     # NEW: Story generation page
│   ├── components/
│   │   ├── ResultItem.tsx       # MODIFY: Add selection
│   │   ├── ResultsList.tsx      # MODIFY: Add create button
│   │   ├── StoryDisplay.tsx     # NEW: Display story
│   │   └── WorkflowProgress.tsx # NEW: Progress indicator
│   ├── lib/
│   │   └── apiClient.ts         # MODIFY: Add story functions
│   └── types/
│       └── index.ts             # MODIFY: Add story types
```

## Components and Interfaces

### 1. Frontend: Post Selection (Modified ResultItem)

**Responsibilities:**
- Handle post selection clicks
- Display visual selection state
- Prevent external navigation when selected

**Key Changes:**
```typescript
interface ResultItemProps {
  post: ViralPost;
  isSelected: boolean;
  onSelect: (post: ViralPost) => void;
}

// Remove <a> tag, use <div> with onClick
// Add selection styling (border, background)
// Emit selection event to parent
```

### 2. Frontend: Create Story Button (Modified ResultsList)

**Responsibilities:**
- Show button when post is selected
- Handle navigation to story page
- Pass selected post data

**Key Methods:**
```typescript
const handleCreateStory = () => {
  if (selectedPost) {
    router.push({
      pathname: '/story/generate',
      query: { postId: selectedPost.id }
    });
    // Or use state management to pass full post data
  }
};
```

### 3. Frontend: Story Generation Page

**Responsibilities:**
- Display selected Reddit post
- Show story generation progress
- Poll backend for status updates
- Display final generated story

**Component Structure:**
```typescript
export default function StoryGeneratePage() {
  const [post, setPost] = useState<ViralPost | null>(null);
  const [story, setStory] = useState<Story | null>(null);
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // On mount: start generation
  useEffect(() => {
    startStoryGeneration();
  }, []);

  // Poll for status updates
  useEffect(() => {
    if (status?.status === 'in_progress') {
      const interval = setInterval(pollStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [status]);

  return (
    <div className="flex h-screen">
      {/* Left: Reddit Post (30%) */}
      <div className="w-1/3 p-6 border-r">
        <RedditPostDisplay post={post} />
      </div>
      
      {/* Right: Generated Story (70%) */}
      <div className="w-2/3 p-6">
        {isLoading && <WorkflowProgress status={status} />}
        {error && <ErrorMessage error={error} />}
        {story && <StoryDisplay story={story} />}
      </div>
    </div>
  );
}
```

### 4. Backend: LLM Configuration (llm_config.py)

**Responsibilities:**
- Initialize Gemini model
- Configure model parameters
- Handle API authentication

**Implementation:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

class LLMConfig:
    def __init__(self):
        self.model_name = settings.gemini_model
        self.api_key = settings.google_api_key
        self.temperature = settings.gemini_temperature
        self.max_tokens = settings.gemini_max_tokens
    
    def get_model(self) -> ChatGoogleGenerativeAI:
        """Get configured Gemini model"""
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )

llm_config = LLMConfig()
```

### 5. Backend: Story Writer Node

**Responsibilities:**
- Accept Reddit post as input
- Generate initial story using Gemini
- Return story text

**Implementation:**
```python
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StrOutputParser

class StoryWriter:
    def __init__(self):
        self.llm = llm_config.get_model()
        self.prompt = ChatPromptTemplate.from_template("""
You are a creative story writer. Transform this Reddit post into an engaging short story.

Reddit Post:
Title: {title}
Content: {content}

Write a compelling 500-word story based on this post. Make it dramatic and engaging.
Focus on:
- Character development
- Emotional depth
- Narrative arc
- Vivid descriptions

Story:
""")
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    async def write_story(self, reddit_post: RedditPost) -> str:
        """Generate initial story from Reddit post"""
        try:
            story = await self.chain.ainvoke({
                "title": reddit_post.title,
                "content": reddit_post.content or reddit_post.title
            })
            return story
        except Exception as e:
            raise Exception(f"Story generation failed: {str(e)}")

story_writer = StoryWriter()
```

### 6. Backend: Story Evaluator Node

**Responsibilities:**
- Evaluate story quality
- Provide numerical score (1-10)
- Generate feedback for improvement

**Implementation:**
```python
from pydantic import BaseModel

class EvaluationResult(BaseModel):
    score: float
    feedback: str
    coherence: float
    engagement: float
    length_appropriate: bool

class StoryEvaluator:
    def __init__(self):
        self.llm = llm_config.get_model()
        self.prompt = ChatPromptTemplate.from_template("""
Evaluate this story on a scale of 1-10 based on:
1. Coherence (does it make sense? logical flow?)
2. Engagement (is it interesting? emotionally compelling?)
3. Length (appropriate length? not too short or long?)

Story:
{story}

Provide your evaluation in this format:
Score: [1-10]
Coherence: [1-10]
Engagement: [1-10]
Length Appropriate: [yes/no]
Feedback: [specific suggestions for improvement]
""")
    
    async def evaluate_story(self, story: str) -> EvaluationResult:
        """Evaluate story and return score + feedback"""
        try:
            response = await self.llm.ainvoke(
                self.prompt.format(story=story)
            )
            
            # Parse response (simplified - use structured output in production)
            lines = response.content.split('\n')
            score = float(lines[0].split(':')[1].strip())
            coherence = float(lines[1].split(':')[1].strip())
            engagement = float(lines[2].split(':')[1].strip())
            length_ok = 'yes' in lines[3].lower()
            feedback = lines[4].split(':', 1)[1].strip()
            
            return EvaluationResult(
                score=score,
                feedback=feedback,
                coherence=coherence,
                engagement=engagement,
                length_appropriate=length_ok
            )
        except Exception as e:
            raise Exception(f"Story evaluation failed: {str(e)}")

story_evaluator = StoryEvaluator()
```

### 7. Backend: Story Rewriter Node

**Responsibilities:**
- Accept original story and feedback
- Generate improved version
- Maintain core narrative

**Implementation:**
```python
class StoryRewriter:
    def __init__(self):
        self.llm = llm_config.get_model()
        self.prompt = ChatPromptTemplate.from_template("""
Rewrite this story based on the feedback provided. Improve the story while maintaining the core narrative.

Original Story:
{story}

Feedback:
{feedback}

Rewritten Story (improved version):
""")
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    async def rewrite_story(self, story: str, feedback: str) -> str:
        """Rewrite story based on evaluator feedback"""
        try:
            rewritten = await self.chain.ainvoke({
                "story": story,
                "feedback": feedback
            })
            return rewritten
        except Exception as e:
            raise Exception(f"Story rewriting failed: {str(e)}")

story_rewriter = StoryRewriter()
```

### 8. Backend: LangGraph Workflow

**Responsibilities:**
- Orchestrate Writer → Evaluator → Rewriter flow
- Manage workflow state
- Implement conditional routing
- Limit rewrites to 1 iteration

**Implementation:**
```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

class StoryWorkflowState(TypedDict):
    # Input
    reddit_post: dict
    
    # Workflow state
    draft_story: str
    evaluation_score: float
    evaluation_feedback: str
    final_story: str
    rewrite_count: int
    current_step: str
    
    # Output
    error: str | None

async def writer_node(state: StoryWorkflowState) -> StoryWorkflowState:
    """Generate initial story"""
    post = RedditPost(**state["reddit_post"])
    story = await story_writer.write_story(post)
    
    return {
        **state,
        "draft_story": story,
        "current_step": "evaluating",
    }

async def evaluator_node(state: StoryWorkflowState) -> StoryWorkflowState:
    """Evaluate story quality"""
    story = state.get("final_story") or state["draft_story"]
    evaluation = await story_evaluator.evaluate_story(story)
    
    return {
        **state,
        "evaluation_score": evaluation.score,
        "evaluation_feedback": evaluation.feedback,
        "current_step": "evaluated",
    }

async def rewriter_node(state: StoryWorkflowState) -> StoryWorkflowState:
    """Rewrite story based on feedback"""
    rewritten = await story_rewriter.rewrite_story(
        state["draft_story"],
        state["evaluation_feedback"]
    )
    
    return {
        **state,
        "final_story": rewritten,
        "rewrite_count": state.get("rewrite_count", 0) + 1,
        "current_step": "rewriting",
    }

def should_rewrite(state: StoryWorkflowState) -> Literal["rewrite", "end"]:
    """Decide if story needs rewriting"""
    score = state["evaluation_score"]
    rewrite_count = state.get("rewrite_count", 0)
    
    # Rewrite if score < 7 and haven't rewritten yet
    if score < 7.0 and rewrite_count < 1:
        return "rewrite"
    return "end"

def create_story_workflow() -> StateGraph:
    """Create LangGraph workflow"""
    workflow = StateGraph(StoryWorkflowState)
    
    # Add nodes
    workflow.add_node("writer", writer_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("rewriter", rewriter_node)
    
    # Add edges
    workflow.set_entry_point("writer")
    workflow.add_edge("writer", "evaluator")
    workflow.add_conditional_edges(
        "evaluator",
        should_rewrite,
        {
            "rewrite": "rewriter",
            "end": END
        }
    )
    workflow.add_edge("rewriter", "evaluator")
    
    return workflow.compile()

story_workflow = create_story_workflow()
```

### 9. Backend: Story API Router

**Responsibilities:**
- Handle story generation requests
- Provide status endpoints
- Manage workflow execution

**Implementation:**
```python
from fastapi import APIRouter, HTTPException
from app.models.story import StoryRequest, StoryResponse, WorkflowStatus
import uuid
import asyncio

router = APIRouter(prefix="/story", tags=["story"])

# In-memory storage (use Redis in production)
workflows = {}
stories = {}

@router.post("/generate", response_model=dict)
async def generate_story(request: StoryRequest):
    """Start story generation workflow"""
    workflow_id = str(uuid.uuid4())
    
    # Start workflow in background
    asyncio.create_task(run_workflow(workflow_id, request))
    
    return {
        "workflow_id": workflow_id,
        "status": "started",
        "message": "Story generation started"
    }

async def run_workflow(workflow_id: str, request: StoryRequest):
    """Execute story generation workflow"""
    try:
        workflows[workflow_id] = {
            "status": "in_progress",
            "current_step": "writing",
            "progress": 0.0
        }
        
        # Run workflow
        result = await story_workflow.ainvoke({
            "reddit_post": {
                "id": request.post_id,
                "title": request.post_title,
                "content": request.post_content
            },
            "rewrite_count": 0,
            "current_step": "writing"
        })
        
        # Store result
        story_id = str(uuid.uuid4())
        stories[story_id] = {
            "id": story_id,
            "content": result.get("final_story") or result["draft_story"],
            "evaluation_score": result["evaluation_score"],
            "rewrite_count": result.get("rewrite_count", 0),
            "workflow_id": workflow_id
        }
        
        workflows[workflow_id] = {
            "status": "completed",
            "current_step": "done",
            "progress": 1.0,
            "story_id": story_id
        }
        
    except Exception as e:
        workflows[workflow_id] = {
            "status": "failed",
            "error": str(e),
            "progress": 0.0
        }

@router.get("/status/{workflow_id}", response_model=WorkflowStatus)
async def get_workflow_status(workflow_id: str):
    """Get workflow status"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_data = workflows[workflow_id]
    
    return WorkflowStatus(
        workflow_id=workflow_id,
        status=workflow_data["status"],
        current_step=workflow_data.get("current_step", ""),
        progress=workflow_data.get("progress", 0.0),
        story_id=workflow_data.get("story_id"),
        error=workflow_data.get("error")
    )

@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: str):
    """Get generated story"""
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story_data = stories[story_id]
    
    return StoryResponse(
        story=Story(**story_data),
        generation_time=0.0,  # TODO: track actual time
        workflow_info={
            "evaluation_score": story_data["evaluation_score"],
            "rewrite_count": story_data["rewrite_count"]
        }
    )
```

## Data Models

### Pydantic Models (models/story.py)

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class StoryRequest(BaseModel):
    post_id: str
    post_title: str
    post_content: str
    options: Optional[dict] = None

class Story(BaseModel):
    id: str
    content: str
    evaluation_score: float
    rewrite_count: int
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict] = None

class StoryResponse(BaseModel):
    story: Story
    generation_time: float
    workflow_info: dict

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: Literal["started", "in_progress", "completed", "failed"]
    current_step: str
    progress: float  # 0.0 to 1.0
    story_id: Optional[str] = None
    error: Optional[str] = None
```

### TypeScript Types (types/index.ts)

```typescript
export interface StoryRequest {
  postId: string;
  postTitle: string;
  postContent: string;
  options?: Record<string, any>;
}

export interface Story {
  id: string;
  content: string;
  evaluationScore: number;
  rewriteCount: number;
  createdAt: string;
  metadata?: Record<string, any>;
}

export interface StoryResponse {
  story: Story;
  generationTime: number;
  workflowInfo: {
    evaluationScore: number;
    rewriteCount: number;
  };
}

export interface WorkflowStatus {
  workflowId: string;
  status: 'started' | 'in_progress' | 'completed' | 'failed';
  currentStep: string;
  progress: number;
  storyId?: string;
  error?: string;
}
```

## Error Handling

### Error Categories

1. **LLM Errors** (503)
   - Gemini API unavailable
   - Rate limiting
   - Timeout

2. **Validation Errors** (400)
   - Invalid post data
   - Missing required fields

3. **Not Found** (404)
   - Workflow ID not found
   - Story ID not found

4. **Internal Errors** (500)
   - Workflow execution failure
   - Unexpected exceptions

### Error Response Format

```python
{
    "error": {
        "type": "llm_error",
        "message": "Gemini API unavailable",
        "retryable": true,
        "retry_after": 60
    }
}
```

## Testing Strategy

### Unit Testing

**Backend:**
- Test each LangChain node independently
- Mock LLM responses
- Test workflow routing logic
- Test API endpoints

**Frontend:**
- Test component rendering
- Test selection state management
- Test API client functions
- Test error handling

### Integration Testing

- Test complete workflow execution
- Test frontend-backend integration
- Test polling mechanism
- Test error scenarios

### Manual Testing

- Test story quality with various Reddit posts
- Test UI/UX flow
- Test loading states and animations
- Test error messages

## Configuration

### Backend Environment Variables

```env
# Gemini Configuration
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2000

# Story Generation
STORY_EVALUATION_THRESHOLD=7.0
STORY_MAX_REWRITES=1
STORY_CACHE_TTL=3600
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Performance Considerations

1. **Async Operations**: All LLM calls are async to prevent blocking
2. **Caching**: Cache generated stories to avoid regeneration
3. **Polling Optimization**: 2-second intervals for status updates
4. **Timeout Handling**: Set reasonable timeouts for LLM calls
5. **Error Recovery**: Implement retry logic for transient failures

## Future Enhancements

1. **Streaming**: Stream story generation in real-time
2. **Multiple Styles**: Allow users to choose story style
3. **Story Editing**: Allow users to edit generated stories
4. **Story Sharing**: Share generated stories
5. **Advanced Evaluation**: More sophisticated evaluation criteria
6. **Persistent Storage**: Store stories in database
7. **User Accounts**: Save stories per user
