/**
 * California School Accountability Dashboard indicator definitions.
 *
 * These define the 8 accountability indicators used in the California
 * School Dashboard system.
 */

export const INDICATORS = {
	ELA: {
		code: 'ELA',
		label: 'English Language Arts',
		shortLabel: 'ELA',
		icon: 'BookOpen',
		invertedScale: false,
		description: 'Academic performance in English Language Arts',
	},
	MATH: {
		code: 'MATH',
		label: 'Mathematics',
		shortLabel: 'Math',
		icon: 'Calculator',
		invertedScale: false,
		description: 'Academic performance in Mathematics',
	},
	SCI: {
		code: 'SCI',
		label: 'Science',
		shortLabel: 'Science',
		icon: 'Flask',
		invertedScale: false,
		description: 'Science assessment results (informational only)',
	},
	CHRONIC: {
		code: 'CHRONIC',
		label: 'Chronic Absenteeism',
		shortLabel: 'Chronic Abs.',
		icon: 'Calendar',
		invertedScale: true,
		description: 'Percentage of students absent 10% or more of school days',
	},
	SUSP: {
		code: 'SUSP',
		label: 'Suspension Rate',
		shortLabel: 'Suspension',
		icon: 'AlertTriangle',
		invertedScale: true,
		description: 'Percentage of students suspended at least once',
	},
	GRAD: {
		code: 'GRAD',
		label: 'Graduation Rate',
		shortLabel: 'Graduation',
		icon: 'GraduationCap',
		invertedScale: false,
		description: 'Four-year cohort graduation rate',
	},
	ELPI: {
		code: 'ELPI',
		label: 'English Learner Progress',
		shortLabel: 'EL Progress',
		icon: 'Languages',
		invertedScale: false,
		description: 'Progress of English Learners toward English proficiency',
	},
	CCI: {
		code: 'CCI',
		label: 'College/Career',
		shortLabel: 'College/Career',
		icon: 'Briefcase',
		invertedScale: false,
		description: 'Percentage of students prepared for college and career',
	},
} as const

export type IndicatorCode = keyof typeof INDICATORS
export type IndicatorConfig = (typeof INDICATORS)[IndicatorCode]

/**
 * Order of indicators for display purposes.
 */
export const INDICATOR_ORDER: IndicatorCode[] = [
	'ELA',
	'MATH',
	'CHRONIC',
	'SUSP',
	'GRAD',
	'ELPI',
	'CCI',
	'SCI',
]

/**
 * Color level names and their CSS colors.
 */
export const COLOR_LEVELS = {
	1: { name: 'Red', color: 'var(--color-cde-dashboard-red)', label: 'Very Low' },
	2: { name: 'Orange', color: 'var(--color-cde-dashboard-orange)', label: 'Low' },
	3: { name: 'Yellow', color: 'var(--color-cde-dashboard-yellow)', label: 'Medium' },
	4: { name: 'Green', color: 'var(--color-cde-dashboard-green)', label: 'High' },
	5: { name: 'Blue', color: 'var(--color-cde-dashboard-blue)', label: 'Very High' },
	0: { name: 'None', color: '#95a5a6', label: 'No Data' },
} as const

export type ColorLevel = keyof typeof COLOR_LEVELS

/**
 * Student group codes and their display names.
 */
export const STUDENT_GROUPS = {
	ALL: 'All Students',
	AA: 'African American',
	AI: 'American Indian',
	AS: 'Asian',
	FI: 'Filipino',
	HI: 'Hispanic',
	PI: 'Pacific Islander',
	WH: 'White',
	MR: 'Two or More Races',
	EL: 'English Learners',
	SED: 'Socioeconomically Disadvantaged',
	SWD: 'Students with Disabilities',
	FOS: 'Foster Youth',
	HOM: 'Homeless',
	MIG: 'Migrant',
} as const

export type StudentGroupCode = keyof typeof STUDENT_GROUPS

/**
 * Statewide CDS code (14 zeros).
 */
export const STATEWIDE_CDS = '00000000000000'

/**
 * Get the display name for an indicator code.
 */
export function getIndicatorLabel(code: string): string {
	return INDICATORS[code as IndicatorCode]?.label ?? code
}

/**
 * Get the short label for an indicator code.
 */
export function getIndicatorShortLabel(code: string): string {
	return INDICATORS[code as IndicatorCode]?.shortLabel ?? code
}

/**
 * Get the color info for a color level.
 */
export function getColorInfo(level: number | null | undefined) {
	return COLOR_LEVELS[(level ?? 0) as ColorLevel] ?? COLOR_LEVELS[0]
}

/**
 * Get the display name for a student group code.
 */
export function getStudentGroupName(code: string): string {
	return STUDENT_GROUPS[code as StudentGroupCode] ?? code
}
