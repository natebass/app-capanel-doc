import { Avatar, AvatarGroup } from '@chakra-ui/react';

export default function UserAvatar() {
	return (
		<AvatarGroup>
			<Avatar.Root>
				<Avatar.Fallback />
				<Avatar.Image />
			</Avatar.Root>
		</AvatarGroup>
	);
}
