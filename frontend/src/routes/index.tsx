import { createFileRoute, Link } from '@tanstack/react-router'

import { Button } from '@/components/ui/button.tsx'
import NavbarD52 from '@/components/ui/navbar/NavbarD52.tsx'

export const Route = createFileRoute('/')({
	component: RouteComponent,
})

function RouteComponent() {
	return (
		<div className='min-h-screen bg-gray-50/50'>
			<NavbarD52 />
			<div className='container mx-auto px-4 pb-8 pt-16 max-w-7xl'>
				{/* First Section: Split Layout */}
				<div className='grid grid-cols-1 md:grid-cols-2 gap-8 mb-24 items-start'>
					{/* Left Side: Product Intro & Audience (Ordered List) */}
					<div className='space-y-6'>
						<h1 className='text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl'>
							California Accountability Panel
						</h1>
						<ol className='list-decimal list-outside ml-5 space-y-6 text-lg text-muted-foreground'>
							{/* Item 1: Primary Action */}
							<li className='pl-2'>
								<span className='block mb-2 text-foreground'>Explore the dashboard.</span>
								<Button render={<Link to='/dashboard'>Find a school</Link>} variant='default' />
								<Button
									render={<Link to='/dashboard'>View state-wide summary</Link>}
									variant='default'
								/>
							</li>

							{/* Item 2: Secondary Action */}
							<li className='pl-2'>
								<span className='block mb-2 text-foreground'>
									Search for a school or district to view performance data.
								</span>
								<Button render={<Link to='/dashboard'>Search now</Link>} variant='outline' />
							</li>

							{/* Item 3: Ghost/Tertiary Action */}
							<li className='pl-2'>
								<span className='block mb-2 text-foreground'>
									Personalize the dashboard by uploading custom CSV data.
								</span>
								<Button render={<Link to='/dashboard'>Upload CSV file</Link>} variant='secondary' />
							</li>
						</ol>
					</div>

					{/* Right Side: Features & Overview (Unordered List) */}
					<div className=' rounded-2xl'>
						<ul className='list-disc  space-y-3 text-gray-600'>
							<li>
								Use
								<a
									href='https://www.cde.ca.gov/ta/ac/cm/fivebyfivecolortables.asp'
									className='pl-2 text-blue-500'
								>
									________________
								</a>{' '}
								to identify strengths and areas for improvement to support student success.
								<br />
								<img src='/gauge-screenshot2.png' className='pt-4 pb-8' />
							</li>
							<li className='pl-2'>
								Over 1,500 schools and districts (including alternative schools) are available. See
								the support list for details.{' '}
							</li>
						</ul>
					</div>
				</div>

				{/* Second Section: How it works */}
				<div className='space-y-12 max-w-4xl mx-auto'>
					<section className='space-y-6'>
						<h2 className='text-3xl font-bold text-gray-900'>
							How does California’s accountability system work?
						</h2>
						<p className='text-lg text-gray-700 leading-relaxed'>
							To help parents and educators identify strengths and areas for improvement, California
							reports how districts, schools (including alternative schools), and student groups are
							performing across state and local measures.
						</p>
					</section>

					<section className='space-y-6'>
						<h3 className='text-2xl font-semibold text-gray-900'>State Measures</h3>
						<p className='text-gray-700'>
							For state measures, performance is based on two factors:
						</p>
						<div className='grid grid-cols-1 sm:grid-cols-2 gap-4'>
							<div className='bg-blue-50 p-4 rounded-xl border border-blue-100 flex items-center'>
								<span className='text-4xl font-bold text-blue-600 mr-4'>1</span>
								<span className='text-blue-900 font-medium'>Current year results</span>
							</div>
							<div className='bg-blue-50 p-4 rounded-xl border border-blue-100 flex items-center'>
								<span className='text-4xl font-bold text-blue-600 mr-4'>2</span>
								<span className='text-blue-900 font-medium'>
									Whether results improved from the prior year
								</span>
							</div>
						</div>
						<p className='text-gray-700 mt-4'>
							Performance on state measures, using comparable statewide data, is represented by one
							of five colors. The performance level (color) is not included when there are fewer
							than 30 students in any year.
						</p>

						{/* Performance Gauges Grid */}
						<div className='grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 py-6'>
							{[
								{
									label: 'Lowest Performance',
									color: 'Red',
									src: 'https://www.caschooldashboard.org/assets/img/gauges/red.png',
								},
								{
									label: 'Orange',
									color: 'Orange',
									src: 'https://www.caschooldashboard.org/assets/img/gauges/orange.png',
								},
								{
									label: 'Yellow',
									color: 'Yellow',
									src: 'https://www.caschooldashboard.org/assets/img/gauges/yellow.png',
								},
								{
									label: 'Green',
									color: 'Green',
									src: 'https://www.caschooldashboard.org/assets/img/gauges/green.png',
								},
								{
									label: 'Highest Performance',
									color: 'Blue',
									src: 'https://www.caschooldashboard.org/assets/img/gauges/blue.png',
								},
							].map((item) => (
								<div key={item.color} className='flex flex-col items-center text-center space-y-2'>
									<img
										src={item.src}
										alt={`${item.color} performance gauge`}
										className='w-24 h-auto'
									/>
									<span className='font-medium text-gray-900'>{item.color}</span>
									{item.label !== item.color && (
										<span className='text-xs text-gray-500 uppercase tracking-wide'>
											{item.label}
										</span>
									)}
								</div>
							))}
						</div>

						<section className='bg-gray-50 p-6 rounded-xl border border-gray-200 mt-8'>
							<h4 className='text-lg font-semibold text-gray-900 mb-2'>Note on Recent Years</h4>
							<p className='text-gray-700 mb-4'>
								Because performance on state measures was based only on current year results for the
								2022 Dashboard (i.e., 2021–22) and the 2023 College/Career Indicator, the color
								dials were replaced with one of five Status levels.
							</p>
							<div className='grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4'>
								{[
									{
										label: 'Lowest Performance',
										color: 'Very Low',
										src: 'https://www.caschooldashboard.org/assets/img/gauges/2022/red.png',
									},
									{
										label: 'Low',
										color: 'Low',
										src: 'https://www.caschooldashboard.org/assets/img/gauges/2022/orange.png',
									},
									{
										label: 'Medium',
										color: 'Medium',
										src: 'https://www.caschooldashboard.org/assets/img/gauges/2022/yellow.png',
									},
									{
										label: 'High',
										color: 'High',
										src: 'https://www.caschooldashboard.org/assets/img/gauges/2022/green.png',
									},
									{
										label: 'Highest Performance',
										color: 'Very High',
										src: 'https://www.caschooldashboard.org/assets/img/gauges/2022/blue.png',
									},
								].map((item) => (
									<div
										key={item.color}
										className='flex flex-col items-center text-center space-y-2'
									>
										<img
											src={item.src}
											alt={`${item.color} performance level`}
											className='w-24 h-auto'
										/>
										<span className='font-medium text-gray-900'>{item.color}</span>
										{item.label !== item.color && (
											<span className='text-xs text-gray-500 uppercase tracking-wide'>
												{item.label}
											</span>
										)}
									</div>
								))}
							</div>
						</section>

						<p className='text-gray-600 mt-4 text-sm'>
							State measures include chronic absenteeism, graduation rate, suspension rate, English
							learner progress, and academic performance (English language arts/literacy,
							mathematics, and science).
						</p>
					</section>

					<section className='space-y-4'>
						<h3 className='text-2xl font-semibold text-gray-900'>Local Measures</h3>
						<p className='text-gray-700 leading-relaxed'>
							Local measures are reported by school districts, county offices of education, and
							charter schools based on data available only at the local level. These measures
							include clean and safe buildings, school climate, parent and family engagement, and
							access to a broad course of study. This information is not available for individual
							schools or student groups.
						</p>
					</section>

					<section className='bg-yellow-50 border-l-4 border-yellow-400 p-4'>
						<p className='text-yellow-800'>
							Based on performance on state and local measures, schools and districts may be
							identified for support to improve student outcomes.
						</p>
					</section>
				</div>
			</div>
		</div>
	)
}
