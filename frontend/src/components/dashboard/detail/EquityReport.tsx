import type { EquityGroupSummary } from '@/lib/client'
import { getStudentGroupName } from '@/lib/constants/indicators'

interface EquityReportProps {
	groups: EquityGroupSummary[]
}

function GroupList({ groups }: { groups: EquityGroupSummary[] }) {
	// Sort groups by percent met descending
	const sortedGroups = [...groups].sort((a, b) => {
		const valA = a.overallMetAndAbovePct ? parseFloat(a.overallMetAndAbovePct) : 0
		const valB = b.overallMetAndAbovePct ? parseFloat(b.overallMetAndAbovePct) : 0
		return valB - valA
	})

	return (
		<div className='space-y-4'>
			{sortedGroups.map((group) => {
				const percent = group.overallMetAndAbovePct ? parseFloat(group.overallMetAndAbovePct) : 0
				return (
					<div key={group.studentGroup} className='space-y-1'>
						<div className='flex items-center justify-between text-sm'>
							<span className='font-medium'>{getStudentGroupName(group.studentGroup)}</span>
							<span className='font-semibold'>{percent.toFixed(1)}%</span>
						</div>
						<div className='h-2 w-full overflow-hidden rounded-full bg-muted'>
							<div className='h-full bg-primary transition-all' style={{ width: `${percent}%` }} />
						</div>
						<div className='text-[10px] text-muted-foreground'>
							{group.studentsTested?.toLocaleString() ?? '0'} students tested
						</div>
					</div>
				)
			})}
		</div>
	)
}

export function EquityReport({ groups }: EquityReportProps) {
	if (groups.length === 0) {
		return (
			<div className='py-8 text-center text-sm text-muted-foreground bg-muted/20 rounded-lg border border-dashed'>
				No student group data available for this selection.
			</div>
		)
	}

	return (
		<div className='space-y-6'>
			<div>
				<h4 className='mb-4 text-sm font-medium text-muted-foreground'>
					Standard Met or Exceeded by Student Group
				</h4>
				<GroupList groups={groups} />
			</div>
		</div>
	)
}

export function EquityReportSkeleton() {
	return (
		<div className='space-y-4'>
			{Array.from({ length: 5 }).map((_, i) => (
				<div key={i} className='space-y-2'>
					<div className='flex justify-between'>
						<div className='h-4 w-32 animate-pulse rounded bg-muted/40' />
						<div className='h-4 w-12 animate-pulse rounded bg-muted/40' />
					</div>
					<div className='h-2 w-full animate-pulse rounded-full bg-muted/40' />
				</div>
			))}
		</div>
	)
}
