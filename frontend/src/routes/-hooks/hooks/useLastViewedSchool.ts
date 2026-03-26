import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useState } from 'react'

import { AcademicIndicatorsService } from '../../../lib/client'
import { STATEWIDE_CDS } from '../../../lib/constants/indicators'

const LOCAL_STORAGE_KEY = 'lastViewedSchool'

interface LastViewedSchool {
	cds: string
	name: string | null
}

interface UseLastViewedSchoolOptions {
	isAuthenticated?: boolean
}

/**
 * Hook for managing last viewed school.
 *
 * Uses localStorage for anonymous users and server-side storage for
 * authenticated users.
 */
export function useLastViewedSchool({ isAuthenticated = false }: UseLastViewedSchoolOptions = {}) {
	const queryClient = useQueryClient()

	// Local state for immediate UI updates
	const [localSchool, setLocalSchool] = useState<LastViewedSchool | null>(() => {
		if (typeof window === 'undefined') return null
		try {
			const stored = localStorage.getItem(LOCAL_STORAGE_KEY)
			return stored ? JSON.parse(stored) : null
		} catch {
			return null
		}
	})

	// Server-side query for authenticated users
	const serverQuery = useQuery({
		queryKey: ['userPreferences', 'lastViewedCds'],
		queryFn: async () => {
			const response = await AcademicIndicatorsService.academicIndicatorsGetLastViewedCds()
			if (response.error) {
				throw new Error('Failed to fetch user preferences')
			}
			return response.data as { last_viewed_cds: string | null }
		},
		enabled: isAuthenticated,
		staleTime: 5 * 60 * 1000, // 5 minutes
	})

	// Server-side mutation for authenticated users
	const serverMutation = useMutation({
		mutationFn: async (cds: string) => {
			const response = await AcademicIndicatorsService.academicIndicatorsUpdateUserPreferences({
				body: { last_viewed_cds: cds },
			})
			if (response.error) {
				throw new Error('Failed to update user preferences')
			}
			return response.data
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ['userPreferences', 'lastViewedCds'] })
		},
	})

	// Determine the effective CDS code
	const effectiveCds = isAuthenticated
		? (serverQuery.data?.last_viewed_cds ?? localSchool?.cds ?? STATEWIDE_CDS)
		: (localSchool?.cds ?? STATEWIDE_CDS)

	// Set last viewed school
	const setLastViewedSchool = useCallback(
		(school: LastViewedSchool) => {
			// Always update localStorage for quick access
			setLocalSchool(school)
			try {
				localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(school))
			} catch {
				// Ignore localStorage errors
			}

			// Also update server if authenticated
			if (isAuthenticated) {
				serverMutation.mutate(school.cds)
			}
		},
		[isAuthenticated, serverMutation],
	)

	// Sync localStorage to state on mount
	useEffect(() => {
		if (typeof window === 'undefined') return
		try {
			const stored = localStorage.getItem(LOCAL_STORAGE_KEY)
			if (stored) {
				setLocalSchool(JSON.parse(stored))
			}
		} catch {
			// Ignore localStorage errors
		}
	}, [])

	return {
		cds: effectiveCds,
		school: localSchool,
		setLastViewedSchool,
		isLoading: isAuthenticated && serverQuery.isLoading,
	}
}

/**
 * Get the last viewed CDS from localStorage only.
 * Useful for initial route setup.
 */
export function getLastViewedCdsFromStorage(): string {
	if (typeof window === 'undefined') return STATEWIDE_CDS
	try {
		const stored = localStorage.getItem(LOCAL_STORAGE_KEY)
		if (stored) {
			const parsed = JSON.parse(stored)
			return parsed.cds || STATEWIDE_CDS
		}
	} catch {
		// Ignore errors
	}
	return STATEWIDE_CDS
}
