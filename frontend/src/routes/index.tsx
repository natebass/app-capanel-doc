import { createFileRoute, Link } from '@tanstack/react-router'

import NavbarD52 from '@/components/common/navbar/navbar-D52'
import { Button } from '@/components/ui/button'

import styles from './index.module.css'

const PERFORMANCE_GAUGES = [
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
]

const STATUS_GAUGES = [
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
]

export const Route = createFileRoute('/')({
	component: RouteComponent,
})

function RouteComponent() {
	return (
		<div className={styles.page}>
			<NavbarD52 />
			<div className={styles.container}>
				<div className={styles.heroGrid}>
					<div className={styles.introSection}>
						<h1 className={styles.title}>California Accountability Panel</h1>
						<ol className={styles.actionList}>
							<li className={styles.actionItem}>
								<span className={styles.actionDescription}>Explore the dashboard.</span>
								<div className={styles.actionButtons}>
									<Button
										render={<Link to='/dashboard'>Find a school</Link>}
										variant='default'
										nativeButton={false}
									/>
									<Button
										render={<Link to='/dashboard'>View state-wide summary</Link>}
										variant='default'
										nativeButton={false}
									/>
								</div>
							</li>

							<li className={styles.actionItem}>
								<span className={styles.actionDescription}>
									Search for a school or district to view performance data.
								</span>
								<Button
									render={<Link to='/dashboard'>Search now</Link>}
									variant='outline'
									nativeButton={false}
								/>
							</li>

							<li className={styles.actionItem}>
								<span className={styles.actionDescription}>
									Personalize the dashboard by uploading custom CSV data.
								</span>
								<Button
									render={<Link to='/dashboard'>Upload CSV file</Link>}
									variant='secondary'
									nativeButton={false}
								/>
							</li>
						</ol>
					</div>

					<div className={styles.featurePanel}>
						<ul className={styles.featureList}>
							<li>
								Use
								<a
									href='https://www.cde.ca.gov/ta/ac/cm/fivebyfivecolortables.asp'
									className={styles.externalLink}
									target='_blank'
									rel='noreferrer'
								>
									________________
								</a>{' '}
								to identify strengths and areas for improvement to support student success.
								<br />
								<img
									src='/gauge-screenshot2.png'
									alt='Accountability gauge graph'
									className={styles.gaugeScreenshot}
								/>
							</li>
							<li className={styles.supportItem}>
								Over 1,500 schools and districts (including alternative schools) are available. See
								the support list for details.
							</li>
						</ul>
					</div>
				</div>

				<div className={styles.content}>
					<section className={styles.section}>
						<h2 className={styles.sectionHeading}>
							How does California’s accountability system work?
						</h2>
						<p className={styles.leadText}>
							To help parents and educators identify strengths and areas for improvement, California
							reports how districts, schools (including alternative schools), and student groups are
							performing across state and local measures.
						</p>
					</section>

					<section className={styles.section}>
						<h3 className={styles.subHeading}>State Measures</h3>
						<p className={styles.bodyText}>
							For state measures, performance is based on two factors:
						</p>
						<div className={styles.factorGrid}>
							<div className={styles.factorCard}>
								<span className={styles.factorNumber}>1</span>
								<span className={styles.factorLabel}>Current year results</span>
							</div>
							<div className={styles.factorCard}>
								<span className={styles.factorNumber}>2</span>
								<span className={styles.factorLabel}>
									Whether results improved from the prior year
								</span>
							</div>
						</div>
						<p className={styles.bodyText}>
							Performance on state measures, using comparable statewide data, is represented by one
							of five colors. The performance level (color) is not included when there are fewer
							than 30 students in any year.
						</p>

						<div className={styles.gaugeGrid}>
							{PERFORMANCE_GAUGES.map((item) => (
								<div key={item.color} className={styles.gaugeItem}>
									<img
										src={item.src}
										alt={`${item.color} performance gauge`}
										className={styles.gaugeImage}
									/>
									<span className={styles.gaugeColor}>{item.color}</span>
									{item.label !== item.color && (
										<span className={styles.gaugeLabel}>{item.label}</span>
									)}
								</div>
							))}
						</div>

						<section className={styles.noteCard}>
							<h4 className={styles.noteHeading}>Note on Recent Years</h4>
							<p className={styles.bodyText}>
								Because performance on state measures was based only on current year results for the
								2022 Dashboard (i.e., 2021–22) and the 2023 College/Career Indicator, the color
								dials were replaced with one of five Status levels.
							</p>
							<div className={styles.gaugeGrid}>
								{STATUS_GAUGES.map((item) => (
									<div key={item.color} className={styles.gaugeItem}>
										<img
											src={item.src}
											alt={`${item.color} performance level`}
											className={styles.gaugeImage}
										/>
										<span className={styles.gaugeColor}>{item.color}</span>
										{item.label !== item.color && (
											<span className={styles.gaugeLabel}>{item.label}</span>
										)}
									</div>
								))}
							</div>
						</section>

						<p className={styles.footnote}>
							State measures include chronic absenteeism, graduation rate, suspension rate, English
							learner progress, and academic performance (English language arts/literacy,
							mathematics, and science).
						</p>
					</section>

					<section className={styles.localSection}>
						<h3 className={styles.subHeading}>Local Measures</h3>
						<p className={styles.bodyText}>
							Local measures are reported by school districts, county offices of education, and
							charter schools based on data available only at the local level. These measures
							include clean and safe buildings, school climate, parent and family engagement, and
							access to a broad course of study. This information is not available for individual
							schools or student groups.
						</p>
					</section>

					<section className={styles.alertSection}>
						<p>
							Based on performance on state and local measures, schools and districts may be
							identified for support to improve student outcomes.
						</p>
					</section>
				</div>
			</div>
		</div>
	)
}
