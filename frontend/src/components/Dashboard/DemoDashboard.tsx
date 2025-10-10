import {
	Badge,
	Box,
	Button,
	Container,
	Grid,
	Heading,
	HStack,
	Icon,
	Tabs,
	Text,
	VStack,
} from '@chakra-ui/react';
import {
	FiActivity,
	FiArrowDown,
	FiArrowUp,
	FiDollarSign,
	FiSettings,
	FiShoppingCart,
	FiTrendingUp,
	FiUser,
} from 'react-icons/fi';
import { Card, CardBody, CardFooter, CardHeader } from '../ui/card';

export default function DemoDashboard() {
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
										<Text fontSize='2xl' fontWeight='bold'>
											2,543
										</Text>
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
							<HStack justify='space-between'>
								<Box>
									<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
										Revenue
									</Text>
									<Text fontSize='2xl' fontWeight='bold'>
										$45,231
									</Text>
									<HStack>
										<Icon as={FiArrowUp} color='green.500' boxSize={3} />
										<Text fontSize='sm' color='green.500'>
											+8.2%
										</Text>
									</HStack>
								</Box>
								<Box p={3} bg='green.50' borderRadius='lg'>
									<Icon as={FiDollarSign} boxSize={6} color='green.500' />
								</Box>
							</HStack>
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
