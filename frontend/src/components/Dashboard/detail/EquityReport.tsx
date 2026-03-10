import type { EquityGroupSummary } from '@/lib/client'
import { COLOR_LEVELS, getStudentGroupName } from '@/lib/constants/indicators'

export type ColorKey = 'red' | 'orange' | 'yellow' | 'green' | 'blue'

const COLOR_KEY_TO_LEVEL: Record<ColorKey, number> = {
	red: 1,
	orange: 2,
	yellow: 3,
	green: 4,
	blue: 5,
}

interface ColorCounts {
	[key: string]: number | undefined
	red?: number
	orange?: number
	yellow?: number
	green?: number
	blue?: number
	none?: number
}

interface EquityReportProps {
	colorCounts: ColorCounts
	groups: EquityGroupSummary[]
	showGroupList?: boolean
	filterColor?: ColorKey | null
}

function ColorBar({ colorCounts }: { colorCounts: ColorCounts }) {
	const red = colorCounts.red ?? 0
	const orange = colorCounts.orange ?? 0
	const yellow = colorCounts.yellow ?? 0
	const green = colorCounts.green ?? 0
	const blue = colorCounts.blue ?? 0
	const total = red + orange + yellow + green + blue

	if (total === 0) {
		return (
			<div className='flex h-8 w-full items-center justify-center rounded bg-muted text-sm text-muted-foreground'>
				No student group data
			</div>
		)
	}

	const segments = [
		{ key: 'red', count: red, color: COLOR_LEVELS[1].color },
		{ key: 'orange', count: orange, color: COLOR_LEVELS[2].color },
		{ key: 'yellow', count: yellow, color: COLOR_LEVELS[3].color },
		{ key: 'green', count: green, color: COLOR_LEVELS[4].color },
		{ key: 'blue', count: blue, color: COLOR_LEVELS[5].color },
	].filter((s) => s.count > 0)

	return (
		<div className='space-y-2'>
			<div className='flex h-8 w-full overflow-hidden rounded'>
				{segments.map((segment) => (
					<div
						key={segment.key}
						className='flex items-center justify-center text-xs font-medium text-white transition-all'
						style={{
							width: `${(segment.count / total) * 100}%`,
							backgroundColor: segment.color,
						}}
					>
						{segment.count}
					</div>
				))}
			</div>
			<div className='flex flex-wrap justify-center gap-4 text-xs'>
				{segments.map((segment) => (
					<span key={segment.key} className='flex items-center gap-1'>
						<span className='h-3 w-3 rounded-full' style={{ backgroundColor: segment.color }} />
						{segment.key.charAt(0).toUpperCase() + segment.key.slice(1)}: {segment.count}
					</span>
				))}
			</div>
		</div>
	)
}

function GroupList({ groups }: { groups: EquityGroupSummary[] }) {
	// Sort groups by color level (red first, then orange, etc.)
	const sortedGroups = [...groups].sort((a, b) => {
		const colorA = a.color ?? 6
		const colorB = b.color ?? 6
		return colorA - colorB
	})

	return (
		<div className='space-y-2'>
			{sortedGroups.map((group) => {
				const colorInfo = COLOR_LEVELS[(group.color ?? 0) as keyof typeof COLOR_LEVELS]
				return (
					<div
						key={group.studentgroup}
						className='flex items-center justify-between rounded-lg border p-2'
					>
						<div className='flex items-center gap-2'>
							<span className='h-4 w-4 rounded-full' style={{ backgroundColor: colorInfo.color }} />
							<span className='font-medium'>{getStudentGroupName(group.studentgroup)}</span>
						</div>
						<div className='text-sm text-muted-foreground'>
							{group.currdenom?.toLocaleString() ?? 'N/A'} students
						</div>
					</div>
				)
			})}
		</div>
	)
}

export function EquityReport({
	colorCounts,
	groups,
	showGroupList = true,
	filterColor,
}: EquityReportProps) {
	// Filter groups by color if filterColor is provided
	const filteredGroups = filterColor
		? groups.filter((g) => g.color === COLOR_KEY_TO_LEVEL[filterColor])
		: groups

	// Create filtered color counts if filterColor is provided
	const filteredColorCounts = filterColor
		? {
				red: filterColor === 'red' ? colorCounts.red : 0,
				orange: filterColor === 'orange' ? colorCounts.orange : 0,
				yellow: filterColor === 'yellow' ? colorCounts.yellow : 0,
				green: filterColor === 'green' ? colorCounts.green : 0,
				blue: filterColor === 'blue' ? colorCounts.blue : 0,
				none: 0,
			}
		: colorCounts

	const colorLabel = filterColor ? filterColor.charAt(0).toUpperCase() + filterColor.slice(1) : null

	return (
		<div className='space-y-4'>
			<div>
				<h4 className='mb-2 text-sm font-medium text-muted-foreground'>
					Student Group Performance Distribution
					{colorLabel && <span className='ml-1'>({colorLabel} only)</span>}
				</h4>
				<ColorBar colorCounts={filteredColorCounts} />
			</div>

			{showGroupList && filteredGroups.length > 0 && (
				<div>
					<h4 className='mb-2 text-sm font-medium text-muted-foreground'>
						Student Groups ({filteredGroups.length})
					</h4>
					<GroupList groups={filteredGroups} />
				</div>
			)}
		</div>
	)
}

export function EquityReportSkeleton() {
	return (
		<div className='space-y-4'>
			<div>
				<div className='mb-2 h-4 w-48 animate-pulse rounded bg-muted/40' />
				<div className='h-8 w-full animate-pulse rounded bg-muted/40' />
			</div>
			<div>
				<div className='mb-2 h-4 w-32 animate-pulse rounded bg-muted/40' />
				<div className='space-y-2'>
					{Array.from({ length: 5 }).map((_, i) => (
						<div key={i} className='h-10 w-full animate-pulse rounded-lg bg-muted/40' />
					))}
				</div>
			</div>
		</div>
	)
}
