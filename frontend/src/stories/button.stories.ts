import type { Meta, StoryObj } from '@storybook/react-vite'
import { fn } from 'storybook/test'

import { Button } from '@/components/ui/button'

const meta = {
	title: 'UI/Button',
	component: Button,
	parameters: {
		layout: 'centered',
	},
	tags: ['autodocs'],
	argTypes: {
		variant: {
			control: 'select',
			options: ['default', 'outline', 'secondary', 'ghost', 'destructive', 'link'],
		},
		size: {
			control: 'select',
			options: ['default', 'xs', 'sm', 'lg', 'icon', 'icon-xs', 'icon-sm', 'icon-lg'],
		},
	},
	args: { onClick: fn() },
} satisfies Meta<typeof Button>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
	args: {
		variant: 'default',
		children: 'Button',
	},
}

export const Outline: Story = {
	args: {
		variant: 'outline',
		children: 'Button',
	},
}

export const Secondary: Story = {
	args: {
		variant: 'secondary',
		children: 'Button',
	},
}

export const Ghost: Story = {
	args: {
		variant: 'ghost',
		children: 'Button',
	},
}

export const Destructive: Story = {
	args: {
		variant: 'destructive',
		children: 'Button',
	},
}

export const Link: Story = {
	args: {
		variant: 'link',
		children: 'Button',
	},
}

export const Large: Story = {
	args: {
		size: 'lg',
		children: 'Button',
	},
}

export const Small: Story = {
	args: {
		size: 'sm',
		children: 'Button',
	},
}

export const ExtraSmall: Story = {
	args: {
		size: 'xs',
		children: 'Button',
	},
}
