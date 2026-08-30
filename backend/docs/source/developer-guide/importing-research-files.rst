.. meta::
   :description lang=en: Running the CAASPP and ELPAC research file importer.

Importing Research Files
================================================================

The importer reads CAASPP and ELPAC research files from a directory or an S3
prefix and loads them into the database.  It is safe to run repeatedly: files
whose size and entity tag have not changed since the last successful load are
skipped, and a file that *is* loaded replaces everything already stored for the
years and tests it covers.

See :doc:`../data/research-files` for what the files contain.

Getting the files
-----------------

Download the statewide research files from the state's reporting site:

* Smarter Balanced — `ResearchFileListSB
  <https://caaspp-elpac.ets.org/caaspp/ResearchFileListSB>`_
* CAST, CSA, CAA, CAA for Science — the equivalent ``ResearchFileList`` pages
* ELPAC — the ``ResearchFiles`` pages on the `ELPAC site
  <https://caaspp-elpac.ets.org/elpac/>`_

Take the **caret-delimited (CSV)** statewide file for each test and year.  Keep
the published file names: the importer reads the administration year out of the
name, and uses the prefix to pick a layout before falling back to matching on
the column headers.

``.zip`` and ``.gz`` archives are unwrapped automatically, so the downloaded
archives can be used as-is.

Configuring the source
----------------------

Set ``RESEARCH_FILE_SOURCE_URI`` in ``.env`` to either a directory or a bucket
prefix:

.. code-block:: bash

   RESEARCH_FILE_SOURCE_URI=/home/you/Downloads/resources

.. code-block:: bash

   RESEARCH_FILE_SOURCE_URI=s3://ca-panel-resources/research-files

The directory is searched recursively, so a folder holding several years of
downloads loads in one pass.

Running an import
-----------------

From the ``backend`` directory:

.. code-block:: bash

   uv run app/scripts/ingest_research_files.py

Useful options:

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Option
     - Effect
   * - ``--source URI``
     - Read from this directory or bucket prefix instead of the configured one.
   * - ``--force``
     - Reload files even when their fingerprint is unchanged.
   * - ``--only FRAGMENT``
     - Only load files whose name contains this text. Repeatable.
   * - ``--year YEAR``
     - Restrict to one administration year. Repeatable.
   * - ``--seed-only``
     - Refresh the reference tables and exit without loading results.

For example, to reload just the 2024–25 Smarter Balanced files:

.. code-block:: bash

   uv run app/scripts/ingest_research_files.py --year 2025 --only sb_ --force

Triggering an import over HTTP
------------------------------

A superuser can start a run from the API.  The request returns immediately and
the import continues in the background.

.. code-block:: bash

   curl -X POST https://your-host/api/v1/ingest/runs \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"force": false, "years": [2025]}'

Progress and history:

.. code-block:: bash

   curl https://your-host/api/v1/ingest/runs -H "Authorization: Bearer $TOKEN"
   curl https://your-host/api/v1/ingest/runs/$RUN_ID -H "Authorization: Bearer $TOKEN"

Each run records every file it touched, its status, how long it took and how
many rows it produced.

What to expect
--------------

Loading every statewide file for two administration years produces 13.4 million
result rows and 24.1 million subscore rows, occupying about **8.4 GB** in
PostgreSQL — roughly half of it index.  Measured on a developer machine with a
local database:

.. list-table:: Statewide files, 2024-25 administration
   :header-rows: 1
   :widths: 34 22 22 22

   * - File
     - Results
     - Subscores
     - Time
   * - ``sb_ca2025_all_csv_ela_v1``
     - 2,018,184
     - 5,276,646
     - 7 min
   * - ``sb_ca2025_all_csv_math_v1``
     - 2,018,337
     - 4,535,258
     - 7 min
   * - ``cast_ca2025_all_csv_v1``
     - 1,370,855
     - 2,153,631
     - 3 min
   * - ``caa_ca2025_all_csv_v1``
     - 885,057
     - —
     - 1 min
   * - ``caas_ca2025_all_csv_v1``
     - 303,040
     - —
     - 17 s
   * - ``csa_ca2025_all_csv_v1``
     - 89,966
     - 130,290
     - 13 s

Most of the wall time is the database, not the parsing: each file is deleted
and reinserted, and the rows go in through ``COPY``.

How it works
------------

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Module
     - Responsibility
   * - :mod:`app.ingest.sources`
     - Lists and opens objects from a directory or S3, unwrapping archives and
       decoding Windows-1252.
   * - :mod:`app.ingest.layouts`
     - Declares the columns of each published layout and picks the right one
       from the file name, header and year.
   * - :mod:`app.ingest.parser`
     - Converts rows, preserving the difference between a withheld value and an
       inapplicable one, and normalising band order.
   * - :mod:`app.ingest.loader`
     - Streams rows into temporary staging tables with ``COPY`` and swaps them
       into place in one transaction.
   * - :mod:`app.ingest.runner`
     - Walks the source, decides what has changed, and records the outcome.

Troubleshooting
---------------

**"No research file layout matches …"**
    The file's columns do not match any known layout.  Check that it is the
    caret-delimited research file rather than a fixed-width one, and that the
    header row is intact.  The message lists the first columns it saw.

**"… matches more than one layout"**
    The file was renamed and its columns are ambiguous.  Restore the published
    file name so the year and test type can be resolved.

**Names contain question marks or replacement characters**
    The file was re-saved as UTF-8 somewhere along the way.  Download it again;
    the state publishes Windows-1252.

**A file is skipped that should not be**
    Its size and entity tag match the last successful load.  Pass ``--force``.
