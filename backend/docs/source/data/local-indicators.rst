.. meta::
   :description lang=en: The LCFF Local Indicators -- the self-reported half of the California School Dashboard.

Local Indicators
================================================================

The Dashboard has two halves and they work nothing alike.
:doc:`dashboard` covers the state half: seven indicators the state measures
and reduces to a performance colour.  This page covers the local half, where
nothing is measured by anyone.

A **local indicator** is a self-assessment.  Each local educational agency
rates itself against an LCFF state priority, reports the result to its own
governing board at a public meeting, and the state records what it said.  There
is no cut point, no five-by-five grid and no colour -- only ``Met``,
``Not Met`` or ``Not Met For Two or More Years``, and whatever the agency chose
to write.

Anything presenting this data has to say so.  A reader who assumes these are
state findings will misread every one of them.

The seven priorities
----------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 40 48

   * - Priority
     - Name
     - Reported by
   * - 1
     - Basic Services and Conditions
     - Every LEA
   * - 2
     - Implementation of State Academic Standards
     - Every LEA
   * - 3
     - Parent and Family Engagement
     - Every LEA
   * - 6
     - School Climate
     - Every LEA
   * - 7
     - Access to a Broad Course of Study
     - Every LEA
   * - 9
     - Coordination of Services for Expelled Students
     - County offices only
   * - 10
     - Coordination of Services for Foster Youth
     - County offices only

Priorities 4, 5 and 8 are LCFF priorities too, but the state measures them
through the state indicators, which is why the numbering has gaps.

The grain is the LEA, not the school
----------------------------------------------------------------

Districts, county offices, and charter schools that are their own LEA.  A
school inside a district has no local indicator report of its own; it inherits
its district's.  A charter school usually reports directly, because it *is* an
LEA.

The API resolves this by walking up the entity ancestry until it finds an
entity that reported, and every response carries ``reportedBy`` saying which
entity actually answered.  Returning a 404 for a school would be wrong -- the
answer exists, it just belongs to the district.

Where the files live
----------------------------------------------------------------

One file per priority per year, at the same host as the state indicators::

   https://www3.cde.ca.gov/researchfiles/cadashboard/Pr{priority}{year}.xlsx

Published for 2018, 2019 and 2021 through 2025.  There is no 2020 file.  Note
that **2021 has local indicators even though the state indicators do not** --
agencies kept self-reporting through the pandemic, so this layer covers a year
the state half cannot.

Spreadsheets, not the text exports
----------------------------------------------------------------

Both formats exist and the importer prefers ``.xlsx``.  The reason is
narrative fidelity: the text export replaces the newlines inside a narrative
field with spaces.  Alameda County Office of Education's 2025 Priority 3
narrative is 2,035 characters in both formats, with **ten paragraph breaks in
the spreadsheet and none in the text**.  For prose a parent is meant to read,
that structure is the difference between a document and a wall.

Pass ``--text`` to the importer to read the text exports anyway; it is faster
and the figures are identical.

The schema changes almost every year
----------------------------------------------------------------

Unlike the state indicator files, these have no stable layout:

* **The delimiter changes.**  2022 and 2023 are tab-delimited; every other year
  is pipe-delimited.
* **Columns are renamed.**  ``CDSCode`` then ``cdsCode`` then ``cdscode``;
  ``PriorityNumber`` then ``priorityId``; ``Performance`` then
  ``countyPerformance``.
* **Column sets are restructured.**  Priority 3 has been published with 8, 21,
  27 and 28 columns.  Priority 6's single ``summary`` became ``summary1``,
  ``summary2`` and ``summary3``.  The board meeting date did not exist at all
  before 2019.

So only a small envelope is given columns -- the CDS code, the LEA name, the
priority, the performance, the meeting date, the additional information and
the year -- matched case-insensitively across every spelling above.  Everything
else is kept verbatim in a ``responses`` JSON column under whatever name the
state used that year.  A new column in next year's file needs no migration.

Ratings and narratives are told apart by what they hold rather than by name,
because the state names them alike: an integer is a self-rating on the
published 1--5 scale, and anything long enough to be a sentence is prose.

Importing
----------------------------------------------------------------

.. code-block:: console

   $ uv run app/scripts/ingest_local_indicators.py --year 2025

``--priority`` narrows to one priority, ``--year`` is repeatable, ``--force``
reloads regardless of fingerprint, and ``--source`` reads from a directory or
an ``s3://`` prefix instead of the state's server.

A load replaces everything stored for the ``(reporting_year,
priority_number)`` pairs a file covers, so re-running converges.  Rows whose
LEA is not in the entity dimension are skipped rather than failing the file;
two of roughly 2,300 are unknown, and losing a file over them helps nobody.
