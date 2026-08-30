.. meta::
   :description lang=en: How the research files map onto the application database.

Data Model
================================================================

The database keeps the shape of the state's own reporting rather than the shape
of its files.  A research file row is an entity, a year, a test, a student group
and a grade, together with an overall distribution and some breakdowns beneath
it — and that is exactly the grain of the two fact tables.

.. mermaid::

   erDiagram
       ENTITIES ||--o{ ASSESSMENT_RESULTS : "reports"
       ASSESSMENTS ||--o{ ASSESSMENT_YEARS : "in each year"
       ASSESSMENT_YEARS ||--o{ SUBSCORE_DEFINITIONS : "reports categories"
       PERFORMANCE_LEVEL_SCHEMES ||--o{ PERFORMANCE_LEVELS : "has levels"
       PERFORMANCE_LEVEL_SCHEMES ||--o{ ASSESSMENT_YEARS : "labels overall"
       PERFORMANCE_LEVEL_SCHEMES ||--o{ SUBSCORE_DEFINITIONS : "labels bands"
       ASSESSMENT_RESULTS ||--o{ ASSESSMENT_SUBSCORES : "broken down by"
       STUDENT_GROUPS ||--o{ ASSESSMENT_RESULTS : "reported for"
       GRADE_LEVELS ||--o{ ASSESSMENT_RESULTS : "reported for"

Reference tables
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Table
     - Contents
   * - ``entities``
     - Every state, county, district and school, keyed by the 14-character CDS
       code, with its reporting level, charter funding type, parent entity and
       the range of years it appears in.
   * - ``assessments``
     - The test catalogue — *Table C* of the record layouts.
   * - ``assessment_years``
     - One row per test and administration year, naming the achievement level
       scheme that year used. This is what lets the CSA change its levels in
       2024–25 without a schema change.
   * - ``subscore_definitions``
     - The areas, domains and composites a test reported in a year, with their
       published names. Resolves "Area 1" to *Reading* for ELA and *Concepts and
       Procedures* for mathematics.
   * - ``performance_level_schemes`` / ``performance_levels``
     - The named, ordered levels each test reports, and the level at which the
       state counts a student as meeting the standard.
   * - ``student_groups``
     - *Table A*, keyed by program and identifier because the two programs word
       the same identifiers differently.
   * - ``grade_levels``
     - *Table B*, including the aggregate codes.

Fact tables
-----------

``assessment_results``
    One row per reported cell: ``(cds_code, test_year, test_id,
    student_group_id, grade)``.  Holds the three counts, the mean scale score,
    up to four levels as count and percentage, the "met or above" figure with a
    note of whether it was published or derived, and the ``suppressed`` flag.

``assessment_subscores``
    One row per area, domain or composite beneath a result cell.  Four bands
    wide — three suffice for most tests, the fourth exists for the Summative
    ELPAC composites — plus an optional mean scale score and a total.  A row is
    written only when the state reported something, so a missing row means "not
    reported", never zero.

Both tables normalise direction: level 1 and band 1 are always the lowest
performance, whichever order the source file printed them in.

Idempotency
-----------

Loading a file deletes everything already stored for the test years and test IDs
that file covers and replaces it, inside one transaction.  Re-running the
importer over an unchanged bucket converges instead of duplicating, and a
corrected file republished by the state replaces the figures it supersedes.

Why the statewide row matters
-----------------------------

The statewide entity — CDS code ``00000000000000`` — has a row for every year,
test, student group and grade the database holds.  Questions like "which years
have data?" and "which grades does this test report?" are answered from that one
entity's slice of the primary key rather than by scanning tens of millions of
rows.

Bookkeeping
-----------

``ingest_runs`` and ``ingest_files`` record every import: which object was read,
its size and entity tag, how long it took, how many rows it produced and any
error.  The importer consults them to skip files whose fingerprint has not
changed since the last successful load.
