import {
	AlertCircleIcon,
	GlobalEducationIcon,
	Location01Icon,
	UserGroupIcon,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { useEffect, useState } from 'react'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { CensusService } from '@/lib/services/censusService'

interface CensusData {
	census_data_id: string
	academic_year: number
	aggregation_level: string
	county_code: string
	district_code: string
	school_code: string
	county_name: string
	district_name: string
	school_name: string
	charter: string
	reporting_category: string
	total_enr: number
	gr_tk: number
	gr_kn: number
	gr_1: number
	gr_2: number
	gr_3: number
	gr_4: number
	gr_5: number
	gr_6: number
	gr_7: number
	gr_8: number
	gr_9: number
	gr_10: number
	gr_11: number
	gr_12: number
}

interface CensusDataCardProps {
	censusDataId: string
	variant?: 'outline' | 'filled' | 'elevated'
	showGradeBreakdown?: boolean
}

function CensusDataCard({ censusDataId, showGradeBreakdown = false }: CensusDataCardProps) {
	const [data, setData] = useState<CensusData | null>(null)
	const [loading, setLoading] = useState<boolean>(true)
	const [error, setError] = useState<string | null>(null)

	useEffect(() => {
		const fetchCensusData = async () => {
			try {
				setLoading(true)
				setError(null)
				const response = await CensusService.getCensusDataById(censusDataId)
				setData(response.data)
			} catch (err) {
				if (err instanceof Error) {
					if (err.message.includes('403')) {
						setError('Access denied: Superuser permissions required')
					} else if (err.message.includes('404')) {
						setError('Census data not found')
					} else {
						setError(err.message)
					}
				} else {
					setError('Failed to fetch census data')
				}
			} finally {
				setLoading(false)
			}
		}

		if (censusDataId) {
			void fetchCensusData()
		}
	}, [censusDataId])

	if (loading) {
		return (
			<Card>
				<CardHeader>
					<Skeleton className='h-6 w-[200px]' />
					<Skeleton className='h-4 w-[150px] mt-2' />
				</CardHeader>
				<CardContent>
					<div className='flex flex-col gap-3'>
						<Skeleton className='h-5 w-full' />
						<Skeleton className='h-5 w-4/5' />
						<Skeleton className='h-10 w-3/5' />
					</div>
				</CardContent>
			</Card>
		)
	}

	if (error) {
		return (
			<Card>
				<CardContent className='pt-6'>
					<Alert variant='destructive'>
						<HugeiconsIcon icon={AlertCircleIcon} className='h-4 w-4' />
						<AlertTitle>Error loading census data</AlertTitle>
						<AlertDescription>{error}</AlertDescription>
					</Alert>
				</CardContent>
				<CardFooter>
					<Button
						size='sm'
						onClick={() => window.location.reload()}
						className='w-full'
						variant='destructive'
					>
						Retry
					</Button>
				</CardFooter>
			</Card>
		)
	}

	if (!data) {
		return (
			<Card>
				<CardContent className='pt-6'>
					<p className='text-muted-foreground text-center'>
						No census data found for ID: {censusDataId}
					</p>
				</CardContent>
			</Card>
		)
	}

	const gradeData = [
		{ label: 'TK', count: data.gr_tk },
		{ label: 'K', count: data.gr_kn },
		{ label: '1', count: data.gr_1 },
		{ label: '2', count: data.gr_2 },
		{ label: '3', count: data.gr_3 },
		{ label: '4', count: data.gr_4 },
		{ label: '5', count: data.gr_5 },
		{ label: '6', count: data.gr_6 },
		{ label: '7', count: data.gr_7 },
		{ label: '8', count: data.gr_8 },
		{ label: '9', count: data.gr_9 },
		{ label: '10', count: data.gr_10 },
		{ label: '11', count: data.gr_11 },
		{ label: '12', count: data.gr_12 },
	].filter((grade) => grade.count > 0)

	return (
		<Card>
			<CardHeader>
				<div className='flex justify-between items-start'>
					<div className='flex flex-col gap-1 flex-1'>
						<div className='flex items-center gap-2'>
							<HugeiconsIcon icon={GlobalEducationIcon} className='h-5 w-5 text-blue-500' />
							<h3 className='font-semibold text-lg line-clamp-2'>{data.school_name}</h3>
						</div>
						<div className='flex items-center gap-2 text-muted-foreground text-sm flex-wrap'>
							<div className='flex items-center gap-1'>
								<HugeiconsIcon icon={Location01Icon} className='h-3 w-3' />
								<span>{data.district_name}</span>
							</div>
							<span>•</span>
							<span>{data.county_name}</span>
						</div>
					</div>
					<div className='flex flex-col gap-1 items-end'>
						<Badge variant={data.charter === 'Y' ? 'default' : 'secondary'}>
							{data.charter === 'Y' ? 'Charter' : 'Public'}
						</Badge>
						<span className='text-xs text-muted-foreground'>AY {data.academic_year}</span>
					</div>
				</div>
			</CardHeader>

			<CardContent>
				<div className='flex flex-col gap-4'>
					{/* Total Enrollment - Main statistic */}
					<div className='text-center w-full'>
						<div className='flex flex-col gap-1'>
							<div className='flex justify-center items-center gap-1 text-sm text-muted-foreground'>
								<HugeiconsIcon icon={UserGroupIcon} className='h-4 w-4' />
								<span>Total Enrollment</span>
							</div>
							<span className='text-2xl font-bold text-blue-500'>
								{data.total_enr.toLocaleString()}
							</span>
							<span className='text-sm text-muted-foreground'>{data.reporting_category}</span>
						</div>
					</div>

					{/* Grade-by-grade breakdown (optional) */}
					{showGradeBreakdown && gradeData.length > 0 && (
						<div className='w-full'>
							<p className='text-sm font-medium mb-3'>Enrollment by Grade</p>
							<div
								className='grid gap-2 max-h-[200px] overflow-y-auto p-1'
								style={{
									gridTemplateColumns: 'repeat(auto-fit, minmax(60px, 1fr))',
								}}
							>
								{gradeData.map((grade) => (
									<div
										key={grade.label}
										className='p-2 bg-muted rounded-md text-center hover:bg-muted/80 transition-colors'
									>
										<p className='text-xs text-muted-foreground'>Grade {grade.label}</p>
										<p className='text-sm font-bold'>{grade.count.toLocaleString()}</p>
									</div>
								))}
							</div>
						</div>
					)}
				</div>
			</CardContent>

			{/* Footer with additional metadata */}
			<CardFooter>
				<div className='flex flex-col gap-2 w-full'>
					<div className='flex justify-between w-full text-xs text-muted-foreground'>
						<span>School Code: {data.school_code}</span>
						<span>District Code: {data.district_code}</span>
					</div>
					{data.aggregation_level && (
						<p className='text-xs text-muted-foreground text-center'>
							Aggregation Level: {data.aggregation_level}
						</p>
					)}
				</div>
			</CardFooter>
		</Card>
	)
}

export { CensusDataCard }
export type { CensusDataCardProps, CensusData }
