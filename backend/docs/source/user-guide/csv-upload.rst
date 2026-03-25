CSV Upload
==========

Use your own data by uploading a CSV file.

----

California Assessment of Student Performance and Progress (CAASPP)
===================================================================

The Smarter Balanced Summative Assessments research files contain comprehensive
results from the California Assessment of Student Performance and Progress
(CAASPP) administrations. These files provide the same underlying data as the
public "Detailed Test Results" website but are optimized for complex statistical
analysis, longitudinal studies, and customized reporting.

.. note::

   No scores are reported for any group or demographic containing fewer than 11
   students.

Research files are categorized by their geographic and administrative scope.
Users can download data at the following levels:

- **Statewide Files.** The entire State of California, including all individual counties, districts, and schools.

- **County Files.** County and all associated districts and schools within that county's jurisdiction.

- **District Files.** District and all schools associated with that district.

.. note::

   "School only" files are not available for individual download. School-level
   data must be extracted from the corresponding District, County, or Statewide
   files.

----

Special Entity Handling
-----------------------

Independent Charter Schools
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Direct-funded independent charter schools are treated as individual districts
within these research files. Consequently, their results are integrated into
the totals for the state, the county in which they reside, and their specific
school-level records.

----

Technical Specifications
------------------------

Before performing data analysis, researchers should consult the supplementary
technical documentation to ensure accurate data interpretation. https://caaspp-elpac.ets.org/caaspp/ResearchFileListSB?ps=true&lstTestYear=2025&lstTestType=B&lstCounty=00&lstDistrict=00000#accurate-results

File Formats and Layouts
~~~~~~~~~~~~~~~~~~~~~~~~

Research file structures and data formats may vary between academic years.
Users must refer to the specific Research File Layout for the corresponding
year to map field headers and data types correctly.

Lookup Tables
~~~~~~~~~~~~~

Lookup tables are provided to map numerical codes within the research files to
human-readable labels for:

- Counties, Districts, and Schools (CDS codes)
- Student Demographic Groups
- Test Subjects and Achievement Levels


Research File Schemas
=====================

2025 Caaspp
=====================

All research files use caret (``^``) as the field delimiter.

----

Common Fields
-------------

The following fields appear as the first 16 columns in all research files.

.. list-table::
   :header-rows: 1
   :widths: 5 30 65

   * - #
     - Field Name
     - Notes
   * - 1
     - County Code
     -
   * - 2
     - District Code
     -
   * - 3
     - District Name
     -
   * - 4
     - School Code
     -
   * - 5
     - School Name
     -
   * - 6
     - Type ID
     -
   * - 7
     - Filler
     -
   * - 8
     - Test Year
     -
   * - 9
     - Test Type
     -
   * - 10
     - Test ID
     -
   * - 11
     - Student Group ID
     -
   * - 12
     - Grade
     -
   * - 13
     - Total Students Enrolled
     -
   * - 14
     - Total Students Tested
     -
   * - 15
     - Total Students Tested with Scores
     -
   * - 16
     - Mean Scale Score
     -

----

File Schemas
------------

Smarter Balanced ELA and Math
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Files:**

- ``sb_ca2025_all_csv_ela_v1.txt``
- ``sb_ca2025_all_csv_math_v1.txt``

Extends the common fields with overall performance levels, four content area
domains, and two composite areas.

.. list-table::
   :header-rows: 1
   :widths: 5 45 50

   * - #
     - Field Name
     - Notes
   * - 17
     - Percentage Standard Exceeded
     -
   * - 18
     - Count Standard Exceeded
     -
   * - 19
     - Percentage Standard Met
     -
   * - 20
     - Count Standard Met
     -
   * - 21
     - Percentage Standard Met and Above
     -
   * - 22
     - Count Standard Met and Above
     -
   * - 23
     - Percentage Standard Nearly Met
     -
   * - 24
     - Count Standard Nearly Met
     -
   * - 25
     - Percentage Standard Not Met
     -
   * - 26
     - Count Standard Not Met
     -
   * - 27
     - Overall Total
     -
   * - 28–34
     - Area 1 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 35–41
     - Area 2 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 42–48
     - Area 3 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 49–55
     - Area 4 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 56–62
     - Composite Area 1 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 63–69
     - Composite Area 2 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -

----

