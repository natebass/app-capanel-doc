import { Avatar, AvatarFallback, AvatarGroup, AvatarImage } from '@/components/ui/avatar'

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
