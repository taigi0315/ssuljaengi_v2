import { ErrorType, ErrorState } from '@/types';
import { ERROR_MESSAGES } from '@/lib/constants';

interface ApiError {
  status?: number;
  name?: string;
  code?: string;
  message?: string;
}

export class ErrorHandler {
  static handleApiError(error: ApiError): ErrorState {
    // Rate limit error
    if (error.status === 429) {
      return {
        type: ErrorType.RATE_LIMIT,
        message: ERROR_MESSAGES.RATE_LIMIT_EXCEEDED,
        retryable: true,
        retryAfter: 60,
      };
    }

    // Server errors
    if (error.status && error.status >= 500) {
      return {
        type: ErrorType.REDDIT_API_ERROR,
        message: ERROR_MESSAGES.REDDIT_API_UNAVAILABLE,
        retryable: true,
      };
    }

    // Network errors
    if (error.name === 'NetworkError' || error.code === 'NETWORK_ERROR') {
      return {
        type: ErrorType.NETWORK_ERROR,
        message: ERROR_MESSAGES.NETWORK_ERROR,
        retryable: true,
      };
    }

    // Timeout errors
    if (error.name === 'TimeoutError' || error.code === 'TIMEOUT') {
      return {
        type: ErrorType.TIMEOUT_ERROR,
        message: ERROR_MESSAGES.TIMEOUT_ERROR,
        retryable: true,
      };
    }

    // Default to network error for unknown errors
    return {
      type: ErrorType.NETWORK_ERROR,
      message: ERROR_MESSAGES.NETWORK_ERROR,
      retryable: true,
    };
  }

  static handleValidationError(message: string): ErrorState {
    return {
      type: ErrorType.VALIDATION_ERROR,
      message,
      retryable: false,
    };
  }
}
