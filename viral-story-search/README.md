# Viral Story Search

A Next.js application that discovers and ranks the most engaging Reddit stories across multiple subreddits within user-specified time ranges.

## Features

- Search viral Reddit stories across popular subreddits
- Custom viral score calculation based on engagement metrics
- Responsive design with TailwindCSS
- TypeScript for type safety
- Comprehensive testing with Jest and property-based testing

## Tech Stack

- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Testing**: Jest, React Testing Library, fast-check (property-based testing)
- **Linting**: ESLint with Next.js config
- **Formatting**: Prettier

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

### Development

```bash
# Start development server
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run linting
npm run lint

# Format code
npm run format

# Build for production
npm run build
```

## Project Structure

```
src/
├── app/                 # Next.js app router pages
├── components/          # React components
├── lib/                 # Configuration and constants
├── types/               # TypeScript type definitions
└── utils/               # Utility functions
    ├── viralScore.ts    # Viral score calculation
    ├── validation.ts    # Input validation
    └── errorHandler.ts  # Error handling utilities
```

## Core Types

The application uses comprehensive TypeScript interfaces for:
- Search criteria and configuration
- Reddit API data structures
- Viral post data models
- Error handling states
- Component props

## Testing Strategy

- **Unit Tests**: Core business logic and utilities
- **Property-Based Tests**: Universal properties using fast-check
- **Integration Tests**: Component interactions and API integration

## Development Guidelines

- All code is formatted with Prettier
- ESLint enforces code quality standards
- TypeScript strict mode enabled
- Comprehensive test coverage required
- Property-based testing for algorithmic correctness

## License

MIT