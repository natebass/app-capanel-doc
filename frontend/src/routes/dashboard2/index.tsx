import { createFileRoute } from '@tanstack/react-router';
import {
	Box,
	Container,
	Grid,
	Heading,
	Text,
	Badge,
	Button,
	Icon,
	HStack,
	VStack,
	Tabs,
	Spinner,
	Skeleton,
	Alert,
} from '@chakra-ui/react';
import {
	Card,
	CardHeader,
	CardBody,
	CardFooter,
} from '../../components/ui/card';
import {
	FiUser,
	FiDollarSign,
	FiTrendingUp,
	FiShoppingCart,
	FiActivity,
	FiSettings,
	FiArrowUp,
	FiArrowDown,
	FiHome,
	FiUsers,
	FiMapPin,
} from 'react-icons/fi';
import {
	useTotalEnrollment,
	useCensusDataById,
} from '../../hooks/useCensusData';
import { useState } from 'react';

// Component to display total enrollment with loading and error states
function TotalEnrollmentDisplay() {
	const { totalEnr, isLoading, isError, hasData } = useTotalEnrollment();

	if (isLoading) {
		return (
			<Box
				display='flex'
				justifyContent='center'
				alignItems='center'
				height='40px'
			>
				<Spinner size='md' color='blue.500' />
			</Box>
		);
	}

	if (isError) {
		return (
			<Box
				color='red.600'
				fontSize='sm'
				bg='red.50'
				border='1px solid'
				borderColor='red.200'
				borderRadius='md'
				p={2}
				textAlign='center'
			>
				Failed to load data
			</Box>
		);
	}

	if (!hasData) {
		return (
			<Text fontSize='2xl' fontWeight='bold'>
				N/A
			</Text>
		);
	}

	// Format the number with commas for thousands
	const formattedTotalEnr = totalEnr?.toLocaleString() || '0';

	return (
		<Text fontSize='2xl' fontWeight='bold'>
			{formattedTotalEnr}
		</Text>
	);
}

