# Gossiptoon V2 - Frontend

A modern Next.js application for discovering viral Reddit stories and transforming them into webtoon-style visual content.

---

## 🚀 Features

| Feature                       | Description                                                 |
| ----------------------------- | ----------------------------------------------------------- |
| **Reddit Story Search**       | Search and rank viral stories across multiple subreddits    |
| **Story Generation**          | AI-powered story transformation with mood selection         |
| **Webtoon Script Builder**    | Interactive script creation with character and scene panels |
| **Character Image Generator** | Generate and customize character designs                    |
| **Scene Image Generator**     | Create scene images with character references               |
| **Video Generator**           | Assemble final video from generated assets                  |

---

## 🛠️ Tech Stack

| Technology        | Version | Purpose                         |
| ----------------- | ------- | ------------------------------- |
| Next.js           | 16.1    | React framework with App Router |
| React             | 19.2    | UI library                      |
| TypeScript        | 5.x     | Type safety                     |
| TailwindCSS       | 4.x     | Styling                         |
| Jest              | 30.x    | Testing                         |
| ESLint + Prettier | Latest  | Code quality                    |

---

## 📋 Prerequisites

- Node.js 18+
- npm 9+

---

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd viral-story-search
npm install
```

### 2. Configure Environment

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open http://localhost:3000

---

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Main search page
│   ├── story/             # Story pages
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/             # React components
│   ├── SearchControls.tsx # Search interface
│   ├── StoryBuilder.tsx   # Story generation
│   ├── ScriptPreview.tsx  # Webtoon script view
│   ├── CharacterImageGenerator.tsx
│   ├── SceneImageGeneratorV2.tsx
│   ├── VideoGenerator.tsx
│   └── ...                # Other components
├── hooks/                  # Custom React hooks
├── lib/                    # Configuration & API client
├── types/                  # TypeScript definitions
└── utils/                  # Utility functions
    ├── viralScore.ts      # Viral score calculation
    ├── validation.ts      # Input validation
    └── errorHandler.ts    # Error handling
```

---

## 📜 Available Scripts

| Command                 | Description              |
| ----------------------- | ------------------------ |
| `npm run dev`           | Start development server |
| `npm run build`         | Build for production     |
| `npm start`             | Start production server  |
| `npm test`              | Run tests                |
| `npm run test:watch`    | Run tests in watch mode  |
| `npm run test:coverage` | Run tests with coverage  |
| `npm run lint`          | Run ESLint               |
| `npm run lint:fix`      | Fix lint errors          |
| `npm run format`        | Format with Prettier     |
| `npm run format:check`  | Check formatting         |

---

## 🧪 Testing

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

### Testing Strategy

| Type                     | Focus                                   |
| ------------------------ | --------------------------------------- |
| **Unit Tests**           | Business logic in utils/                |
| **Property-Based Tests** | Algorithmic correctness with fast-check |
| **Component Tests**      | React components with Testing Library   |

---

## 🎨 UI Components

### Main Components

| Component                 | Description                              |
| ------------------------- | ---------------------------------------- |
| `SearchControls`          | Subreddit and time range selection       |
| `ResultsList`             | Display search results with viral scores |
| `StoryBuilder`            | Story generation with mood selection     |
| `ScriptPreview`           | Webtoon script viewer with panels        |
| `CharacterImageGenerator` | Character design interface               |
| `CharacterImageDisplay`   | Character gallery with variations        |
| `SceneImageGeneratorV2`   | Scene image creation with references     |
| `VideoGenerator`          | Video assembly and download              |

### Utility Components

| Component          | Description                 |
| ------------------ | --------------------------- |
| `LoadingSpinner`   | Loading state indicator     |
| `ErrorMessage`     | Error display with retry    |
| `WorkflowProgress` | Multi-step workflow tracker |

---

## 🔧 Development Guidelines

### Code Style

- TypeScript strict mode enabled
- ESLint + Prettier for formatting
- All components use TypeScript
- Props should be typed with interfaces

### Best Practices

1. Keep components focused and reusable
2. Use custom hooks for shared logic
3. Handle loading and error states
4. Write tests for business logic
5. Use semantic HTML elements

---

## 🐛 Troubleshooting

### Development Server Issues

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
npm install
```

### API Connection Issues

1. Verify backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Ensure no CORS errors in browser console

### Build Errors

```bash
# Check TypeScript errors
npx tsc --noEmit

# Check lint errors
npm run lint
```
