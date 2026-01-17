'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ViralPost, Story, WorkflowStatus, StoryGenre } from '@/types';
import { generateStory, getStoryStatus, getStory } from '@/lib/apiClient';

export default function StoryGeneratePage() {
  const [post, setPost] = useState<ViralPost | null>(null);
  const [genre, setGenre] = useState<StoryGenre>('MODERN_ROMANCE_DRAMA_MANHWA');
  const [story, setStory] = useState<Story | null>(null);
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [workflowId, setWorkflowId] = useState<string | null>(null);

  const router = useRouter();

  // Load selected post and genre from sessionStorage
  useEffect(() => {
    const storedPost = sessionStorage.getItem('selectedPost');
    const storedGenre = sessionStorage.getItem('selectedGenre');
    
    if (storedGenre) {
      setGenre(storedGenre as StoryGenre);
    }
    
    if (storedPost) {
      try {
        const parsedPost = JSON.parse(storedPost);
        setPost(parsedPost);
      } catch (err) {
        setError('Failed to load selected post');
        setIsLoading(false);
      }
    } else {
      setError('No post selected. Please go back and select a post.');
      setIsLoading(false);
    }
  }, []);

  // Start story generation when post is loaded
  useEffect(() => {
    if (post && !workflowId) {
      startStoryGeneration();
    }
  }, [post, workflowId]);

  // Poll for status updates
  useEffect(() => {
    if (workflowId && status?.status === 'in_progress') {
      const interval = setInterval(() => {
        pollStatus();
      }, 2000); // Poll every 2 seconds

      return () => clearInterval(interval);
    }
  }, [workflowId, status]);

  // Start story generation
  const startStoryGeneration = async () => {
    if (!post) return;

    try {
      setIsLoading(true);
      setError(null);

      const response = await generateStory({
        postId: post.id,
        postTitle: post.title,
        postContent: post.title, // Using title as content for now
        genre: genre,
      });

      setWorkflowId(response.workflowId);
      setStatus({
        workflowId: response.workflowId,
        status: 'in_progress',
        currentStep: 'Writing',
        progress: 0.1,
      });
    } catch (err) {
      console.error('Story generation error:', err);
      setError(err instanceof Error ? err.message : 'Failed to start story generation');
      setIsLoading(false);
    }
  };

  // Poll for workflow status
  const pollStatus = async () => {
    if (!workflowId) return;

    try {
      const statusData = await getStoryStatus(workflowId);
      setStatus(statusData);

      // If completed, fetch the story
      if (statusData.status === 'completed' && statusData.storyId) {
        const storyData = await getStory(statusData.storyId);
        setStory(storyData.story);
        setIsLoading(false);
      }

      // If failed, show error
      if (statusData.status === 'failed') {
        setError(statusData.error || 'Story generation failed');
        setIsLoading(false);
      }
    } catch (err) {
      console.error('Status polling error:', err);
      // Don't set error here, just log it - we'll retry on next poll
    }
  };

  // Handle retry
  const handleRetry = () => {
    setWorkflowId(null);
    setStatus(null);
    setStory(null);
    setError(null);
    setIsLoading(true);
  };

  // Handle back navigation
  const handleBack = () => {
    router.push('/');
  };

  // Loading state
  if (isLoading && !error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50 flex items-center justify-center p-4">
        <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl p-8">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {status?.currentStep || 'Preparing'}...
            </h2>
            <p className="text-gray-600 mb-4">
              {status?.currentStep === 'Writing' && 'Creating your story from the Reddit post'}
              {status?.currentStep === 'Evaluating' && 'Reviewing story quality'}
              {status?.currentStep === 'Rewriting' && 'Improving the story based on feedback'}
              {!status?.currentStep && 'Starting story generation'}
            </p>
            {status?.progress !== undefined && (
              <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
                <div
                  className="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${status.progress * 100}%` }}
                ></div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-red-50 to-gray-100 flex items-center justify-center p-4">
        <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl p-8">
          <div className="text-center">
            <div className="text-6xl mb-4">❌</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Story Generation Failed
            </h2>
            <p className="text-red-600 mb-6">{error}</p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={handleRetry}
                className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors"
              >
                Try Again
              </button>
              <button
                onClick={handleBack}
                className="px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition-colors"
              >
                Go Back
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Success state - show post and story side by side
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <span className="text-xl">←</span>
            <span className="font-semibold">Back to Search</span>
          </button>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
            ✨ Generated Story
          </h1>
          <div className="w-24"></div> {/* Spacer for centering */}
        </div>
      </header>

      {/* Main Content - Split View */}
      <main className="container mx-auto px-4 py-6 sm:py-8">
        <div className="flex flex-col lg:flex-row gap-6 max-w-7xl mx-auto">
          {/* Left: Reddit Post (30%) */}
          <div className="lg:w-1/3">
            <div className="bg-white rounded-lg shadow-lg p-6 sticky top-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <span>📝</span>
                <span>Original Post</span>
              </h2>
              {post && (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-bold text-gray-900 mb-2">{post.title}</h3>
                    <div className="flex flex-wrap gap-2 text-sm text-gray-600">
                      <span className="px-2 py-1 bg-blue-100 rounded">r/{post.subreddit}</span>
                      <span className="px-2 py-1 bg-purple-100 rounded">⚡ {post.viralScore.toFixed(1)}</span>
                      <span className="px-2 py-1 bg-orange-100 rounded">↑ {post.upvotes}</span>
                      <span className="px-2 py-1 bg-gray-100 rounded">💬 {post.comments}</span>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    <p>👤 u/{post.author}</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Generated Story (70%) */}
          <div className="lg:w-2/3">
            <div className="bg-white rounded-lg shadow-lg p-6 sm:p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <span>📖</span>
                <span>Your Story</span>
              </h2>
              {story && (
                <div className="space-y-6">
                  <div className="prose prose-lg max-w-none">
                    {story.content.split('\n\n').map((paragraph, index) => (
                      <p key={index} className="text-gray-800 leading-relaxed mb-4">
                        {paragraph}
                      </p>
                    ))}
                  </div>

                  {/* Story Metadata */}
                  <div className="border-t pt-6 mt-8">
                    <h3 className="text-sm font-semibold text-gray-700 mb-3">Story Details</h3>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">Quality Score:</span>
                        <span className="px-2 py-1 bg-green-100 text-green-700 rounded font-bold">
                          {story.evaluationScore.toFixed(1)}/10
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">Rewrites:</span>
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded">
                          {story.rewriteCount}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">Word Count:</span>
                        <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded">
                          {story.content.split(/\s+/).length}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
