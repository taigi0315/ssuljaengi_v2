import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import * as fc from 'fast-check';
import SubredditSelector from '../SubredditSelector';
import { SubredditOption } from '@/types';

// Mock sessionStorage for testing
const mockSessionStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

// Replace the global sessionStorage with our mock
Object.defineProperty(window, 'sessionStorage', {
  value: mockSessionStorage,
});

describe('SubredditSelector Property Tests', () => {
  const defaultSubreddits: SubredditOption[] = [
    {
      name: 'AmItheAsshole',
      displayName: 'r/AmItheAsshole',
      description: 'Moral judgment stories',
      isPopular: true
    },
    {
      name: 'relationship_advice',
      displayName: 'r/relationship_advice',
      description: 'Relationship guidance and stories',
      isPopular: true
    },
    {
      name: 'tifu',
      displayName: 'r/tifu',
      description: 'Today I F***ed Up stories',
      isPopular: true
    },
    {
      name: 'confession',
      displayName: 'r/confession',
      description: 'Personal confessions',
      isPopular: true
    },
    {
      name: 'pettyrevenge',
      displayName: 'r/pettyrevenge',
      description: 'Small revenge stories',
      isPopular: true
    },
    {
      name: 'maliciouscompliance',
      displayName: 'r/maliciouscompliance',
      description: 'Following rules to the letter',
      isPopular: true
    }
  ];

  // Clean up after each test
  afterEach(() => {
    cleanup();
    mockSessionStorage.clear();
    jest.clearAllMocks();
  });

  // Clean up before each test to ensure isolation
  beforeEach(() => {
    cleanup();
    mockSessionStorage.clear();
    jest.clearAllMocks();
  });

  // Generator for valid subreddit names from default list
  const subredditNameArbitrary = fc.constantFrom(
    'AmItheAsshole',
    'relationship_advice',
    'tifu',
    'confession',
    'pettyrevenge',
    'maliciouscompliance'
  );

  // Generator for arrays of subreddit names
  const subredditArrayArbitrary = fc.array(subredditNameArbitrary, { minLength: 0, maxLength: 6 });

  // Feature: viral-story-search, Property 3: Subreddit Toggle Behavior
  // **Validates: Requirements 2.2**
  describe('Property 3: Subreddit Toggle Behavior', () => {
    it('should toggle subreddit selection state when checkbox is clicked', () => {
      fc.assert(
        fc.property(
          subredditArrayArbitrary,
          subredditNameArbitrary,
          (initialSelected, targetSubreddit) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            mockSessionStorage.clear();
            jest.clearAllMocks();

            const mockOnChange = jest.fn();
            const uniqueInitialSelected = [...new Set(initialSelected)];

            const { unmount } = render(
              <SubredditSelector
                selected={uniqueInitialSelected}
                onChange={mockOnChange}
                availableSubreddits={defaultSubreddits}
              />
            );

            // Find the checkbox for the target subreddit using a more specific selector
            const targetOption = defaultSubreddits.find(sub => sub.name === targetSubreddit);
            if (!targetOption) {
              unmount();
              return;
            }

            // Use a more specific query to avoid conflicts
            const checkboxes = screen.getAllByRole('checkbox');
            const targetCheckbox = checkboxes.find(checkbox => {
              const label = checkbox.closest('label');
              return label && label.textContent?.includes(targetOption.displayName);
            });

            if (!targetCheckbox) {
              unmount();
              return;
            }

            const wasSelected = uniqueInitialSelected.includes(targetSubreddit);

            // Click the checkbox
            fireEvent.click(targetCheckbox);

            // Property: onChange should be called exactly once
            expect(mockOnChange).toHaveBeenCalledTimes(1);

            // Property: If subreddit was selected, it should be removed from the array
            // If it wasn't selected, it should be added to the array
            const expectedNewSelection = wasSelected
              ? uniqueInitialSelected.filter(name => name !== targetSubreddit)
              : [...uniqueInitialSelected, targetSubreddit];

            expect(mockOnChange).toHaveBeenCalledWith(expectedNewSelection);

            // Clean up immediately after test
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should maintain correct checkbox states for any selection combination', () => {
      fc.assert(
        fc.property(
          subredditArrayArbitrary,
          (selectedSubreddits) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            mockSessionStorage.clear();
            jest.clearAllMocks();

            const mockOnChange = jest.fn();
            const uniqueSelected = [...new Set(selectedSubreddits)];

            const { unmount } = render(
              <SubredditSelector
                selected={uniqueSelected}
                onChange={mockOnChange}
                availableSubreddits={defaultSubreddits}
              />
            );

            // Property: Each checkbox should reflect the correct selection state
            const checkboxes = screen.getAllByRole('checkbox');
            defaultSubreddits.forEach((subreddit, index) => {
              const checkbox = checkboxes[index];
              const shouldBeChecked = uniqueSelected.includes(subreddit.name);
              
              if (shouldBeChecked) {
                expect(checkbox).toBeChecked();
              } else {
                expect(checkbox).not.toBeChecked();
              }
            });

            // Property: Selection count should be displayed correctly
            // The count is now in a separate span, so we need to check for the container
            const container = screen.getByText(/Selected:/i).parentElement;
            expect(container).toHaveTextContent(`Selected: ${uniqueSelected.length}`);

            // Clean up immediately after test
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should handle multiple sequential toggle operations correctly', () => {
      fc.assert(
        fc.property(
          fc.array(subredditNameArbitrary, { minLength: 1, maxLength: 6 }),
          (toggleSequence) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            mockSessionStorage.clear();
            jest.clearAllMocks();

            const mockOnChange = jest.fn();
            let currentSelection: string[] = [];

            const { rerender, unmount } = render(
              <SubredditSelector
                selected={currentSelection}
                onChange={mockOnChange}
                availableSubreddits={defaultSubreddits}
              />
            );

            // Property: Each toggle should call onChange and produce a valid selection
            toggleSequence.forEach((subredditName) => {
              const targetOption = defaultSubreddits.find(sub => sub.name === subredditName);
              if (!targetOption) return;

              // Find and click the checkbox
              const targetIndex = defaultSubreddits.findIndex(sub => sub.name === subredditName);
              const checkboxes = screen.getAllByRole('checkbox');
              const checkbox = checkboxes[targetIndex];
              
              if (!checkbox) return;

              const callsBefore = mockOnChange.mock.calls.length;
              
              fireEvent.click(checkbox);

              // Property: onChange should be called after each click
              expect(mockOnChange.mock.calls.length).toBeGreaterThan(callsBefore);

              // Get the latest value passed to onChange
              const latestCall = mockOnChange.mock.calls[mockOnChange.mock.calls.length - 1];
              const actualNewSelection = latestCall[0];
              
              // Property: The new selection should be an array
              expect(Array.isArray(actualNewSelection)).toBe(true);
              
              // Property: The new selection should not contain duplicates
              const uniqueSelection = [...new Set(actualNewSelection)];
              expect(actualNewSelection.length).toBe(uniqueSelection.length);
              
              // Update our tracking to match what the component actually did
              currentSelection = actualNewSelection;

              // Re-render with the actual selection from the component
              rerender(
                <SubredditSelector
                  selected={currentSelection}
                  onChange={mockOnChange}
                  availableSubreddits={defaultSubreddits}
                />
              );
            });

            // Clean up immediately after test
            unmount();
            cleanup();
          }
        ),
        { numRuns: 50 }
      );
    });
  });

  // Feature: viral-story-search, Property 4: Session Subreddit Persistence
  // **Validates: Requirements 2.5**
  describe('Property 4: Session Subreddit Persistence', () => {
    it('should save selection to sessionStorage when subreddits are selected', () => {
      fc.assert(
        fc.property(
          subredditArrayArbitrary.filter(arr => arr.length > 0), // Only non-empty arrays
          (selectedSubreddits) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            mockSessionStorage.clear();
            jest.clearAllMocks();

            const mockOnChange = jest.fn();
            const uniqueSelected = [...new Set(selectedSubreddits)];

            const { unmount } = render(
              <SubredditSelector
                selected={uniqueSelected}
                onChange={mockOnChange}
                availableSubreddits={defaultSubreddits}
              />
            );

            // Property: sessionStorage.setItem should be called with the selection
            expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
              'selectedSubreddits',
              JSON.stringify(uniqueSelected)
            );

            // Clean up immediately after test
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should remove from sessionStorage when no subreddits are selected', () => {
      fc.assert(
        fc.property(
          fc.constant([]), // Empty array
          (emptySelection) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            mockSessionStorage.clear();
            jest.clearAllMocks();

            const mockOnChange = jest.fn();

            const { unmount } = render(
              <SubredditSelector
                selected={emptySelection}
                onChange={mockOnChange}
                availableSubreddits={defaultSubreddits}
              />
            );

            // Property: sessionStorage.removeItem should be called when selection is empty
            expect(mockSessionStorage.removeItem).toHaveBeenCalledWith('selectedSubreddits');

            // Clean up immediately after test
            unmount();
            cleanup();
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should load saved selection from sessionStorage on mount when current selection is empty', () => {
      fc.assert(
        fc.property(
          subredditArrayArbitrary.filter(arr => arr.length > 0), // Only non-empty arrays
          (savedSelection) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            mockSessionStorage.clear();
            jest.clearAllMocks();

            const mockOnChange = jest.fn();
            const uniqueSaved = [...new Set(savedSelection)];

            // Pre-populate sessionStorage with saved selection
            mockSessionStorage.setItem('selectedSubreddits', JSON.stringify(uniqueSaved));

            const { unmount } = render(
              <SubredditSelector
                selected={[]} // Start with empty selection
                onChange={mockOnChange}
                availableSubreddits={defaultSubreddits}
              />
            );

            // Property: onChange should be called with the saved selection from sessionStorage
            expect(mockOnChange).toHaveBeenCalledWith(uniqueSaved);

            // Property: sessionStorage.getItem should be called to retrieve saved selection
            expect(mockSessionStorage.getItem).toHaveBeenCalledWith('selectedSubreddits');

            // Clean up immediately after test
            unmount();
            cleanup();
          }
        ),
        { numRuns: 100 }
      );
    });

    it('should persist selection changes across component re-renders', () => {
      fc.assert(
        fc.property(
          subredditNameArbitrary,
          subredditNameArbitrary,
          (firstSubreddit, secondSubreddit) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            mockSessionStorage.clear();
            jest.clearAllMocks();

            const mockOnChange = jest.fn();
            let currentSelection: string[] = [];

            const { rerender, unmount } = render(
              <SubredditSelector
                selected={currentSelection}
                onChange={mockOnChange}
                availableSubreddits={defaultSubreddits}
              />
            );

            // Select first subreddit using index-based approach
            const firstIndex = defaultSubreddits.findIndex(sub => sub.name === firstSubreddit);
            if (firstIndex === -1) {
              unmount();
              cleanup();
              return;
            }

            const checkboxes = screen.getAllByRole('checkbox');
            const firstCheckbox = checkboxes[firstIndex];
            fireEvent.click(firstCheckbox);

            // Update selection and re-render
            currentSelection = [firstSubreddit];
            rerender(
              <SubredditSelector
                selected={currentSelection}
                onChange={mockOnChange}
                availableSubreddits={defaultSubreddits}
              />
            );

            // Property: sessionStorage should contain the first selection
            expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
              'selectedSubreddits',
              JSON.stringify([firstSubreddit])
            );

            // Select second subreddit (if different)
            if (firstSubreddit !== secondSubreddit) {
              const secondIndex = defaultSubreddits.findIndex(sub => sub.name === secondSubreddit);
              if (secondIndex === -1) {
                unmount();
                cleanup();
                return;
              }

              const updatedCheckboxes = screen.getAllByRole('checkbox');
              const secondCheckbox = updatedCheckboxes[secondIndex];
              fireEvent.click(secondCheckbox);

              // Update selection and re-render
              currentSelection = [firstSubreddit, secondSubreddit];
              rerender(
                <SubredditSelector
                  selected={currentSelection}
                  onChange={mockOnChange}
                  availableSubreddits={defaultSubreddits}
                />
              );

              // Property: sessionStorage should contain both selections
              expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
                'selectedSubreddits',
                JSON.stringify([firstSubreddit, secondSubreddit])
              );
            }

            // Clean up immediately after test
            unmount();
            cleanup();
          }
        ),
        { numRuns: 50 }
      );
    });

    it('should handle invalid sessionStorage data gracefully', () => {
      fc.assert(
        fc.property(
          fc.oneof(
            fc.constant('invalid json'),
            fc.constant('{"not": "array"}'),
            fc.constant('null'),
            fc.constant('')
          ),
          (invalidData) => {
            // Ensure proper cleanup before each property test iteration
            cleanup();
            mockSessionStorage.clear();
            jest.clearAllMocks();

            const mockOnChange = jest.fn();

            // Pre-populate sessionStorage with invalid data
            mockSessionStorage.getItem.mockReturnValue(invalidData);

            const { unmount } = render(
              <SubredditSelector
                selected={[]}
                onChange={mockOnChange}
                availableSubreddits={defaultSubreddits}
              />
            );

            // Property: Component should not crash with invalid sessionStorage data
            const subredditLabel = screen.getAllByText(/Subreddits/i)[0];
            expect(subredditLabel).toBeInTheDocument();

            // Property: onChange should not be called with invalid data
            // The component handles invalid JSON gracefully and doesn't call onChange
            expect(mockOnChange).not.toHaveBeenCalled();

            // Clean up immediately after test
            unmount();
            cleanup();
          }
        ),
        { numRuns: 50 }
      );
    });
  });
});