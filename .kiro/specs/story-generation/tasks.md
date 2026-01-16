# Implementation Plan: AI Story Generation (Phase 2)

## Overview

This plan implements AI-powered story generation using LangChain and LangGraph. Users can select Reddit posts and generate creative stories through an automated Writer → Evaluator → Rewriter workflow powered by Google Gemini 2.0 Flash.

**Goal**: Enable users to transform Reddit posts into engaging stories with automated quality control.

## Tasks

- [x] 1. Backend: Install LangChain dependencies
  - Add to `backend/requirements.txt`: langchain, langchain-google-genai, langgraph, google-generativeai
  - Install dependencies: `pip install -r requirements.txt`
  - Verify installation
  - _Requirements: 3.3, 12.1_

- [x] 2. Backend: Configure Gemini model
  - [x] 2.1 Create `app/services/llm_config.py`
    - Import ChatGoogleGenerativeAI from langchain-google-genai
    - Create LLMConfig class
    - Load API key from settings.google_api_key
    - Configure model name (gemini-2.0-flash), temperature (0.7), max_tokens (2000)
    - Implement get_model() method returning configured model
    - _Requirements: 3.1, 3.5, 12.2_

  - [x] 2.2 Update `app/config.py` with Gemini settings
    - Add google_api_key: str field (required)
    - Add gemini_model: str field (default: "gemini-2.0-flash")
    - Add gemini_temperature: float field (default: 0.7)
    - Add gemini_max_tokens: int field (default: 2000)
    - Add story_evaluation_threshold: float field (default: 7.0)
    - Add story_max_rewrites: int field (default: 1)
    - _Requirements: 12.1, 12.3, 12.4_

  - [x] 2.3 Update `backend/.env.example` with Gemini config
    - Add GOOGLE_API_KEY with instructions
    - Add GEMINI_MODEL with default
    - Add GEMINI_TEMPERATURE with default
    - Add GEMINI_MAX_TOKENS with default
    - Add STORY_EVALUATION_THRESHOLD with default
    - Add STORY_MAX_REWRITES with default
    - _Requirements: 12.5_

- [x] 3. Backend: Create story data models
  - [x] 3.1 Create `app/models/story.py`
    - Implement StoryRequest model (post_id, post_title, post_content, options)
    - Implement Story model (id, content, evaluation_score, rewrite_count, created_at, metadata)
    - Implement StoryResponse model (story, generation_time, workflow_info)
    - Implement WorkflowStatus model (workflow_id, status, current_step, progress, story_id, error)
    - Implement EvaluationResult model (score, feedback, coherence, engagement, length_appropriate)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 4. Backend: Implement Story Writer node
  - [x] 4.1 Create `app/services/story_writer.py`
    - Import LangChain components (ChatPromptTemplate, StrOutputParser)
    - Create StoryWriter class
    - Define prompt template for story generation (placeholder prompt)
    - Implement write_story(reddit_post) async method
    - Use LangChain chain: prompt | llm | parser
    - Handle errors and raise descriptive exceptions
    - _Requirements: 3.2, 3.3, 13.1, 13.4_

- [x] 5. Backend: Implement Story Evaluator node
  - [x] 5.1 Create `app/services/story_evaluator.py`
    - Import LangChain components
    - Create StoryEvaluator class
    - Define evaluation prompt template (score 1-10, coherence, engagement, length)
    - Implement evaluate_story(story) async method
    - Parse LLM response into EvaluationResult
    - Return score, feedback, and sub-scores
    - _Requirements: 4.1, 4.2, 4.3, 13.2, 13.4_

- [x] 6. Backend: Implement Story Rewriter node
  - [x] 6.1 Create `app/services/story_rewriter.py`
    - Import LangChain components
    - Create StoryRewriter class
    - Define rewrite prompt template (improve based on feedback)
    - Implement rewrite_story(story, feedback) async method
    - Use LangChain chain: prompt | llm | parser
    - Handle errors
    - _Requirements: 6.1, 6.2, 6.3, 13.3, 13.4_

