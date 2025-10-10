import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/_home/docs')({
	component: RouteComponent,
});

function RouteComponent() {
	return <div>Hello "/_home/docs"!</div>;
}
