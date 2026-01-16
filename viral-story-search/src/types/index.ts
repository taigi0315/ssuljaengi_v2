// Core data types for the Viral Story Search application

export interface SearchCriteria {
  timeRange: '1h' | '1d' | '10d' | '100d';
  subreddits: string[];
  postCount: number;
}

export interface TimeRangeOption {
  value: string;
  label: string;
  description: string;
}

export interface SubredditOption {
  name: string;
  displayName: string;
  description: string;
  isPopular: boolean;
}

export interface ViralPost {
  id: string;
  title: string;
  subreddit: string;
  url: string;
  upvotes: number;
  comments: number;
  viralScore: number;
  createdAt: Date;
  author: string;
}

export interface ViralMetrics {
  upvotes: number;
  comments: number;
  hoursSincePosted: number;
  engagementRate: number;
}

export interface RedditPost {
  id: string;
  title: string;
  subreddit: string;
  permalink: string;
  score: number;
  num_comments: number;
  created_utc: number;
  author: string;
  is_removed: boolean;
  is_deleted: boolean;
}

// API Types
export interface SearchRequest {
  timeRange: string;
  subreddits: string[];
  postCount: number;
}

export interface SearchResponse {
  posts: ViralPost[];
  totalFound: number;
  searchCriteria: SearchCriteria;
  executionTime: number;
}

// Error Types
export enum ErrorType {
  REDDIT_API_ERROR = 'reddit_api_error',
  RATE_LIMIT = 'rate_limit',
  NETWORK_ERROR = 'network_error',
  VALIDATION_ERROR = 'validation_error',
  TIMEOUT_ERROR = 'timeout_error',
}

export interface ErrorState {
  type: ErrorType;
  message: string;
  retryable: boolean;
  retryAfter?: number;
}

// Component Props Types
export interface SearchControlsProps {
  onSearch: (criteria: SearchCriteria) => void;
  isLoading: boolean;
}

export interface TimeRangeSelectorProps {
  selected: string;
  onChange: (range: string) => void;
  options?: TimeRangeOption[];
}

export interface SubredditSelectorProps {
  selected: string[];
  onChange: (subreddits: string[]) => void;
  availableSubreddits: SubredditOption[];
}

export interface PostCountInputProps {
  value: number;
  onChange: (count: number) => void;
  error?: string;
}

export interface ResultsListProps {
  posts: ViralPost[];
  searchCriteria: SearchCriteria;
  isLoading: boolean;
  error: string | null;
  selectedPost?: ViralPost | null;
  onPostSelect?: (post: ViralPost) => void;
  onCreateStory?: () => void;
}

export interface ResultItemProps {
  post: ViralPost;
  isSelected?: boolean;
  onSelect?: (post: ViralPost) => void;
}

export interface ErrorMessageProps {
  error: ErrorState;
  onRetry?: () => void;
}

// Configuration Types
export interface SearchConfig {
  defaultTimeRange: string;
  defaultPostCount: number;
  maxPostCount: number;
  minUpvotes: number;
  minComments: number;
  cacheTimeout: number;
}

// Reddit API Client Interface
export interface RedditApiClient {
  fetchPosts(
    subreddit: string,
    timeRange: string,
    limit: number
  ): Promise<RedditPost[]>;
  validateSubreddit(name: string): Promise<boolean>;
}

// Story Generation Types (Phase 2)
export type StoryMood = 'rofan' | 'modern_romance' | 'slice_of_life' | 'revenge' | 'high_teen';

export interface StoryMoodOption {
  id: StoryMood;
  name: string;
  emoji: string;
  description: string;
}

export interface StoryRequest {
  postId: string;
  postTitle: string;
  postContent: string;
  mood: StoryMood;
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
  progress: number; // 0.0 to 1.0
  storyId?: string;
  error?: string;
}

// Story Component Props
export interface StoryDisplayProps {
  story: Story;
}

export interface WorkflowProgressProps {
  status: WorkflowStatus | null;
}

export interface RedditPostDisplayProps {
  post: ViralPost;
}

// Webtoon Types (Phase 3)
export interface Character {
  name: string;
  visual_description: string;
}

export interface WebtoonPanel {
  panel_number: number;
  shot_type: string;
  active_character_names: string[];
  visual_prompt: string;
  dialogue?: string;
}

export interface WebtoonScript {
  script_id: string;
  story_id: string;
  characters: Character[];
  panels: WebtoonPanel[];
  character_images: Record<string, CharacterImage[]>;
  created_at: string;
}

export interface CharacterImage {
  id: string;
  character_name: string;
  description: string;
  image_url: string;
  created_at: string;
  is_selected: boolean;
}

export interface GenerateWebtoonRequest {
  story_id: string;
}

export interface GenerateCharacterImageRequest {
  script_id: string;
  character_name: string;
  description: string;
}
