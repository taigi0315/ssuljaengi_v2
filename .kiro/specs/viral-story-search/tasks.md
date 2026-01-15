# Implementation Plan: Viral Story Search

## Overview

This implementation plan creates a Reddit viral story finder with a Next.js frontend and REST API backend. The system allows users to search for viral Reddit posts across multiple subreddits with configurable time ranges and post counts.

## Tasks

- [x] 1. Set up project structure and core interfaces
  - Create Next.js project with TypeScript and TailwindCSS
  - Set up project directory structure (components, pages, api, types)
  - Define core TypeScript interfaces and types
  - Configure ESLint, Prettier, and testing framework
  - _Requirements: 7.1, 7.4_

- [x] 2. Implement Reddit API client and viral score calculation
  - [x] 2.1 Create Reddit API client module
    - Implement RedditApiClient class with fetchPosts method
    - Add error handling for API failures and rate limiting
    - Configure API endpoints and authentication
    - _Requirements: 5.1, 8.1, 8.2_

  - [x] 2.2 Write property test for Reddit API client
    - **Property 10: Search Execution with Valid Criteria**
    - **Validates: Requirements 5.1**

  - [x] 2.3 Implement viral score calculation algorithm
    - Create calculateViralScore function with the specified formula
    - Add post filtering logic (minimum upvotes/comments, exclude removed posts)
    - Implement post ranking and sorting functionality
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 2.4 Write property tests for viral score calculation
    - **Property 7: Viral Score Calculation**
    - **Property 8: Results Sorting by Viral Score**
    - **Property 9: Post Filtering Criteria**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [-] 3. Create search API endpoint
  - [x] 3.1 Implement POST /api/search endpoint
    - Create API route handler for search requests
    - Add request validation and error handling
    - Integrate Reddit API client and viral score calculation
    - Implement response formatting and caching
    - _Requirements: 5.1, 5.3, 5.4, 5.5_

  - [x] 3.2 Write property tests for search API
    - **Property 13: API Error Handling**
    - **Validates: Requirements 5.4**

  - [x] 3.3 Write unit tests for API endpoint
    - Test successful search responses
    - Test error handling for various failure scenarios
    - Test request validation
    - _Requirements: 5.1, 5.3, 5.4_

- [x] 4. Build search controls components
  - [x] 4.1 Create TimeRangeSelector component
    - Implement time range selection UI (1h, 1d, 10d, 100d)
    - Add selection highlighting and state management
    - Set default to 1 day time range
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 4.2 Write property tests for time range selection
    - **Property 1: Time Range Selection Persistence**
    - **Property 2: Time Range Change Clears Results**
    - **Validates: Requirements 1.2, 1.4**

  - [x] 4.3 Create SubredditSelector component
    - Implement checkbox list for subreddit selection
    - Add toggle functionality and session persistence
    - Include required subreddits (AITA, relationship_advice, etc.)
    - Add validation to prevent search with no subreddits selected
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 4.4 Write property tests for subreddit selection
    - **Property 3: Subreddit Toggle Behavior**
    - **Property 4: Session Subreddit Persistence**
    - **Validates: Requirements 2.2, 2.5**

  - [x] 4.5 Create PostCountInput component
    - Implement post count input field with validation
    - Set default value to 20 posts
    - Add validation for range 1-100 with error messages
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 4.6 Write property tests for post count validation
    - **Property 5: Post Count Validation**
    - **Property 6: Invalid Input Error Display**
    - **Validates: Requirements 3.2, 3.4**

- [x] 5. Checkpoint - Ensure search controls work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Build results display components
  - [x] 6.1 Create ResultsList component
    - Implement results container with loading and error states
    - Add empty results handling
    - Display search criteria used for current results
    - _Requirements: 6.3, 6.4, 6.5_

  - [x] 6.2 Create ResultItem component
    - Implement individual result display with all required fields
    - Add clickable post titles that open Reddit links in new tabs
    - Format viral score, upvotes, comments, and post age
    - _Requirements: 6.1, 6.2_

  - [ ]* 6.3 Write property tests for results display
    - **Property 14: Result Item Information Completeness**
    - **Property 15: Post Title Link Behavior**
    - **Property 16: Search Criteria Display**
    - **Validates: Requirements 6.1, 6.2, 6.5**

- [x] 7. Implement main search functionality
  - [x] 7.1 Create SearchControls container component
    - Integrate all search control components
    - Implement search execution logic
    - Add loading state management during searches
    - _Requirements: 5.2, 7.5_

  - [ ]* 7.2 Write property tests for search controls
    - **Property 11: Loading State Display**
    - **Property 12: Successful Search Result Display**
    - **Property 17: User Interaction Visual Feedback**
    - **Validates: Requirements 5.2, 5.3, 7.5**

  - [x] 7.3 Create main App component
    - Integrate SearchControls and ResultsList components
    - Implement global state management for search data
    - Add responsive layout and styling
    - _Requirements: 7.1, 7.2_

  - [x] 7.4 Write integration tests for complete search flow
    - Test end-to-end search workflow
    - Test state management across components
    - Test responsive behavior
    - _Requirements: 5.1, 5.3, 6.1_

- [x] 8. Implement error handling and validation
  - [x] 8.1 Create ErrorMessage component
    - Implement error display with different error types
    - Add retry functionality for recoverable errors
    - Include specific error messages for different scenarios
    - _Requirements: 8.1, 8.2, 8.3, 8.5_

  - [x] 8.2 Add comprehensive input validation
    - Implement client-side validation for all inputs
    - Add field highlighting for validation errors
    - Create validation error display system
    - _Requirements: 8.4_

  - [ ]* 8.3 Write property tests for error handling
    - **Property 18: Validation Error Field Highlighting**
    - **Property 19: Recoverable Error Retry Option**
    - **Validates: Requirements 8.4, 8.5**

  - [ ]* 8.4 Write unit tests for error scenarios
    - Test specific error messages for different error types
    - Test retry functionality
    - Test validation error display
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 9. Add styling and responsive design
  - [x] 9.1 Implement responsive layout with TailwindCSS
    - Create mobile-first responsive design
    - Add proper spacing, typography, and color scheme
    - Implement hover states and visual feedback
    - _Requirements: 7.1, 7.2, 7.4, 7.5_

  - [x] 9.2 Add loading spinners and visual indicators
    - Create loading spinner component
    - Add visual feedback for all user interactions
    - Implement smooth transitions and animations
    - _Requirements: 5.2, 7.5_

- [x] 10. Performance optimization and caching
  - [x] 10.1 Implement search result caching
    - Add client-side caching for search results
    - Implement cache invalidation strategies
    - Add request debouncing for search inputs
    - _Requirements: 5.5_

  - [x] 10.2 Optimize API requests
    - Implement parallel requests for multiple subreddits
    - Add request timeout handling
    - Optimize data processing and sorting
    - _Requirements: 5.1, 5.5_

- [x] 11. Final integration and testing
  - [x] 11.1 Integration testing and bug fixes
    - Test complete application workflow
    - Fix any integration issues
    - Verify all requirements are met
    - _Requirements: All_

  - [ ]* 11.2 Write comprehensive property-based test suite
    - Ensure all 19 correctness properties are implemented
    - Run property tests with minimum 100 iterations each
    - Verify test coverage meets requirements
    - **Validates: All correctness properties**

- [x] 12. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties using fast-check library
- Unit tests validate specific examples and edge cases
- Integration tests verify complete user workflows
- The system uses Next.js with TypeScript for type safety and modern development practices