import { Skeleton } from '@/components/ui/skeleton.tsx'
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from '@/components/ui/table.tsx'

const PendingItems = () => (
	<Table>
		<TableHeader>
			<TableRow>
				<TableHead className='w-40'>ID</TableHead>
				<TableHead className='w-40'>Title</TableHead>
				<TableHead className='w-40'>Description</TableHead>
				<TableHead className='w-40'>Actions</TableHead>
			</TableRow>
		</TableHeader>
		<TableBody>
			{[...Array(5)].map((_, index) => (
				<TableRow key={index}>
					<TableCell>
						<Skeleton className='h-4 w-full' />
					</TableCell>
					<TableCell>
						<Skeleton className='h-4 w-full' />
					</TableCell>
					<TableCell>
						<Skeleton className='h-4 w-full' />
					</TableCell>
					<TableCell>
						<Skeleton className='h-4 w-full' />
					</TableCell>
				</TableRow>
			))}
		</TableBody>
	</Table>
)

export default PendingItems
