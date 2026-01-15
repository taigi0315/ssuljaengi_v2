import { SearchRequest, SearchResponse } from '@/types';

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
