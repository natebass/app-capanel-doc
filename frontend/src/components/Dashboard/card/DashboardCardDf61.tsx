import { Card, CardContent } from '@/components/ui/card'

const data = {
	indicators: [
		{ name: 'English Language Arts' },
		{ name: 'Mathematics' },
		{ name: 'Suspension Rate' },
		{ name: 'Chronic Absenteeism' },
		{ name: 'English Learner Progress' },
		{ name: 'Science' },
		{ name: 'Graduation Rate' },
		{ name: 'College / Career' },
	],
}
export default function DashboardCardDf61() {
	return (
		<div>
			{data.indicators.map((_indicator, index) => (
				<Card key={index}>
					<CardContent>{/* You can render indicator-specific content here */}</CardContent>
				</Card>
			))}
		</div>
	)
}
