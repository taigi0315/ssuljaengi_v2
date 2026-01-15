import React from 'react';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import * as fc from 'fast-check';
import TimeRangeSelector from '../TimeRangeSelector';
import { TimeRangeOption } from '@/types';

describe('TimeRangeSelector Property Tests', () => {
  // Clean up after each test to prevent DOM pollution
  afterEach(() => {
    cleanup();
  });

  // Generator for valid time range values from default options
  const defaultTimeRangeValueArbitrary = fc.constantFrom('1h', '1d', '10d', '100d');

  // Feature: viral-story-search, Property 1: Time Range Selection Persistence
  // **Validates: Requirements 1.2**
  describe('Property 1: Time Range Selection Persistence', () => {
    it('should persist the selected time range across multiple interactions', () => {
      fc.assert(
        fc.property(
          defaultTimeRangeValueArbitrary,
          defaultTimeRangeValueArbitrary,
          (initialSelection, newSelection) => {
            const mockOnChange = jest.fn();
            
            // Render with initial selection
            const { rerender, unmount } = render(
              <TimeRangeSelector
                selected={initialSelection}
                onChange={mockOnChange}
              />
            );

            // Property: Initial selection should be visually highlighted
            const initialButton = screen.getByText(getButtonTextForValue(initialSelection));
            expect(initialButton).toHaveClass('bg-blue-600', 'text-white', 'border-blue-600');

            // Click on a different time range (only if different to avoid duplicate elements)
            if (initialSelection !== newSelection) {
              const newButton = screen.getByText(getButtonTextForValue(newSelection));
              fireEvent.click(newButton);

              // Property: onChange should be called with the new selection
              expect(mockOnChange).toHaveBeenCalledWith(newSelection);

              // Simulate parent component updating the selected prop
              rerender(
                <TimeRangeSelector
                  selected={newSelection}
                  onChange={mockOnChange}
                />
              );

              // Property: New selection should now be visually highlighted
              const updatedNewButton = screen.getByText(getButtonTextForValue(newSelection));
              expect(updatedNewButton).toHaveClass('bg-blue-600', 'text-white', 'border-blue-600');

              // Property: Previous selection should no longer be highlighted
              const updatedInitialButton = screen.getByText(getButtonTextForValue(initialSelection));
              expect(updatedInitialButton).toHaveClass('bg-white', 'text-gray-700', 'border-gray-300');
            } else {
              // Same selection - clicking should still call onChange
              const sameButton = screen.getByText(getButtonTextForValue(initialSelection));
              fireEvent.click(sameButton);
              expect(mockOnChange).toHaveBeenCalledWith(initialSelection);
            }

            // Clean up
            unmount();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should maintain consistent visual state for any selected time range', () => {
      fc.assert(
        fc.property(
          defaultTimeRangeValueArbitrary,
          (selectedValue) => {
            const mockOnChange = jest.fn();

            const { unmount } = render(
              <TimeRangeSelector
                selected={selectedValue}
                onChange={mockOnChange}
              />
            );

            // Property: Selected option should be highlighted
            const selectedButton = screen.getByText(getButtonTextForValue(selectedValue));
            expect(selectedButton).toHaveClass('bg-blue-600', 'text-white', 'border-blue-600');

            // Property: All other options should not be highlighted
            const allTimeRanges = ['1h', '1d', '10d', '100d'];
            allTimeRanges
              .filter(range => range !== selectedValue)
              .forEach(range => {
                const button = screen.getByText(getButtonTextForValue(range));
                expect(button).toHaveClass('bg-white', 'text-gray-700', 'border-gray-300');
              });

            // Clean up
            unmount();
          }
        ),
        { numRuns: 100 }
      );
    });
  });

  // Feature: viral-story-search, Property 2: Time Range Change Clears Results
  // **Validates: Requirements 1.4**
  describe('Property 2: Time Range Change Clears Results', () => {
    it('should trigger onChange callback for any time range selection change', () => {
      fc.assert(
        fc.property(
          defaultTimeRangeValueArbitrary,
          defaultTimeRangeValueArbitrary,
          (currentSelection, newSelection) => {
            const mockOnChange = jest.fn();

            const { unmount } = render(
              <TimeRangeSelector
                selected={currentSelection}
                onChange={mockOnChange}
              />
            );

            // Click on the new time range
            const newButton = screen.getByText(getButtonTextForValue(newSelection));
            fireEvent.click(newButton);

            // Property: onChange should always be called when a time range is clicked
            expect(mockOnChange).toHaveBeenCalledWith(newSelection);
            expect(mockOnChange).toHaveBeenCalledTimes(1);

            // Property: The callback should receive the exact value that was clicked
            expect(mockOnChange).toHaveBeenLastCalledWith(newSelection);

            // Clean up
            unmount();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should provide consistent callback behavior across all default time range options', () => {
      fc.assert(
        fc.property(
          defaultTimeRangeValueArbitrary,
          (initialSelection) => {
            const mockOnChange = jest.fn();

            const { unmount } = render(
              <TimeRangeSelector
                selected={initialSelection}
                onChange={mockOnChange}
              />
            );

            // Property: Each option click should trigger onChange with correct value
            const allTimeRanges = ['1h', '1d', '10d', '100d'];
            allTimeRanges.forEach((timeRange) => {
              mockOnChange.mockClear();
              
              const button = screen.getByText(getButtonTextForValue(timeRange));
              fireEvent.click(button);

              expect(mockOnChange).toHaveBeenCalledTimes(1);
              expect(mockOnChange).toHaveBeenCalledWith(timeRange);
            });

            // Clean up
            unmount();
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should handle sequential time range changes consistently', () => {
      fc.assert(
        fc.property(
          fc.array(defaultTimeRangeValueArbitrary, { minLength: 1, maxLength: 4 }),
          (timeRangeSequence) => {
            // Remove duplicates to avoid DOM conflicts
            const uniqueSequence = [...new Set(timeRangeSequence)];
            if (uniqueSequence.length < 2) return; // Need at least 2 different values

            const mockOnChange = jest.fn();
            const initialSelection = uniqueSequence[0];

            const { unmount } = render(
              <TimeRangeSelector
                selected={initialSelection}
                onChange={mockOnChange}
              />
            );

            // Property: Sequential clicks should each trigger onChange
            uniqueSequence.slice(1).forEach((timeRange, index) => {
              const button = screen.getByText(getButtonTextForValue(timeRange));
              fireEvent.click(button);

              // Each click should increment the call count
              expect(mockOnChange).toHaveBeenCalledTimes(index + 1);
              expect(mockOnChange).toHaveBeenLastCalledWith(timeRange);
            });

            // Property: Total calls should match the number of clicks
            expect(mockOnChange).toHaveBeenCalledTimes(uniqueSequence.length - 1);

            // Clean up
            unmount();
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  // Helper function to map time range values to button text
  function getButtonTextForValue(value: string): string {
    const mapping: Record<string, string> = {
      '1h': '1 Hour',
      '1d': '1 Day',
      '10d': '10 Days',
      '100d': '100 Days',
    };
    return mapping[value] || value;
  }
});