- [x] 7. Backend: Implement LangGraph workflow
  - [x] 7.1 Create `app/workflows/story_workflow.py`
    - Import LangGraph components (StateGraph, END)
    - Define StoryWorkflowState TypedDict (reddit_post, draft_story, evaluation_score, evaluation_feedback, final_story, rewrite_count, current_step, error)
    - Implement writer_node(state) async function
    - Implement evaluator_node(state) async function
    - Implement rewriter_node(state) async function
    - Implement should_rewrite(state) routing function (score < 7 and rewrite_count < 1)
    - Create workflow graph: writer → evaluator → conditional(rewriter or END)
    - Add edge: rewriter → evaluator (for re-evaluation)
    - Compile and export workflow
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 8. Backend: Create story API endpoints
  - [x] 8.1 Create `app/routers/story.py`
    - Create FastAPI router with prefix "/story"
    - Initialize in-memory storage for workflows and stories (dict)
    - _Requirements: 7.1_

  - [x] 8.2 Implement POST /story/generate endpoint
    - Accept StoryRequest body
    - Generate unique workflow_id (uuid)
    - Start workflow in background task (asyncio.create_task)
    - Return workflow_id and status "started"
    - _Requirements: 7.1, 7.4_

  - [x] 8.3 Implement run_workflow background task
    - Update workflow status to "in_progress"
    - Execute story_workflow.ainvoke with reddit_post data
    - Store result in stories dict with unique story_id
    - Update workflow status to "completed" with story_id
    - Handle errors and update status to "failed"
    - _Requirements: 5.1, 5.5, 6.5_

  - [x] 8.4 Implement GET /story/status/{workflow_id} endpoint
    - Accept workflow_id path parameter
    - Look up workflow in storage
    - Return WorkflowStatus (status, current_step, progress, story_id, error)
    - Return 404 if workflow not found
    - _Requirements: 7.2, 7.4, 10.1_

  - [x] 8.5 Implement GET /story/{story_id} endpoint
    - Accept story_id path parameter
    - Look up story in storage
    - Return StoryResponse (story, generation_time, workflow_info)
    - Return 404 if story not found
    - _Requirements: 7.3_

  - [x] 8.6 Register story router in `app/main.py`
    - Import story router
    - Add router to FastAPI app
    - _Requirements: 7.1_

- [x] 9. Backend: Add error handling
  - [x] 9.1 Update `app/utils/exceptions.py`
    - Add LLMException class
    - Add StoryGenerationException class
    - Add WorkflowException class
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [x] 9.2 Add exception handlers in `app/main.py`
    - Add handler for LLMException (503)
    - Add handler for StoryGenerationException (500)
    - Add handler for WorkflowException (500)
    - _Requirements: 3.4, 11.1, 11.2, 11.3, 11.4_

- [ ] 10. Checkpoint - Test backend independently
  - Update `.env` with GOOGLE_API_KEY
  - Run backend: `cd backend && uvicorn app.main:app --reload --port 8000`
  - Test story generation with curl or Postman:
    ```bash
    curl -X POST http://localhost:8000/story/generate \
      -H "Content-Type: application/json" \
      -d '{
        "post_id": "test123",
        "post_title": "AITA for leaving my wedding?",
        "post_content": "I found out my fiancé was cheating..."
      }'
    ```
  - Check workflow status with returned workflow_id
  - Retrieve generated story with story_id
  - Verify workflow executes: Writer → Evaluator → (conditional) Rewriter
  - Check API docs at `http://localhost:8000/docs`
  - Ask the user if questions arise

- [x] 11. Frontend: Add story types
  - [x] 11.1 Update `viral-story-search/src/types/index.ts`
    - Add StoryRequest interface
    - Add Story interface
    - Add StoryResponse interface
    - Add WorkflowStatus interface
    - Export all story types
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 12. Frontend: Update API client
  - [x] 12.1 Update `viral-story-search/src/lib/apiClient.ts`
    - Import story types
    - Implement generateStory(request: StoryRequest) function
    - Implement getStoryStatus(workflowId: string) function
    - Implement getStory(storyId: string) function
    - Handle errors and throw with descriptive messages
    - Use same base URL and error handling pattern
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 13. Frontend: Update search page for post selection
  - [x] 13.1 Update `viral-story-search/src/app/page.tsx`
    - Add selectedPost state (useState<ViralPost | null>)
    - Add handlePostSelect callback
    - Pass selectedPost and onSelect to ResultsList
    - _Requirements: 1.1_

  - [x] 13.2 Update `viral-story-search/src/components/ResultsList.tsx`
    - Accept selectedPost and onSelect props
    - Pass to ResultItem components
    - Add "Create Story" button at bottom (only show when selectedPost exists)
    - Implement handleCreateStory: navigate to /story/generate with post data
    - Style button prominently
    - _Requirements: 1.3, 1.4, 2.1, 2.2_

  - [x] 13.3 Update `viral-story-search/src/components/ResultItem.tsx`
    - Accept isSelected and onSelect props
    - Change from <a> tag to <div> with onClick
    - Remove external link navigation
    - Add onClick handler: call onSelect(post)
    - Add visual selection state (border, background color, shadow)
    - Add hover state
    - _Requirements: 1.1, 1.2, 1.5_

