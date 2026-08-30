# California Accountability Panel front-end documentation

The test suite for React components using Storybook, Vitest, and Playwright.

- Experiment with components while previewing them with Storybook.
- A light-weight development environment without Docker.

## Quick start

### Prerequisites

Before running anything, first create the required `.env` files.
See [environment variable documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/environment-variables).

- Node.js (v24 or later)
- Vite+
- Playwright (with browser installed)

### Start Storybook

Open [http://localhost:6006](http://localhost:6006) with your browser to see the result. Storybook hosts the component
stories and all written documentation.

```sh
vp run storybook
```

### Start the website

The full website is included so you can run and experiment with it locally
on [http://localhost:3000](http://localhost:3000).

```sh
vp dev
```

## Test

This website primarily uses Storybook. It is also a home for a bigger test suite using Vitest and Playwright.
For more information see
the [testing guide](https://innovate-for-california-doc.vercel.app/?path=/docs/developer-guide--docs#install-pnpm).

> [!WARNING]
> Critical Playwright tests should also be included in the main website repository.

## VSCode support

> [!Note]
> PNPM commands must be run from the frontend folder. It is recommended to open the frontend folder directly in VSCode.
> To run from the root of the project, it is recommended to use Make.

This project comes with a .vscode/ folder to help get up and running with VSCode.

- Start debugging with F5. More run configurations can be found in [launch.json](.vscode/launch.json).
- View recommended project extensions by typing @recommended in the VSCode extension search.

## Security

Please report and security issues or bugs to product@opensac.org.

## Resources

- [Contributing guide](.github/CONTRIBUTING.md)
- [Developer Guide index](https://opensacorg.github.io/app-capanel-doc/developer-guide/)
- [Components guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/components)
- [Storybook guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/storybook)
- [Extended backend/frontend README reference](https://opensacorg.github.io/app-capanel-doc/developer-guide/readme-reference)
