import React from 'react';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import * as fc from 'fast-check';
import PostCountInput from '../PostCountInput';

describe('PostCountInput Property Tests', () => {
  // Clean up after each test to prevent DOM pollution
  afterEach(() => {
    cleanup();
  });

  // Clean up before each test to ensure isolation
  beforeEach(() => {
    cleanup();
  });

  // Generator for valid post count values (1-100)
  const validPostCountArbitrary = fc.integer({ min: 1, max: 100 });

  // Generator for invalid post count values (outside 1-100 range)
  const invalidPostCountArbitrary = fc.oneof(
    fc.integer({ min: -1000, max: 0 }), // Negative and zero values
    fc.integer({ min: 101, max: 1000 }) // Values above maximum
  );

  // Generator for non-numeric strings (excluding decimal numbers which parseInt can handle)
  const nonNumericStringArbitrary = fc.oneof(
    fc.string().filter(s => isNaN(parseInt(s, 10))),
    fc.constantFrom('abc', 'test', 'NaN', 'Infinity', '-Infinity', '', 'hello123world')
  );

  // Feature: viral-story-search, Property 5: Post Count Validation
  // **Validates: Requirements 3.2**
  describe('Property 5: Post Count Validation', () => {
    it('should accept any valid post count value between 1 and 100', () => {
      fc.assert(
        fc.property(
          validPostCountArbitrary,
          (validCount) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            
            const mockOnChange = jest.fn();
            const mockError = undefined;

            const { unmount } = render(
              <PostCountInput
                value={20} // Start with default
                onChange={mockOnChange}
                error={mockError}
              />
            );

            // Find the input field using ID to avoid conflicts
            const input = screen.getByDisplayValue('20') as HTMLInputElement;

            // Clear and enter the valid count
            fireEvent.change(input, { target: { value: validCount.toString() } });

            // Property: Valid values should not show validation errors
            const errorElements = screen.queryAllByText(/Post count must be at least|Post count cannot exceed|Please enter a valid number/);
            expect(errorElements).toHaveLength(0);

            // Property: onChange should be called with valid values (unless it's the same as current value)
            if (validCount !== 20) {
              expect(mockOnChange).toHaveBeenCalledWith(validCount);
            }

            // Property: Input should display the entered value
            expect(input.value).toBe(validCount.toString());

            // Clean up immediately
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should reject invalid post count values outside the 1-100 range', () => {
      fc.assert(
        fc.property(
          invalidPostCountArbitrary,
          (invalidCount) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            
            const mockOnChange = jest.fn();
            const mockError = undefined;

            const { unmount } = render(
              <PostCountInput
                value={20} // Start with default
                onChange={mockOnChange}
                error={mockError}
              />
            );

            // Find the input field using ID to avoid conflicts
            const input = screen.getByDisplayValue('20') as HTMLInputElement;

            // Clear and enter the invalid count
            fireEvent.change(input, { target: { value: invalidCount.toString() } });

            // Property: Invalid values should show validation errors
            let hasValidationError = false;
            
            if (invalidCount <= 0) {
              const errorElement = screen.queryByText(/Post count must be at least 1/);
              hasValidationError = errorElement !== null;
            } else if (invalidCount > 100) {
              const errorElement = screen.queryByText(/Post count cannot exceed 100/);
              hasValidationError = errorElement !== null;
            }

            expect(hasValidationError).toBe(true);

            // Property: onChange should not be called with invalid values
            // (mockOnChange might be called initially with default value, but not with invalid value)
            const changeCallsWithInvalidValue = mockOnChange.mock.calls.filter(
              call => call[0] === invalidCount
            );
            expect(changeCallsWithInvalidValue).toHaveLength(0);

            // Clean up immediately
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should handle non-numeric input values correctly', () => {
      fc.assert(
        fc.property(
          nonNumericStringArbitrary,
          (nonNumericValue) => {
            // Skip empty strings as they have special handling
            if (nonNumericValue === '') return;

            // Ensure proper cleanup before each property test iteration
            cleanup();
            
            const mockOnChange = jest.fn();
            const mockError = undefined;

            const { unmount } = render(
              <PostCountInput
                value={20} // Start with default
                onChange={mockOnChange}
                error={mockError}
              />
            );

            // Find the input field using ID to avoid conflicts
            const input = screen.getByDisplayValue('20') as HTMLInputElement;

            // Clear and enter the non-numeric value
            fireEvent.change(input, { target: { value: nonNumericValue } });

            // Property: Non-numeric values should show validation error
            const errorElement = screen.queryByText(/Please enter a valid number/);
            expect(errorElement).toBeInTheDocument();

            // Property: onChange should not be called with non-numeric values
            const changeCallsWithNonNumeric = mockOnChange.mock.calls.filter(
              call => isNaN(call[0])
            );
            expect(changeCallsWithNonNumeric).toHaveLength(0);

            // Clean up immediately
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should reset to default value on blur when input is invalid', () => {
      fc.assert(
        fc.property(
          fc.oneof(
            invalidPostCountArbitrary,
            nonNumericStringArbitrary.filter(s => s !== '' && isNaN(parseInt(s, 10)))
          ),
          (invalidInput) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            
            const mockOnChange = jest.fn();
            const mockError = undefined;

            const { unmount } = render(
              <PostCountInput
                value={20} // Start with default
                onChange={mockOnChange}
                error={mockError}
              />
            );

            // Find the input field using ID to avoid conflicts
            const input = screen.getByDisplayValue('20') as HTMLInputElement;

            // Enter invalid input
            fireEvent.change(input, { target: { value: invalidInput.toString() } });

            // Trigger blur event
            fireEvent.blur(input);

            // Property: Input should reset to default value (20) after blur with invalid input
            expect(input.value).toBe('20');

            // Property: onChange should be called with default value after reset
            expect(mockOnChange).toHaveBeenCalledWith(20);

            // Property: Validation error should be cleared after reset
            const errorElements = screen.queryAllByText(/Post count must be at least|Post count cannot exceed|Please enter a valid number/);
            expect(errorElements).toHaveLength(0);

            // Clean up immediately
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // Feature: viral-story-search, Property 6: Invalid Input Error Display
  // **Validates: Requirements 3.4**
  describe('Property 6: Invalid Input Error Display', () => {
    it('should display appropriate error messages for any invalid input', () => {
      fc.assert(
        fc.property(
          fc.oneof(
            fc.integer({ min: -100, max: 0 }), // Below minimum
            fc.integer({ min: 101, max: 200 }), // Above maximum
            fc.constantFrom('abc', 'test', 'NaN', 'hello') // Non-numeric (excluding decimals)
          ),
          (invalidInput) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            
            const mockOnChange = jest.fn();
            const mockError = undefined;

            const { unmount } = render(
              <PostCountInput
                value={20} // Start with default
                onChange={mockOnChange}
                error={mockError}
              />
            );

            // Find the input field using ID to avoid conflicts
            const input = screen.getByDisplayValue('20') as HTMLInputElement;

            // Enter invalid input
            fireEvent.change(input, { target: { value: invalidInput.toString() } });

            // Property: Error message should be displayed for invalid input
            let expectedErrorFound = false;
            
            if (typeof invalidInput === 'number') {
              if (invalidInput <= 0) {
                const errorElement = screen.queryByText(/Post count must be at least 1/);
                expectedErrorFound = errorElement !== null;
              } else if (invalidInput > 100) {
                const errorElement = screen.queryByText(/Post count cannot exceed 100/);
                expectedErrorFound = errorElement !== null;
              }
            } else {
              // Non-numeric input (that parseInt can't parse)
              if (isNaN(parseInt(invalidInput, 10))) {
                const errorElement = screen.queryByText(/Please enter a valid number/);
                expectedErrorFound = errorElement !== null;
              }
            }

            expect(expectedErrorFound).toBe(true);

            // Property: Error should be displayed in a styled error container
            const errorContainer = screen.queryByText(/Post count must be at least|Post count cannot exceed|Please enter a valid number/)?.closest('div');
            if (errorContainer) {
              expect(errorContainer).toHaveClass('text-red-600');
            }

            // Clean up immediately
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should prevent search execution by not calling onChange with invalid values', () => {
      fc.assert(
        fc.property(
          fc.oneof(
            invalidPostCountArbitrary,
            nonNumericStringArbitrary.filter(s => s !== '') // Exclude empty string
          ),
          (invalidInput) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            
            const mockOnChange = jest.fn();
            const mockError = undefined;

            const { unmount } = render(
              <PostCountInput
                value={20} // Start with default
                onChange={mockOnChange}
                error={mockError}
              />
            );

            // Find the input field using ID to avoid conflicts
            const input = screen.getByDisplayValue('20') as HTMLInputElement;

            // Clear previous calls
            mockOnChange.mockClear();

            // Enter invalid input
            fireEvent.change(input, { target: { value: invalidInput.toString() } });

            // Property: onChange should not be called with invalid values
            // This prevents search execution with invalid parameters
            const invalidCalls = mockOnChange.mock.calls.filter(call => {
              const value = call[0];
              return typeof value === 'number' && (value < 1 || value > 100 || isNaN(value));
            });
            expect(invalidCalls).toHaveLength(0);

            // Property: If onChange was called, it should only be with valid values
            mockOnChange.mock.calls.forEach(call => {
              const value = call[0];
              expect(typeof value).toBe('number');
              expect(value).toBeGreaterThanOrEqual(1);
              expect(value).toBeLessThanOrEqual(100);
              expect(Number.isFinite(value)).toBe(true);
            });

            // Clean up immediately
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should display external error messages when provided via props', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(
            'This is an error message',
            'Invalid input provided',
            'Server error occurred',
            'Network connection failed',
            'Please try again later'
          ),
          validPostCountArbitrary,
          (externalError, validValue) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            
            const mockOnChange = jest.fn();

            const { unmount } = render(
              <PostCountInput
                value={validValue}
                onChange={mockOnChange}
                error={externalError}
              />
            );

            // Property: External error should be displayed even with valid input
            const errorElement = screen.queryByText(externalError);
            expect(errorElement).toBeInTheDocument();

            // Property: Error should be displayed in styled error container
            const errorContainer = errorElement?.closest('div');
            if (errorContainer) {
              expect(errorContainer).toHaveClass('text-red-600');
            }

            // Property: Input field should have error styling when external error is present
            const input = screen.getByDisplayValue(validValue.toString()) as HTMLInputElement;
            expect(input).toHaveClass('border-red-300');

            // Clean up immediately
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should display external errors when provided, even with invalid input', () => {
      fc.assert(
        fc.property(
          fc.constantFrom(
            'External error message',
            'API call failed',
            'Network timeout',
            'Server unavailable',
            'Please check connection'
          ),
          fc.integer({ min: -50, max: -1 }), // Only negative numbers
          (externalError, invalidValue) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            
            const mockOnChange = jest.fn();

            const { unmount } = render(
              <PostCountInput
                value={20} // Start with valid value
                onChange={mockOnChange}
                error={externalError}
              />
            );

            // Find the input field using ID to avoid conflicts
            const input = screen.getByDisplayValue('20') as HTMLInputElement;

            // Enter invalid input
            fireEvent.change(input, { target: { value: invalidValue.toString() } });

            // Property: External error should be displayed (takes priority over validation errors)
            const externalErrorElement = screen.queryByText(externalError);
            expect(externalErrorElement).toBeInTheDocument();

            // Property: Validation errors should not be visible when external error is present
            const validationErrors = screen.queryAllByText(/Post count must be at least|Post count cannot exceed|Please enter a valid number/);
            expect(validationErrors.length).toBe(0);

            // Clean up immediately
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should clear validation errors when valid input is entered', () => {
      fc.assert(
        fc.property(
          invalidPostCountArbitrary,
          validPostCountArbitrary,
          (invalidValue, validValue) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            
            const mockOnChange = jest.fn();
            const mockError = undefined;

            const { unmount } = render(
              <PostCountInput
                value={20} // Start with default
                onChange={mockOnChange}
                error={mockError}
              />
            );

            // Find the input field using ID to avoid conflicts
            const input = screen.getByDisplayValue('20') as HTMLInputElement;

            // First, enter invalid input to trigger error
            fireEvent.change(input, { target: { value: invalidValue.toString() } });

            // Verify error is displayed
            let errorDisplayed = false;
            if (invalidValue <= 0) {
              errorDisplayed = screen.queryByText(/Post count must be at least 1/) !== null;
            } else if (invalidValue > 100) {
              errorDisplayed = screen.queryByText(/Post count cannot exceed 100/) !== null;
            }
            expect(errorDisplayed).toBe(true);

            // Then, enter valid input
            fireEvent.change(input, { target: { value: validValue.toString() } });

            // Property: Validation error should be cleared when valid input is entered
            const errorElements = screen.queryAllByText(/Post count must be at least|Post count cannot exceed|Please enter a valid number/);
            expect(errorElements).toHaveLength(0);

            // Property: Input should not have error styling with valid input
            expect(input).not.toHaveClass('border-red-300');
            expect(input).toHaveClass('border-gray-300');

            // Clean up immediately
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});