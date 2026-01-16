# Requirements Document: AI Story Generation (Phase 2)

## Introduction

This specification describes Phase 2 of the viral-story-search application: adding AI-powered story generation using LangChain and LangGraph. Users will be able to select a Reddit post and generate a creative story using Google's Gemini 2.0 Flash model with an automated review and rewrite workflow.

## Glossary

- **Story_Writer**: LangChain node that generates initial story from Reddit post
- **Story_Evaluator**: LangChain node that evaluates story quality and provides feedback
- **Story_Rewriter**: LangChain node that rewrites story based on evaluator feedback
- **LangGraph_Workflow**: Orchestration system managing Writer → Evaluator → Rewriter flow
- **Gemini_Model**: Google's Gemini 2.0 Flash LLM used for story generation
- **Story_Page**: Frontend page displaying selected post and generated story
- **Selection_State**: UI state tracking which Reddit post user has selected

## Requirements

### Requirement 1: Post Selection UI

**User Story:** As a user, I want to select a Reddit post from search results, so that I can generate a story from it.

#### Acceptance Criteria

1. WHEN a user clicks on a Reddit post result, THE Frontend SHALL highlight the selected post visually
2. WHEN a post is selected, THE Frontend SHALL prevent navigation to external Reddit URL
3. WHEN a post is selected, THE Frontend SHALL display a "Create Story" button at the bottom of results
4. WHEN no post is selected, THE Frontend SHALL hide the "Create Story" button
5. WHEN a user selects a different post, THE Frontend SHALL update the selection state and maintain the "Create Story" button

### Requirement 2: Story Generation Navigation

**User Story:** As a user, I want to navigate to a story generation page when I click "Create Story", so that I can view the AI-generated story.

#### Acceptance Criteria

1. WHEN a user clicks "Create Story", THE Frontend SHALL navigate to the story generation page
2. WHEN navigating to story page, THE Frontend SHALL pass the selected Reddit post data
3. WHEN navigating to story page, THE Frontend SHALL animate the transition with a slide-left effect
4. THE story generation page SHALL display the selected Reddit post on the left side
5. THE story generation page SHALL display the generated story on the right side

### Requirement 3: Story Generation Backend

**User Story:** As a developer, I want to implement AI story generation using LangChain and Gemini, so that users can get creative stories from Reddit posts.

#### Acceptance Criteria

1. THE Backend SHALL use Google Gemini 2.0 Flash model for story generation
2. THE Backend SHALL implement a Story_Writer that accepts Reddit post and generates initial story
3. THE Backend SHALL use LangChain for LLM interactions
4. WHEN story generation fails, THE Backend SHALL return descriptive error messages
5. THE Backend SHALL configure Gemini with appropriate temperature and token limits

### Requirement 4: Story Evaluation System

**User Story:** As a system, I want to automatically evaluate generated stories, so that low-quality stories can be improved.

#### Acceptance Criteria

1. THE Story_Evaluator SHALL score stories on a scale of 1-10
2. THE Story_Evaluator SHALL evaluate coherence, engagement, and length
3. THE Story_Evaluator SHALL provide specific feedback for improvement
4. WHEN evaluation score is below 7, THE System SHALL trigger a rewrite
5. WHEN evaluation score is 7 or above, THE System SHALL accept the story

### Requirement 5: LangGraph Workflow Orchestration

**User Story:** As a system, I want to orchestrate the story generation workflow using LangGraph, so that stories are automatically reviewed and improved.

#### Acceptance Criteria

1. THE LangGraph_Workflow SHALL execute nodes in order: Writer → Evaluator → (conditional) Rewriter
2. WHEN Story_Evaluator score is below threshold, THE Workflow SHALL route to Story_Rewriter
3. WHEN Story_Evaluator score meets threshold, THE Workflow SHALL complete and return story
4. THE Workflow SHALL limit rewrites to maximum 1 iteration
5. THE Workflow SHALL track state including draft_story, evaluation_score, feedback, and rewrite_count

### Requirement 6: Story Rewriting

**User Story:** As a system, I want to automatically rewrite low-quality stories, so that users receive better content.

#### Acceptance Criteria

1. THE Story_Rewriter SHALL accept original story and evaluator feedback as input
2. THE Story_Rewriter SHALL generate improved story based on feedback
3. THE Story_Rewriter SHALL maintain the core narrative from original story
4. WHEN rewrite is complete, THE System SHALL re-evaluate the rewritten story
5. THE System SHALL return the rewritten story regardless of second evaluation score

### Requirement 7: Story API Endpoints

**User Story:** As a frontend developer, I want REST API endpoints for story generation, so that I can integrate story generation into the UI.

#### Acceptance Criteria

