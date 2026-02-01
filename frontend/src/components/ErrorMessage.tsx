'use client';

import React from 'react';
import { ErrorState, ErrorType } from '@/types';

export interface ErrorMessageProps {
  error: ErrorState | string | null;
  onRetry?: () => void;
}

/**
 * ErrorMessage Component
 * 
 * Displays error messages with different styles based on error type.
 * Provides retry functionality for recoverable errors.
 * 
 * Requirements: 8.1, 8.2, 8.3, 8.5
 */
export default function ErrorMessage({ error, onRetry }: ErrorMessageProps) {
  if (!error) {
    return null;
  }

  // Handle string errors (simple error messages)
  if (typeof error === 'string') {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 shadow-md animate-pulse">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg
              className="h-6 w-6 text-red-400"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3 flex-1">
            <p className="text-sm font-semibold text-red-800">{error}</p>
          </div>
          {onRetry && (
            <div className="ml-3 flex-shrink-0">
              <button
                onClick={onRetry}
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-semibold rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all transform hover:scale-105 active:scale-95"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Handle structured ErrorState objects
  const { type, message, retryable, retryAfter } = error;

  // Get error-specific styling and icon
  const getErrorStyles = () => {
    switch (type) {
      case ErrorType.VALIDATION_ERROR:
        return {
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          textColor: 'text-yellow-800',
          iconColor: 'text-yellow-400',
          buttonBg: 'bg-yellow-100',
          buttonHover: 'hover:bg-yellow-200',
          buttonText: 'text-yellow-700',
          buttonRing: 'focus:ring-yellow-500',
        };
      case ErrorType.RATE_LIMIT:
        return {
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
          textColor: 'text-orange-800',
          iconColor: 'text-orange-400',
          buttonBg: 'bg-orange-100',
          buttonHover: 'hover:bg-orange-200',
          buttonText: 'text-orange-700',
          buttonRing: 'focus:ring-orange-500',
        };
      case ErrorType.NETWORK_ERROR:
      case ErrorType.TIMEOUT_ERROR:
      case ErrorType.REDDIT_API_ERROR:
      default:
        return {
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-800',
          iconColor: 'text-red-400',
          buttonBg: 'bg-red-100',
          buttonHover: 'hover:bg-red-200',
          buttonText: 'text-red-700',
          buttonRing: 'focus:ring-red-500',
        };
    }
  };

  const styles = getErrorStyles();

  // Get user-friendly error title
  const getErrorTitle = () => {
    switch (type) {
      case ErrorType.REDDIT_API_ERROR:
        return 'Reddit Service Unavailable';
      case ErrorType.RATE_LIMIT:
        return 'Too Many Requests';
      case ErrorType.NETWORK_ERROR:
        return 'Connection Error';
      case ErrorType.VALIDATION_ERROR:
        return 'Invalid Input';
      case ErrorType.TIMEOUT_ERROR:
        return 'Request Timeout';
      default:
        return 'Error';
    }
  };

  // Get specific error message based on type
  const getErrorMessage = () => {
    switch (type) {
      case ErrorType.REDDIT_API_ERROR:
        return message || 'Reddit service temporarily unavailable. Please try again later.';
      case ErrorType.RATE_LIMIT:
        return retryAfter
          ? `Too many requests. Please wait ${retryAfter} seconds before trying again.`
          : 'Too many requests. Please wait before trying again.';
      case ErrorType.NETWORK_ERROR:
        return message || 'Connection error. Please check your internet connection.';
      case ErrorType.VALIDATION_ERROR:
        return message || 'Please check your input and try again.';
      case ErrorType.TIMEOUT_ERROR:
        return message || 'Request timed out. Please try again.';
      default:
        return message || 'An unexpected error occurred.';
    }
  };

  return (
    <div
      className={`${styles.bgColor} border-2 ${styles.borderColor} rounded-lg p-4 shadow-md`}
      role="alert"
    >
      <div className="flex items-start">
        {/* Error Icon */}
        <div className="flex-shrink-0">
          {type === ErrorType.VALIDATION_ERROR ? (
            <svg
              className={`h-6 w-6 ${styles.iconColor}`}
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
          ) : type === ErrorType.RATE_LIMIT ? (
            <svg
              className={`h-6 w-6 ${styles.iconColor}`}
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            <svg
              className={`h-6 w-6 ${styles.iconColor}`}
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>

        {/* Error Content */}
        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-bold ${styles.textColor}`}>
            {getErrorTitle()}
          </h3>
          <p className={`mt-1 text-sm ${styles.textColor}`}>
            {getErrorMessage()}
          </p>
        </div>

        {/* Retry Button */}
        {retryable && onRetry && (
          <div className="ml-3 flex-shrink-0">
            <button
              onClick={onRetry}
              className={`
                inline-flex items-center px-3 py-1.5 border border-transparent 
                text-xs font-semibold rounded-md ${styles.buttonText} ${styles.buttonBg} 
                ${styles.buttonHover} focus:outline-none focus:ring-2 
                focus:ring-offset-2 ${styles.buttonRing} transition-all
                transform hover:scale-105 active:scale-95
              `}
              aria-label="Retry the operation"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
