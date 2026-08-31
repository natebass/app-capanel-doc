/**
 * The accountability report — the layer caschooldashboard.org actually shows.
 *
 * Where /dashboard reports what students scored, this reports how the state
 * judged a school: one performance colour per indicator, the student groups
 * beneath it, and the history behind it.
 *
 * Five of the seven indicators here (chronic absenteeism, suspension,
 * graduation, college/career, English learner progress) have no assessment
 * source at all — they come from the state's own Dashboard files.
 *
 * The selection lives in the URL, so any view of this report is a link.
 */
import { useQuery } from '@tanstack/react-query'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useMemo } from 'react'
import { z } from 'zod'

import { IndicatorCard } from '@/components/accountability/IndicatorCard'
import { IndicatorTrend } from '@/components/accountability/IndicatorTrend'
import { StudentGroupBreakdown } from '@/components/accountability/StudentGroupBreakdown'
import NavbarD52 from '@/components/common/navbar/navbar-D52'
import { LocalMeasures } from '@/components/local-indicators/LocalMeasures'
import { EntityPicker } from '@/components/results/EntityPicker'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { EntityPublic } from '@/lib/client'
import {
	type AccountabilitySelection,
	ALL_STUDENTS,
	dashboardCatalogQuery,
	indicatorGroupsQuery,
	indicatorsQuery,
	STATEWIDE_CDS,
} from '@/lib/services/accountability'
import { entityQuery } from '@/lib/services/assessments'
import ScrollReset from '@/routes/-hooks/hooks/ScrollReset'

/**
 * The router parses search values as JSON, so a CDS code that looks like a
 * number comes back as one. It is a code, not a quantity, so it is coerced
 * back to a string here.
 */
const searchSchema = z.object({
	cds: z.coerce.string().length(14).default(STATEWIDE_CDS),
	year: z.coerce.number().int().optional(),
	studentGroup: z.coerce.string().default(ALL_STUDENTS),
	indicator: z.coerce.string().optional(),
})

export const Route = createFileRoute('/accountability/')({
	validateSearch: searchSchema,
	component: AccountabilityPage,
})

