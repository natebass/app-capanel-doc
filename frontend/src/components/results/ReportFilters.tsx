import { Label } from '@/components/ui/label'
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
		<div className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
			<div className='space-y-1.5'>
				<Label htmlFor='filter-year'>Year</Label>
				<Select
					items={yearItems}
					value={String(values.year)}
					onValueChange={(value) => onChange({ year: Number(value) })}
				>
					<SelectTrigger id='filter-year' className='w-full'>
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
				<Label htmlFor='filter-grade'>Grade</Label>
				<Select
					items={gradeItems}
					value={values.grade}
					onValueChange={(grade) => grade && onChange({ grade })}
				>
					<SelectTrigger id='filter-grade' className='w-full'>
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
			</div>

			<div className='space-y-1.5'>
				<Label htmlFor='filter-group'>Student group</Label>
				<Select
					items={groupItems}
					value={String(values.studentGroup)}
					onValueChange={(value) => onChange({ studentGroup: Number(value) })}
				>
					<SelectTrigger id='filter-group' className='w-full'>
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
			</div>

			{showSchoolType ? (
				<div className='space-y-1.5'>
					<Label htmlFor='filter-school-type'>Schools included</Label>
					<Select
						items={schoolTypeItems}
						value={values.schoolType}
						onValueChange={(value) => onChange({ schoolType: value as SchoolType })}
					>
						<SelectTrigger id='filter-school-type' className='w-full'>
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
				</div>
			) : null}
		</div>
	)
}
