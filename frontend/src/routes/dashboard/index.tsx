/**
 * The assessment results report.
 *
 * Mirrors what the state publishes at caaspp-elpac.ets.org — pick an entity, a
 * year, a grade and a student group, and see every test's achievement
 * distribution — with the parts its own site makes you visit separately
 * (reporting categories, results over time, every student group, every grade,
 * and the schools inside a district) available on the same page.
 *
 * The selection lives in the URL, so any view of this report is a link.
 */
import { useQuery } from '@tanstack/react-query'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useMemo } from 'react'
import { z } from 'zod'

import NavbarD52 from '@/components/common/navbar/navbar-D52'
import { AchievementLegend } from '@/components/results/AchievementBar'
import { ChildEntityTable } from '@/components/results/ChildEntityTable'
import { GradeTable } from '@/components/results/GradeTable'
import { ReportFilters } from '@/components/results/ReportFilters'
import { ResultCard } from '@/components/results/ResultCard'
import { StudentGroupTable } from '@/components/results/StudentGroupTable'
import { SubscorePanel } from '@/components/results/SubscorePanel'
import { TrendChart } from '@/components/results/TrendChart'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ScrollReset from '@/hooks/ScrollReset'
import type { EntityPublic, SchoolType } from '@/lib/client'
import {
	ALL_GRADES,
	ALL_STUDENTS_GROUP,
	catalogQuery,
	entityQuery,
	overviewQuery,
	type ReportSelection,
	STATEWIDE_CDS,
} from '@/lib/services/assessments'

/**
 * The router parses search values as JSON, so a CDS code or a grade that looks
 * like a number comes back as one. Both are codes, not quantities — grade "03"
 * must not become 3 — so they are coerced back to strings here.
 */
const searchSchema = z.object({
	cds: z.coerce.string().length(14).default(STATEWIDE_CDS),
	year: z.coerce.number().int().optional(),
	grade: z.coerce.string().max(2).default(ALL_GRADES),
	studentGroup: z.coerce.number().int().default(ALL_STUDENTS_GROUP),
	schoolType: z.enum(['all', 'charter', 'non-charter']).default('all'),
	testId: z.coerce.number().int().optional(),
})

export const Route = createFileRoute('/dashboard/')({
	validateSearch: searchSchema,
	component: ResultsPage,
})

