import { useNavigate } from '@tanstack/react-router'
import { Building2, Clock, GraduationCap, MapPin, Search, Sparkles, TrendingUp } from 'lucide-react'
import * as React from 'react'

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
import { cn } from '@/lib/utils.ts'

import styles from './SearchBar.module.css'

const RECENT_SEARCHES_KEY = 'search-history'
const MAX_RECENT = 5

interface SearchResult {
	id: string
	label: string
	type: 'school' | 'district' | 'county'
	cds: string
	county?: string
	district?: string
}

interface SearchBarProps {
	className?: string
	placeholder?: string
}

// Mock data - replace with actual API calls
const SUGGESTED_SCHOOLS: SearchResult[] = [
	{
		id: '1',
		label: 'Los Angeles Unified School District',
		type: 'district',
		cds: '19647330000000',
		county: 'Los Angeles',
	},
	{
		id: '2',
		label: 'San Diego Unified School District',
		type: 'district',
		cds: '37683380000000',
		county: 'San Diego',
	},
	{
		id: '3',
		label: 'Fresno Unified School District',
		type: 'district',
		cds: '10621660000000',
		county: 'Fresno',
	},
]

const QUICK_FILTERS = [
	{ id: 'top-performing', label: 'Top Performing Schools', icon: TrendingUp },
	{ id: 'nearby', label: 'Schools Near Me', icon: MapPin },
	{ id: 'charter', label: 'Charter Schools', icon: Sparkles },
]

function getRecentSearches(): SearchResult[] {
	if (typeof window === 'undefined') return []
	try {
		const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
		return stored ? JSON.parse(stored) : []
	} catch {
		return []
	}
}

function addRecentSearch(result: SearchResult) {
	const recent = getRecentSearches().filter((r) => r.cds !== result.cds)
	const updated = [result, ...recent].slice(0, MAX_RECENT)
	localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated))
}

function clearRecentSearches() {
	localStorage.removeItem(RECENT_SEARCHES_KEY)
}

function getTypeIcon(type: SearchResult['type']) {
	switch (type) {
		case 'school':
			return GraduationCap
		case 'district':
			return Building2
		case 'county':
			return MapPin
		default:
			return GraduationCap
	}
}

export default function SearchBar({
	className,
	placeholder = 'Search schools, districts...',
}: SearchBarProps) {
	const [open, setOpen] = React.useState(false)
	const [query, setQuery] = React.useState('')
	const [recentSearches, setRecentSearches] = React.useState<SearchResult[]>([])
	const navigate = useNavigate()

	// Load recent searches on mount
	React.useEffect(() => {
		setRecentSearches(getRecentSearches())
	}, [open])

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

	const handleSelect = (result: SearchResult) => {
		addRecentSearch(result)
		setOpen(false)
		setQuery('')
		navigate({ to: '/dashboard', search: { q: result.cds } })
	}

	const handleClearRecent = (e: React.MouseEvent) => {
		e.stopPropagation()
		clearRecentSearches()
		setRecentSearches([])
	}

	// Filter suggestions based on query
	const filteredSuggestions = React.useMemo(() => {
		if (!query) return SUGGESTED_SCHOOLS
		return SUGGESTED_SCHOOLS.filter(
			(s) =>
				s.label.toLowerCase().includes(query.toLowerCase()) ||
				s.county?.toLowerCase().includes(query.toLowerCase()),
		)
	}, [query])

	return (
		<div className={styles.searchbar}>
			{/* Trigger Button */}
			<button type='button' onClick={() => setOpen(true)} className={cn(styles.trigger, className)}>
				<Search className='h-4 w-4 shrink-0' />
				<span className='flex-1 text-left truncate'>{placeholder}</span>
				<KbdGroup className='hidden sm:flex'>
					<Kbd>⌘</Kbd>
					<Kbd>K</Kbd>
				</KbdGroup>
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
						placeholder='Search schools, districts, counties...'
						value={query}
						onValueChange={setQuery}
					/>
					<CommandList className={styles.commandList}>
						<CommandEmpty className='py-12'>
							<div className={styles.emptyContainer}>
								<Search className={styles.emptyIcon} />
								<p>No results found for "{query}"</p>
								<p className='text-xs'>Try searching by school name, district, or county</p>
							</div>
						</CommandEmpty>

						{/* Recent Searches */}
						{recentSearches.length > 0 && !query && (
							<CommandGroup
								heading={
									<div className={styles.headingRow}>
										<span className={styles.headingLabel}>
											<Clock className='h-3 w-3' />
											Recent
										</span>
										<button type='button' onClick={handleClearRecent} className={styles.clearBtn}>
											Clear
										</button>
									</div>
								}
							>
								{recentSearches.map((result) => {
									const Icon = getTypeIcon(result.type)
									return (
										<CommandItem
											key={`recent-${result.cds}`}
											value={result.cds}
											onSelect={() => handleSelect(result)}
											className={styles.commandItem}
										>
											<div className={styles.iconBox}>
												<Icon className='h-4 w-4' />
											</div>
											<div className='flex flex-col'>
												<span className='font-medium'>{result.label}</span>
												{result.county && (
													<span className={styles.resultMeta}>{result.county} County</span>
												)}
											</div>
										</CommandItem>
									)
								})}
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
												<filter.icon className='h-4 w-4' />
											</div>
											<span>{filter.label}</span>
										</CommandItem>
									))}
								</CommandGroup>
								<CommandSeparator />
							</>
						)}

						{/* Suggestions / Search Results */}
						<CommandGroup heading={query ? 'Results' : 'Suggested'}>
							{filteredSuggestions.map((result) => {
								const Icon = getTypeIcon(result.type)
								return (
									<CommandItem
										key={result.cds}
										value={result.cds}
										onSelect={() => handleSelect(result)}
										className={styles.commandItem}
									>
										<div className={styles.iconBox}>
											<Icon className='h-4 w-4' />
										</div>
										<div className={styles.resultContent}>
											<span className='font-medium'>{result.label}</span>
											<span className={styles.resultMeta}>
												{result.type.charAt(0).toUpperCase() + result.type.slice(1)}
												{result.county && ` • ${result.county} County`}
											</span>
										</div>
									</CommandItem>
								)
							})}
						</CommandGroup>
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