// Census Data Search Card Component with tabs
function CensusDataSearchCard() {
	// State to manage which census data ID to search for
	const [searchId, setSearchId] = useState<string | null>(null);

	// Sample ID for demonstration - in a real app, this would come from user input or URL params
	const sampleId = '123e4567-e89b-12d3-a456-426614174000';

	// Fetch census data by ID when searchId is set
	const {
		data: censusData,
		isLoading,
		isError,
		error,
	} = useCensusDataById(searchId);

	// Component to display census data content
	function CensusDataContent({ censusData, isLoading, isError, error }) {
		if (isLoading) {
			return (
				<VStack align='stretch' gap={2}>
					<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
						Census Data
					</Text>
					<Skeleton height='32px' width='120px' />
					<Skeleton height='16px' width='100px' />
				</VStack>
			);
		}

		if (isError) {
			return (
				<VStack align='stretch' gap={2}>
					<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
						Census Data
					</Text>
					<Box
						color='red.600'
						fontSize='sm'
						bg='red.50'
						border='1px solid'
						borderColor='red.200'
						borderRadius='md'
						p={2}
						textAlign='center'
					>
						Failed to load census data
					</Box>
				</VStack>
			);
		}

		if (!censusData?.data) {
			return (
				<VStack align='stretch' gap={2}>
					<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
						Census Data
					</Text>
					<Text fontSize='lg' color='fg.muted'>
						No data found
					</Text>
				</VStack>
			);
		}

		const data = censusData.data;

		return (
			<VStack align='stretch' gap={2}>
				<HStack justify='space-between'>
					<VStack align='start' spacing={0}>
						<Text fontSize='xs' color='fg.muted'>
							{data.school_name || 'Unknown School'}
						</Text>
						<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
							Total Enrollment
						</Text>
					</VStack>
					<Icon as={FiHome} color='blue.500' boxSize={4} />
				</HStack>
				<Text fontSize='2xl' fontWeight='bold' color='blue.500'>
					{data.total_enr?.toLocaleString() || '0'}
				</Text>
				<HStack>
					<Badge
						colorScheme={data.charter === 'Y' ? 'purple' : 'gray'}
						size='xs'
					>
						{data.charter === 'Y' ? 'Charter' : 'Public'}
					</Badge>
					<Text fontSize='xs' color='fg.muted'>
						AY {data.academic_year}
					</Text>
				</HStack>
			</VStack>
		);
	}

	return (
		<Tabs.Root defaultValue='found-id' variant='subtle' size='lg'>
			<Tabs.List mb={3}>
				<Tabs.Trigger value='found-id'>Found ID</Tabs.Trigger>
				<Tabs.Trigger value='default'>Default</Tabs.Trigger>
				<Tabs.Trigger value='last-searched'>Last Searched</Tabs.Trigger>
			</Tabs.List>

			<Tabs.Content value='found-id'>
				<VStack gap={3}>
					<CensusDataContent
						censusData={censusData}
						isLoading={isLoading}
						isError={isError}
						error={error}
					/>
					{!searchId && (
						<Button
							size='xs'
							colorScheme='blue'
							variant='outline'
							onClick={() => setSearchId(sampleId)}
						>
							Load Sample Data
						</Button>
					)}
				</VStack>
			</Tabs.Content>

			<Tabs.Content value='default'>
				<VStack align='stretch' gap={2}>
					<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
						Default View
					</Text>
					<Text fontSize='2xl' fontWeight='bold'>
						-
					</Text>
					<HStack>
						<Icon as={FiUsers} color='gray.500' boxSize={3} />
						<Text fontSize='sm' color='fg.muted'>
							No data selected
						</Text>
					</HStack>
				</VStack>
			</Tabs.Content>

			<Tabs.Content value='last-searched'>
				<VStack align='stretch' gap={2}>
					<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
						Last Searched
					</Text>
					<Text fontSize='2xl' fontWeight='bold'>
						{searchId ? '✓' : '-'}
					</Text>
					<HStack>
						<Icon as={FiActivity} color='blue.500' boxSize={3} />
						<Text fontSize='sm' color='fg.muted'>
							{searchId ? 'Data loaded' : 'No recent searches'}
						</Text>
					</HStack>
				</VStack>
			</Tabs.Content>
		</Tabs.Root>
	);
}

export const Route = createFileRoute('/dashboard2/')({
	component: Dashboard2Page,
});

