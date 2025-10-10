import { createFileRoute } from '@tanstack/react-router';
import DashboardD09 from '../../components/Dashboard/DashboardD09';
import NavbarD52 from '../../components/ui/navbar/NavbarD52';
import ScrollReset from '../../hooks/ScrollReset';

export const Route = createFileRoute('/dashboard/')({
	component: DashboardPage,
});

function DashboardPage() {
	return (
		<div className='min-h-screen bg-[#f3f4fa]'>
			<ScrollReset />
			<NavbarD52 shadow />
			<DashboardD09
				data={{
					organization: 'D909',
				}}
			/>
			;
		</div>
	);
}
