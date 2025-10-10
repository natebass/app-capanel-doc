'use client';

import { Box, type BoxProps } from '@chakra-ui/react';
import { forwardRef } from 'react';

/**
 * Card component props extending Chakra UI BoxProps
 *
 * @interface CardProps
 * @extends BoxProps
 */
export interface CardProps extends BoxProps {
	/**
	 * Visual style variant for the card
	 *
	 * - `outline`: Clean border design with transparent background (default)
	 * - `filled`: Solid muted background, no border
	 * - `elevated`: Clean background with subtle shadow for depth
	 *
	 * @default "outline"
	 */
	variant?: 'outline' | 'filled' | 'elevated';
}

/**
 * Card component - A flexible container for grouping related content and actions
 *
 * @example
 * ```tsx
 * <Card variant="elevated">
 *   <CardHeader>
 *     <Heading size="md">Title</Heading>
 *   </CardHeader>
 *   <CardBody>
 *     <Text>Content goes here</Text>
 *   </CardBody>
 *   <CardFooter>
 *     <Button>Action</Button>
 *   </CardFooter>
 * </Card>
 * ```
 *
 * @param variant - Visual style variant (outline | filled | elevated)
 * @param props - All Chakra UI Box props are supported
 */
export const Card = forwardRef<HTMLDivElement, CardProps>(
	({ variant = 'outline', ...props }, ref) => {
		const baseStyles = {
			borderRadius: 'lg',
			overflow: 'hidden',
			position: 'relative' as const,
		};

		const variantStyles = {
			outline: {
				border: '1px solid',
				borderColor: 'border.default',
				bg: 'bg.panel',
			},
			filled: {
				bg: 'bg.muted',
			},
			elevated: {
				bg: 'bg.panel',
				boxShadow: 'lg',
			},
		};

		return (
			<Box ref={ref} {...baseStyles} {...variantStyles[variant]} {...props} />
		);
	},
);

Card.displayName = 'Card';

/**
 * CardHeader component - Container for card title, subtitle, and header actions
 *
 * @example
 * ```tsx
 * <CardHeader>
 *   <HStack justify="space-between">
 *     <Heading size="md">Card Title</Heading>
 *     <Badge>Status</Badge>
 *   </HStack>
 * </CardHeader>
 * ```
 *
 * Features:
 * - Consistent padding (px=6, py=4)
 * - Bottom border separator
 * - Supports all Chakra UI Box props
 */
export const CardHeader = forwardRef<HTMLDivElement, BoxProps>((props, ref) => (
	<Box
		ref={ref}
		px={6}
		py={4}
		borderBottomWidth='1px'
		borderColor='border.default'
		{...props}
	/>
));

CardHeader.displayName = 'CardHeader';

/**
 * CardBody component - Main content area of the card
 *
 * @example
 * ```tsx
 * <CardBody>
 *   <Text>Your main content goes here</Text>
 *   <Button mt={4}>Action Button</Button>
 * </CardBody>
 * ```
 *
 * Features:
 * - Consistent padding (px=6, py=4)
 * - No borders or separators
 * - Supports all Chakra UI Box props
 * - Primary content container
 */
export const CardBody = forwardRef<HTMLDivElement, BoxProps>((props, ref) => (
	<Box ref={ref} px={6} py={4} {...props} />
));

CardBody.displayName = 'CardBody';

/**
 * CardFooter component - Container for actions and secondary content
 *
 * @example
 * ```tsx
 * <CardFooter>
 *   <HStack spacing={3}>
 *     <Button colorScheme="blue">Save</Button>
 *     <Button variant="ghost">Cancel</Button>
 *   </HStack>
 * </CardFooter>
 * ```
 *
 * Features:
 * - Consistent padding (px=6, py=4)
 * - Top border separator
 * - Supports all Chakra UI Box props
 * - Ideal for action buttons
 */
export const CardFooter = forwardRef<HTMLDivElement, BoxProps>((props, ref) => (
	<Box
		ref={ref}
		px={6}
		py={4}
		borderTopWidth='1px'
		borderColor='border.default'
		{...props}
	/>
));

CardFooter.displayName = 'CardFooter';