function ResultsPage() {
	const search = Route.useSearch()
	const navigate = useNavigate({ from: Route.fullPath })

	const catalog = useQuery(catalogQuery(search.year))
	const ancestry = useQuery(entityQuery(search.cds))

	const year = search.year ?? catalog.data?.testYear
	const selection: ReportSelection | undefined = year
		? {
				cds: search.cds,
				year,
				studentGroup: search.studentGroup,
				grade: search.grade,
				schoolType: search.schoolType as SchoolType,
			}
		: undefined

	const overview = useQuery({
		...overviewQuery(selection ?? ({} as ReportSelection)),
		enabled: Boolean(selection),
	})

	const entity = ancestry.data?.entity
	const isSchool = entity?.entityLevel === 'school'

	const selectedTestId = useMemo(() => {
		if (search.testId) return search.testId
		return overview.data?.results[0]?.testId
	}, [search.testId, overview.data])

	const selectedAssessment = catalog.data?.assessments.find(
		(assessment) => assessment.testId === selectedTestId,
	)

	/** Only offer grades the selected test actually reports. */
	const grades = useMemo(() => {
		if (!catalog.data) return []
		const codes = new Set(
			selectedAssessment?.grades ?? catalog.data.assessments.flatMap((item) => item.grades),
		)
		return catalog.data.grades.filter((grade) => codes.has(grade.code))
	}, [catalog.data, selectedAssessment])

	function update(next: Partial<z.infer<typeof searchSchema>>) {
		void navigate({ search: (previous) => ({ ...previous, ...next }) })
	}

	function chooseEntity(next: EntityPublic) {
		update({ cds: next.cdsCode })
	}

	/**
	 * Only the statewide code names itself without a lookup. Anything else has
	 * to be fetched, so its heading is a skeleton rather than a guess — a wrong
	 * school name is worse than no school name.
	 */
	const displayName =
		entity?.displayName ?? (search.cds === STATEWIDE_CDS ? 'State of California' : null)

	/**
	 * The state is every entity's last ancestor, so naming it in the line
	 * distinguishes nothing.
	 */
	const ancestorLine =
		ancestry.data?.ancestors
			.filter((item) => item.cdsCode !== STATEWIDE_CDS)
			.map((item) => item.displayName)
			.join(' · ') || (ancestry.data || search.cds === STATEWIDE_CDS ? 'Statewide results' : null)

	if (catalog.isPending) {
		return (
			<div>
				<NavbarD52 />
				<div className='container max-w-7xl mx-auto px-4 py-8'>
					<div className='flex flex-col gap-8'>
						<Skeleton className='h-10 w-96' />
						<Skeleton className='h-24 w-full' />
						<Skeleton className='h-64 w-full' />
					</div>
				</div>
			</div>
		)
	}

	if (catalog.error) {
		return (
			<div>
				<NavbarD52 />
				<div className='container max-w-7xl mx-auto px-4 py-8'>
					<Alert variant='destructive'>
						<AlertTitle>No assessment data</AlertTitle>
						<AlertDescription>
							{catalog.error.message} Run the research file importer to load results.
						</AlertDescription>
					</Alert>
				</div>
			</div>
		)
	}

	return (
		<div className='bg-[#f3f4fa]'>
			<ScrollReset />
			<NavbarD52 />
			<div className='container max-w-7xl mx-auto px-4 py-8'>
				<div className='flex flex-col gap-8'>
					{/* Page Header */}
					<div>
						<div className='flex flex-wrap items-center gap-3 mb-2'>
							{displayName ? (
								<h1 className='text-3xl font-bold'>{displayName}</h1>
							) : (
								<Skeleton className='h-9 w-80 max-w-full rounded-md' />
							)}
							{entity?.isCharter ? <Badge variant='outline'>Charter school</Badge> : null}
						</div>
						{/* The filters read as part of the sentence naming the entity,
						    because that is what they are: the rest of what the heading
						    above means. */}
						<div className='flex flex-wrap items-center justify-between gap-y-2'>
							<div className='flex flex-wrap items-center gap-2'>
								{ancestorLine ? (
									<p className='text-muted-foreground text-lg'>{ancestorLine}</p>
								) : (
									<Skeleton className='h-6 w-56 max-w-full rounded-md' />
								)}
							</div>
							{catalog.data ? (
								<ReportFilters
									catalog={catalog.data}
									grades={grades}
									showSchoolType={!isSchool}
									values={{
										year: year ?? catalog.data.testYear,
										grade: search.grade,
										studentGroup: search.studentGroup,
										schoolType: search.schoolType as SchoolType,
									}}
									onChange={update}
								/>
							) : null}
						</div>
					</div>

					{search.schoolType !== 'all' && !isSchool ? (
						<Alert>
							<AlertTitle>Recalculated figures</AlertTitle>
							<AlertDescription>
								The state publishes one aggregate covering every school, so charter-filtered results
								are summed from the school rows underneath. Counts are exact; mean scale scores are
								weighted by the number of tests with valid scores.
							</AlertDescription>
						</Alert>
					) : null}

					<section className='space-y-4'>
						<h2 className='text-lg font-medium'>Results</h2>
						{overview.isPending ? (
							<div className='grid gap-4 md:grid-cols-2'>
								<Skeleton className='h-80 w-full' />
								<Skeleton className='h-80 w-full' />
							</div>
						) : overview.error ? (
							<Alert variant='destructive'>
								<AlertDescription>{overview.error.message}</AlertDescription>
							</Alert>
						) : overview.data && overview.data.results.length > 0 ? (
							<div className='grid gap-4 md:grid-cols-2'>
								{overview.data.results.map((result) => (
									<ResultCard
										key={result.testId}
										result={result}
										assessment={catalog.data?.assessments.find(
											(assessment) => assessment.testId === result.testId,
										)}
										comparisons={overview.data.comparisons}
										selected={result.testId === selectedTestId}
										onSelect={() => update({ testId: result.testId })}
									/>
								))}
							</div>
						) : (
							<p className='text-sm text-muted-foreground'>
								Nothing was reported for this combination of year, grade and student group.
							</p>
						)}
					</section>

					{selection && selectedTestId && selectedAssessment ? (
						<section className='space-y-4'>
							<div className='flex flex-wrap items-baseline justify-between gap-2'>
								<h2 className='text-lg font-medium'>{selectedAssessment.name}</h2>
								<AchievementLegend levels={selectedAssessment.levelScheme.levels} />
							</div>
							<Card>
								<CardHeader className='pb-0'>
									<CardTitle className='sr-only'>Detailed reports</CardTitle>
								</CardHeader>
								<CardContent className='pt-4'>
									<Tabs defaultValue='categories'>
										<TabsList className='mb-4 flex-wrap'>
											<TabsTrigger value='categories'>Areas and domains</TabsTrigger>
											<TabsTrigger value='trend'>Over time</TabsTrigger>
											<TabsTrigger value='groups'>Student groups</TabsTrigger>
											<TabsTrigger value='grades'>By grade</TabsTrigger>
											{!isSchool ? (
												<TabsTrigger value='inside'>Inside this entity</TabsTrigger>
											) : null}
										</TabsList>
										<TabsContent value='categories'>
											<SubscorePanel selection={selection} testId={selectedTestId} />
										</TabsContent>
										<TabsContent value='trend'>
											<TrendChart selection={selection} testId={selectedTestId} />
										</TabsContent>
										<TabsContent value='groups'>
											<StudentGroupTable selection={selection} testId={selectedTestId} />
										</TabsContent>
										<TabsContent value='grades'>
											<GradeTable
												selection={selection}
												testId={selectedTestId}
												onSelectGrade={(grade) => update({ grade })}
											/>
										</TabsContent>
										{!isSchool ? (
											<TabsContent value='inside'>
												<ChildEntityTable
													selection={selection}
													testId={selectedTestId}
													onSelectEntity={chooseEntity}
												/>
											</TabsContent>
										) : null}
									</Tabs>
								</CardContent>
							</Card>
						</section>
					) : null}

					<footer className='border-t pt-4 text-xs text-muted-foreground'>
						Source: California Department of Education research files, published at{' '}
						<a
							className='underline underline-offset-2'
							href='https://caaspp-elpac.ets.org/caaspp/Default'
							target='_blank'
							rel='noreferrer'
						>
							caaspp-elpac.ets.org
						</a>
						. Results are withheld for any group of fewer than 11 students.
					</footer>
				</div>
			</div>
		</div>
	)
}
