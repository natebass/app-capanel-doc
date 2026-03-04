# Frontend Documentation

This directory contains documentation for the frontend application components and patterns.

## Available Documentation

### 📋 [Chakra UI Cards Documentation](./CHAKRA_UI_CARDS.md)

Comprehensive guide covering:

- **Card Component API** - Props, variants, and subcomponents
- **Implementation Examples** - Statistics cards, activity feeds, quick actions
- **Dashboard Patterns** - Real-world usage in the dashboard route
- **Best Practices** - Responsive design, accessibility, performance
- **Advanced Patterns** - Loading states, interactive cards, menus
- **Troubleshooting** - Common issues and solutions

### Key Features Covered

✅ **Three Card Variants**

- `outline` - Clean border design (default)
- `filled` - Solid background emphasis
- `elevated` - Subtle shadow for depth

✅ **Component Structure**

- `Card` - Root container
- `CardHeader` - Title and actions
- `CardBody` - Main content area
- `CardFooter` - Secondary actions

✅ **Dashboard Examples**

- Statistics grid with KPI metrics
- Real-time activity feed
- Quick actions panel
- System status indicators
- Performance metrics
- Storage usage visualization

✅ **Production Ready**

- TypeScript support
- Responsive design
- Accessibility features
- Performance optimizations

## Quick Start

```tsx
import { Card, CardHeader, CardBody, CardFooter } from '../components/ui/card'

function ExampleCard() {
	return (
		<Card variant='elevated'>
			<CardHeader>
				<Heading size='md'>Dashboard Stats</Heading>
			</CardHeader>
			<CardBody>
				<Text>Your content here</Text>
			</CardBody>
			<CardFooter>
				<Button colorScheme='blue'>Action</Button>
			</CardFooter>
		</Card>
	)
}
```

## Live Examples

View the implemented dashboard with all card examples at:

- Route: `/_home/dashboard`
- File: `src/routes/_home/index.tsx`

## Component Location

- Card component: `src/components/ui/card.tsx`
- TypeScript definitions included
- Full Chakra UI Box props support

---

For questions or contributions to the documentation, please refer to the main project README.
