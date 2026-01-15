# Requirements Document

## Introduction

The Viral Story Search system enables users to discover the most viral Reddit stories within specified time ranges across selected subreddits. The system calculates virality using a formula based on engagement metrics and presents results in an intuitive web interface.

## Glossary

- **System**: The Viral Story Search application
- **User**: Person using the application to find viral stories
- **Viral_Score**: Calculated metric determining story virality based on upvotes, comments, and time
- **Subreddit**: Reddit community (e.g., r/AmItheAsshole, r/relationship_advice)
- **Time_Range**: Period for searching posts (1 hour, 1 day, 10 days, 100 days)
- **Post_Count**: Number of top viral posts to retrieve and display
- **Reddit_API**: Reddit's API for fetching post data

## Requirements

### Requirement 1: Time Range Selection

**User Story:** As a user, I want to select different time ranges for searching viral stories, so that I can find recent trending content or discover older viral posts.

#### Acceptance Criteria

1. WHEN a user visits the search interface, THE System SHALL display time range options: 1 hour, 1 day, 10 days, and 100 days
2. WHEN a user selects a time range, THE System SHALL highlight the selected option and use it for subsequent searches
3. THE System SHALL default to 1 day time range on initial load
4. WHEN a time range is changed, THE System SHALL clear previous search results

### Requirement 2: Subreddit Selection

**User Story:** As a user, I want to select which subreddits to include in my search, so that I can focus on communities that interest me.

#### Acceptance Criteria

1. THE System SHALL display a list of popular subreddits as checkboxes
2. WHEN a user clicks a subreddit checkbox, THE System SHALL toggle its inclusion in the search
3. THE System SHALL include at least these subreddits: r/AmItheAsshole, r/relationship_advice, r/tifu, r/confession, r/pettyrevenge, r/maliciouscompliance
4. WHEN no subreddits are selected, THE System SHALL prevent search execution and display a warning message
5. THE System SHALL remember selected subreddits during the session

### Requirement 3: Post Count Configuration

**User Story:** As a user, I want to specify how many viral posts to retrieve, so that I can control the amount of content displayed.

#### Acceptance Criteria

1. THE System SHALL provide an input field for specifying post count
2. WHEN a user enters a post count, THE System SHALL validate it is between 1 and 100
3. THE System SHALL default to 20 posts
4. WHEN an invalid post count is entered, THE System SHALL display an error message and prevent search

### Requirement 4: Viral Score Calculation

**User Story:** As a system administrator, I want the system to calculate viral scores using engagement metrics, so that the most engaging content is prioritized.

#### Acceptance Criteria

1. THE System SHALL calculate viral score using the formula: (upvotes + comments * 2) / (hours_since_posted + 1)
2. WHEN retrieving posts, THE System SHALL sort results by viral score in descending order
3. THE System SHALL only include posts with minimum 10 upvotes and 5 comments
4. THE System SHALL exclude posts marked as removed or deleted by moderators

### Requirement 5: Search Execution

**User Story:** As a user, I want to execute searches with my selected criteria, so that I can find viral stories matching my preferences.

#### Acceptance Criteria

1. WHEN a user clicks the search button with valid criteria, THE System SHALL fetch posts from selected subreddits within the time range
2. WHEN search is executing, THE System SHALL display a loading indicator
3. WHEN search completes successfully, THE System SHALL display results sorted by viral score
4. WHEN search fails due to API errors, THE System SHALL display an error message with retry option
5. THE System SHALL complete searches within 30 seconds or timeout with appropriate message

### Requirement 6: Results Display

**User Story:** As a user, I want to see search results with post details, so that I can evaluate and access interesting stories.

#### Acceptance Criteria

1. WHEN displaying results, THE System SHALL show post title, subreddit, viral score, upvotes, comments, and post age
2. WHEN a user clicks on a post title, THE System SHALL open the original Reddit post in a new tab
3. THE System SHALL display results in a clean, readable list format
4. WHEN no results are found, THE System SHALL display a "No viral posts found" message
5. THE System SHALL display the search criteria used for the current results

### Requirement 7: User Interface Design

**User Story:** As a user, I want an intuitive and responsive interface, so that I can easily configure searches and view results on any device.

#### Acceptance Criteria

1. THE System SHALL provide a responsive design that works on desktop, tablet, and mobile devices
2. THE System SHALL use clear visual hierarchy with search controls at the top and results below
3. WHEN the interface loads, THE System SHALL display all controls in an accessible and organized layout
4. THE System SHALL use consistent styling and follow modern web design principles
5. THE System SHALL provide visual feedback for all user interactions (hover states, loading states, etc.)

### Requirement 8: Error Handling

**User Story:** As a user, I want clear error messages when something goes wrong, so that I understand what happened and how to proceed.

#### Acceptance Criteria

1. WHEN Reddit API is unavailable, THE System SHALL display "Reddit service temporarily unavailable" message
2. WHEN API rate limits are exceeded, THE System SHALL display "Too many requests, please wait" message with countdown
3. WHEN network errors occur, THE System SHALL display "Connection error, please check your internet" message
4. WHEN invalid search parameters are provided, THE System SHALL highlight the problematic fields with specific error messages
5. THE System SHALL provide a "Try Again" button for recoverable errors