/**
 * The shape this report takes before its data arrives.
 *
 * The accountability catalogue is reference data: the indicators the state
 * measures, the student groups it reports them for, and the years it has
 * published. It changes only when new Dashboard files are imported, which
 * makes it the one thing on this page worth guessing at — the guess is right
 * almost every time, and being right early is what lets the page draw its own
 * structure instead of a grey box.
 *
 * Two guesses, in order. The catalogue this browser last saw is tried first,
 * because it came from this deployment's own API and so is true for this
 * deployment's data. Failing that, the snapshot below, which is what the state
 * had published as of 2024-25.
 *
 * Nothing here is ever shown as a state figure. An assumed catalogue names the
 * indicators and populates the filters; every measured number stays a skeleton
 * until the API answers.
 */
import type { DashboardCatalog } from '@/lib/client'

const STORAGE_KEY = 'accountabilityCatalog'

/**
 * The state's own indicators, as published for 2024-25.
 *
 * Only ever seen on a browser's first visit — after that the remembered
 * catalogue is newer than this one and takes its place.
 */
const PUBLISHED_2025: DashboardCatalog = {
	reportingYear: 2025,
	years: [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018],
	indicators: [
		{
			code: 'ELA',
			name: 'English Language Arts/Literacy',
			shortName: 'ELA',
			lowerIsBetter: false,
			unit: 'dfs',
			sortOrder: 1,
			isInformational: false,
		},
		{
			code: 'MATH',
			name: 'Mathematics',
			shortName: 'Math',
			lowerIsBetter: false,
			unit: 'dfs',
			sortOrder: 2,
			isInformational: false,
		},
		{
			code: 'CHRO',
			name: 'Chronic Absenteeism',
			shortName: 'Chronic Absenteeism',
			lowerIsBetter: true,
			unit: 'percent',
			sortOrder: 3,
			isInformational: false,
		},
		{
			code: 'SUSP',
			name: 'Suspension Rate',
			shortName: 'Suspension',
			lowerIsBetter: true,
			unit: 'percent',
			sortOrder: 4,
			isInformational: false,
		},
		{
			code: 'GRAD',
			name: 'Graduation Rate',
			shortName: 'Graduation',
			lowerIsBetter: false,
			unit: 'percent',
			sortOrder: 5,
			isInformational: false,
		},
		{
			code: 'CCI',
			name: 'College/Career',
			shortName: 'College/Career',
			lowerIsBetter: false,
			unit: 'percent',
			sortOrder: 6,
			isInformational: false,
		},
		{
			code: 'ELPI',
			name: 'English Learner Progress',
			shortName: 'EL Progress',
			lowerIsBetter: false,
			unit: 'percent',
			sortOrder: 7,
			isInformational: false,
		},
		{
			code: 'SCIENCE',
			name: 'Science',
			shortName: 'Science',
			lowerIsBetter: false,
			unit: 'points',
			sortOrder: 8,
			isInformational: false,
		},
		{
			code: 'ELPACPART',
			name: 'ELPAC Participation Rate',
			shortName: 'ELPAC Participation',
			lowerIsBetter: false,
			unit: 'percent',
			sortOrder: 9,
			isInformational: true,
		},
	],
	studentGroups: [
		{ code: 'ALL', name: 'All Students' },
		{ code: 'AA', name: 'Black/African American' },
		{ code: 'AI', name: 'American Indian or Alaska Native' },
		{ code: 'AS', name: 'Asian' },
		{ code: 'FI', name: 'Filipino' },
		{ code: 'HI', name: 'Hispanic' },
		{ code: 'PI', name: 'Native Hawaiian or Pacific Islander' },
		{ code: 'WH', name: 'White' },
		{ code: 'MR', name: 'Two or More Races' },
		{ code: 'EL', name: 'English Learners' },
		{ code: 'ELO', name: 'English Learners Only' },
		{ code: 'LTEL', name: 'Long-Term English Learners' },
		{ code: 'RFP', name: 'Reclassified Fluent English Proficient' },
		{ code: 'EO', name: 'English Only' },
		{ code: 'SED', name: 'Socioeconomically Disadvantaged' },
		{ code: 'SWD', name: 'Students with Disabilities' },
		{ code: 'FOS', name: 'Foster Youth' },
		{ code: 'HOM', name: 'Homeless Youth' },
		{ code: 'SBA', name: 'Smarter Balanced Assessment' },
		{ code: 'CAA', name: 'California Alternate Assessment' },
		{ code: 'CAST', name: 'California Science Test' },
	],
	colors: { '1': 'Red', '2': 'Orange', '3': 'Yellow', '4': 'Green', '5': 'Blue' },
}

