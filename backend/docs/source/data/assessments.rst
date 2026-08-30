.. meta::
   :description lang=en: The tests reported by CAASPP and ELPAC, and what each one measures.

Assessments
================================================================

Eleven tests are reported across the two programs.  The **Test ID** is the
identifier used in every research file and in this application's database; the
**Test Type** is the code that appears in a CAASPP file's ``Test Type`` column
and in the reporting site's URLs.

.. list-table:: CAASPP
   :header-rows: 1
   :widths: 8 8 30 54

   * - Test ID
     - Type
     - Test
     - What it measures
   * - 1
     - ``B``
     - Smarter Balanced English Language Arts/Literacy
     - Grades 3–8 and 11. Reports four achievement levels, four reporting
       *areas* and two *composite areas*.
   * - 2
     - ``B``
     - Smarter Balanced Mathematics
     - Grades 3–8 and 11. Three areas and two composite areas; the file carries
       a fourth area column that mathematics does not use.
   * - 17
     - ``X``
     - California Science Test (CAST)
     - Grades 5 and 8, and once in high school. Three science domains.
   * - 39
     - ``R``
     - California Spanish Assessment (CSA)
     - Optional. Grades 3–8 and 9–12. Redesigned for 2024–25; see
       :doc:`interpreting-results`.
   * - 3
     - ``A``
     - CAA for English Language Arts/Literacy
     - The alternate assessment, for students whose individualized education
       program designates it. Three levels.
   * - 4
     - ``A``
     - CAA for Mathematics
     - As above, for mathematics.
   * - 18
     - ``Y``
     - CAA for Science
     - The alternate science assessment.

.. list-table:: ELPAC
   :header-rows: 1
   :widths: 8 10 30 52

   * - Test ID
     - Type
     - Test
     - What it measures
   * - 21
     - ``SA``
     - Summative ELPAC
     - Annual progress in English for students already identified as English
       learners. Four overall levels, an oral and a written language composite,
       and four domains.
   * - 22
     - ``IA``
     - Initial ELPAC
     - Identifies whether a student entering a California school is an English
       learner. Three outcomes, plus oral and written language composites.
   * - 23
     - ``ALTSA``
     - Summative Alternate ELPAC
     - The summative alternate for English learners with the most significant
       cognitive disabilities. Three levels, overall only.
   * - 24
     - ``ALTIA``
     - Initial Alternate ELPAC
     - The initial alternate. Three outcomes, overall only.

The application seeds this catalogue in
:mod:`app.ingest.reference_data`, so a test's name, program and level scheme are
available before any file has been imported.

Where each test's results live
------------------------------

The public reports are one page per test type, and the research file downloads
sit alongside them:

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Test
     - Report
     - Research files
   * - Smarter Balanced
     - ``/caaspp/DashViewReportSB``
     - ``/caaspp/ResearchFileListSB``
   * - CAST
     - ``/caaspp/DashViewReportCAST``
     - ``/caaspp/ResearchFileListCAST``
   * - CSA
     - ``/caaspp/DashViewReportCSA``
     - ``/caaspp/ResearchFileListCSA``
   * - CAA (ELA/math)
     - ``/caaspp/DashViewReportCAA``
     - ``/caaspp/ResearchFileListCAA``
   * - CAA for Science
     - ``/caaspp/DashViewReportCAAS``
     - ``/caaspp/ResearchFileListCAAS``
   * - Summative ELPAC
     - ``/elpac/DashViewReportSA``
     - ``/elpac/ResearchFilesSA``
   * - Initial ELPAC
     - ``/elpac/DashViewReportIA``
     - ``/elpac/ResearchFilesIA``
   * - Alternate ELPAC
     - ``/elpac/DashViewReportALTSA``, ``/elpac/DashViewReportALTIA``
     - ``/elpac/ResearchFilesALTSA``, ``/elpac/ResearchFilesALTIA``

All paths are relative to ``https://caaspp-elpac.ets.org``.
