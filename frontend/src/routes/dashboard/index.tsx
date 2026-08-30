import {
	ArrowLeft01Icon,
	BookOpen01Icon,
	Calculator01Icon,
	TestTube01Icon,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute, useRouter } from '@tanstack/react-router'
import { Suspense, useCallback, useMemo, useState } from 'react'
import {
	Area,
	AreaChart,
	Bar,
	BarChart,
	CartesianGrid,
	Cell,
	Line,
	LineChart,
	Pie,
	PieChart,
	PolarAngleAxis,
	PolarGrid,
	PolarRadiusAxis,
	Radar,
	RadarChart,
	RadialBar,
	RadialBarChart,
	XAxis,
	YAxis,
} from 'recharts'
import { z } from 'zod'

import NavbarD52 from '@/components/common/navbar/navbar-D52'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
	ChartContainer,
	ChartLegend,
	ChartLegendContent,
	ChartTooltip,
	ChartTooltipContent,
} from '@/components/ui/chart'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select'
import { STATEWIDE_CDS } from '@/lib/constants/indicators'
import ScrollReset from '@/routes/-hooks/hooks/ScrollReset'
import {
	useDashboardSummary,
	useDashboardSummarySuspense,
	useEquityReport,
} from '@/routes/-hooks/hooks/useDashboardData'
import { useLastViewedSchool } from '@/routes/-hooks/hooks/useLastViewedSchool'

import styles from './index.module.css'

const AVAILABLE_YEARS = ['2025', '2024'] as const
type ReportingYear = (typeof AVAILABLE_YEARS)[number]

const SUBJECTS = [
	{ id: '1', label: 'English Language Arts', shortLabel: 'ELA', icon: BookOpen01Icon },
	{ id: '2', label: 'Mathematics', shortLabel: 'Math', icon: Calculator01Icon },
	{ id: '3', label: 'Science (CAST)', shortLabel: 'Science', icon: TestTube01Icon },
] as const

type SubjectId = (typeof SUBJECTS)[number]['id']

type EquityGroup = {
	studentGroup: string
	overallMetAndAbovePct?: string | null
	studentsTested?: string | null
}

type SummaryIndicator = {
	testId: string
	grade: string
	studentsEnrolled: string
	studentsTested: string
	overallMeanScaleScore?: string | null
	overallMetAndAbovePct?: string | null
	levels?: Record<string, number> | null
}

const EMPTY_EQUITY_GROUPS: EquityGroup[] = []

const PIE_COLORS = [
	'var(--color-chart-1)',
	'var(--color-chart-2)',
	'var(--color-chart-3)',
	'var(--color-chart-4)',
	'var(--color-chart-5)',
	'#0891b2',
	'#65a30d',
	'#db2777',
]

const levelColorMap = {
	level4: '#0f766e',
	level3: '#2563eb',
	level2: '#d97706',
	level1: '#dc2626',
} as const

const searchSchema = z.object({
	q: z.coerce.string().optional(),
	year: z.coerce
		.string()
		.optional()
		.transform((value) =>
			value === '2024' || value === '2025' ? (value as ReportingYear) : undefined,
		),
	subject: z.coerce
		.string()
		.optional()
		.transform((value) =>
			value === '1' || value === '2' || value === '3' ? (value as SubjectId) : undefined,
		),
})

const snapshotChartConfig = {
	proficiency: { label: 'Met Standard', color: 'var(--color-chart-2)' },
	participation: { label: 'Participation', color: 'var(--color-chart-4)' },
} as const

const performanceChartConfig = {
	level4: { label: 'Exceeded', color: levelColorMap.level4 },
	level3: { label: 'Met', color: levelColorMap.level3 },
	level2: { label: 'Nearly Met', color: levelColorMap.level2 },
	level1: { label: 'Not Met', color: levelColorMap.level1 },
} as const

const trendChartConfig = {
	pct: { label: 'Met/Exceeded', color: 'var(--color-chart-2)' },
} as const

const testedChartConfig = {
	tested: { label: 'Tested', color: 'var(--color-chart-3)' },
	enrolled: { label: 'Enrolled', color: 'var(--color-chart-5)' },
} as const

const scaleChartConfig = {
	scale: { label: 'Mean Scale Score', color: 'var(--color-chart-1)' },
} as const

