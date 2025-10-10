import { Box, HStack, Icon, Text } from '@chakra-ui/react';
import { FiArrowUp, FiDollarSign } from 'react-icons/fi';
import { Card, CardBody } from '../../ui/card';

export default function DashboardCardD655() {
	return (
		<Card variant='elevated'>
			<CardBody>
				<HStack justify='space-between'>
					<Box>
						<Text fontSize='sm' color='fg.muted' fontWeight='medium'>
							2024-2025 Cohort Total
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
	);
}
