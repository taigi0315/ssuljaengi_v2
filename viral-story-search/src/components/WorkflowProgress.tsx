import React from 'react';
import { WorkflowProgressProps } from '@/types';

const WorkflowProgress: React.FC<WorkflowProgressProps> = ({ status }) => {
  if (!status) {
    return (
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mb-4"></div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Preparing...</h2>
        <p className="text-gray-600">Starting story generation</p>
      </div>
    );
  }

  const getStepMessage = (step: string) => {
    switch (step.toLowerCase()) {
      case 'writing':
        return 'Creating your story from the Reddit post';
      case 'evaluating':
      case 'evaluated':
        return 'Reviewing story quality';
      case 'rewriting':
        return 'Improving the story based on feedback';
      default:
        return 'Processing...';
    }
  };

  const getStepIcon = (step: string) => {
    switch (step.toLowerCase()) {
      case 'writing':
        return '✍️';
      case 'evaluating':
      case 'evaluated':
        return '🔍';
      case 'rewriting':
        return '✨';
      default:
        return '⚙️';
    }
  };

  return (
    <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl p-8">
      <div className="text-center">
        {/* Spinner */}
        <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mb-4"></div>
        
        {/* Current Step */}
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center justify-center gap-2">
          <span className="text-3xl">{getStepIcon(status.currentStep)}</span>
          <span>{status.currentStep}...</span>
        </h2>
        
        {/* Step Message */}
        <p className="text-gray-600 mb-6">
          {getStepMessage(status.currentStep)}
        </p>

        {/* Progress Bar */}
        {status.progress !== undefined && (
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div
              className="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${status.progress * 100}%` }}
            ></div>
          </div>
        )}

        {/* Progress Percentage */}
        <p className="text-sm text-gray-500">
          {Math.round((status.progress || 0) * 100)}% complete
        </p>

        {/* Workflow Steps Indicator */}
        <div className="mt-8 flex justify-center items-center gap-4">
          <div className={`flex flex-col items-center ${status.currentStep.toLowerCase() === 'writing' ? 'text-purple-600' : 'text-gray-400'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${status.currentStep.toLowerCase() === 'writing' ? 'bg-purple-100' : 'bg-gray-100'}`}>
              ✍️
            </div>
            <span className="text-xs mt-1 font-semibold">Write</span>
          </div>
          
          <div className="w-8 h-0.5 bg-gray-300"></div>
          
          <div className={`flex flex-col items-center ${status.currentStep.toLowerCase().includes('evaluat') ? 'text-purple-600' : 'text-gray-400'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${status.currentStep.toLowerCase().includes('evaluat') ? 'bg-purple-100' : 'bg-gray-100'}`}>
              🔍
            </div>
            <span className="text-xs mt-1 font-semibold">Evaluate</span>
          </div>
          
          <div className="w-8 h-0.5 bg-gray-300"></div>
          
          <div className={`flex flex-col items-center ${status.currentStep.toLowerCase() === 'rewriting' ? 'text-purple-600' : 'text-gray-400'}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${status.currentStep.toLowerCase() === 'rewriting' ? 'bg-purple-100' : 'bg-gray-100'}`}>
              ✨
            </div>
            <span className="text-xs mt-1 font-semibold">Refine</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowProgress;
