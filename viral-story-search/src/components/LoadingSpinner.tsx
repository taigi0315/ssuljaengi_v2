'use client';

import React from 'react';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  message?: string;
  submessage?: string;
}

/**
 * LoadingSpinner Component
 * 
 * Displays an animated loading spinner with optional message.
 * Provides visual feedback during async operations.
 * 
 * Requirements: 5.2, 7.5
 */
export default function LoadingSpinner({ 
  size = 'md', 
  message = 'Loading...', 
  submessage 
}: LoadingSpinnerProps) {
  // Size configurations
  const sizeClasses = {
    sm: 'h-8 w-8 border-2',
    md: 'h-12 w-12 border-3',
    lg: 'h-16 w-16 border-4',
    xl: 'h-24 w-24 border-4'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
    xl: 'text-xl'
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4 py-8">
      {/* Spinner */}
      <div className="relative">
        <div
          className={`
            ${sizeClasses[size]}
            animate-spin rounded-full 
            border-blue-200 border-t-blue-600
          `}
          role="status"
          aria-label="Loading"
        >
          <span className="sr-only">Loading...</span>
        </div>
        
        {/* Pulse effect */}
        <div
          className={`
            ${sizeClasses[size]}
            absolute inset-0 rounded-full 
            border-blue-300 animate-ping opacity-20
          `}
        />
      </div>

      {/* Message */}
      {message && (
        <p className={`${textSizeClasses[size]} text-gray-700 font-semibold animate-pulse`}>
          {message}
        </p>
      )}

      {/* Submessage */}
      {submessage && (
        <p className="text-sm text-gray-500 animate-pulse">
          {submessage}
        </p>
      )}

      {/* Loading dots animation */}
      <div className="flex space-x-2">
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
    </div>
  );
}
