import { SearchRequest, SearchResponse, StoryRequest, StoryResponse, WorkflowStatus, Story } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Search for viral posts using the Python backend
 * @param criteria Search criteria including time range, subreddits, and post count
 * @returns SearchResponse with posts and metadata
 * @throws Error if the request fails
 */
export async function searchPosts(criteria: SearchRequest): Promise<SearchResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        time_range: criteria.timeRange,
        subreddits: criteria.subreddits,
        post_count: criteria.postCount,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: { message: 'An unexpected error occurred' },
      }));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    // Transform snake_case response to camelCase for frontend
    return {
      posts: data.posts.map((post: any) => ({
        id: post.id,
        title: post.title,
        subreddit: post.subreddit,
        url: post.url,
        upvotes: post.upvotes,
        comments: post.comments,
        viralScore: post.viral_score,
        createdAt: new Date(post.created_at),
        author: post.author,
      })),
      totalFound: data.total_found,
      searchCriteria: {
        timeRange: data.search_criteria.time_range,
        subreddits: data.search_criteria.subreddits,
        postCount: data.search_criteria.post_count,
      },
      executionTime: data.execution_time,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to search posts');
  }
}

/**
 * Generate a story from a Reddit post using AI
 * @param request Story request with post data
 * @returns Object with workflow_id to track generation progress
 * @throws Error if the request fails
 */
export async function generateStory(request: StoryRequest): Promise<{ workflowId: string; status: string; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/story/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        post_id: request.postId,
        post_title: request.postTitle,
        post_content: request.postContent,
        mood: request.mood,
        options: request.options,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: { message: 'Story generation failed' },
      }));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      workflowId: data.workflow_id,
      status: data.status,
      message: data.message,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to start story generation');
  }
}

/**
 * Get the status of a story generation workflow
 * @param workflowId Workflow ID returned from generateStory
 * @returns WorkflowStatus with current progress
 * @throws Error if the request fails
 */
export async function getStoryStatus(workflowId: string): Promise<WorkflowStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/story/status/${workflowId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: { message: 'Failed to get workflow status' },
      }));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      workflowId: data.workflow_id,
      status: data.status,
      currentStep: data.current_step,
      progress: data.progress,
      storyId: data.story_id,
      error: data.error,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to get story status');
  }
}

/**
 * Get a generated story by ID
 * @param storyId Story ID returned from workflow status
 * @returns StoryResponse with the generated story
 * @throws Error if the request fails
 */
export async function getStory(storyId: string): Promise<StoryResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/story/${storyId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: { message: 'Failed to get story' },
      }));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      story: {
        id: data.story.id,
        content: data.story.content,
        evaluationScore: data.story.evaluation_score,
        rewriteCount: data.story.rewrite_count,
        createdAt: data.story.created_at,
        metadata: data.story.metadata,
      },
      generationTime: data.generation_time,
      workflowInfo: {
        evaluationScore: data.workflow_info.evaluation_score,
        rewriteCount: data.workflow_info.rewrite_count,
      },
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to get story');
  }
}