const radarChartConfig = {
	level4: { label: 'Exceeded', color: levelColorMap.level4 },
	level3: { label: 'Met', color: levelColorMap.level3 },
	level2: { label: 'Nearly Met', color: levelColorMap.level2 },
	level1: { label: 'Not Met', color: levelColorMap.level1 },
} as const

export const Route = createFileRoute('/dashboard/')({
	component: DashboardPage,
	validateSearch: searchSchema,
})

function parseCount(value: string | null | undefined) {
	const parsed = Number.parseInt(value ?? '', 10)
	return Number.isFinite(parsed) ? parsed : 0
}

function parsePercentage(value: string | null | undefined) {
	if (value == null) {
		return null
	}

	const parsed = Number.parseFloat(value)
	return Number.isFinite(parsed) ? parsed : null
}

function formatCompactNumber(value: number) {
	return value.toLocaleString()
}

function formatGradeLabel(grade: string) {
	return grade === '13' ? 'All Grades' : `Grade ${grade}`
}

function calculateAvgPct(data: { indicators?: SummaryIndicator[] } | undefined, subjectId: string) {
	const subjectIndicators = (data?.indicators ?? []).filter(
		(indicator) => indicator.testId === subjectId,
	)
	let weightedPctSum = 0
	let weightedPctCount = 0

	for (const indicator of subjectIndicators) {
		const tested = parseCount(indicator.studentsTested)
		const pct = parsePercentage(indicator.overallMetAndAbovePct)
		if (pct !== null && tested > 0) {
			weightedPctSum += pct * tested
			weightedPctCount += tested
		}
	}

	return weightedPctCount > 0
		? Number.parseFloat((weightedPctSum / weightedPctCount).toFixed(1))
		: null
}

function getChangeLabel(current: number | null, previous: number | null) {
	if (current === null || previous === null) {
		return 'Single-year view'
	}

	const delta = current - previous
	if (Math.abs(delta) < 0.1) {
		return 'Flat vs prior year'
	}

	return `${delta > 0 ? '+' : ''}${delta.toFixed(1)} pts vs prior year`
}

function EmptyChartState({
	title,
	description,
	height = 'h-[320px]',
}: {
	title: string
	description: string
	height?: string
}) {
	return (
		<div
			className={`flex ${height} items-center justify-center rounded-xl border border-dashed px-6 text-center`}
		>
			<div className='space-y-2'>
				<p className='text-sm font-semibold text-foreground'>{title}</p>
				<p className='text-sm text-muted-foreground'>{description}</p>
			</div>
		</div>
	)
}

function DashboardPage() {
	const { q, year: urlYear, subject: urlSubject } = Route.useSearch()
	const navigate = Route.useNavigate()
	const router = useRouter()
	const { cds: lastViewedCds } = useLastViewedSchool()

	const effectiveCds = q || lastViewedCds || STATEWIDE_CDS
	const effectiveYear: ReportingYear = urlYear || '2025'
	const effectiveSubjectId: SubjectId = urlSubject || '1'

	const activeSubject = useMemo(
		() => SUBJECTS.find((subject) => subject.id === effectiveSubjectId) ?? SUBJECTS[0],
		[effectiveSubjectId],
	)

	const handleYearChange = useCallback(
		(nextYear: ReportingYear) => {
			if (nextYear === effectiveYear) {
				return
			}
			void navigate({ search: (previous) => ({ ...previous, year: nextYear }) })
		},
		[effectiveYear, navigate],
	)

	const handleSubjectChange = useCallback(
		(nextSubject: SubjectId) => {
			if (nextSubject === effectiveSubjectId) {
				return
			}
			void navigate({ search: (previous) => ({ ...previous, subject: nextSubject }) })
		},
		[effectiveSubjectId, navigate],
	)

	return (
		<div className={styles.page}>
			<ScrollReset />
			<NavbarD52 shadow />
			<div className={styles.container}>
				<div className={styles.topBar}>
					<Button
						variant='outline'
						size='sm'
						onClick={() => router.history.back()}
						className={styles.backButton}
					>
						<HugeiconsIcon icon={ArrowLeft01Icon} className='h-4 w-4' />
						Go back
					</Button>
					<div className={styles.filterGroup}>
						<div className={styles.filterItem}>
							<span className={styles.filterLabel}>Subject:</span>
							<Select
								value={effectiveSubjectId}
								onValueChange={(value) => handleSubjectChange(value as SubjectId)}
							>
								<SelectTrigger className={styles.filterSelectTrigger}>
									<SelectValue placeholder={activeSubject.shortLabel}>
										{activeSubject.shortLabel}
									</SelectValue>
								</SelectTrigger>
								<SelectContent>
									{SUBJECTS.map((subject) => (
										<SelectItem key={subject.id} value={subject.id}>
											{subject.shortLabel}
										</SelectItem>
									))}
								</SelectContent>
							</Select>
						</div>
						<div className={styles.filterDivider} />
						<div className={styles.filterItem}>
							<span className={styles.filterLabel}>Year:</span>
							<Select
								value={effectiveYear}
								onValueChange={(value) => handleYearChange(value as ReportingYear)}
							>
								<SelectTrigger className={styles.yearSelectTrigger}>
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									{AVAILABLE_YEARS.map((availableYear) => (
										<SelectItem key={availableYear} value={availableYear}>
											{availableYear}
										</SelectItem>
									))}
								</SelectContent>
							</Select>
						</div>
					</div>
				</div>

				<Suspense fallback={<DashboardSkeleton />}>
					<DashboardContent
						cds={effectiveCds}
						year={effectiveYear}
						subjectId={effectiveSubjectId}
					/>
				</Suspense>
			</div>
		</div>
	)
}

