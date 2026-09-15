import {
	Select,
	SelectContent,
	SelectGroup,
	SelectItem,
	SelectLabel,
	SelectTrigger,
	SelectValue,
} from '@/components/ui/select'
/**
 * The report controls: administration year, grade, student group and, for
 * aggregates, the charter filter.
 *
 * The options come from the catalogue endpoint rather than being hard-coded,
 * so a newly imported administration or a newly reported student group appears
 * without a frontend change.
 *
 * They sit on one line in the page header, beside the entity they qualify,
 * rather than in a card of their own — what they select is the rest of what
 * the heading above them means. That leaves no room for a label above each
 * one, so the label is the trigger's accessible name and the closed trigger
 * shows the current value, which is the thing worth reading anyway.
 */
import type { Catalog, GradePublic, SchoolType, StudentGroupPublic } from '@/lib/client'

export type FilterValues = {
	year: number
	grade: string
	studentGroup: number
	schoolType: SchoolType
}

const SCHOOL_TYPES: { value: SchoolType; label: string }[] = [
	{ value: 'all', label: 'All schools' },
	{ value: 'charter', label: 'Charter schools' },
	{ value: 'non-charter', label: 'Non-charter schools' },
]

/**
 * Base UI's select renders the raw value in the trigger unless it is given the
 * value-to-label mapping, so every select below passes its `items`.
 */
type SelectItemOption = { value: string; label: string }

function groupByCategory(groups: readonly StudentGroupPublic[]) {
	const byCategory = new Map<string, StudentGroupPublic[]>()
	for (const group of groups) {
		const bucket = byCategory.get(group.category)
		if (bucket) bucket.push(group)
		else byCategory.set(group.category, [group])
	}
	return [...byCategory.entries()]
}

export function ReportFilters({
	catalog,
	values,
	grades,
	onChange,
	showSchoolType,
}: {
	catalog: Catalog
	values: FilterValues
	/** Restricted to the grades the selected test actually reports. */
	grades: readonly GradePublic[]
	onChange: (next: Partial<FilterValues>) => void
	showSchoolType: boolean
}) {
	const programGroups = catalog.studentGroups.filter((group) => group.program === 'CAASPP')

	const yearItems: SelectItemOption[] = catalog.years.map((year) => ({
		value: String(year),
		label: `${year - 1}\u2013${String(year).slice(2)}`,
	}))
	const gradeItems: SelectItemOption[] = grades.map((grade) => ({
		value: grade.code,
		label: grade.label,
	}))
	const groupItems: SelectItemOption[] = programGroups.map((group) => ({
		value: String(group.studentGroupId),
		label: group.name,
	}))
	const schoolTypeItems: SelectItemOption[] = SCHOOL_TYPES.map((option) => ({
		value: option.value,
		label: option.label,
	}))

	return (
		<div className='flex flex-wrap items-center gap-2'>
			<Select
				items={yearItems}
				value={String(values.year)}
				onValueChange={(value) => onChange({ year: Number(value) })}
			>
				<SelectTrigger id='filter-year' aria-label='Year' className='w-36'>
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

			<Select
				items={gradeItems}
				value={values.grade}
				onValueChange={(grade) => grade && onChange({ grade })}
			>
				<SelectTrigger id='filter-grade' aria-label='Grade' className='w-36'>
					<SelectValue />
				</SelectTrigger>
				<SelectContent>
					{grades.map((grade) => (
						<SelectItem key={grade.code} value={grade.code}>
							{grade.label}
						</SelectItem>
					))}
				</SelectContent>
			</Select>

			<Select
				items={groupItems}
				value={String(values.studentGroup)}
				onValueChange={(value) => onChange({ studentGroup: Number(value) })}
			>
				<SelectTrigger id='filter-group' aria-label='Student group' className='w-56'>
					<SelectValue />
				</SelectTrigger>
				<SelectContent className='max-h-80'>
					{groupByCategory(programGroups).map(([category, groups]) => (
						<SelectGroup key={category}>
							<SelectLabel>{category}</SelectLabel>
							{groups.map((group) => (
								<SelectItem key={group.studentGroupId} value={String(group.studentGroupId)}>
									{group.name}
								</SelectItem>
							))}
						</SelectGroup>
					))}
				</SelectContent>
			</Select>

			{showSchoolType ? (
				<Select
					items={schoolTypeItems}
					value={values.schoolType}
					onValueChange={(value) => onChange({ schoolType: value as SchoolType })}
				>
					<SelectTrigger id='filter-school-type' aria-label='Schools included' className='w-44'>
						<SelectValue />
					</SelectTrigger>
					<SelectContent>
						{SCHOOL_TYPES.map((option) => (
							<SelectItem key={option.value} value={option.value}>
								{option.label}
							</SelectItem>
						))}
					</SelectContent>
				</Select>
			) : null}
		</div>
	)
}
