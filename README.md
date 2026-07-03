# California Accountability Panel Documentation

Documentation for the California Accountability Panel. https://github.com/opensacorg/app-capanel-web

- [User guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/)
- [Developer guide](https://opensacorg.github.io/app-capanel-doc/developer-guide/)
- [README extended reference](https://opensacorg.github.io/app-capanel-doc/developer-guide/readme-reference)

> [!Note]
> This project must be manually kept in sync by copy-pasting files to and from the main application. See the [sync documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/documentation-repository-sync).

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [pnpm](https://pnpm.io/)
- [Make](https://www.gnu.org/software/make/)

## Quickstart

Run common commands from the root of the project using `make`.

> [!Important] 
> Before running anything, first create the required `.env` files. See [environment variable documentation](https://opensacorg.github.io/app-capanel-doc/developer-guide/environment-variables).

#### **TODO:** Improve environment variable documentation.

- [ ] Add public/mock env files to the root and frontend folder.
- [ ] Document in this README the commonly needed and missed environment variables that are required to first run.

### Backend documentation (Sphinx)

`make reload`

### Frontend documentation (Storybook)

`make storybook`

## Contribute

You can get involved by joining our Meetup group and Slack channel. For more information on contributing to the project, see the [contribution guide](https://opensacorg.github.io/app-capanel-doc/contribute).

```
$env:IMPORT_RESOURCES_HOST_PATH="$HOME/Downloads/resources"; docker compose up -d db; docker compose run --rm prestart bash scripts/prestart-with-data.sh
```