function DashboardContent({
	cds,
	year,
	subjectId,
}: {
	cds: string
	year: ReportingYear
	subjectId: SubjectId
}) {
	const { data: summaryData } = useDashboardSummarySuspense(cds, year)
	const prevYear = year === '2025' ? '2024' : null
	const { data: prevSummaryData } = useDashboardSummary(cds, prevYear || '2024', 'ALL')
	const reportingYear = summaryData.testYear || year
	const entityName = cds === STATEWIDE_CDS ? 'California Statewide' : 'Assessment Dashboard'
	const activeSubject = useMemo(
		() => SUBJECTS.find((subject) => subject.id === subjectId) ?? SUBJECTS[0],
		[subjectId],
	)
	const { data: equityData, isLoading: isEquityLoading } = useEquityReport(
		cds,
		subjectId,
		reportingYear,
	)
	const equityGroups = Array.isArray(equityData?.groups) ? equityData.groups : EMPTY_EQUITY_GROUPS
	const [selectedGroup, setSelectedGroup] = useState<string | null>(null)

	const subjectIndicators = useMemo(
		() => (summaryData.indicators ?? []).filter((indicator) => indicator.testId === subjectId),
		[summaryData.indicators, subjectId],
	)

	const summaryStats = useMemo(() => {
		const totalEnrolled = subjectIndicators.reduce(
			(sum, indicator) => sum + parseCount(indicator.studentsEnrolled),
			0,
		)
		const totalTested = subjectIndicators.reduce(
			(sum, indicator) => sum + parseCount(indicator.studentsTested),
			0,
		)
		let weightedPctSum = 0
		let weightedPctCount = 0
		let weightedScaleSum = 0
		let weightedScaleCount = 0

		for (const indicator of subjectIndicators) {
			const tested = parseCount(indicator.studentsTested)
			const pct = parsePercentage(indicator.overallMetAndAbovePct)
			const scale = parsePercentage(indicator.overallMeanScaleScore)
			if (pct !== null && tested > 0) {
				weightedPctSum += pct * tested
				weightedPctCount += tested
			}
			if (scale !== null && tested > 0) {
				weightedScaleSum += scale * tested
				weightedScaleCount += tested
			}
		}

		return {
			gradeCount: subjectIndicators.length,
			totalEnrolled,
			totalTested,
			avgPct: weightedPctCount > 0 ? weightedPctSum / weightedPctCount : null,
			avgScale: weightedScaleCount > 0 ? weightedScaleSum / weightedScaleCount : null,
			participationPct:
				totalEnrolled > 0
					? Number.parseFloat(((totalTested / totalEnrolled) * 100).toFixed(1))
					: null,
		}
	}, [subjectIndicators])

	const gradePerformanceData = useMemo(
		() =>
			[...subjectIndicators]
				.sort((left, right) => parseCount(left.grade) - parseCount(right.grade))
				.map((indicator) => {
					const tested = parseCount(indicator.studentsTested)
					const enrolled = parseCount(indicator.studentsEnrolled)
					const meanScale = parsePercentage(indicator.overallMeanScaleScore)
					return {
						grade: formatGradeLabel(indicator.grade),
						tested,
						enrolled,
						meanScale,
						metPct: parsePercentage(indicator.overallMetAndAbovePct),
						level4: indicator.levels?.['Standard Exceeded (Level 4)'] ?? 0,
						level3: indicator.levels?.['Standard Met (Level 3)'] ?? 0,
						level2: indicator.levels?.['Standard Nearly Met (Level 2)'] ?? 0,
						level1: indicator.levels?.['Standard Not Met (Level 1)'] ?? 0,
					}
				}),
		[subjectIndicators],
	)

	const trendData = useMemo(
		() =>
			[
				{ year: '2024', pct: calculateAvgPct(prevSummaryData, subjectId) },
				{ year: '2025', pct: calculateAvgPct(summaryData, subjectId) },
			].filter((entry) => entry.pct !== null),
		[prevSummaryData, subjectId, summaryData],
	)

	const levelRadarData = useMemo(() => {
		const totals = {
			level4: 0,
			level3: 0,
			level2: 0,
			level1: 0,
		}
		let weightTotal = 0

		for (const item of gradePerformanceData) {
			const weight = item.tested > 0 ? item.tested : 1
			totals.level4 += item.level4 * weight
			totals.level3 += item.level3 * weight
			totals.level2 += item.level2 * weight
			totals.level1 += item.level1 * weight
			weightTotal += weight
		}

		if (weightTotal === 0) {
			return []
		}

		return [
			{ metric: 'Exceeded', value: Number.parseFloat((totals.level4 / weightTotal).toFixed(1)) },
			{ metric: 'Met', value: Number.parseFloat((totals.level3 / weightTotal).toFixed(1)) },
			{ metric: 'Nearly Met', value: Number.parseFloat((totals.level2 / weightTotal).toFixed(1)) },
			{ metric: 'Not Met', value: Number.parseFloat((totals.level1 / weightTotal).toFixed(1)) },
		]
	}, [gradePerformanceData])

	const equityPieData = useMemo(
		() =>
			equityGroups
				.filter((group) => group.studentGroup?.toLowerCase() !== 'all students')
				.map((group, index) => ({
					name: group.studentGroup || 'Unknown',
					tested: parseCount(group.studentsTested),
					metPct: parsePercentage(group.overallMetAndAbovePct),
					fill: PIE_COLORS[index % PIE_COLORS.length],
				}))
				.filter((group) => group.tested > 0)
				.sort((left, right) => right.tested - left.tested),
		[equityGroups],
	)

	const groupComparisonData = useMemo(
		() =>
			[...equityPieData]
				.sort((left, right) => (right.metPct ?? -1) - (left.metPct ?? -1))
				.slice(0, 6)
				.map((group) => ({
					group: group.name,
					metPct: group.metPct ?? 0,
					tested: group.tested,
				})),
		[equityPieData],
	)

	const activeGroup =
		selectedGroup != null
			? (equityPieData.find((group) => group.name === selectedGroup) ?? null)
			: null

	const snapshotData = [
		{
			name: 'snapshot',
			proficiency: summaryStats.avgPct ?? 0,
			participation: summaryStats.participationPct ?? 0,
		},
	]

	const changeLabel = getChangeLabel(
		trendData.at(-1)?.pct ?? null,
		trendData.length > 1 ? (trendData[0]?.pct ?? null) : null,
	)

	return (
		<div className={styles.content}>
			<div className={styles.header}>
				<h1>{entityName}</h1>
				<p className={styles.meta}>
					{reportingYear} {activeSubject.label} assessment view
				</p>
			</div>

			<div className='grid gap-6 lg:grid-cols-12'>
				<Card className='border shadow-sm lg:col-span-8'>
					<CardHeader className='flex flex-col gap-4 border-b bg-muted/20 md:flex-row md:items-end md:justify-between'>
						<div className='space-y-2'>
							<CardTitle className='flex items-center gap-3 text-2xl'>
								<span className='rounded-2xl bg-primary/10 p-3 text-primary'>
									<HugeiconsIcon icon={activeSubject.icon} className='h-7 w-7' />
								</span>
								{activeSubject.label}
							</CardTitle>
							<CardDescription>
								Assessment snapshot across tested grades. Metrics stay visible even when a slice has
								sparse reporting.
							</CardDescription>
						</div>
						<div className='rounded-xl border bg-background px-4 py-3 text-sm'>
							<p className='text-muted-foreground'>Year-over-year signal</p>
							<p className='mt-1 text-lg font-semibold'>{changeLabel}</p>
						</div>
					</CardHeader>
					<CardContent className='grid gap-6 pt-6 lg:grid-cols-[320px_1fr]'>
						<ChartContainer
							config={snapshotChartConfig}
							className='mx-auto aspect-square max-h-[280px]'
						>
							<RadialBarChart
								data={snapshotData}
								innerRadius='35%'
								outerRadius='100%'
								startAngle={90}
								endAngle={-270}
								barSize={18}
							>
								<ChartTooltip
									cursor={false}
									content={
										<ChartTooltipContent
											formatter={(value, name) => (
												<>
													<span className='text-muted-foreground'>{String(name)}</span>
													<span className='font-medium'>{Number(value).toFixed(1)}%</span>
												</>
											)}
										/>
									}
								/>
								<RadialBar
									dataKey='participation'
									cornerRadius={12}
									fill='var(--color-participation)'
								/>
								<RadialBar
									dataKey='proficiency'
									cornerRadius={12}
									fill='var(--color-proficiency)'
								/>
								<ChartLegend content={<ChartLegendContent />} />
							</RadialBarChart>
						</ChartContainer>
						<div className='grid gap-4 sm:grid-cols-2 xl:grid-cols-4'>
							<MetricPanel
								label='Students Tested'
								value={formatCompactNumber(summaryStats.totalTested)}
								note='Across all reported grades'
							/>
							<MetricPanel
								label='Participation'
								value={
									summaryStats.participationPct !== null
										? `${summaryStats.participationPct.toFixed(1)}%`
										: 'Unavailable'
								}
								note={
									summaryStats.totalEnrolled > 0
										? `${formatCompactNumber(summaryStats.totalEnrolled)} enrolled`
										: 'Enrollment not reported'
								}
							/>
							<MetricPanel
								label='Met or Exceeded'
								value={
									summaryStats.avgPct !== null
										? `${summaryStats.avgPct.toFixed(1)}%`
										: 'Unavailable'
								}
								note='Weighted by students tested'
							/>
							<MetricPanel
								label='Mean Scale Score'
								value={
									summaryStats.avgScale !== null ? summaryStats.avgScale.toFixed(1) : 'Unavailable'
								}
								note={`${summaryStats.gradeCount || 0} reporting grades`}
							/>
						</div>
					</CardContent>
				</Card>

				<Card className='border shadow-sm lg:col-span-4'>
					<CardHeader>
						<CardTitle className='text-xl'>Achievement Profile</CardTitle>
						<CardDescription>
							Weighted performance shape for {activeSubject.shortLabel} across level bands.
						</CardDescription>
					</CardHeader>
					<CardContent>
						{levelRadarData.length > 0 ? (
							<ChartContainer
								config={radarChartConfig}
								className='mx-auto aspect-square max-h-[300px]'
							>
								<RadarChart data={levelRadarData}>
									<ChartTooltip content={<ChartTooltipContent />} />
									<PolarGrid />
									<PolarAngleAxis dataKey='metric' />
									<PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
									<Radar
										dataKey='value'
										name='value'
										stroke='var(--color-level3)'
										fill='var(--color-level3)'
										fillOpacity={0.2}
										strokeWidth={2}
									/>
								</RadarChart>
							</ChartContainer>
						) : (
							<EmptyChartState
								title='No performance profile yet'
								description='This selection has no reported level distribution in the current dataset.'
								height='h-[300px]'
							/>
						)}
					</CardContent>
				</Card>
			</div>

			<div className='grid gap-6 lg:grid-cols-12'>
				<Card className='border shadow-sm lg:col-span-7'>
					<CardHeader>
						<CardTitle className='text-xl'>Performance Levels by Grade</CardTitle>
						<CardDescription>
							Stacked distribution for {activeSubject.label} in {reportingYear}.
						</CardDescription>
					</CardHeader>
					<CardContent>
						{gradePerformanceData.length > 0 ? (
							<ChartContainer config={performanceChartConfig} className='h-[360px] w-full'>
								<BarChart data={gradePerformanceData} barGap={6}>
									<CartesianGrid vertical={false} />
									<XAxis dataKey='grade' tickLine={false} axisLine={false} interval={0} />
									<YAxis tickFormatter={(value) => `${value}%`} tickLine={false} axisLine={false} />
									<ChartTooltip
										content={
											<ChartTooltipContent
												formatter={(value, name, item) => (
													<>
														<span className='text-muted-foreground'>{String(name)}</span>
														<span className='font-medium'>
															{Number(value).toFixed(1)}%
															{item?.payload?.tested
																? ` • ${item.payload.tested.toLocaleString()} tested`
																: ''}
														</span>
													</>
												)}
											/>
										}
									/>
									<ChartLegend content={<ChartLegendContent />} />
									<Bar
										dataKey='level1'
										stackId='levels'
										fill='var(--color-level1)'
										radius={[0, 0, 6, 6]}
									/>
									<Bar dataKey='level2' stackId='levels' fill='var(--color-level2)' />
									<Bar dataKey='level3' stackId='levels' fill='var(--color-level3)' />
									<Bar
										dataKey='level4'
										stackId='levels'
										fill='var(--color-level4)'
										radius={[6, 6, 0, 0]}
									/>
								</BarChart>
							</ChartContainer>
						) : (
							<EmptyChartState
								title='No grade-level performance rows'
								description='The current selection returned no performance-level rows to stack.'
							/>
						)}
					</CardContent>
				</Card>

				<Card className='border shadow-sm lg:col-span-5'>
					<CardHeader>
						<CardTitle className='text-xl'>Grade Volume</CardTitle>
						<CardDescription>
							Tested and enrolled counts by grade for the selected subject.
						</CardDescription>
					</CardHeader>
					<CardContent>
						{gradePerformanceData.length > 0 ? (
							<ChartContainer config={testedChartConfig} className='h-[360px] w-full'>
								<BarChart data={gradePerformanceData}>
									<CartesianGrid vertical={false} />
									<XAxis dataKey='grade' tickLine={false} axisLine={false} interval={0} />
									<YAxis tickLine={false} axisLine={false} />
									<ChartTooltip content={<ChartTooltipContent />} />
									<ChartLegend content={<ChartLegendContent />} />
									<Bar dataKey='enrolled' fill='var(--color-enrolled)' radius={[6, 6, 0, 0]} />
									<Bar dataKey='tested' fill='var(--color-tested)' radius={[6, 6, 0, 0]} />
								</BarChart>
							</ChartContainer>
						) : (
							<EmptyChartState
								title='No grade counts available'
								description='Enrollment and tested counts are not present for this slice.'
							/>
						)}
					</CardContent>
				</Card>
			</div>

			<div className='grid gap-6 lg:grid-cols-12'>
				<Card className='border shadow-sm lg:col-span-6'>
					<CardHeader>
						<CardTitle className='text-xl'>Performance Trend</CardTitle>
						<CardDescription>
							Area and line view of met-or-exceeded percentage across available years.
						</CardDescription>
					</CardHeader>
					<CardContent>
						{trendData.length > 0 ? (
							<ChartContainer config={trendChartConfig} className='h-[320px] w-full'>
								<AreaChart data={trendData}>
									<defs>
										<linearGradient id='dashboard-trend-fill' x1='0' y1='0' x2='0' y2='1'>
											<stop offset='5%' stopColor='var(--color-pct)' stopOpacity={0.35} />
											<stop offset='95%' stopColor='var(--color-pct)' stopOpacity={0.05} />
										</linearGradient>
									</defs>
									<CartesianGrid vertical={false} />
									<XAxis dataKey='year' tickLine={false} axisLine={false} />
									<YAxis
										domain={[0, 100]}
										tickFormatter={(value) => `${value}%`}
										tickLine={false}
										axisLine={false}
									/>
									<ChartTooltip
										content={
											<ChartTooltipContent
												formatter={(value) => (
													<span className='font-medium'>{Number(value).toFixed(1)}%</span>
												)}
											/>
										}
									/>
									<Area
										type='monotone'
										dataKey='pct'
										fill='url(#dashboard-trend-fill)'
										stroke='var(--color-pct)'
										strokeWidth={3}
									/>
									<Line
										type='monotone'
										dataKey='pct'
										stroke='var(--color-pct)'
										strokeWidth={0}
										dot={{ r: 5 }}
										activeDot={{ r: 6 }}
									/>
								</AreaChart>
							</ChartContainer>
						) : (
							<EmptyChartState
								title='Trend needs at least one reported year'
								description='As more reporting years are added, this chart will show movement over time.'
							/>
						)}
					</CardContent>
				</Card>

				<Card className='border shadow-sm lg:col-span-6'>
					<CardHeader>
						<CardTitle className='text-xl'>Mean Scale by Grade</CardTitle>
						<CardDescription>
							Line view of average scale score across reporting grades in {reportingYear}.
						</CardDescription>
					</CardHeader>
					<CardContent>
						{gradePerformanceData.some((item) => item.meanScale !== null) ? (
							<ChartContainer config={scaleChartConfig} className='h-[320px] w-full'>
								<LineChart data={gradePerformanceData.filter((item) => item.meanScale !== null)}>
									<CartesianGrid vertical={false} />
									<XAxis dataKey='grade' tickLine={false} axisLine={false} interval={0} />
									<YAxis
										tickLine={false}
										axisLine={false}
										domain={['dataMin - 5', 'dataMax + 5']}
									/>
									<ChartTooltip
										content={
											<ChartTooltipContent
												formatter={(value) => (
													<span className='font-medium'>{Number(value).toFixed(1)}</span>
												)}
											/>
										}
									/>
									<Line
										type='monotone'
										dataKey='meanScale'
										stroke='var(--color-scale)'
										strokeWidth={3}
										dot={{ r: 4 }}
										activeDot={{ r: 6 }}
									/>
								</LineChart>
							</ChartContainer>
						) : (
							<EmptyChartState
								title='Mean scale score not reported'
								description='The selected assessment slice contains percentages, but no scale-score series.'
							/>
						)}
					</CardContent>
				</Card>
			</div>

			<div className='grid gap-6 lg:grid-cols-12'>
				<Card className='border shadow-sm lg:col-span-7'>
					<CardHeader>
						<CardTitle className='text-xl'>Demographic Composition</CardTitle>
						<CardDescription>
							Tested-student share by student group. Select a slice to inspect that group.
						</CardDescription>
					</CardHeader>
					<CardContent>
						{isEquityLoading ? (
							<EmptyChartState
								title='Loading demographic detail'
								description='The summary is ready. Group-level breakdown is still loading.'
							/>
						) : equityPieData.length > 0 ? (
							<div className='grid gap-6 lg:grid-cols-[360px_1fr]'>
								<ChartContainer
									config={Object.fromEntries(
										equityPieData.map((group) => [
											group.name,
											{ label: group.name, color: group.fill },
										]),
									)}
									className='mx-auto aspect-square max-h-[340px]'
								>
									<PieChart>
										<ChartTooltip
											content={
												<ChartTooltipContent
													nameKey='name'
													formatter={(value, _name, item) => (
														<>
															<div className='grid gap-1'>
																<span className='text-muted-foreground'>Tested</span>
																<span className='font-medium'>
																	{Number(value).toLocaleString()}
																</span>
															</div>
															{item?.payload?.metPct !== null &&
															item?.payload?.metPct !== undefined ? (
																<div className='grid gap-1'>
																	<span className='text-muted-foreground'>Met</span>
																	<span className='font-medium'>
																		{Number(item.payload.metPct).toFixed(1)}%
																	</span>
																</div>
															) : null}
														</>
													)}
												/>
											}
										/>
										<Pie
											data={equityPieData}
											dataKey='tested'
											nameKey='name'
											innerRadius={72}
											outerRadius={118}
											paddingAngle={3}
											onClick={(entry) =>
												entry?.name &&
												setSelectedGroup(entry.name === selectedGroup ? null : entry.name)
											}
										>
											{equityPieData.map((entry) => (
												<Cell
													key={entry.name}
													fill={entry.fill}
													opacity={selectedGroup && selectedGroup !== entry.name ? 0.35 : 1}
												/>
											))}
										</Pie>
									</PieChart>
								</ChartContainer>
								<div className='space-y-4'>
									<div className='grid gap-3 sm:grid-cols-2'>
										<MetricPanel
											label='Groups Reported'
											value={String(equityPieData.length)}
											note='Excludes all-students rollup'
										/>
										<MetricPanel
											label='Students in Groups'
											value={formatCompactNumber(
												equityPieData.reduce((sum, group) => sum + group.tested, 0),
											)}
											note='Across reported groups'
										/>
									</div>
									{activeGroup ? (
										<div className='rounded-2xl border bg-muted/20 p-5'>
											<p className='text-sm font-semibold text-foreground'>{activeGroup.name}</p>
											<div className='mt-4 grid gap-3 sm:grid-cols-2'>
												<MetricPanel
													label='Students Tested'
													value={formatCompactNumber(activeGroup.tested)}
													note='Selected group volume'
												/>
												<MetricPanel
													label='Met Standard'
													value={
														activeGroup.metPct !== null
															? `${activeGroup.metPct.toFixed(1)}%`
															: 'Unavailable'
													}
													note='Selected group performance'
												/>
											</div>
										</div>
									) : (
										<div className='rounded-2xl border border-dashed p-6 text-sm text-muted-foreground'>
											Select a pie slice to inspect a student group without leaving the dashboard.
										</div>
									)}
								</div>
							</div>
						) : (
							<EmptyChartState
								title='No demographic composition available'
								description='This dataset does not include student-group detail for the selected subject.'
							/>
						)}
					</CardContent>
				</Card>

				<Card className='border shadow-sm lg:col-span-5'>
					<CardHeader>
						<CardTitle className='text-xl'>Group Comparison</CardTitle>
						<CardDescription>
							Highest reported met-or-exceeded percentages among available student groups.
						</CardDescription>
					</CardHeader>
					<CardContent>
						{isEquityLoading ? (
							<EmptyChartState
								title='Loading group comparison'
								description='Waiting on grouped assessment detail from the API.'
							/>
						) : groupComparisonData.length > 0 ? (
							<ChartContainer
								config={{ metPct: { label: 'Met Standard', color: 'var(--color-chart-2)' } }}
								className='h-[360px] w-full'
							>
								<BarChart
									data={groupComparisonData}
									layout='vertical'
									margin={{ left: 8, right: 8 }}
								>
									<CartesianGrid horizontal={false} />
									<XAxis
										type='number'
										domain={[0, 100]}
										tickFormatter={(value) => `${value}%`}
										tickLine={false}
										axisLine={false}
									/>
									<YAxis
										type='category'
										dataKey='group'
										width={110}
										tickLine={false}
										axisLine={false}
									/>
									<ChartTooltip
										content={
											<ChartTooltipContent
												formatter={(value, _name, item) => (
													<>
														<span className='text-muted-foreground'>{item?.payload?.group}</span>
														<span className='font-medium'>
															{Number(value).toFixed(1)}% •{' '}
															{item?.payload?.tested?.toLocaleString()} tested
														</span>
													</>
												)}
											/>
										}
									/>
									<Bar dataKey='metPct' fill='var(--color-metPct)' radius={[0, 8, 8, 0]} />
								</BarChart>
							</ChartContainer>
						) : (
							<EmptyChartState
								title='No group percentages reported'
								description='Student-group performance percentages are unavailable for this slice.'
							/>
						)}
					</CardContent>
				</Card>
			</div>
		</div>
	)
}

