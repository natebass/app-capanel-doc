Frontend Components
===================

This page documents the frontend component system used in the ``frontend`` app.

Source of truth
---------------

- ``frontend/package.json``
- ``frontend/components.json``
- ``frontend/src/components``

Component stack
---------------

The frontend uses a React + TypeScript component architecture with:

- ``react`` and ``react-dom`` for UI rendering
- ``class-variance-authority``, ``clsx``, and ``tailwind-merge`` for variant-driven styling
- ``@base-ui/react`` for accessible primitives
- ``storybook`` for component development and documentation
- ``shadcn`` configuration via ``frontend/components.json``

shadcn/ui configuration
-----------------------

The file ``frontend/components.json`` defines shared component conventions:

- ``style``: ``base-maia``
- ``tsx``: ``true``
- ``iconLibrary``: ``hugeicons``
- ``tailwind.css``: ``src/globals.css``
- Aliases:
  - ``@/components`` for components
  - ``@/components/ui`` for foundational UI pieces
  - ``@/lib`` and ``@/lib/utils`` for shared logic
  - ``@/lib/hooks`` for reusable hooks

Component directory structure
-----------------------------

The main component directories currently include:

.. code-block:: text

   frontend/src/components/
   ├── ui/               # Reusable design-system style components
   ├── Dashboard/        # Dashboard feature components (cards, detail views)
   ├── Admin/            # Admin feature actions and tables
   ├── Items/            # Item CRUD and table helpers
   ├── Sidebar/          # App navigation shell pieces
   ├── UserSettings/     # User account/settings flows
   ├── Common/           # Shared application-level components
   ├── form/             # Form components and form hooks
   ├── status/           # Loading/error/not-found state components
   └── stories/          # Storybook stories and docs assets

Recommended usage
-----------------

- Build from ``components/ui`` when possible to keep interaction and styling consistent.
- Place feature-specific composition in feature folders (for example ``Dashboard/`` or ``Admin/``).
- Keep cross-feature shared components in ``Common/`` only when they are not tightly coupled to one domain.
- Store component stories near ``components/stories`` so Storybook stays current with implementation.

Adding a new component
----------------------

1. Choose location:
   - Base/reusable UI: ``frontend/src/components/ui``
   - Feature-specific: relevant feature folder under ``frontend/src/components``
2. Implement the component in TypeScript (``.tsx``).
3. Add or update Storybook stories in ``frontend/src/components/stories``.
4. Validate locally:
   - ``npm run dev``
   - ``npm run storybook``
   - ``npm run lint``

Related documentation
---------------------

- :doc:`storybook`
- :doc:`/feature/e1/components/MetricCard`