function Dashboard2Page() {
	return (
		<Container maxW='7xl' py={8}>
			<VStack gap={8} align='stretch'>
				{/* Page Header */}
				<Box>
					<Heading size='2xl' mb={2}>
						Dashboard
					</Heading>
					<Text color='fg.muted' fontSize='lg'>
						Welcome back! Here's an overview of your application.
					</Text>
				</Box>

				{/* Stats Cards */}
				<Grid
					templateColumns={{
						base: '1fr',
						md: 'repeat(2, 1fr)',
						lg: 'repeat(4, 1fr)',
					}}
					gap={6}
				>
					<Card variant='elevated'>
						<CardBody>
							<Tabs.Root defaultValue='total' variant='subtle' size='lg'>
								<Tabs.List mb={3}>
									<Tabs.Trigger value='total'>Total</Tabs.Trigger>
									<Tabs.Trigger value='active'>Active</Tabs.Trigger>
									<Tabs.Trigger value='new'>New</Tabs.Trigger>
								</Tabs.List>

								<Tabs.Content value='total'>
									<VStack align='stretch' gap={2}>
										<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
											Total Users
										</Text>
										<TotalEnrollmentDisplay />
										<HStack>
											<Icon as={FiArrowUp} color='green.500' boxSize={3} />
											<Text fontSize='sm' color='green.500'>
												+12.5% from last month
											</Text>
										</HStack>
									</VStack>
								</Tabs.Content>

								<Tabs.Content value='active'>
									<VStack align='stretch' gap={2}>
										<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
											Active Users (30d)
										</Text>
										<Text fontSize='2xl' fontWeight='bold'>
											1,987
										</Text>
										<HStack>
											<Icon as={FiArrowUp} color='green.500' boxSize={3} />
											<Text fontSize='sm' color='green.500'>
												+8.3% from last month
											</Text>
										</HStack>
									</VStack>
								</Tabs.Content>

								<Tabs.Content value='new'>
									<VStack align='stretch' gap={2}>
										<Text fontSize='lg' color='fg.muted' fontWeight='medium'>
											New Users (7d)
										</Text>
										<Text fontSize='2xl' fontWeight='bold'>
											142
										</Text>
										<HStack>
											<Icon as={FiArrowDown} color='red.500' boxSize={3} />
											<Text fontSize='sm' color='red.500'>
												-5.2% from last week
											</Text>
										</HStack>
									</VStack>
								</Tabs.Content>
							</Tabs.Root>
						</CardBody>
					</Card>

					<Card variant='elevated'>
						<CardBody>
							<CensusDataSearchCard />
						</CardBody>
					</Card>

					<Card variant='elevated'>
						<CardBody>
							<HStack justify='space-between'>
								<Box>
									<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
										Orders
									</Text>
									<Text fontSize='2xl' fontWeight='bold'>
										1,234
									</Text>
									<HStack>
										<Icon as={FiArrowDown} color='red.500' boxSize={3} />
										<Text fontSize='sm' color='red.500'>
											-3.1%
										</Text>
									</HStack>
								</Box>
								<Box p={3} bg='orange.50' borderRadius='lg'>
									<Icon as={FiShoppingCart} boxSize={6} color='orange.500' />
								</Box>
							</HStack>
						</CardBody>
					</Card>

					<Card variant='elevated'>
						<CardBody>
							<HStack justify='space-between'>
								<Box>
									<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
										Growth Rate
									</Text>
									<Text fontSize='2xl' fontWeight='bold'>
										15.3%
									</Text>
									<HStack>
										<Icon as={FiArrowUp} color='green.500' boxSize={3} />
										<Text fontSize='sm' color='green.500'>
											+2.4%
										</Text>
									</HStack>
								</Box>
								<Box p={3} bg='purple.50' borderRadius='lg'>
									<Icon as={FiTrendingUp} boxSize={6} color='purple.500' />
								</Box>
							</HStack>
						</CardBody>
					</Card>
				</Grid>

				{/* Main Content Cards */}
				<Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
					{/* Activity Card */}
					<Card variant='outline'>
						<CardHeader>
							<HStack justify='space-between'>
								<Heading size='md'>Recent Activity</Heading>
								<Badge colorScheme='blue' variant='subtle'>
									Live
								</Badge>
							</HStack>
						</CardHeader>
						<CardBody>
							<VStack gap={4} align='stretch'>
								<HStack>
									<Box p={2} bg='blue.50' borderRadius='md'>
										<Icon as={FiUser} color='blue.500' />
									</Box>
									<Box flex={1}>
										<Text fontWeight='medium'>New user registered</Text>
										<Text fontSize='sm' color='fg.muted'>
											john.doe@example.com joined 2 minutes ago
										</Text>
									</Box>
									<Text fontSize='xs' color='fg.muted'>
										2m ago
									</Text>
								</HStack>

								<HStack>
									<Box p={2} bg='green.50' borderRadius='md'>
										<Icon as={FiDollarSign} color='green.500' />
									</Box>
									<Box flex={1}>
										<Text fontWeight='medium'>Payment received</Text>
										<Text fontSize='sm' color='fg.muted'>
											$299.00 from Premium subscription
										</Text>
									</Box>
									<Text fontSize='xs' color='fg.muted'>
										5m ago
									</Text>
								</HStack>

								<HStack>
									<Box p={2} bg='orange.50' borderRadius='md'>
										<Icon as={FiShoppingCart} color='orange.500' />
									</Box>
									<Box flex={1}>
										<Text fontWeight='medium'>New order placed</Text>
										<Text fontSize='sm' color='fg.muted'>
											Order #1234 for $89.99
										</Text>
									</Box>
									<Text fontSize='xs' color='fg.muted'>
										15m ago
									</Text>
								</HStack>
							</VStack>
						</CardBody>
						<CardFooter>
							<Button variant='ghost' size='sm' width='full'>
								View all activity
							</Button>
						</CardFooter>
					</Card>

					{/* Quick Actions Card */}
					<Card variant='filled'>
						<CardHeader>
							<Heading size='md'>Quick Actions</Heading>
						</CardHeader>
						<CardBody>
							<VStack gap={3}>
								<Button width='full' colorScheme='blue' variant='solid'>
									<Icon as={FiUser} mr={2} />
									Add New User
								</Button>
								<Button width='full' colorScheme='green' variant='outline'>
									<Icon as={FiActivity} mr={2} />
									View Analytics
								</Button>
								<Button width='full' colorScheme='gray' variant='outline'>
									<Icon as={FiSettings} mr={2} />
									Settings
								</Button>
							</VStack>
						</CardBody>
					</Card>
				</Grid>

				{/* Additional Example Cards */}
				<Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6}>
					<Card variant='outline'>
						<CardHeader>
							<Heading size='sm'>System Status</Heading>
						</CardHeader>
						<CardBody>
							<VStack gap={3} align='stretch'>
								<HStack justify='space-between'>
									<Text fontSize='sm'>API Status</Text>
									<Badge colorScheme='green' size='sm'>
										Operational
									</Badge>
								</HStack>
								<HStack justify='space-between'>
									<Text fontSize='sm'>Database</Text>
									<Badge colorScheme='green' size='sm'>
										Healthy
									</Badge>
								</HStack>
								<HStack justify='space-between'>
									<Text fontSize='sm'>Cache</Text>
									<Badge colorScheme='yellow' size='sm'>
										Warning
									</Badge>
								</HStack>
							</VStack>
						</CardBody>
					</Card>

					<Card variant='elevated'>
						<CardHeader>
							<Heading size='sm'>Performance</Heading>
						</CardHeader>
						<CardBody>
							<VStack gap={3}>
								<Box textAlign='center'>
									<Text fontSize='xs' color='fg.muted' fontWeight='medium'>
										Response Time
									</Text>
									<Text fontSize='lg' fontWeight='bold'>
										234ms
									</Text>
									<HStack justify='center'>
										<Icon as={FiArrowDown} color='green.500' boxSize={3} />
										<Text fontSize='sm' color='green.500'>
											-12ms from last hour
										</Text>
									</HStack>
								</Box>
							</VStack>
						</CardBody>
					</Card>

					<Card variant='outline'>
						<CardHeader>
							<Heading size='sm'>Storage Usage</Heading>
						</CardHeader>
						<CardBody>
							<VStack gap={2}>
								<HStack justify='space-between' width='full'>
									<Text fontSize='sm'>Used</Text>
									<Text fontSize='sm' fontWeight='medium'>
										45.2 GB
									</Text>
								</HStack>
								<HStack justify='space-between' width='full'>
									<Text fontSize='sm'>Available</Text>
									<Text fontSize='sm' fontWeight='medium'>
										54.8 GB
									</Text>
								</HStack>
								<Box width='full' height={2} bg='gray.200' borderRadius='full'>
									<Box
										width='45.2%'
										height='full'
										bg='blue.500'
										borderRadius='full'
									/>
								</Box>
							</VStack>
						</CardBody>
					</Card>
				</Grid>
			</VStack>
		</Container>
	);
}
