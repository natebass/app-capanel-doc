import { Avatar, AvatarFallback, AvatarGroup, AvatarImage } from '@/components/ui/avatar.tsx'

export default function UserAvatar() {
	return (
		<AvatarGroup>
			<Avatar>
				<AvatarFallback />
				<AvatarImage />
			</Avatar>
		</AvatarGroup>
	)
}