- [x] 14. Frontend: Create story generation page
  - [x] 14.1 Create `viral-story-search/src/app/story/generate/page.tsx`
    - Create StoryGeneratePage component
    - Accept post data from router state/query
    - Add state: post, story, status, isLoading, error
    - Implement useEffect to start generation on mount
    - Implement useEffect to poll status every 2 seconds while in_progress
    - Implement startStoryGeneration: call apiClient.generateStory
    - Implement pollStatus: call apiClient.getStoryStatus
    - When status is completed, fetch story with apiClient.getStory
    - Layout: flex container with left (30%) and right (70%) sections
    - _Requirements: 2.3, 2.4, 2.5, 9.1, 9.2, 10.1, 10.2_

- [x] 15. Frontend: Create story display components
  - [x] 15.1 Create `viral-story-search/src/components/StoryDisplay.tsx`
    - Accept story prop
    - Display story content with proper formatting
    - Add paragraphs, spacing, typography
    - Show evaluation score and rewrite count in metadata section
    - Style for readability
    - _Requirements: 9.3, 9.5_

  - [x] 15.2 Create `viral-story-search/src/components/WorkflowProgress.tsx`
    - Accept status prop (WorkflowStatus)
    - Display current step (Writing, Evaluating, Rewriting)
    - Show progress bar (0-100%)
    - Show loading spinner
    - Display step-specific messages
    - _Requirements: 10.2, 10.3, 10.4_

  - [x] 15.3 Create `viral-story-search/src/components/RedditPostDisplay.tsx`
    - Accept post prop (ViralPost)
    - Display post title, subreddit, author
    - Display post content (if available)
    - Display upvotes, comments, viral score
    - Style as card with proper spacing
    - _Requirements: 9.1_

- [ ] 16. Frontend: Add page transition animation
  - [ ] 16.1 Install framer-motion (optional)
    - Run: `npm install framer-motion`
    - Or use CSS transitions
    - _Requirements: 2.3_

  - [ ] 16.2 Add slide-left animation
    - Wrap page content in motion.div (if using framer-motion)
    - Or add CSS transition classes
    - Animate: current page slides left, new page slides in from right
    - Duration: 300-500ms
    - _Requirements: 2.3_

- [ ] 17. Frontend: Add error handling UI
  - [ ] 17.1 Update error display in story page
    - Show error message when story generation fails
    - Add retry button
    - Handle different error types (LLM error, timeout, validation)
    - Style error messages clearly
    - _Requirements: 9.4, 11.1, 11.2, 11.3, 11.4_

- [ ] 18. Final checkpoint - End-to-end testing
  - Start backend: `cd backend && uvicorn app.main:app --reload --port 8000`
  - Start frontend: `cd viral-story-search && npm run dev`
  - Open browser to `http://localhost:3000`
  - Search for Reddit posts
  - Select a post (verify visual selection)
  - Click "Create Story" button
  - Verify navigation to story page with slide animation
  - Verify Reddit post displays on left
  - Verify progress indicator shows workflow steps
  - Wait for story generation to complete
  - Verify generated story displays on right
  - Check that story is readable and well-formatted
  - Test error handling (stop backend mid-generation)
  - Test with different Reddit posts
  - Ask the user if questions arise

## Notes

- This is Phase 2: AI Story Generation with LangChain/LangGraph
- Phase 3 (future): Advanced LangGraph workflows, image generation
- All LLM calls are async to prevent blocking
- Workflow is limited to 1 rewrite maximum
- Stories are cached in memory (use Redis in production)
- Prompts are placeholders and can be optimized later
- Each task references specific requirements for traceability
- Checkpoints ensure the system works at key milestones
