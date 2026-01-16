'use client';

import { useState, useEffect } from 'react';
import { ViralPost, Story, WorkflowStatus, StoryMood } from '@/types';
import { generateStory, getStoryStatus, getStory } from '@/lib/apiClient';
import MoodSelector from './MoodSelector';
import RedditPostDisplay from './RedditPostDisplay';

interface StoryBuilderProps {
  post: ViralPost;
  onGenerateImages?: (storyId: string) => void;
}

export default function StoryBuilder({ post, onGenerateImages }: StoryBuilderProps) {
  const [selectedMood, setSelectedMood] = useState<StoryMood | null>(null);
  const [story, setStory] = useState<Story | null>(null);
  const [status, setStatus] = useState<WorkflowStatus | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [workflowId, setWorkflowId] = useState<string | null>(null);

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
  const handleGenerateStory = async () => {
    if (!selectedMood) return;

    try {
      setIsGenerating(true);
      setError(null);
      setStory(null);

      const response = await generateStory({
        postId: post.id,
        postTitle: post.title,
        postContent: post.title, // Using title as content for now
        mood: selectedMood,
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
      setIsGenerating(false);
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
        setIsGenerating(false);
      }

      // If failed, show error
      if (statusData.status === 'failed') {
        setError(statusData.error || 'Story generation failed');
        setIsGenerating(false);
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
    setIsGenerating(false);
  };

  return (
    <div className="space-y-6">
      {/* Selected Post Display */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span>📝</span>
          <span>Selected Post</span>
        </h2>
        <RedditPostDisplay post={post} />
      </div>

      {/* Mood Selection */}
      {!story && !isGenerating && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <MoodSelector
            selectedMood={selectedMood}
            onMoodSelect={setSelectedMood}
          />

          {/* Generate Button */}
          <div className="mt-6 text-center">
            <button
              onClick={handleGenerateStory}
              disabled={!selectedMood}
              className={`
                px-8 py-4 rounded-lg font-bold text-lg transition-all
                ${selectedMood
                  ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-xl hover:scale-105'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }
              `}
            >
              {selectedMood ? '✨ Create Story' : '👆 Select a mood first'}
            </button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isGenerating && !story && (
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {status?.currentStep || 'Preparing'}...
            </h2>
            <p className="text-gray-600 mb-4">
              {status?.currentStep === 'writing' && 'Creating your story from the Reddit post'}
              {status?.currentStep === 'evaluating' && 'Reviewing story quality'}
              {status?.currentStep === 'rewriting' && 'Improving the story based on feedback'}
              {!status?.currentStep && 'Starting story generation'}
            </p>
            {status?.progress !== undefined && (
              <div className="w-full max-w-md mx-auto bg-gray-200 rounded-full h-3 mb-2">
                <div
                  className="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${status.progress * 100}%` }}
                ></div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center">
            <div className="text-6xl mb-4">❌</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Story Generation Failed
            </h2>
            <p className="text-red-600 mb-6">{error}</p>
            <button
              onClick={handleRetry}
              className="px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Generated Story Display */}
      {story && (
        <div className="bg-white rounded-lg shadow-lg p-6 sm:p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <span>📖</span>
            <span>Your Story</span>
          </h2>
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

            {/* Generate Another Button */}
            <div className="flex gap-4 justify-center pt-4">
              <button
                onClick={handleRetry}
                className="px-6 py-3 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 transition-all"
              >
                🔄 Generate Another Story
              </button>
              
              {onGenerateImages && (
                <button
                  onClick={() => onGenerateImages(story.id)}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
                >
                  🎨 Generate Images
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
