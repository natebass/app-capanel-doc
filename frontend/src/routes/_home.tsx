import { createFileRoute, Outlet } from '@tanstack/react-router';
import NavbarD52 from '../components/ui/navbar/NavbarD52';
import ScrollReset from '../hooks/ScrollReset';

export const Route = createFileRoute('/_home')({
	component: HomeLayout,
});

function HomeLayout() {
	return (
		<div className='min-h-screen'>
			<ScrollReset />
			<NavbarD52 />
			<Outlet />
		</div>
	);
}
