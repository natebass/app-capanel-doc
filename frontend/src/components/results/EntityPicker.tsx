/**
 * Search for a school, district or county by name or CDS code.
 *
 * The state's own reports make you walk a county → district → school cascade;
 * a single search is faster when you already know what you are looking for, so
 * this searches every level at once and labels each result with its level.
 */
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
	Command,
	CommandEmpty,
	CommandGroup,
	CommandInput,
	CommandItem,
	CommandList,
} from '@/components/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import type { EntityPublic } from '@/lib/client'
import { entitySearchQuery } from '@/lib/services/assessments'
import { useDebounce } from '@/routes/-hooks/hooks/useDebounce'

const LEVEL_LABEL: Record<string, string> = {
	state: 'State',
	county: 'County',
	district: 'District',
	school: 'School',
}

export function EntityPicker({
	entity,
	onSelect,
}: {
	entity: EntityPublic | undefined
	onSelect: (entity: EntityPublic) => void
}) {
	const [open, setOpen] = useState(false)
	const [term, setTerm] = useState('')
	const debounced = useDebounce(term, 250)
	const { data, isFetching } = useQuery(entitySearchQuery(debounced))

	return (
		<Popover open={open} onOpenChange={setOpen}>
			<PopoverTrigger
				render={
					<Button
						variant='outline'
						aria-haspopup='dialog'
						aria-expanded={open}
						className='w-full justify-between font-normal sm:w-96'
					/>
				}
			>
				<span className='truncate'>{entity?.displayName ?? 'Choose a school or district'}</span>
				{entity ? (
					<Badge variant='secondary' className='ml-2 shrink-0'>
						{LEVEL_LABEL[entity.entityLevel] ?? entity.entityLevel}
					</Badge>
				) : null}
			</PopoverTrigger>
			<PopoverContent className='w-[min(32rem,calc(100vw-2rem))] p-0' align='start'>
				<Command shouldFilter={false}>
					<CommandInput
						placeholder='Search by name or CDS code…'
						value={term}
						onValueChange={setTerm}
					/>
					<CommandList>
						<CommandEmpty>
							{term.trim().length < 2
								? 'Type at least two characters.'
								: isFetching
									? 'Searching…'
									: 'Nothing matched.'}
						</CommandEmpty>
						<CommandGroup>
							{data?.data.map((match) => (
								<CommandItem
									key={match.cdsCode}
									value={match.cdsCode}
									onSelect={() => {
										onSelect(match)
										setOpen(false)
										setTerm('')
									}}
								>
									<div className='flex min-w-0 flex-1 flex-col'>
										<span className='truncate'>{match.displayName}</span>
										<span className='truncate text-xs text-muted-foreground'>
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
					</CommandList>
				</Command>
			</PopoverContent>
		</Popover>
	)
}
