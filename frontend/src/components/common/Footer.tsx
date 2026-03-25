import { GithubIcon, Linkedin01Icon, NewTwitterIcon } from '@hugeicons/core-free-icons'
import { HugeiconsIcon } from '@hugeicons/react'

const socialLinks = [
	{
		icon: GithubIcon,
		href: 'https://github.com/fastapi/fastapi',
		label: 'GitHub',
	},
	{ icon: NewTwitterIcon, href: 'https://x.com/fastapi', label: 'X' },
	{
		icon: Linkedin01Icon,
		href: 'https://linkedin.com/company/fastapi',
		label: 'LinkedIn',
	},
]

export function Footer() {
	const currentYear = new Date().getFullYear()

	return (
		<footer className='border-t py-4 px-6'>
			<div className='flex flex-col items-center justify-between gap-4 sm:flex-row'>
				<p className='text-muted-foreground text-sm'>Full Stack FastAPI Template - {currentYear}</p>
				<div className='flex items-center gap-4'>
					{socialLinks.map(({ icon: Icon, href, label }) => (
						<a
							key={label}
							href={href}
							target='_blank'
							rel='noopener noreferrer'
							aria-label={label}
							className='text-muted-foreground hover:text-foreground transition-colors'
						>
							<HugeiconsIcon icon={Icon} className='h-5 w-5' />
						</a>
					))}
				</div>
			</div>
		</footer>
	)
}
