/**
 * One indicator, every student group the state reports it for.
 *
 * This is the view the accountability system exists for: a school's overall
 * colour can be green while a student group inside it is red, and the
 * Dashboard is designed to make that visible rather than average it away.
 */
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from '@/components/ui/table'
import type { IndicatorGroupReport, IndicatorResult } from '@/lib/client'
import {
	DASHBOARD_COLORS,
	describeChange,
	explainMissingColor,
	formatStatus,
} from '@/lib/services/accountability'

function ColorPill({ result }: { result: IndicatorResult }) {
	const swatch = result.color ? DASHBOARD_COLORS[result.color] : undefined
	if (!swatch) {
		// "Not rated" and "not enough students" are different things, and the
		// state means the first far more often than readers assume.
		return (
			<span className='text-xs text-muted-foreground' title={explainMissingColor(result) ?? ''}>
				Not rated
			</span>
		)
	}
	return (
		<span
			className='rounded-full px-2 py-0.5 text-xs font-medium'
			style={{ backgroundColor: swatch.token, color: swatch.text }}
		>
			{swatch.name}
		</span>
	)
}

export function StudentGroupBreakdown({
	report,
	unit,
	lowerIsBetter,
	groupNames,
}: {
	report: IndicatorGroupReport
	unit: string
	lowerIsBetter: boolean
	groupNames: Record<string, string>
}) {
	const rows = [...(report.allStudents ? [report.allStudents] : []), ...report.groups]

	if (rows.length === 0) {
		return (
			<p className='text-sm text-muted-foreground'>
				The state reports no student groups for this indicator and year.
			</p>
		)
	}

	return (
		<div className='overflow-x-auto'>
			<Table>
				<TableHeader>
					<TableRow>
						<TableHead>Student group</TableHead>
						<TableHead className='text-right'>Status</TableHead>
						<TableHead className='text-right'>Change</TableHead>
						<TableHead>Colour</TableHead>
						<TableHead className='text-right'>Students</TableHead>
					</TableRow>
				</TableHeader>
				<TableBody>
					{rows.map((row) => {
						const change = describeChange(row.change, lowerIsBetter)
						const isAll = row.studentGroupCode === 'ALL'
						return (
							<TableRow key={row.studentGroupCode} className={isAll ? 'font-medium' : undefined}>
								<TableCell>{groupNames[row.studentGroupCode] ?? row.studentGroupCode}</TableCell>
								<TableCell className='text-right tabular-nums'>
									{formatStatus(row.currStatus, unit)}
								</TableCell>
								<TableCell className='text-right tabular-nums text-muted-foreground'>
									{change.label}
								</TableCell>
								<TableCell>
									<ColorPill result={row} />
								</TableCell>
								<TableCell className='text-right tabular-nums text-muted-foreground'>
									{row.currDenominator?.toLocaleString() ?? '—'}
								</TableCell>
							</TableRow>
						)
					})}
				</TableBody>
			</Table>
		</div>
	)
}
