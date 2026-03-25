import { createFileRoute } from '@tanstack/react-router'
import {ComponentExample} from "@/components/component-example";


export const Route = createFileRoute('/report/')({
	component: ReportPage,
})

function ReportPage() {


	return (
		<ComponentExample/>
	)
}
