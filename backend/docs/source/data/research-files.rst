.. meta::
   :description lang=en: File names, formats, encodings and suppression rules for the CAASPP and ELPAC research files.

Research Files
================================================================

The research files carry the same figures as the public "Test Results" reports,
in bulk.  One file holds every entity at every level for one test type and one
administration year.

File names
----------

Statewide files follow a fixed pattern::

    <program>_ca<year>_all_<format>[_<subject>]_v1.zip

``sb_ca2025_all_csv_ela_v1.zip``, for example, is the 2024–25 Smarter Balanced
English language arts/literacy file in caret-delimited form.  The importer reads
the year straight out of the name, so keeping the published names is the
simplest way to make a file self-describing.

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Prefix
     - Contents
   * - ``sb_``
     - Smarter Balanced. Split into ``_ela_`` and ``_math_`` files, plus a
       combined file.
   * - ``cast_``
     - California Science Test.
   * - ``csa_``
     - California Spanish Assessment.
   * - ``caa_``
     - CAA for English language arts/literacy and mathematics.
   * - ``caas_``
     - CAA for Science.
   * - ``<name>entities_``
     - The entity file: county, district and school names and codes as they
       existed in that administration year.

Formats
-------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Administration years
     - Statewide file formats
   * - 2019–20 and later
     - Fixed-width, and caret-delimited (``^``) with a header row.
   * - 2018–19 and earlier
     - Fixed-width, and comma-delimited with a header row.

Countywide and districtwide files became caret-delimited from 2023–24.  This
application reads the delimited form; the importer detects the delimiter from
the header row, so both eras load without configuration.

.. note::

   Files are encoded in Windows code page 1252, not UTF-8.  District and school
   names contain characters — accented letters, and a soft hyphen inside
   "Ever–EL" — that are not valid UTF-8, so decoding as UTF-8 either fails or
   corrupts names.

Scope of a file
---------------

Research files are published at three scopes:

**Statewide**
    The state, every county, every district and every school.

**Countywide**
    One county and the districts and schools inside it.

**Districtwide**
    One district and its schools.

There is no school-only download; school rows are extracted from one of the
files above.  Because each file already contains every level, importing the
statewide file for a year is sufficient — importing a county file afterwards
adds nothing new.

.. warning::

   Direct-funded independent charter schools are reported as districts in their
   own right.  Their results roll into the state and county totals and appear
   again as school-level rows, so summing districts within a county and summing
   schools within a county give different answers unless charters are handled
   deliberately.  This application records the funding type on the entity, so a
   charter can be included or excluded explicitly.

Suppressed and inapplicable values
----------------------------------

Two different kinds of blank appear, and they do not mean the same thing.

``*``
    The figure exists but is withheld.  California reports no scores for any
    group with fewer than 11 students, to avoid identifying individuals.

*(empty)*
    The figure does not apply.  The most common case is the mean scale score on
    an "all grades" row: scale scores are not comparable between grades, so the
    state deliberately publishes no cross-grade mean.

The importer stores both as ``NULL`` and sets a ``suppressed`` flag for the
first, so a report can say "withheld" where the state withheld and "not
reported" where it does not apply.  See :doc:`interpreting-results`.

Lookup tables
-------------

Three small files accompany the research files and are reproduced as seed data
in this application so that a fresh database is usable before any import:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - File
     - Contents
   * - ``Tests.zip``
     - Test IDs and names — :doc:`assessments`.
   * - ``StudentGroups.zip``
     - Student group IDs, names and categories — :doc:`student-groups`.
   * - ``<name>entities_csv.zip``
     - County, district and school names and CDS codes for one year.

The entity file is the only source of county *names*; research file rows carry
district and school names but leave the county name blank.  The 58 county names
are therefore seeded in :mod:`app.ingest.reference_data` as well.