/**
 * A catalogue is only worth trusting if it still looks like one, because the
 * snapshot in storage may have been written by an older build.
 */
function isUsable(value: unknown): value is DashboardCatalog {
	const catalog = value as Partial<DashboardCatalog> | null
	return Boolean(
		catalog &&
		typeof catalog.reportingYear === 'number' &&
		Array.isArray(catalog.years) &&
		catalog.years.length > 0 &&
		Array.isArray(catalog.indicators) &&
		catalog.indicators.length > 0 &&
		Array.isArray(catalog.studentGroups) &&
		catalog.studentGroups.length > 0,
	)
}

function recall(): DashboardCatalog | null {
	if (typeof window === 'undefined') return null
	try {
		const stored = localStorage.getItem(STORAGE_KEY)
		if (!stored) return null
		const parsed: unknown = JSON.parse(stored)
		return isUsable(parsed) ? parsed : null
	} catch {
		return null
	}
}

/**
 * Held at module scope so the placeholder keeps one identity for as long as
 * the guess itself is unchanged. React Query hands `placeholderData` straight
 * to the component, and a fresh object on every render would restart every
 * memo that depends on the catalogue.
 *
 * Filled on first use rather than on import. `localStorage.getItem` and the
 * parse behind it are synchronous main-thread work, and this module is reached
 * from the shared bundle — resolving it eagerly would put that work in front of
 * the first paint of every page in the application, including the pages that
 * never show this report. Deferring it means only the page that needs a guess
 * pays for one, at the moment it is about to draw with it.
 */
let assumed: DashboardCatalog | null = null

/** The best guess available right now. */
export function assumedCatalog(): DashboardCatalog {
	assumed ??= recall() ?? PUBLISHED_2025
	return assumed
}

/** Whether the guess came from this deployment rather than the snapshot. */
export function isRemembered(): boolean {
	return assumedCatalog() !== PUBLISHED_2025
}

/**
 * Keep a catalogue the API actually returned, for the next visit.
 *
 * Called from the query function rather than an effect so the guess is updated
 * once per fetch, not once per render of every component that reads it.
 */
export function rememberCatalog(catalog: DashboardCatalog): void {
	if (!isUsable(catalog)) return
	assumed = catalog
	if (typeof window === 'undefined') return
	try {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(catalog))
	} catch {
		// A browser that refuses storage still gets the in-memory guess above.
	}
}

/**
 * The indicator this page opens on when nothing has said otherwise.
 *
 * The API sorts its results by the catalogue's own `sortOrder`, so the first
 * indicator in the catalogue is the one that will be selected once the results
 * arrive — for any entity that reports it. Guessing it lets the breakdown
 * beneath the grid start fetching in parallel with the grid itself instead of
 * waiting for it.
 */
export function assumedIndicator(catalog: DashboardCatalog): string | undefined {
	return catalog.indicators
		.filter((indicator) => !indicator.isInformational)
		.reduce<(typeof catalog.indicators)[number] | undefined>(
			(best, indicator) => (!best || indicator.sortOrder < best.sortOrder ? indicator : best),
			undefined,
		)?.code
}
