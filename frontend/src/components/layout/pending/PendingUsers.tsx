import { Skeleton } from '@/components/ui/skeleton.tsx'
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from '@/components/ui/table.tsx'

const PendingUsers = () => (
	<Table>
		<TableHeader>
			<TableRow>
				<TableHead className='w-40'>Full name</TableHead>
				<TableHead className='w-40'>Email</TableHead>
				<TableHead className='w-40'>Role</TableHead>
				<TableHead className='w-40'>Status</TableHead>
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
					<TableCell>
						<Skeleton className='h-4 w-full' />
					</TableCell>
				</TableRow>
			))}
		</TableBody>
	</Table>
)

export default PendingUsers