function MetricPanel({ label, value, note }: { label: string; value: string; note: string }) {
	return (
		<div className='rounded-2xl border bg-background p-4 shadow-sm'>
			<p className='text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground'>
				{label}
			</p>
			<p className='mt-3 text-3xl font-semibold tracking-tight text-foreground'>{value}</p>
			<p className='mt-2 text-sm text-muted-foreground'>{note}</p>
		</div>
	)
}

function DashboardSkeleton() {
	return (
		<div className={styles.content}>
			<div className={styles.header}>
				<div className={styles.skeleton} style={{ height: 32, width: 256 }} />
				<div className={styles.skeleton} style={{ height: 16, width: 224, marginTop: 8 }} />
			</div>
			<div className='grid gap-6 lg:grid-cols-12'>
				<div className='h-[360px] rounded-2xl border bg-card lg:col-span-8' />
				<div className='h-[360px] rounded-2xl border bg-card lg:col-span-4' />
			</div>
			<div className='grid gap-6 lg:grid-cols-2'>
				<div className='h-[360px] rounded-2xl border bg-card' />
				<div className='h-[360px] rounded-2xl border bg-card' />
			</div>
			<div className='grid gap-6 lg:grid-cols-2'>
				<div className='h-[360px] rounded-2xl border bg-card' />
				<div className='h-[360px] rounded-2xl border bg-card' />
			</div>
		</div>
	)
}