1. THE Backend SHALL provide POST /story/generate endpoint accepting Reddit post data
2. THE Backend SHALL provide GET /story/status/{workflow_id} endpoint for progress tracking
3. THE Backend SHALL provide GET /story/{story_id} endpoint for retrieving generated stories
4. WHEN story generation is in progress, THE status endpoint SHALL return current workflow step
5. WHEN story generation is complete, THE status endpoint SHALL return the final story

### Requirement 8: Story Data Models

**User Story:** As a developer, I want well-defined data models for stories, so that data is consistently structured.

#### Acceptance Criteria

1. THE Backend SHALL define StoryRequest model with post_id, post_title, post_content fields
2. THE Backend SHALL define Story model with id, content, metadata, evaluation_score fields
3. THE Backend SHALL define StoryResponse model with story, generation_time, workflow_info fields
4. THE Backend SHALL define WorkflowStatus model with status, current_step, progress fields
5. THE Backend SHALL validate all request/response data using Pydantic

### Requirement 9: Frontend Story Display

**User Story:** As a user, I want to see the generated story in a clean, readable format, so that I can enjoy the content.

#### Acceptance Criteria

1. THE Story_Page SHALL display the original Reddit post on the left side (30% width)
2. THE Story_Page SHALL display the generated story on the right side (70% width)
3. WHEN story is generating, THE Story_Page SHALL show loading state with progress indicator
4. WHEN story generation fails, THE Story_Page SHALL display error message with retry option
5. THE Story_Page SHALL format the story text with proper paragraphs and spacing

### Requirement 10: Workflow Progress Tracking

**User Story:** As a user, I want to see the progress of story generation, so that I know the system is working.

#### Acceptance Criteria

1. THE Frontend SHALL poll the status endpoint every 2 seconds during generation
2. THE Frontend SHALL display current workflow step (Writing, Evaluating, Rewriting)
3. THE Frontend SHALL show progress percentage (0-100%)
4. WHEN workflow moves to rewriting, THE Frontend SHALL indicate "Improving story..."
5. WHEN workflow completes, THE Frontend SHALL stop polling and display final story

### Requirement 11: Error Handling

**User Story:** As a user, I want clear error messages when story generation fails, so that I understand what went wrong.

#### Acceptance Criteria

1. WHEN Gemini API fails, THE Backend SHALL return "LLM service unavailable" error
2. WHEN API rate limit is exceeded, THE Backend SHALL return "Rate limit exceeded, try again later"
3. WHEN invalid post data is provided, THE Backend SHALL return "Invalid post data" error
4. WHEN timeout occurs, THE Backend SHALL return "Story generation timeout" error
5. THE Frontend SHALL display all error messages to the user with retry option

### Requirement 12: Environment Configuration

**User Story:** As a developer, I want to configure Gemini API through environment variables, so that I can manage credentials securely.

#### Acceptance Criteria

1. THE Backend SHALL load Gemini API key from GOOGLE_API_KEY environment variable
2. THE Backend SHALL load model name from GEMINI_MODEL environment variable (default: gemini-2.0-flash)
3. WHEN GOOGLE_API_KEY is missing, THE Backend SHALL fail to start with clear error message
4. THE Backend SHALL support configurable temperature and max_tokens via environment
5. THE .env.example SHALL document all required Gemini configuration variables

### Requirement 13: Story Prompts

**User Story:** As a developer, I want placeholder prompts for story generation, so that I can test the workflow before optimizing prompts.

#### Acceptance Criteria

1. THE Story_Writer SHALL use a simple prompt template for initial implementation
2. THE Story_Evaluator SHALL use a simple scoring prompt for initial implementation
3. THE Story_Rewriter SHALL use a simple improvement prompt for initial implementation
4. THE prompts SHALL be configurable and easy to modify
5. THE prompts SHALL include clear instructions for the LLM

### Requirement 14: Response Caching

**User Story:** As a system, I want to cache generated stories, so that users can retrieve them without regenerating.

#### Acceptance Criteria

1. THE Backend SHALL store generated stories in memory cache with story_id as key
2. THE Backend SHALL cache stories for 1 hour (configurable TTL)
3. WHEN a user requests a cached story, THE Backend SHALL return it immediately
4. THE Backend SHALL implement LRU eviction when cache is full
5. THE Backend SHALL include cache hit/miss in response metadata

### Requirement 15: Frontend API Client Updates

**User Story:** As a frontend developer, I want API client functions for story generation, so that I can easily call backend endpoints.

#### Acceptance Criteria

1. THE apiClient SHALL provide generateStory(postData) function
2. THE apiClient SHALL provide getStoryStatus(workflowId) function
3. THE apiClient SHALL provide getStory(storyId) function
4. THE apiClient SHALL handle errors and throw with descriptive messages
5. THE apiClient SHALL use the same base URL and error handling as search endpoints