function AccountabilityPage() {
	const search = Route.useSearch()
	const navigate = useNavigate({ from: Route.fullPath })

	const catalog = useQuery(dashboardCatalogQuery(search.year))
	const ancestry = useQuery(entityQuery(search.cds))

	const year = search.year ?? catalog.data?.reportingYear
	const selection: AccountabilitySelection | undefined = year
		? { cds: search.cds, year, studentGroup: search.studentGroup }
		: undefined

	const indicators = useQuery({
		...indicatorsQuery(selection ?? ({} as AccountabilitySelection)),
		enabled: Boolean(selection),
	})

	const entity = ancestry.data?.entity

	const selectedIndicator = useMemo(
		() => search.indicator ?? indicators.data?.results[0]?.indicatorCode,
		[search.indicator, indicators.data],
	)

	const indicatorMeta = catalog.data?.indicators.find((item) => item.code === selectedIndicator)

	const groups = useQuery({
		...indicatorGroupsQuery(selection ?? ({} as AccountabilitySelection), selectedIndicator ?? ''),
		enabled: Boolean(selection && selectedIndicator),
	})

	/** Base UI needs the value-to-label mapping to render the closed trigger. */
	const yearItems = useMemo(
		() =>
			(catalog.data?.years ?? []).map((item) => ({
				value: String(item),
				label: `${item - 1}\u2013${String(item).slice(2)}`,
			})),
		[catalog.data],
	)

	const groupItems = useMemo(
		() =>
			(catalog.data?.studentGroups ?? []).map((group) => ({
				value: group.code,
				label: group.name,
			})),
		[catalog.data],
	)

	const groupNames = useMemo(
		() =>
			Object.fromEntries(
				(catalog.data?.studentGroups ?? []).map((group) => [group.code, group.name]),
			),
		[catalog.data],
	)

	function update(next: Partial<z.infer<typeof searchSchema>>) {
		void navigate({ search: (previous) => ({ ...previous, ...next }) })
	}

	function chooseEntity(next: EntityPublic) {
		update({ cds: next.cdsCode })
	}

	if (catalog.isPending) {
		return (
			<>
				<NavbarD52 />
				<main className='mx-auto w-full max-w-6xl space-y-6 px-4 py-8'>
					<Skeleton className='h-10 w-96' />
					<Skeleton className='h-24 w-full' />
					<Skeleton className='h-64 w-full' />
				</main>
			</>
		)
	}

	if (catalog.error) {
		return (
			<>
				<NavbarD52 />
				<main className='mx-auto w-full max-w-6xl px-4 py-8'>
					<Alert variant='destructive'>
						<AlertTitle>No accountability data</AlertTitle>
						<AlertDescription>
							{catalog.error.message} Run <code>uv run app/scripts/ingest_dashboard_files.py</code>{' '}
							to load the state's Dashboard files.
						</AlertDescription>
					</Alert>
				</main>
			</>
		)
	}

	return (
		<>
			<ScrollReset />
			<NavbarD52 />
			<main className='mx-auto w-full max-w-6xl space-y-8 px-4 py-8'>
				<header className='space-y-3'>
					<div className='space-y-1'>
						<h1 className='text-2xl font-semibold tracking-tight'>
							{entity?.displayName ?? 'California'}
						</h1>
						<p className='text-sm text-muted-foreground'>
							{ancestry.data?.ancestors.map((item) => item.displayName).join(' · ') ||
								'Statewide accountability'}
						</p>
					</div>
					<div className='flex flex-wrap items-center gap-2'>
						<EntityPicker entity={entity} onSelect={chooseEntity} />
						{search.cds !== STATEWIDE_CDS ? (
							<Button variant='ghost' size='sm' onClick={() => update({ cds: STATEWIDE_CDS })}>
								Back to statewide
							</Button>
						) : null}
						{entity?.isCharter ? <Badge variant='outline'>Charter school</Badge> : null}
					</div>
				</header>

				<Card>
					<CardContent className='grid gap-4 pt-6 sm:grid-cols-2'>
						<div className='space-y-1.5'>
							<Label htmlFor='accountability-year'>Year</Label>
							<Select
								items={yearItems}
								value={String(year ?? '')}
								onValueChange={(value) => update({ year: Number(value) })}
							>
								<SelectTrigger id='accountability-year' className='w-full'>
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									{yearItems.map((item) => (
										<SelectItem key={item.value} value={item.value}>
											{item.label}
										</SelectItem>
									))}
								</SelectContent>
							</Select>
						</div>
						<div className='space-y-1.5'>
							<Label htmlFor='accountability-group'>Student group</Label>
							<Select
								items={groupItems}
								value={search.studentGroup}
								onValueChange={(value) => value && update({ studentGroup: value })}
							>
								<SelectTrigger id='accountability-group' className='w-full'>
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									{groupItems.map((item) => (
										<SelectItem key={item.value} value={item.value}>
											{item.label}
										</SelectItem>
									))}
								</SelectContent>
							</Select>
						</div>
					</CardContent>
				</Card>

				{indicators.data?.includesProjections ? (
					<Alert>
						<AlertTitle>Some figures are projections</AlertTitle>
						<AlertDescription>
							The state has not published the Dashboard for this year yet. Anything marked{' '}
							<strong>Projected</strong> was worked out from the underlying data using the state's
							published cut points, and may differ from the figure the state eventually publishes.
						</AlertDescription>
					</Alert>
				) : null}

				{indicators.isPending ? (
					<Skeleton className='h-48 w-full' />
				) : indicators.error ? (
					<Alert variant='destructive'>
						<AlertDescription>{indicators.error.message}</AlertDescription>
					</Alert>
				) : indicators.data && indicators.data.results.length > 0 ? (
					<section className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
						{indicators.data.results.map((result) => {
							const meta = catalog.data?.indicators.find(
								(item) => item.code === result.indicatorCode,
							)
							return (
								<IndicatorCard
									key={`${result.indicatorCode}-${result.studentGroupCode}`}
									result={result}
									unit={meta?.unit ?? 'percent'}
									lowerIsBetter={meta?.lowerIsBetter ?? false}
									selected={result.indicatorCode === selectedIndicator}
									onSelect={(code) => update({ indicator: code })}
								/>
							)
						})}
					</section>
				) : (
					<Alert>
						<AlertTitle>Nothing reported</AlertTitle>
						<AlertDescription>
							The state reports no indicators for this entity, year and student group.
						</AlertDescription>
					</Alert>
				)}

				{selectedIndicator && indicatorMeta ? (
					<Card>
						<CardHeader>
							<CardTitle className='text-base'>{indicatorMeta.name}</CardTitle>
						</CardHeader>
						<CardContent>
							<Tabs defaultValue='groups'>
								<TabsList>
									<TabsTrigger value='groups'>Student groups</TabsTrigger>
									<TabsTrigger value='trend'>Over time</TabsTrigger>
								</TabsList>
								<TabsContent value='groups' className='pt-4'>
									{groups.isPending ? (
										<Skeleton className='h-64 w-full' />
									) : groups.error ? (
										<p className='text-sm text-destructive'>{groups.error.message}</p>
									) : groups.data ? (
										<StudentGroupBreakdown
											report={groups.data}
											unit={indicatorMeta.unit}
											lowerIsBetter={indicatorMeta.lowerIsBetter}
											groupNames={groupNames}
										/>
									) : null}
								</TabsContent>
								<TabsContent value='trend' className='pt-4'>
									{selection ? (
										<IndicatorTrend
											selection={selection}
											indicator={selectedIndicator}
											unit={indicatorMeta.unit}
										/>
									) : null}
								</TabsContent>
							</Tabs>
						</CardContent>
					</Card>
				) : null}

				{selection ? <LocalMeasures cds={selection.cds} year={selection.year} /> : null}

				<footer className='border-t pt-6 text-xs text-muted-foreground'>
					<p>
						Source: California Department of Education, California School Dashboard downloadable
						data files. Figures are reproduced as published. A group shown as{' '}
						<strong>Not rated</strong> either sits outside the accountability system (English
						learners only, reclassified, English only, and the assessment-type groups are reported
						for information), has fewer than 30 students, or has only one year of data.
					</p>
				</footer>
			</main>
		</>
	)
}
