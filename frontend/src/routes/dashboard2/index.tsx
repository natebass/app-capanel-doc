import {
	ActivityIcon,
	AnalyticsUpIcon,
	ArrowDown01Icon,
	ArrowUp01Icon,
	Dollar01Icon,
	Home01Icon,
	Settings02Icon,
	ShoppingBasket01Icon,
	UserGroupIcon,
	UserIcon,
} from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Spinner } from '@/components/ui/spinner'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useCensusDataById, useTotalEnrollment } from '@/routes/-hooks/hooks/useCensusData'

export const Route = createFileRoute('/dashboard2/')({
	component: Dashboard2Page,
})

// Component to display total enrollment with loading and error states
function TotalEnrollmentDisplay() {
	const { totalEnr, isLoading, isError, hasData } = useTotalEnrollment()

	if (isLoading) {
		return (
			<div className='flex justify-center items-center h-10'>
				<Spinner className='h-5 w-5 text-blue-500' />
			</div>
		)
	}

	if (isError) {
		return (
			<div className='text-red-600 text-sm bg-red-50 border border-red-200 rounded-md p-2 text-center'>
				Failed to load data
			</div>
		)
	}

	if (!hasData) {
		return <p className='text-2xl font-bold'>N/A</p>
	}

	// Format the number with commas for thousands
	const formattedTotalEnr = totalEnr?.toLocaleString() || '0'

	return <p className='text-2xl font-bold'>{formattedTotalEnr}</p>
}

// Census Data Search Card Component with tabs
function CensusDataSearchCard() {
	// State to manage which census data ID to search for
	const [searchId, setSearchId] = useState<string | null>(null)

	// Sample ID for demonstration - in a real app, this would come from user input or URL params
	const sampleId = '123e4567-e89b-12d3-a456-426614174000'

	// Fetch census data by ID when searchId is set
	const { data: censusData, isLoading, isError } = useCensusDataById(searchId)

	// Component to display census data content
	function CensusDataContent({
		censusData,
		isLoading,
		isError,
	}: {
		censusData: any
		isLoading: boolean
		isError: boolean
	}) {
		if (isLoading) {
			return (
				<div className='flex flex-col gap-2'>
					<p className='text-sm text-muted-foreground font-medium'>Census Data</p>
					<Skeleton className='h-8 w-[120px]' />
					<Skeleton className='h-4 w-[100px]' />
				</div>
			)
		}

		if (isError) {
			return (
				<div className='flex flex-col gap-2'>
					<p className='text-sm text-muted-foreground font-medium'>Census Data</p>
					<div className='text-red-600 text-sm bg-red-50 border border-red-200 rounded-md p-2 text-center'>
						Failed to load census data
					</div>
				</div>
			)
		}

		if (!censusData?.data) {
			return (
				<div className='flex flex-col gap-2'>
					<p className='text-sm text-muted-foreground font-medium'>Census Data</p>
					<p className='text-lg text-muted-foreground'>No data found</p>
				</div>
			)
		}

		const data = censusData.data

		return (
			<div className='flex flex-col gap-2'>
				<div className='flex justify-between items-start'>
					<div className='flex flex-col gap-0'>
						<span className='text-xs text-muted-foreground'>
							{data.school_name || 'Unknown School'}
						</span>
						<span className='text-sm text-muted-foreground font-medium'>Total Enrollment</span>
					</div>
					<HugeiconsIcon icon={Home01Icon} className='h-4 w-4 text-blue-500' />
				</div>
				<p className='text-2xl font-bold text-blue-500'>
					{data.total_enr?.toLocaleString() || '0'}
				</p>
				<div className='flex items-center gap-2'>
					<Badge variant={data.charter === 'Y' ? 'default' : 'secondary'} className='text-xs'>
						{data.charter === 'Y' ? 'Charter' : 'Public'}
					</Badge>
					<span className='text-xs text-muted-foreground'>AY {data.academic_year}</span>
				</div>
			</div>
		)
	}

	return (
		<Tabs defaultValue='found-id'>
			<TabsList className='mb-3'>
				<TabsTrigger value='found-id'>Found ID</TabsTrigger>
				<TabsTrigger value='default'>Default</TabsTrigger>
				<TabsTrigger value='last-searched'>Last Searched</TabsTrigger>
			</TabsList>

			<TabsContent value='found-id'>
				<div className='flex flex-col gap-3'>
					<CensusDataContent censusData={censusData} isLoading={isLoading} isError={isError} />
					{!searchId && (
						<Button size='xs' variant='outline' onClick={() => setSearchId(sampleId)}>
							Load Sample Data
						</Button>
					)}
				</div>
			</TabsContent>

			<TabsContent value='default'>
				<div className='flex flex-col gap-2'>
					<p className='text-sm text-muted-foreground font-medium'>Default View</p>
					<p className='text-2xl font-bold'>-</p>
					<div className='flex items-center gap-2'>
						<HugeiconsIcon icon={UserGroupIcon} className='h-3 w-3 text-gray-500' />
						<span className='text-sm text-muted-foreground'>No data selected</span>
					</div>
				</div>
			</TabsContent>

			<TabsContent value='last-searched'>
				<div className='flex flex-col gap-2'>
					<p className='text-sm text-muted-foreground font-medium'>Last Searched</p>
					<p className='text-2xl font-bold'>{searchId ? '✓' : '-'}</p>
					<div className='flex items-center gap-2'>
						<HugeiconsIcon icon={ActivityIcon} className='h-3 w-3 text-blue-500' />
						<span className='text-sm text-muted-foreground'>
							{searchId ? 'Data loaded' : 'No recent searches'}
						</span>
					</div>
				</div>
			</TabsContent>
		</Tabs>
	)
}

