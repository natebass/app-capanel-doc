Database Troubleshooting
================================================================

This section provides common SQL queries and commands to help you troubleshoot the database and verify data integrity.

Troubleshooting SQL Queries
---------------------------

Use these queries to check the status and structure of the `academicindicator` table.

### Verify record counts by reporting year

.. code-block:: sql

    SELECT reportingyear, COUNT(*)
    FROM academicindicator
    GROUP BY reportingyear;

### Check counts for a specific reporting year (e.g., 2025)

.. code-block:: sql

    SELECT COUNT(*)
    FROM academicindicator
    WHERE reportingyear = '2025';

### Inspect data for a specific CDS and student group

.. note::
    The CDS code ``00000000000000`` is used for **statewide data**.

.. code-block:: sql

    SELECT cds, reportingyear, studentgroup
    FROM academicindicator
    WHERE cds = '00000000000000';

### List distinct indicators and student groups for a specific year and CDS

.. code-block:: sql

    SELECT DISTINCT indicator, studentgroup
    FROM academicindicator
    WHERE cds = '00000000000000' AND reportingyear = '2025'
    LIMIT 20;

### Find CDS codes with a specific prefix

.. code-block:: sql

    SELECT DISTINCT cds
    FROM academicindicator
    WHERE cds LIKE '000000%'
    LIMIT 10;

### Check table structure

To verify the columns and their data types:

.. code-block:: sql

    SELECT column_name, data_type, character_maximum_length, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'academicindicator'
    ORDER BY ordinal_position;

Shell Configuration
-------------------

If you use the Fish shell, you may need to source your configuration to ensure all aliases and environment variables are loaded:

.. code-block:: bash

    source ~/.config/fish/config.fish
