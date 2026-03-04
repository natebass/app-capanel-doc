import { createFileRoute } from '@tanstack/react-router'

import { DefaultError } from '@/components/status/DefaultError'
import { DefaultNotFound } from '@/components/status/DefaultNotFound'
import { DefaultPending } from '@/components/status/DefaultPending'
import { StatusTemplateLayout } from '@/components/status/StatusTemplateLayout'

export const Route = createFileRoute('/_status')({
	component: StatusTemplateLayout,
	head: () => ({
		meta: [{ title: 'Status - FastAPI Cloud' }],
	}),
	// Route-specific status handlers for the _status user group
	// These provide a consistent experience within the status section
	notFoundComponent: () => <DefaultNotFound fullPage={false} />,
	errorComponent: ({ error, reset, info }) => (
		<DefaultError error={error} reset={reset} info={info} fullPage={false} />
	),
	pendingComponent: () => (
		<DefaultPending fullPage={false} variant='card' message='Loading status...' />
	),
})