function Dashboard2Page() {
	return (
		<div className='container max-w-7xl mx-auto py-8'>
			<div className='flex flex-col gap-8'>
				{/* Page Header */}
				<div>
					<h1 className='text-3xl font-bold mb-2'>Dashboard</h1>
					<p className='text-muted-foreground text-lg'>
						Welcome back! Here's an overview of your application.
					</p>
				</div>

				{/* Stats Cards */}
				<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
					<Card>
						<CardContent className='pt-6'>
							<Tabs defaultValue='total'>
								<TabsList className='mb-3'>
									<TabsTrigger value='total'>Total</TabsTrigger>
									<TabsTrigger value='active'>Active</TabsTrigger>
									<TabsTrigger value='new'>New</TabsTrigger>
								</TabsList>

								<TabsContent value='total'>
									<div className='flex flex-col gap-2'>
										<p className='text-sm text-muted-foreground font-medium'>Total Users</p>
										<TotalEnrollmentDisplay />
										<div className='flex items-center gap-1'>
											<HugeiconsIcon icon={ArrowUp01Icon} className='h-3 w-3 text-green-500' />
											<span className='text-sm text-green-500'>+12.5% from last month</span>
										</div>
									</div>
								</TabsContent>

								<TabsContent value='active'>
									<div className='flex flex-col gap-2'>
										<p className='text-sm text-muted-foreground font-medium'>Active Users (30d)</p>
										<p className='text-2xl font-bold'>1,987</p>
										<div className='flex items-center gap-1'>
											<HugeiconsIcon icon={ArrowUp01Icon} className='h-3 w-3 text-green-500' />
											<span className='text-sm text-green-500'>+8.3% from last month</span>
										</div>
									</div>
								</TabsContent>

								<TabsContent value='new'>
									<div className='flex flex-col gap-2'>
										<p className='text-lg text-muted-foreground font-medium'>New Users (7d)</p>
										<p className='text-2xl font-bold'>142</p>
										<div className='flex items-center gap-1'>
											<HugeiconsIcon icon={ArrowDown01Icon} className='h-3 w-3 text-red-500' />
											<span className='text-sm text-red-500'>-5.2% from last week</span>
										</div>
									</div>
								</TabsContent>
							</Tabs>
						</CardContent>
					</Card>

					<Card>
						<CardContent className='pt-6'>
							<CensusDataSearchCard />
						</CardContent>
					</Card>

					<Card>
						<CardContent className='pt-6'>
							<div className='flex justify-between items-center'>
								<div>
									<p className='text-sm text-muted-foreground font-medium'>Orders</p>
									<p className='text-2xl font-bold'>1,234</p>
									<div className='flex items-center gap-1'>
										<HugeiconsIcon icon={ArrowDown01Icon} className='h-3 w-3 text-red-500' />
										<span className='text-sm text-red-500'>-3.1%</span>
									</div>
								</div>
								<div className='p-3 bg-orange-50 rounded-lg'>
									<HugeiconsIcon icon={ShoppingBasket01Icon} className='h-6 w-6 text-orange-500' />
								</div>
							</div>
						</CardContent>
					</Card>

					<Card>
						<CardContent className='pt-6'>
							<div className='flex justify-between items-center'>
								<div>
									<p className='text-sm text-muted-foreground font-medium'>Growth Rate</p>
									<p className='text-2xl font-bold'>15.3%</p>
									<div className='flex items-center gap-1'>
										<HugeiconsIcon icon={ArrowUp01Icon} className='h-3 w-3 text-green-500' />
										<span className='text-sm text-green-500'>+2.4%</span>
									</div>
								</div>
								<div className='p-3 bg-purple-50 rounded-lg'>
									<HugeiconsIcon icon={AnalyticsUpIcon} className='h-6 w-6 text-purple-500' />
								</div>
							</div>
						</CardContent>
					</Card>
				</div>

				{/* Main Content Cards */}
				<div className='grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6'>
					{/* Activity Card */}
					<Card className='border'>
						<CardHeader>
							<div className='flex justify-between items-center'>
								<h2 className='text-lg font-semibold'>Recent Activity</h2>
								<Badge variant='secondary'>Live</Badge>
							</div>
						</CardHeader>
						<CardContent>
							<div className='flex flex-col gap-4'>
								<div className='flex items-center gap-3'>
									<div className='p-2 bg-blue-50 rounded-md'>
										<HugeiconsIcon icon={UserIcon} className='text-blue-500' />
									</div>
									<div className='flex-1'>
										<p className='font-medium'>New user registered</p>
										<p className='text-sm text-muted-foreground'>
											john.doe@example.com joined 2 minutes ago
										</p>
									</div>
									<span className='text-xs text-muted-foreground'>2m ago</span>
								</div>

								<div className='flex items-center gap-3'>
									<div className='p-2 bg-green-50 rounded-md'>
										<HugeiconsIcon icon={Dollar01Icon} className='text-green-500' />
									</div>
									<div className='flex-1'>
										<p className='font-medium'>Payment received</p>
										<p className='text-sm text-muted-foreground'>
											$299.00 from Premium subscription
										</p>
									</div>
									<span className='text-xs text-muted-foreground'>5m ago</span>
								</div>

								<div className='flex items-center gap-3'>
									<div className='p-2 bg-orange-50 rounded-md'>
										<HugeiconsIcon icon={ShoppingBasket01Icon} className='text-orange-500' />
									</div>
									<div className='flex-1'>
										<p className='font-medium'>New order placed</p>
										<p className='text-sm text-muted-foreground'>Order #1234 for $89.99</p>
									</div>
									<span className='text-xs text-muted-foreground'>15m ago</span>
								</div>
							</div>
						</CardContent>
						<CardFooter>
							<Button variant='ghost' size='sm' className='w-full'>
								View all activity
							</Button>
						</CardFooter>
					</Card>

					{/* Quick Actions Card */}
					<Card className='bg-muted/50'>
						<CardHeader>
							<h2 className='text-lg font-semibold'>Quick Actions</h2>
						</CardHeader>
						<CardContent>
							<div className='flex flex-col gap-3'>
								<Button className='w-full'>
									<HugeiconsIcon icon={UserIcon} className='mr-2' />
									Add New User
								</Button>
								<Button variant='outline' className='w-full'>
									<HugeiconsIcon icon={ActivityIcon} className='mr-2' />
									View Analytics
								</Button>
								<Button variant='outline' className='w-full'>
									<HugeiconsIcon icon={Settings02Icon} className='mr-2' />
									Settings
								</Button>
							</div>
						</CardContent>
					</Card>
				</div>

				{/* Additional Example Cards */}
				<div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
					<Card className='border'>
						<CardHeader>
							<h3 className='text-base font-semibold'>System Status</h3>
						</CardHeader>
						<CardContent>
							<div className='flex flex-col gap-3'>
								<div className='flex justify-between items-center'>
									<span className='text-sm'>API Status</span>
									<Badge variant='default' className='bg-green-500'>
										Operational
									</Badge>
								</div>
								<div className='flex justify-between items-center'>
									<span className='text-sm'>Database</span>
									<Badge variant='default' className='bg-green-500'>
										Healthy
									</Badge>
								</div>
								<div className='flex justify-between items-center'>
									<span className='text-sm'>Cache</span>
									<Badge variant='default' className='bg-yellow-500'>
										Warning
									</Badge>
								</div>
							</div>
						</CardContent>
					</Card>

					<Card>
						<CardHeader>
							<h3 className='text-base font-semibold'>Performance</h3>
						</CardHeader>
						<CardContent>
							<div className='flex flex-col gap-3'>
								<div className='text-center'>
									<p className='text-xs text-muted-foreground font-medium'>Response Time</p>
									<p className='text-lg font-bold'>234ms</p>
									<div className='flex justify-center items-center gap-1'>
										<HugeiconsIcon icon={ArrowDown01Icon} className='h-3 w-3 text-green-500' />
										<span className='text-sm text-green-500'>-12ms from last hour</span>
									</div>
								</div>
							</div>
						</CardContent>
					</Card>

					<Card className='border'>
						<CardHeader>
							<h3 className='text-base font-semibold'>Storage Usage</h3>
						</CardHeader>
						<CardContent>
							<div className='flex flex-col gap-2'>
								<div className='flex justify-between w-full'>
									<span className='text-sm'>Used</span>
									<span className='text-sm font-medium'>45.2 GB</span>
								</div>
								<div className='flex justify-between w-full'>
									<span className='text-sm'>Available</span>
									<span className='text-sm font-medium'>54.8 GB</span>
								</div>
								<div className='w-full h-2 bg-gray-200 rounded-full'>
									<div className='h-full bg-blue-500 rounded-full' style={{ width: '45.2%' }} />
								</div>
							</div>
						</CardContent>
					</Card>
				</div>
			</div>
		</div>
	)
}
