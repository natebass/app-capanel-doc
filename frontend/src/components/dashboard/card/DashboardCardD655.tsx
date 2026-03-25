import { ArrowUp01Icon, Dollar01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'

import { Card, CardContent } from '@/components/ui/card'

export default function DashboardCardD655() {
	return (
		<Card>
			<CardContent className='pt-6'>
				<div className='flex justify-between items-center'>
					<div>
						<p className='text-sm text-muted-foreground font-medium'>2024-2025 Cohort Total</p>
						<p className='text-2xl font-bold'>$45,231</p>
						<div className='flex items-center gap-1'>
							<HugeiconsIcon icon={ArrowUp01Icon} className='h-3 w-3 text-green-500' />
							<span className='text-sm text-green-500'>+8.2%</span>
						</div>
					</div>
					<div className='p-3 bg-green-50 rounded-lg'>
						<HugeiconsIcon icon={Dollar01Icon} className='h-6 w-6 text-green-500' />
					</div>
				</div>
			</CardContent>
		</Card>
	)
}
