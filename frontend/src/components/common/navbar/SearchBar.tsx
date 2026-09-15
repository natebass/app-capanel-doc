/**
 * The entity picker, in the navigation bar.
 *
 * Every report on this site is about one school, district or county, so the
 * choice of entity belongs where it is always reachable rather than repeated
 * on each page. The trigger names the entity that was last chosen *here* and
 * labels its level; an entity arrived at any other way — a link, a table row,
 * a pasted URL — leaves the "search…" prompt in place, so the trigger reads as
 * a record of what was searched rather than a second copy of the page heading.
 *
 * Selecting keeps you where you are. A reader comparing accountability reports
 * does not want to be dropped onto the assessment dashboard halfway through,
 * so the current route's other search parameters — year, student group, grade
 * — survive the change of entity.
 */
import {
	Building01Icon,
	Clock01Icon,
	MapsLocation01Icon,
	School01Icon,
	Search01Icon,
	Sorting05Icon,
	SparklesIcon,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, useRouterState } from '@tanstack/react-router'
import * as React from 'react'

import { Badge } from '@/components/ui/badge'
import {
	Command,
	CommandDialog,
	CommandEmpty,
	CommandGroup,
	CommandInput,
	CommandItem,
	CommandList,
	CommandSeparator,
} from '@/components/ui/command'
import { Kbd, KbdGroup } from '@/components/ui/kbd'
import { useDebounce } from '@/hooks/useDebounce'
import type { EntityPublic } from '@/lib/client'
import { entitySearchQuery } from '@/lib/services/assessments'
import { cn } from '@/lib/utils.ts'

import styles from './SearchBar.module.css'

const RECENT_SEARCHES_KEY = 'search-history'
const MAX_RECENT = 5

const LEVEL_LABEL: Record<string, string> = {
	state: 'State',
	county: 'County',
	district: 'District',
	school: 'School',
}

/** What a recent search keeps: enough to redraw the row without a request. */
interface RecentEntity {
	cds: string
	label: string
	level: string
	meta?: string
}

interface SearchBarProps {
	className?: string
	placeholder?: string
}

/**
 * Somewhere to start from an empty box.
 *
 * Static, and the three largest districts in the state rather than anything
 * measured — they are a starting point, not a recommendation. Selecting one
 * goes through the same path a search result does, so these are real
 * destinations even though the list itself is hard-coded.
 */
const SUGGESTED_SCHOOLS: RecentEntity[] = [
	{
		cds: '19647330000000',
		label: 'Los Angeles Unified School District',
		level: 'district',
		meta: 'Los Angeles',
	},
	{
		cds: '37683380000000',
		label: 'San Diego Unified School District',
		level: 'district',
		meta: 'San Diego',
	},
	{
		cds: '10621660000000',
		label: 'Fresno Unified School District',
		level: 'district',
		meta: 'Fresno',
	},
]

/** Stubs. None of these do anything yet. */
const QUICK_FILTERS = [
	{ id: 'top-performing', label: 'Top Performing Schools', icon: Sorting05Icon },
	{ id: 'nearby', label: 'Schools Near Me', icon: MapsLocation01Icon },
	{ id: 'charter', label: 'Charter Schools', icon: SparklesIcon },
]

function getRecentSearches(): RecentEntity[] {
	if (typeof window === 'undefined') return []
	try {
		const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
		const parsed = stored ? JSON.parse(stored) : []
		// The key held a different shape before entities were real; anything
		// that does not look like one now is dropped rather than rendered.
		return Array.isArray(parsed)
			? parsed.filter((item): item is RecentEntity => typeof item?.cds === 'string' && item.label)
			: []
	} catch {
		return []
	}
}

function storeRecentSearches(recent: RecentEntity[]) {
	try {
		localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(recent))
	} catch {
		// A browser refusing storage is not worth failing a navigation over.
	}
}

function getTypeIcon(level: string) {
	switch (level) {
		case 'school':
			return School01Icon
		case 'district':
			return Building01Icon
		case 'county':
		case 'state':
			return MapsLocation01Icon
		default:
			return School01Icon
	}
}

