import { createFileRoute } from '@tanstack/react-router'

import { DefaultError } from '@/components/common/status/DefaultError'
import { DefaultNotFound } from '@/components/common/status/DefaultNotFound'
import { DefaultPending } from '@/components/common/status/DefaultPending'
import { StatusTemplateLayout } from '@/components/common/status/StatusTemplateLayout'

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
