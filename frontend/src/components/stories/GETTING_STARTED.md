# Getting Started with Frontend Development

## Quick Start

This guide will help you get up and running with the frontend development environment quickly.

### Prerequisites

Before you begin, ensure you have:

- **Node.js 18+** (use `node --version` to check)
- **npm or yarn** package manager
- **Git** for version control
- **VS Code** (recommended) with extensions:
  - ES7+ React/Redux/React-Native snippets
  - TypeScript Importer
  - Prettier - Code formatter
  - Auto Rename Tag
  - Bracket Pair Colorizer

### Installation Steps

1. **Navigate to the frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server:**

   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open your browser:**
   - Go to `http://localhost:5173`
   - You should see the application running

### Development Workflow

#### File Structure Overview

```
src/
├── components/          # Reusable components
│   └── ui/             # Base UI components (Cards, Buttons, etc.)
├── routes/             # Page components (TanStack Router)
├── hooks/              # Custom React hooks
├── services/           # API services and utilities
├── client/             # Generated OpenAPI client
├── assets/             # Static assets
└── main.tsx           # Application entry point
```

#### Making Your First Change

1. **Edit a component:**

   ```bash
   # Open the dashboard file
   code src/routes/_home/dashboard.tsx
   ```

2. **Make a small change:**
   - Find a text element and change its content
   - Save the file (Ctrl+S)

3. **See the change:**
   - Your browser should automatically reload
   - If not, refresh the page

#### Working with Components

**Create a new component:**

```tsx
// src/components/MyComponent.tsx
import { Box, Text } from '@chakra-ui/react'

interface MyComponentProps {
	message: string
}

export function MyComponent({ message }: MyComponentProps) {
	return (
		<Box p={4} bg='blue.50' borderRadius='md'>
			<Text>{message}</Text>
		</Box>
	)
}
```

**Use it in another component:**

```tsx
import { MyComponent } from '../components/MyComponent'

function SomePage() {
	return (
		<div>
			<MyComponent message='Hello, World!' />
		</div>
	)
}
```

### Common Tasks

#### Adding a New Page

1. Create a new file in `src/routes/`
2. Export a component with the page content
3. The router will automatically pick it up

#### Styling with Chakra UI

```tsx
// Use Chakra UI props for styling
<Box
	bg='white' // Background color
	p={6} // Padding
	borderRadius='lg' // Border radius
	shadow='md' // Box shadow
>
	<Text fontSize='xl' fontWeight='bold' color='blue.500'>
		Styled text
	</Text>
</Box>
```

#### Making API Calls

```tsx
import { useQuery } from '@tanstack/react-query'
import { ApiService } from '../client'

function MyComponent() {
	const { data, isLoading, error } = useQuery({
		queryKey: ['my-data'],
		queryFn: () => ApiService.getData(),
	})

	if (isLoading) return <div>Loading...</div>
	if (error) return <div>Error: {error.message}</div>

	return <div>{JSON.stringify(data)}</div>
}
```

### Debugging

#### Browser Developer Tools

- **F12** to open DevTools
- **Console tab**: Check for JavaScript errors
- **Network tab**: Monitor API requests
- **Elements tab**: Inspect HTML and CSS

#### React DevTools

1. Install the React DevTools browser extension
2. Open DevTools and find the "React" tab
3. Inspect component props and state

#### Common Issues

**Port already in use:**

```bash
# Kill process on port 5173
npx kill-port 5173
# or use a different port
npm run dev -- --port 3000
```

**Module not found:**

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors:**

```bash
# Check TypeScript compilation
npx tsc --noEmit
```

### Next Steps

Once you're comfortable with the basics:

1. **Read the component documentation** → `docs/components/`
2. **Learn about API integration** → `docs/api/`
3. **Follow tutorials** → `docs/tutorials/`
4. **Understand the project architecture** → `docs/guides/ARCHITECTURE.md`

### Getting Help

- **Documentation**: Check the `docs/` folder for detailed guides
- **Code Examples**: Look at existing components in `src/components/`
- **API Reference**: Generated docs at `http://localhost/docs` (when backend is running)
- **Community**: Ask questions in team chat or create GitHub issues

### Useful Commands

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format

# Run tests
npm run test

# Generate API client
npm run generate-client
```

Happy coding! 🚀
