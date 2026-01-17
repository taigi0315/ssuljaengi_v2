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
        mood: request.genre,  // Backend still expects 'mood' key for now
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

/**
 * Generate a webtoon script from a story
 * @param storyId Story ID to convert to webtoon script
 * @returns WebtoonScript with characters and panels
 * @throws Error if the request fails
 */
export async function generateWebtoonScript(storyId: string): Promise<import('@/types').WebtoonScript> {
  try {
    const response = await fetch(`${API_BASE_URL}/webtoon/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        story_id: storyId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: { message: 'Webtoon script generation failed' },
      }));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      script_id: data.script_id,
      story_id: data.story_id,
      characters: data.characters,
      panels: data.panels,
      character_images: data.character_images || {},
      created_at: data.created_at,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to generate webtoon script');
  }
}

/**
 * Generate a character image
 * @param request Character image generation request
 * @returns CharacterImage with image URL
 * @throws Error if the request fails
 */
export async function generateCharacterImage(request: import('@/types').GenerateCharacterImageRequest): Promise<import('@/types').CharacterImage> {
  try {
    const response = await fetch(`${API_BASE_URL}/webtoon/character/image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: { message: 'Character image generation failed' },
      }));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      id: data.id,
      character_name: data.character_name,
      description: data.description,
      image_url: data.image_url,
      created_at: data.created_at,
      is_selected: data.is_selected,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to generate character image');
  }
}

/**
 * Get a webtoon script by ID
 * @param scriptId Script ID
 * @returns WebtoonScript with all data
 * @throws Error if the request fails
 */
export async function getWebtoonScript(scriptId: string): Promise<import('@/types').WebtoonScript> {
  try {
    const response = await fetch(`${API_BASE_URL}/webtoon/${scriptId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: { message: 'Failed to get webtoon script' },
      }));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      script_id: data.script_id,
      story_id: data.story_id,
      characters: data.characters,
      panels: data.panels,
      character_images: data.character_images || {},
      created_at: data.created_at,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to get webtoon script');
  }
}

/**
 * Select a character image as reference for scene generation
 * @param scriptId Script ID
 * @param imageId Image ID to select
 * @returns Success message
 * @throws Error if the request fails
 */
export async function selectCharacterImage(scriptId: string, imageId: string): Promise<{ message: string; image_id: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/webtoon/character/image/select?script_id=${scriptId}&image_id=${imageId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: { message: 'Failed to select character image' },
      }));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to select character image');
  }
}

/**
 * Get all images for a character
 * @param scriptId Script ID
 * @param characterName Character name
 * @returns Array of CharacterImage
 * @throws Error if the request fails
 */
export async function getCharacterImages(scriptId: string, characterName: string): Promise<import('@/types').CharacterImage[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/webtoon/character/${scriptId}/${characterName}/images`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: { message: 'Failed to get character images' },
      }));
      throw new Error(errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    return data.map((img: any) => ({
      id: img.id,
      character_name: img.character_name,
      description: img.description,
      image_url: img.image_url,
      created_at: img.created_at,
      is_selected: img.is_selected,
    }));
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to get character images');
  }
}
