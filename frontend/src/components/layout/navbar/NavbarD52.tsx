import { Link } from '@tanstack/react-router'
import { FaMagnifyingGlass } from 'react-icons/fa6'

import MobileButton from './MobileButton'
import SearchBar from './SearchBar'
import SettingsButton from './SettingsButton'

import styles from './NavbarD52.module.css'

export default function NavbarD52({ shadow = false }: { shadow?: boolean }) {
	return (
		<div
			className={`${styles.container} ${shadow ? styles.containerShadow : styles.containerBorder}`}
		>
			<nav className={styles.nav}>
				<div className={styles.logoWrapper}>
					<Link className={styles.logoLink} to='/'>
						<img src='/assets/logo/logo.svg' alt='Logo' className='h-10' />
						<span className='hidden md:block'>
							<span className='font-bold'>California Accountability</span> Panel
						</span>
					</Link>
				</div>
				<div className={styles.right}>
					<SearchBar />
					<FaMagnifyingGlass className={styles.searchIcon} />
					<div className={styles.linksContainer}>
						<Link
							to='/'
							className={styles.link}
							activeProps={{
								className: styles.linkSelected,
							}}
						>
							Home
						</Link>
						<Link
							to='/dashboard'
							className={styles.link}
							activeProps={{
								className: styles.linkSelected,
							}}
						>
							Dashboard
						</Link>
						<Link
							to='/report'
							className={styles.link}
							activeProps={{
								className: styles.linkSelected,
							}}
						>
							Report
						</Link>
						<SettingsButton />
					</div>
				</div>
				<MobileButton />
			</nav>
		</div>
	)
}
