import { Search01Icon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'
import { Link } from '@tanstack/react-router'

import { assetUrl } from '@/lib/utils'

import MobileButton from '../../button/MobileButton'
import SettingsButton from '../../button/SettingsButton'
import SearchBar from './SearchBar'

import styles from './navbar-D52.module.css'

/**
 * The default navigation bar. It is sticky because it provides access to search and settings.
 */
export default function NavbarD52({ shadow = false }: { shadow?: boolean }) {
	return (
		<div
			className={`${styles.container} ${shadow ? styles.containerShadow : styles.containerBorder}`}
		>
			<nav className={styles.nav}>
				<div className={styles.logoWrapper}>
					<Link className={styles.logoLink} to='/'>
						<img src={assetUrl('/assets/logo/logo.svg')} alt='Logo' className='h-10' />
						<span className='hidden md:block font-figtree font-semibold'>
							California <span className='italic'>Dashboard</span>
						</span>
					</Link>
				</div>
				<div className={styles.right}>
					<SearchBar />
					<HugeiconsIcon icon={Search01Icon} className={styles.searchIcon} />
					<div className={styles.linksContainer}>
						<Link
							to='/dashboard'
							className={styles.link}
							activeProps={{
								className: styles.linkSelected,
							}}
						>
							Statewide
						</Link>
						<Link
							to='/accountability'
							className={styles.link}
							activeProps={{
								className: styles.linkSelected,
							}}
						>
							Individual
						</Link>
						<SettingsButton />
					</div>
				</div>
				<MobileButton />
			</nav>
		</div>
	)
}