function toRecent(entity: EntityPublic): RecentEntity {
	return {
		cds: entity.cdsCode,
		label: entity.displayName,
		level: entity.entityLevel,
		meta: [entity.districtName, entity.countyName]
			.filter((part) => part && part !== entity.displayName)
			.join(' · '),
	}
}

export default function SearchBar({
	className,
	placeholder = 'Search schools, districts...',
}: SearchBarProps) {
	const [open, setOpen] = React.useState(false)
	const [query, setQuery] = React.useState('')
	const [recentSearches, setRecentSearches] = React.useState<RecentEntity[]>(getRecentSearches)
	/** The last entity picked from this box; not whatever the route points at. */
	const [picked, setPicked] = React.useState<RecentEntity | null>(null)
	const debounced = useDebounce(query, 250)
	const navigate = useNavigate()

	const pathname = useRouterState({ select: (state) => state.location.pathname })

	const { data: results, isFetching } = useQuery(entitySearchQuery(debounced))

	// Keyboard shortcut to open
	React.useEffect(() => {
		const down = (e: KeyboardEvent) => {
			if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
				e.preventDefault()
				setOpen((prev) => !prev)
			}
		}
		document.addEventListener('keydown', down)
		return () => document.removeEventListener('keydown', down)
	}, [])

	const goTo = (cds: string) => {
		// Staying on the current report keeps the rest of the selection — the
		// year, the student group — rather than resetting it to a default.
		if (pathname.startsWith('/accountability')) {
			void navigate({ to: '/accountability', search: (previous) => ({ ...previous, cds }) })
			return
		}
		if (pathname.startsWith('/dashboard')) {
			void navigate({ to: '/dashboard', search: (previous) => ({ ...previous, cds }) })
			return
		}
		void navigate({ to: '/dashboard', search: { cds } })
	}

	const handleSelect = (entity: RecentEntity) => {
		const updated = [entity, ...recentSearches.filter((item) => item.cds !== entity.cds)].slice(
			0,
			MAX_RECENT,
		)
		setRecentSearches(updated)
		storeRecentSearches(updated)
		setPicked(entity)
		setOpen(false)
		setQuery('')
		goTo(entity.cds)
	}

	const handleClearRecent = (e: React.MouseEvent) => {
		e.stopPropagation()
		storeRecentSearches([])
		setRecentSearches([])
	}

	const matches = results?.data ?? []

	return (
		<div className={styles.searchbar}>
			{/* Trigger Button */}
			<button type='button' onClick={() => setOpen(true)} className={cn(styles.trigger, className)}>
				<HugeiconsIcon icon={Search01Icon} className='h-4 w-4 shrink-0' />
				{picked ? (
					<>
						<span className='flex-1 text-left truncate text-foreground'>{picked.label}</span>
						<Badge variant='secondary' className='shrink-0'>
							{LEVEL_LABEL[picked.level] ?? picked.level}
						</Badge>
					</>
				) : (
					<>
						<span className='flex-1 text-left truncate'>{placeholder}</span>
						<KbdGroup className='hidden sm:flex'>
							<Kbd>⌘</Kbd>
							<Kbd>K</Kbd>
						</KbdGroup>
					</>
				)}
			</button>

			{/* Command Dialog */}
			<CommandDialog
				open={open}
				onOpenChange={setOpen}
				title='Search'
				description='Search for schools, districts, or counties'
				className={styles.dialog}
			>
				<Command shouldFilter={false}>
					<CommandInput
						placeholder='Search by name or CDS code…'
						value={query}
						onValueChange={setQuery}
					/>
					<CommandList className={styles.commandList}>
						{/* Only ever seen mid-search: with the box empty there are always
						    the quick actions and the suggestions below to show. */}
						<CommandEmpty className='py-12'>
							<div className={styles.emptyContainer}>
								<HugeiconsIcon icon={Search01Icon} className={styles.emptyIcon} />
								<p>{isFetching ? 'Searching…' : `No results found for "${query}"`}</p>
							</div>
						</CommandEmpty>

						{/* Recent Searches */}
						{recentSearches.length > 0 && !query && (
							<CommandGroup
								heading={
									<div className={styles.headingRow}>
										<span className={styles.headingLabel}>
											<HugeiconsIcon icon={Clock01Icon} className='h-3 w-3' />
											Recent
										</span>
										<button type='button' onClick={handleClearRecent} className={styles.clearBtn}>
											Clear
										</button>
									</div>
								}
							>
								{recentSearches.map((entity) => (
									<CommandItem
										key={`recent-${entity.cds}`}
										value={entity.cds}
										onSelect={() => handleSelect(entity)}
										className={styles.commandItem}
									>
										<div className={styles.iconBox}>
											<HugeiconsIcon icon={getTypeIcon(entity.level)} className='h-4 w-4' />
										</div>
										<div className={styles.resultContent}>
											<span className='font-medium truncate'>{entity.label}</span>
											{entity.meta ? (
												<span className={styles.resultMeta}>{entity.meta}</span>
											) : null}
										</div>
										<Badge variant='secondary' className='ml-2 shrink-0'>
											{LEVEL_LABEL[entity.level] ?? entity.level}
										</Badge>
									</CommandItem>
								))}
							</CommandGroup>
						)}

						{recentSearches.length > 0 && !query && <CommandSeparator />}

						{/* Quick Filters */}
						{!query && (
							<>
								<CommandGroup heading='Quick Actions'>
									{QUICK_FILTERS.map((filter) => (
										<CommandItem key={filter.id} value={filter.id} className={styles.commandItem}>
											<div className={styles.iconBoxPrimary}>
												<HugeiconsIcon icon={filter.icon} className='h-4 w-4' />
											</div>
											<span>{filter.label}</span>
										</CommandItem>
									))}
								</CommandGroup>
								<CommandSeparator />

								{/* Suggestions */}
								<CommandGroup heading='Suggested'>
									{SUGGESTED_SCHOOLS.map((entity) => (
										<CommandItem
											key={entity.cds}
											value={entity.cds}
											onSelect={() => handleSelect(entity)}
											className={styles.commandItem}
										>
											<div className={styles.iconBox}>
												<HugeiconsIcon icon={getTypeIcon(entity.level)} className='h-4 w-4' />
											</div>
											<div className={styles.resultContent}>
												<span className='font-medium truncate'>{entity.label}</span>
												<span className={styles.resultMeta}>
													{LEVEL_LABEL[entity.level] ?? entity.level}
													{entity.meta ? ` • ${entity.meta} County` : ''}
												</span>
											</div>
										</CommandItem>
									))}
								</CommandGroup>
							</>
						)}

						{/* Search Results */}
						{matches.length > 0 ? (
							<CommandGroup heading='Results'>
								{matches.map((match) => (
									<CommandItem
										key={match.cdsCode}
										value={match.cdsCode}
										onSelect={() => handleSelect(toRecent(match))}
										className={styles.commandItem}
									>
										<div className={styles.iconBox}>
											<HugeiconsIcon icon={getTypeIcon(match.entityLevel)} className='h-4 w-4' />
										</div>
										<div className={styles.resultContent}>
											<span className='font-medium truncate'>{match.displayName}</span>
											<span className={cn(styles.resultMeta, 'truncate')}>
												{[match.districtName, match.countyName]
													.filter((part) => part && part !== match.displayName)
													.join(' · ')}
											</span>
										</div>
										<div className='ml-2 flex shrink-0 items-center gap-1'>
											{match.isCharter ? <Badge variant='outline'>Charter</Badge> : null}
											<Badge variant='secondary'>
												{LEVEL_LABEL[match.entityLevel] ?? match.entityLevel}
											</Badge>
										</div>
									</CommandItem>
								))}
							</CommandGroup>
						) : null}
					</CommandList>

					{/* Footer */}
					<div className={styles.footer}>
						<div className={styles.footerNav}>
							<span className={styles.footerHint}>
								<Kbd>↑↓</Kbd> Navigate
							</span>
							<span className={styles.footerHint}>
								<Kbd>↵</Kbd> Select
							</span>
							<span className={styles.footerHint}>
								<Kbd>Esc</Kbd> Close
							</span>
						</div>
						<span>Powered by CA Dashboard</span>
					</div>
				</Command>
			</CommandDialog>
		</div>
	)
}