California Alternate Assessments (CAA and CAAS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Files:**

- ``caa_ca2025_all_csv_v1.txt``
- ``caas_ca2025_all_csv_v1.txt``

Extends the common fields with three performance levels and an overall total.

.. list-table::
   :header-rows: 1
   :widths: 5 45 50

   * - #
     - Field Name
     - Notes
   * - 17
     - Percentage Level 3
     -
   * - 18
     - Count Level 3
     -
   * - 19
     - Percentage Level 2
     -
   * - 20
     - Count Level 2
     -
   * - 21
     - Percentage Level 1
     -
   * - 22
     - Count Level 1
     -
   * - 23
     - Overall Total
     -

----

California Science Test (CAST)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File:** ``cast_ca2025_all_csv_v1.txt``

Extends the common fields with overall performance levels and three science
domain breakdowns.

.. list-table::
   :header-rows: 1
   :widths: 5 50 45

   * - #
     - Field Name
     - Notes
   * - 17
     - Percentage Standard Exceeded
     -
   * - 18
     - Count Standard Exceeded
     -
   * - 19
     - Percentage Standard Met
     -
   * - 20
     - Count Standard Met
     -
   * - 21
     - Percentage Standard Met and Above
     -
   * - 22
     - Count Standard Met and Above
     -
   * - 23
     - Percentage Standard Nearly Met
     -
   * - 24
     - Count Standard Nearly Met
     -
   * - 25
     - Percentage Standard Not Met
     -
   * - 26
     - Count Standard Not Met
     -
   * - 27
     - Overall Total
     -
   * - 28–34
     - Life Sciences Domain — Percent Below Standard, Count Below Standard, Percent Near Standard, Count Near Standard, Percent Above Standard, Count Above Standard, Total
     -
   * - 35–41
     - Physical Sciences Domain — Percent Below Standard, Count Below Standard, Percent Near Standard, Count Near Standard, Percent Above Standard, Count Above Standard, Total
     -
   * - 42–48
     - Earth and Space Sciences Domain — Percent Below Standard, Count Below Standard, Percent Near Standard, Count Near Standard, Percent Above Standard, Count Above Standard, Total
     -

----

California Spanish Assessment (CSA)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File:** ``csa_ca2025_all_csv_v1.txt``

.. note::

   The 2025 CSA schema differs significantly from 2024. Field 16 is renamed
   ``Overall Mean Scale Score``. Overall performance uses Level 1–3 terminology
   (replacing Range 1–3). Four language domains and two composites with
   independent mean scale scores are added.

Extends the common fields with overall performance levels, four language
domain breakdowns, and two composite scores.

.. list-table::
   :header-rows: 1
   :widths: 5 50 45

   * - #
     - Field Name
     - Notes
   * - 16
     - Overall Mean Scale Score
     - Renamed from ``Mean Scale Score`` in 2024
   * - 17
     - Percent Level 3
     -
   * - 18
     - Count Level 3
     -
   * - 19
     - Percent Level 2
     -
   * - 20
     - Count Level 2
     -
   * - 21
     - Percent Level 1
     -
   * - 22
     - Count Level 1
     -
   * - 23
     - Overall Total
     -
   * - 24–30
     - Listening Domain — Percent Level 1, Count Level 1, Percent Level 2, Count Level 2, Percent Level 3, Count Level 3, Total
     -
   * - 31–37
     - Writing Domain — Percent Level 1, Count Level 1, Percent Level 2, Count Level 2, Percent Level 3, Count Level 3, Total
     -
   * - 38–44
     - Reading Domain — Percent Level 1, Count Level 1, Percent Level 2, Count Level 2, Percent Level 3, Count Level 3, Total
     -
   * - 45–51
     - Speaking Domain — Percent Level 1, Count Level 1, Percent Level 2, Count Level 2, Percent Level 3, Count Level 3, Total
     -
   * - 52–59
     - Composite 1 — Mean Scale Score, Percent Level 1, Count Level 1, Percent Level 2, Count Level 2, Percent Level 3, Count Level 3, Total
     -
   * - 60–67
     - Composite 2 — Mean Scale Score, Percent Level 1, Count Level 1, Percent Level 2, Count Level 2, Percent Level 3, Count Level 3, Total
     -


2024 Caaspp
=====================

All research files use caret (``^``) as the field delimiter.

----

Common Fields
-------------

The following fields appear as the first 16 columns in all research files.

.. list-table::
   :header-rows: 1
   :widths: 5 30 65

   * - #
     - Field Name
     - Notes
   * - 1
     - County Code
     -
   * - 2
     - District Code
     -
   * - 3
     - District Name
     -
   * - 4
     - School Code
     -
   * - 5
     - School Name
     -
   * - 6
     - Type ID
     -
   * - 7
     - Filler
     -
   * - 8
     - Test Year
     -
   * - 9
     - Test Type
     -
   * - 10
     - Test ID
     -
   * - 11
     - Student Group ID
     -
   * - 12
     - Grade
     -
   * - 13
     - Total Students Enrolled
     -
   * - 14
     - Total Students Tested
     -
   * - 15
     - Total Students Tested with Scores
     -
   * - 16
     - Mean Scale Score
     -

----

File Schemas
------------

Smarter Balanced ELA and Math
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Files:**

- ``sb_ca2024_all_csv_ela_v1.txt``
- ``sb_ca2024_all_csv_math_v1.txt``

Extends the common fields with overall performance levels, four content area
domains, and two composite areas.

.. list-table::
   :header-rows: 1
   :widths: 5 45 50

   * - #
     - Field Name
     - Notes
   * - 17
     - Percentage Standard Exceeded
     -
   * - 18
     - Count Standard Exceeded
     -
   * - 19
     - Percentage Standard Met
     -
   * - 20
     - Count Standard Met
     -
   * - 21
     - Percentage Standard Met and Above
     -
   * - 22
     - Count Standard Met and Above
     -
   * - 23
     - Percentage Standard Nearly Met
     -
   * - 24
     - Count Standard Nearly Met
     -
   * - 25
     - Percentage Standard Not Met
     -
   * - 26
     - Count Standard Not Met
     -
   * - 27
     - Overall Total
     -
   * - 28–34
     - Area 1 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 35–41
     - Area 2 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 42–48
     - Area 3 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 49–55
     - Area 4 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 56–62
     - Composite Area 1 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -
   * - 63–69
     - Composite Area 2 — Percentage Above Standard, Count Above Standard, Percentage Near Standard, Count Near Standard, Percentage Below Standard, Count Below Standard, Total
     -

----

California Alternate Assessments (CAA and CAAS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Files:**

- ``caa_ca2024_all_csv_v1.txt``
- ``caas_ca2024_all_csv_v1.txt``

Extends the common fields with three performance levels and an overall total.

.. list-table::
   :header-rows: 1
   :widths: 5 45 50

   * - #
     - Field Name
     - Notes
   * - 17
     - Percentage Level 3
     -
   * - 18
     - Count Level 3
     -
   * - 19
     - Percentage Level 2
     -
   * - 20
     - Count Level 2
     -
   * - 21
     - Percentage Level 1
     -
   * - 22
     - Count Level 1
     -
   * - 23
     - Overall Total
     -

----

California Science Test (CAST)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File:** ``cast_ca2024_all_csv_v1.txt``

Extends the common fields with overall performance levels and three science
domain breakdowns.

.. list-table::
   :header-rows: 1
   :widths: 5 50 45

   * - #
     - Field Name
     - Notes
   * - 17
     - Percentage Standard Exceeded
     -
   * - 18
     - Count Standard Exceeded
     -
   * - 19
     - Percentage Standard Met
     -
   * - 20
     - Count Standard Met
     -
   * - 21
     - Percentage Standard Met and Above
     -
   * - 22
     - Count Standard Met and Above
     -
   * - 23
     - Percentage Standard Nearly Met
     -
   * - 24
     - Count Standard Nearly Met
     -
   * - 25
     - Percentage Standard Not Met
     -
   * - 26
     - Count Standard Not Met
     -
   * - 27
     - Overall Total
     -
   * - 28–34
     - Life Sciences Domain — Percent Below Standard, Count Below Standard, Percent Near Standard, Count Near Standard, Percent Above Standard, Count Above Standard, Total
     -
   * - 35–41
     - Physical Sciences Domain — Percent Below Standard, Count Below Standard, Percent Near Standard, Count Near Standard, Percent Above Standard, Count Above Standard, Total
     -
   * - 42–48
     - Earth and Space Sciences Domain — Percent Below Standard, Count Below Standard, Percent Near Standard, Count Near Standard, Percent Above Standard, Count Above Standard, Total
     -

----

California Spanish Assessment (CSA)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File:** ``csa_ca2024_all_csv_v1.txt``

Extends the common fields with three performance ranges and an overall total.

.. list-table::
   :header-rows: 1
   :widths: 5 45 50

   * - #
     - Field Name
     - Notes
   * - 17
     - Percent Range 3
     -
   * - 18
     - Count Range 3
     -
   * - 19
     - Percent Range 2
     -
   * - 20
     - Count Range 2
     -
   * - 21
     - Percent Range 1
     -
   * - 22
     - Count Range 1
     -
   * - 23
     - Overall Total
     -
