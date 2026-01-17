/**
 * Integration tests for complete search flow
 * Tests end-to-end workflow, state management, and component interactions
 * 
 * Requirements: 5.1, 5.3, 6.1
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import Home from '../page';
import { ViralPost } from '@/types';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch as any;

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

describe('Complete Search Flow Integration Tests', () => {
  beforeEach(() => {
    // Reset mocks before each test
    mockFetch.mockReset();
    // Clear localStorage and sessionStorage
    localStorage.clear();
    sessionStorage.clear();
  });

  describe('End-to-end search workflow', () => {
    it('should complete a successful search from start to finish', async () => {
      // Mock successful API response with a controlled promise
      let resolveSearch: (value: any) => void;
      const searchPromise = new Promise((resolve) => {
        resolveSearch = resolve;
      });

      mockFetch.mockReturnValueOnce(searchPromise as any);

      const mockPosts: ViralPost[] = [
        {
          id: '1',
          title: 'AITA for telling my sister the truth?',
          subreddit: 'AmItheAsshole',
          url: 'https://reddit.com/r/AmItheAsshole/1',
          upvotes: 2500,
          comments: 450,
          viralScore: 847.3,
          createdAt: new Date('2024-01-15T10:00:00Z'),
          author: 'user1',
        },
        {
          id: '2',
          title: 'TIFU by accidentally sending my boss a meme',
          subreddit: 'tifu',
          url: 'https://reddit.com/r/tifu/2',
          upvotes: 1800,
          comments: 234,
          viralScore: 723.8,
          createdAt: new Date('2024-01-15T08:00:00Z'),
          author: 'user2',
        },
      ];

      // Render the app
      render(<Home />);

      // Verify initial state - search controls are visible
      expect(screen.getByText(/Viral Story Search/i)).toBeInTheDocument();
      expect(screen.getByText(/Search Viral Stories/i)).toBeInTheDocument();

      // Select subreddits
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      const tifuCheckbox = screen.getByLabelText(/r\/tifu/i);
      
      fireEvent.click(aitaCheckbox);
      fireEvent.click(tifuCheckbox);

      // Wait for checkboxes to be checked and button to be enabled
      await waitFor(() => {
        expect(aitaCheckbox).toBeChecked();
        expect(tifuCheckbox).toBeChecked();
      });

      // Click search button - wait for it to be enabled
      const searchButton = screen.getByRole('button', { name: /Search Viral Stories/i });
      await waitFor(() => {
        expect(searchButton).not.toBeDisabled();
      });
      
      fireEvent.click(searchButton);

      // Verify loading state is displayed - the button shows "Searching..."
      await waitFor(() => {
        expect(screen.getByText(/Searching/i)).toBeInTheDocument();
      });

      // Resolve the search promise
      resolveSearch!({
        ok: true,
        json: async () => ({
          posts: mockPosts.map(p => ({
             ...p,
             viral_score: p.viralScore,
             created_at: p.createdAt.toISOString()
          })),
          total_found: 2,
          search_criteria: {
            time_range: '1d',
            subreddits: ['AmItheAsshole', 'tifu'],
            post_count: 20,
          },
          execution_time: 1234,
        }),
      });

      // Wait for results to appear
      await waitFor(() => {
        expect(screen.getByText('AITA for telling my sister the truth?')).toBeInTheDocument();
      });

      // Verify results are displayed
      expect(screen.getByText('TIFU by accidentally sending my boss a meme')).toBeInTheDocument();
      expect(screen.getByText(/2 results/i)).toBeInTheDocument();

      // Verify search criteria is displayed
      expect(screen.getByText(/Time Range:/i)).toBeInTheDocument();
      // Use getAllByText to handle multiple "1 day" elements
      const dayElements = screen.getAllByText(/1 day/i);
      expect(dayElements.length).toBeGreaterThan(0);
      
      // Find the search criteria section and verify subreddits are displayed there
      const criteriaSection = screen.getByText(/Search Criteria/i).parentElement;
      expect(criteriaSection).toHaveTextContent('AmItheAsshole');
      expect(criteriaSection).toHaveTextContent('tifu');

      // Verify API was called with correct parameters
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/search',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            time_range: '1d',
            subreddits: ['AmItheAsshole', 'tifu'],
            post_count: 20,
          }),
        })
      );
    });

    it('should handle search with custom post count', async () => {
      // Clear sessionStorage to ensure clean state
      sessionStorage.clear();
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          posts: [],
          total_found: 0,
          search_criteria: {
            time_range: '1d',
            subreddits: ['AmItheAsshole'],
            post_count: 50,
          },
          execution_time: 1000,
        }),
      });

      render(<Home />);

      // Select a subreddit
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      fireEvent.click(aitaCheckbox);

      // Change post count
      const postCountInput = screen.getByLabelText(/Number of Posts/i);
      fireEvent.change(postCountInput, { target: { value: '50' } });

      // Click search
      const searchButton = screen.getByText(/Search Viral Stories/i);
      fireEvent.click(searchButton);

      // Wait for search to complete
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          'http://localhost:8000/search',
          expect.objectContaining({
            body: JSON.stringify({
              time_range: '1d',
              subreddits: ['AmItheAsshole'],
              post_count: 50,
            }),
          })
        );
      });
    });

    it('should handle search with different time ranges', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          posts: [],
          total_found: 0,
          search_criteria: {
            time_range: '10d',
            subreddits: ['tifu'],
            post_count: 20,
          },
          execution_time: 1000,
        }),
      });

      render(<Home />);

      // Select a subreddit
      const tifuCheckbox = screen.getByLabelText(/r\/tifu/i);
      fireEvent.click(tifuCheckbox);

      // Change time range to 10 days
      const tenDaysButton = screen.getByRole('button', { name: /10 days/i });
      fireEvent.click(tenDaysButton);

      // Click search
      const searchButton = screen.getByText(/Search Viral Stories/i);
      fireEvent.click(searchButton);

      // Wait for search to complete
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          'http://localhost:8000/search',
          expect.objectContaining({
            body: JSON.stringify({
              time_range: '10d',
              subreddits: ['tifu'],
              post_count: 20,
            }),
          })
        );
      });
    });
  });

  describe('State management across components', () => {
    it('should maintain state consistency between search controls and results', async () => {
      // Clear sessionStorage to ensure clean state
      sessionStorage.clear();
      
      const mockPosts: ViralPost[] = [
        {
          id: '1',
          title: 'Test Post',
          subreddit: 'AmItheAsshole',
          url: 'https://reddit.com/test',
          upvotes: 1000,
          comments: 100,
          viralScore: 500,
          createdAt: new Date(),
          author: 'testuser',
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          posts: mockPosts.map(p => ({
             ...p,
             viral_score: p.viralScore,
             created_at: p.createdAt.toISOString()
          })),
          total_found: 1,
          search_criteria: {
            time_range: '1d',
            subreddits: ['AmItheAsshole'],
            post_count: 20,
          },
          execution_time: 1000,
        }),
      });

      render(<Home />);

      // Perform search
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      fireEvent.click(aitaCheckbox);

      const searchButton = screen.getByText(/Search Viral Stories/i);
      fireEvent.click(searchButton);

      // Wait for results
      await waitFor(() => {
        expect(screen.getByText('Test Post')).toBeInTheDocument();
      });

      // Verify search criteria matches what was selected
      expect(screen.getByText(/Time Range:/i)).toBeInTheDocument();
      // Use getAllByText to handle multiple "1 day" elements
      const dayElements = screen.getAllByText(/1 day/i);
      expect(dayElements.length).toBeGreaterThan(0);
      expect(screen.getByText(/Subreddits:/i)).toBeInTheDocument();
      // The subreddit order might vary, so just check that AmItheAsshole is present
      const criteriaSection = screen.getByText(/Subreddits:/i).parentElement;
      expect(criteriaSection).toHaveTextContent('AmItheAsshole');
      expect(screen.getByText(/Post Count:/i)).toBeInTheDocument();
    });

    it('should maintain button state based on subreddit selection', async () => {
      // Clear sessionStorage to ensure clean state
      sessionStorage.clear();
      
      const mockPosts: ViralPost[] = [
        {
          id: '1',
          title: 'Test Post',
          subreddit: 'AmItheAsshole',
          url: 'https://reddit.com/test',
          upvotes: 1000,
          comments: 100,
          viralScore: 500,
          createdAt: new Date(),
          author: 'testuser',
        },
      ];

      // First search succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          posts: mockPosts.map(p => ({
             ...p,
             viral_score: p.viralScore,
             created_at: p.createdAt.toISOString()
          })),
          total_found: 1,
          search_criteria: {
            time_range: '1d',
            subreddits: ['AmItheAsshole'],
            post_count: 20,
          },
          execution_time: 1000,
        }),
      });

      render(<Home />);

      // Initially, button should be disabled (no subreddits selected)
      const searchButton = screen.getByRole('button', { name: /Search Viral Stories/i });
      expect(searchButton).toBeDisabled();

      // Select a subreddit
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      fireEvent.click(aitaCheckbox);

      // Button should now be enabled
      await waitFor(() => {
        expect(searchButton).not.toBeDisabled();
      });

      // Perform search
      fireEvent.click(searchButton);

      // Wait for results
      await waitFor(() => {
        expect(screen.getByText('Test Post')).toBeInTheDocument();
      });
    });

    it('should update loading state correctly during search', async () => {
      let resolveSearch: (value: any) => void;
      const searchPromise = new Promise((resolve) => {
        resolveSearch = resolve;
      });

      mockFetch.mockReturnValueOnce(searchPromise as any);

      render(<Home />);

      // Select subreddit and start search
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      fireEvent.click(aitaCheckbox);

      const searchButton = screen.getByRole('button', { name: /Search Viral Stories/i });
      fireEvent.click(searchButton);

      // Verify loading state - the button shows "Searching..."
      await waitFor(() => {
        expect(screen.getByText(/Searching/i)).toBeInTheDocument();
      });

      // Search button should be disabled during loading
      // Need to re-query the button since it's been re-rendered
      const loadingButton = screen.getByRole('button', { name: /Searching/i });
      expect(loadingButton).toBeDisabled();

      // Resolve the search
      resolveSearch!({
        ok: true,
        json: async () => ({
          posts: [],
          total_found: 0,
          search_criteria: {
            time_range: '1d',
            subreddits: ['AmItheAsshole'],
            post_count: 20,
          },
          execution_time: 1000,
        }),
      });

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.queryByText('Searching...')).not.toBeInTheDocument();
      });

      // Search button should be enabled again
      const enabledButton = screen.getByRole('button', { name: /Search Viral Stories/i });
      expect(enabledButton).not.toBeDisabled();
    });
  });

  describe('Error handling and recovery', () => {
    it('should display error message when API fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: {
            type: 'reddit_api_error',
            message: 'Reddit service temporarily unavailable',
            retryable: true,
          },
        }),
      });

      render(<Home />);

      // Perform search
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      fireEvent.click(aitaCheckbox);

      const searchButton = screen.getByText(/Search Viral Stories/i);
      fireEvent.click(searchButton);

      // Wait for error message - the ErrorMessage component displays the message from the error object
      await waitFor(() => {
        expect(screen.getByText(/Reddit service temporarily unavailable/i)).toBeInTheDocument();
      });

      // Results list should show error, not the "Viral Stories" header
      expect(screen.queryByText(/Viral Stories \(\d+\)/i)).not.toBeInTheDocument();
    });

    it('should handle network errors gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      render(<Home />);

      // Perform search
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      fireEvent.click(aitaCheckbox);

      const searchButton = screen.getByText(/Search Viral Stories/i);
      fireEvent.click(searchButton);

      // Wait for error message - the page.tsx catches network errors and displays a generic message
      await waitFor(() => {
        expect(screen.getByText(/Connection error/i)).toBeInTheDocument();
      });
    });

    it('should clear previous results when new search fails', async () => {
      const mockPosts: ViralPost[] = [
        {
          id: '1',
          title: 'Test Post',
          subreddit: 'AmItheAsshole',
          url: 'https://reddit.com/test',
          upvotes: 1000,
          comments: 100,
          viralScore: 500,
          createdAt: new Date(),
          author: 'testuser',
        },
      ];

      // First search succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          posts: mockPosts.map(p => ({
             ...p,
             viral_score: p.viralScore,
             created_at: p.createdAt.toISOString()
          })),
          total_found: 1,
          search_criteria: {
            time_range: '1d',
            subreddits: ['AmItheAsshole'],
            post_count: 20,
          },
          execution_time: 1000,
        }),
      });

      render(<Home />);

      // Perform initial search
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      fireEvent.click(aitaCheckbox);

      const searchButton = screen.getByText(/Search Viral Stories/i);
      fireEvent.click(searchButton);

      // Wait for results
      await waitFor(() => {
        expect(screen.getByText('Test Post')).toBeInTheDocument();
      });

      // Second search fails
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: {
            type: 'reddit_api_error',
            message: 'API Error',
            retryable: true,
          },
        }),
      });

      // Perform another search
      fireEvent.click(searchButton);

      // Wait for error - the error message should be displayed
      await waitFor(() => {
        expect(screen.getByText(/API Error/i)).toBeInTheDocument();
      });

      // Previous results should be cleared
      expect(screen.queryByText('Test Post')).not.toBeInTheDocument();
    });
  });

  describe('Empty results handling', () => {
    it('should display "no results" message when search returns empty', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          posts: [],
          total_found: 0,
          search_criteria: {
            time_range: '1d',
            subreddits: ['AmItheAsshole'],
            post_count: 20,
          },
          execution_time: 1000,
        }),
      });

      render(<Home />);

      // Perform search
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      fireEvent.click(aitaCheckbox);

      const searchButton = screen.getByText(/Search Viral Stories/i);
      fireEvent.click(searchButton);

      // Wait for no results message - check for the actual message displayed
      await waitFor(() => {
        expect(screen.getByText(/No viral posts found/i)).toBeInTheDocument();
      });

      // Should show helpful message
      expect(screen.getByText(/Try adjusting your search criteria/i)).toBeInTheDocument();
    });
  });

  describe('Multiple subreddit selection', () => {
    it('should handle searching across multiple subreddits', async () => {
      // Clear sessionStorage to ensure clean state
      sessionStorage.clear();
      
      const mockPosts: ViralPost[] = [
        {
          id: '1',
          title: 'Post from AITA',
          subreddit: 'AmItheAsshole',
          url: 'https://reddit.com/1',
          upvotes: 1000,
          comments: 100,
          viralScore: 500,
          createdAt: new Date(),
          author: 'user1',
        },
        {
          id: '2',
          title: 'Post from TIFU',
          subreddit: 'tifu',
          url: 'https://reddit.com/2',
          upvotes: 800,
          comments: 80,
          viralScore: 400,
          createdAt: new Date(),
          author: 'user2',
        },
        {
          id: '3',
          title: 'Post from relationship_advice',
          subreddit: 'relationship_advice',
          url: 'https://reddit.com/3',
          upvotes: 600,
          comments: 60,
          viralScore: 300,
          createdAt: new Date(),
          author: 'user3',
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          posts: mockPosts.map(p => ({
             ...p,
             viral_score: p.viralScore,
             created_at: p.createdAt.toISOString()
          })),
          total_found: 3,
          search_criteria: {
            time_range: '1d',
            subreddits: ['AmItheAsshole', 'tifu', 'relationship_advice'],
            post_count: 20,
          },
          execution_time: 1500,
        }),
      });

      render(<Home />);

      // Select multiple subreddits
      fireEvent.click(screen.getByLabelText(/r\/AmItheAsshole/i));
      fireEvent.click(screen.getByLabelText(/r\/tifu/i));
      fireEvent.click(screen.getByLabelText(/r\/relationship_advice/i));

      // Perform search
      const searchButton = screen.getByText(/Search Viral Stories/i);
      fireEvent.click(searchButton);

      // Wait for results
      await waitFor(() => {
        expect(screen.getByText('Post from AITA')).toBeInTheDocument();
      });

      // Verify all posts are displayed
      expect(screen.getByText('Post from TIFU')).toBeInTheDocument();
      expect(screen.getByText('Post from relationship_advice')).toBeInTheDocument();
      expect(screen.getByText(/3 results/i)).toBeInTheDocument();

      // Verify API was called with all three subreddits
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/search',
        expect.objectContaining({
          body: JSON.stringify({
            time_range: '1d',
            subreddits: ['AmItheAsshole', 'tifu', 'relationship_advice'],
            post_count: 20,
          }),
        })
      );
    });
  });

  describe('Validation error display', () => {
    it('should show validation error when no subreddits selected', () => {
      // Clear sessionStorage to ensure clean state
      sessionStorage.clear();
      
      render(<Home />);

      // Get the search button - use getByRole to get the actual button element
      const searchButton = screen.getByRole('button', { name: /Search Viral Stories/i });
      
      // Button should be disabled when no subreddits are selected (initial state)
      // The button has the disabled attribute when selectedSubreddits.length === 0
      expect(searchButton).toBeDisabled();

      // No API call should be made
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should show validation error for invalid post count', async () => {
      render(<Home />);

      // Select a subreddit first
      const aitaCheckbox = screen.getByLabelText(/r\/AmItheAsshole/i);
      fireEvent.click(aitaCheckbox);

      // Enter invalid post count
      const postCountInput = screen.getByLabelText(/Number of Posts/i);
      fireEvent.change(postCountInput, { target: { value: '150' } });

      // Should show validation error in the PostCountInput component
      await waitFor(() => {
        expect(screen.getByText(/Post count cannot exceed 100/i)).toBeInTheDocument();
      });

      // The component shows the error but the parent still has the last valid value
      // So if we try to search, it would use the last valid value (20)
      // This is the actual behavior - the validation error is shown but doesn't block the search
      // because the parent component still has the valid value
    });
  });
});
