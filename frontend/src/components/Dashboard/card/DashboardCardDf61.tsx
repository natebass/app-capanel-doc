import { Card, CardBody } from "../../ui/card";

const data = {
	indicators: [
		{name: "English Language Arts"},
		{name: "Mathematics"},
		{name: "Suspension Rate"},
		{name: "Chronic Absenteeism"},
		{name: "English Learner Progress"},
		{name: "Science"},
		{name: "Graduation Rate"},
		{name: "College / Career"},
	]
}
export default function DashboardCardDf61() {
	return (
		{data.indicators.forEach((indicator) => (
		<Card variant="elevated">
			<CardBody>
			
			</CardBody>
		</Card>
		}
	);
}
