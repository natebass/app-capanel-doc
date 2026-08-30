.. meta::
   :description lang=en: Column layouts of the CAASPP and ELPAC research files.

Record Layouts
================================================================

Every research file starts with the same identifying columns and then diverges
according to how the test reports achievement.  The state publishes the
authoritative layout for each test and year; this page summarises the parts the
importer relies on.  :mod:`app.ingest.layouts` encodes them.

.. note::

   The importer matches columns **by name**, not by position.  A file with an
   added column still loads, and a file whose columns do not match any known
   layout is rejected rather than silently misread.

Identifying columns
-------------------

.. list-table:: CAASPP files
   :header-rows: 1
   :widths: 30 70

   * - Column
     - Meaning
   * - ``County Code``
     - Two digits. ``00`` on the statewide row.
   * - ``District Code``
     - Five digits. ``00000`` on state and county rows.
   * - ``School Code``
     - Seven digits. ``0000000`` above the school level.
   * - ``District Name``, ``School Name``
     - Present on the rows for that level; blank above it.
   * - ``Type ID``
     - ``04`` state, ``05`` county, ``06`` district, ``07`` school,
       ``09`` direct-funded charter, ``10`` locally funded charter.
   * - ``Test Year``
     - The spring of the administration: ``2025`` means 2024–25.
   * - ``Test Type``
     - ``B``, ``X``, ``R``, ``A`` or ``Y`` — see :doc:`assessments`.
   * - ``Test ID``
     - The test — see :doc:`assessments`.
   * - ``Student Group ID``
     - The reported group — see :doc:`student-groups`.
   * - ``Grade``
     - The grade or aggregate — see :doc:`grades`.

ELPAC files use the same concepts with compact column names — ``CountyCode``,
``StudentGroupID``, ``TestID`` — and no ``Test Type`` column, since the test ID
identifies the assessment on its own.

.. warning::

   The two programs number ``Type ID`` differently.  CAASPP uses ``07`` for a
   school and ``06`` for a district; ELPAC uses ``01`` for a school and ``02``
   for a district, with ``04`` meaning the state in both.  Reading the value as
   though it had one meaning mislabels every ELPAC row.  This application
   derives the reporting level from the CDS code parts instead, which agree
   across both programs, and uses ``Type ID`` only to identify charters.

Count columns
-------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Column
     - Meaning
   * - ``Total Students Enrolled``
     - Students eligible to take the test.
   * - ``Total Students Tested``
     - Students who were administered it. Excludes parent/guardian exemptions,
       significant medical emergencies, and assigned students who did not test.
   * - ``Total Students Tested with Scores``
     - Students who answered enough questions for a valid score. The
       denominator for the mean scale score.
   * - ``Overall Total``
     - Students counted across all achievement levels. The denominator for the
       level percentages.

Achievement columns by test
---------------------------

**Smarter Balanced and CAST** report four levels and publish a combined
proficiency figure:

``Percentage/Count Standard Exceeded``, ``Standard Met``,
``Standard Met and Above``, ``Standard Nearly Met``, ``Standard Not Met``.

**CAA and CAA for Science** report three levels and no proficiency figure:

``Percentage/Count Level 3``, ``Level 2``, ``Level 1``.

**CSA** reported ``Percent/Count Range 1–3`` through 2023–24 and
``Percent/Count Level 1–3`` from 2024–25.

**Summative ELPAC** reports ``OverallPerfLvl1Pcnt`` through
``OverallPerfLvl4Count``; **Initial ELPAC** reports ``NoviceELPerfLvl…``,
``IntermediateELPerfLvl…`` and ``IFEPPerfLvl…``.

Reporting categories
--------------------

Beneath the overall score, tests publish areas, domains or composites.  Smarter
Balanced names them only by position, and the position means different things in
each subject:

.. list-table::
   :header-rows: 1
   :widths: 26 37 37

   * - Column group
     - English language arts/literacy
     - Mathematics
   * - Area 1
     - Reading
     - Concepts and Procedures
   * - Area 2
     - Writing
     - Problem Solving
   * - Area 3
     - Speaking/Listening
     - Communicating Reasoning
   * - Area 4
     - Research/Inquiry
     - *not reported*
   * - Composite Area 1
     - Reading and Listening
     - Concepts and Procedures
   * - Composite Area 2
     - Writing and Research
     - Mathematical Practices

CAST reports three domains — Life Sciences, Physical Sciences, and Earth and
Space Sciences.  The CSA from 2024–25 reports Listening, Writing, Reading and
Speaking domains plus an Oral Literacy and a Written Literacy composite, each
composite carrying its own mean scale score.  The Summative ELPAC reports Oral
Language and Written Language composites — with mean scale scores and four
levels each — plus Listening, Speaking, Reading and Writing domains at three
levels.

.. important::

   The bands are printed in different directions.  Smarter Balanced areas run
   *above*, *near*, *below* standard; CAST domains run *below*, *near*,
   *above*.  The importer normalises every breakdown so that band 1 is always
   the lowest performance, which is why a single query serves every test.
