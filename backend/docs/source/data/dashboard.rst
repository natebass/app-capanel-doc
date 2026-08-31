.. meta::
   :description lang=en: How California publishes School Dashboard accountability results, and how this application stores them.

California School Dashboard
================================================================

The Dashboard is a different publication from the research files, and the
difference matters.  The research files say **what students scored**; the
Dashboard says **how the state judged a school**.  Five of its seven indicators
have no assessment source at all.

.. list-table::
   :header-rows: 1
   :widths: 22 30 24 24

   * - Layer
     - Source
     - Grain
     - Carries
   * - Assessment detail
     - ``caaspp-elpac.ets.org`` research files
     - entity × year × test × student group × grade
     - domains, subscores, scale scores
   * - Accountability
     - CDE Dashboard data files
     - entity × year × indicator × student group
     - status, change, colour, n-size
   * - Underlying counts
     - `CDE downloadable files <https://www.cde.ca.gov/ds/ad/downloadabledata.asp>`_
     - entity × year × student group
     - absenteeism, discipline, graduates

The two layers complement each other rather than substituting: the Dashboard
files carry a performance colour but no grade or domain breakdown, and the
research files carry grade and domain detail but no accountability result.
This application ingests the first two; the third is not yet loaded.

Where the files live
----------------------------------------------------------------

The state publishes one tab-delimited file per indicator per year at a
predictable address::

   https://www3.cde.ca.gov/researchfiles/cadashboard/{indicator}download{year}.txt

with ``{indicator}`` one of ``ela``, ``math``, ``chronic``, ``susp``, ``grad``,
``elpi``, ``cci`` or ``science``, and ``{year}`` the spring year of the school
year covered — ``2025`` means 2024–25.  A matching ``.xlsx`` exists alongside
each one; this application reads the text version.

Three things differ from the research files and catch people out:

* **The encoding is UTF-8**, not the Windows code page 1252 the research files
  use.
* **The files are revised in place** after release.  The 2024–25 academic files
  were reissued four months after the Dashboard came out, at the same URL.  The
  importer fingerprints each file by entity tag and size, so a revision is
  picked up and replaces what it supersedes.
* **There are no county rows.**  Only ``S`` (school), ``D`` (district) and
  ``X`` (state) appear in ``rtype``.

Release timing
----------------------------------------------------------------

The Dashboard lags the school year it describes by roughly six months.  The
2025 Dashboard was released on 15 November 2025, while the chronic absenteeism
and discipline data behind it had to be certified in CALPADS by 31 July.  That
gap — data certified in the summer, judgement published in the autumn — is what
:mod:`app.service.dashboard_projection` exists to fill.

No Dashboard was published for 2020 or 2021.  Graduation and college/career
files exist for those years, but with no colours; every other indicator has no
file at all.  Reports must show that as a break rather than as missing data.

One envelope, seven indicators
----------------------------------------------------------------

Every indicator file shares the same record envelope::

   cds, rtype, schoolname, districtname, countyname, charter_flag, coe_flag,
   dass_flag, studentgroup, curr*/prior*, change, statuslevel, changelevel,
   color, box, currnsizemet, priornsizemet, accountabilitymet, indicator,
   reportingyear

so one table, ``dashboard_indicator_results``, serves all of them.  Only the
measure columns differ, and the ones that do not fit — the two dozen
``curr_prep_*`` pathway columns in the college/career file, the
``currprogressed*`` columns in the English learner progress file — are kept
verbatim in a ``source_extras`` JSON column rather than being flattened into
columns that are null six times out of seven.

Two quirks are worth knowing:

* The chronic absenteeism file spells ``changeLevel`` with a capital L; every
  other file uses ``changelevel``.  Columns are matched case-insensitively.
* The ``indicator`` column was only added in 2023, and the English learner
  progress files had no ``studentgroup`` column before 2024 because every row
  is English learners.  Both are recovered from the file name.

.. _dashboard-rules:

How a colour is decided
----------------------------------------------------------------

An entity's colour is a lookup on two things: where it stands (**status**) and
how far it moved (**change**).  Each is cut into five bands, and a
five-by-five grid maps the pair onto one of five colours.

The bands and grids are published as `fifteen HTML tables
<https://www.cde.ca.gov/ta/ac/cm/fivebyfivecolortables.asp>`_ and are
transcribed into ``dashboard_cutpoints`` and ``dashboard_color_cells`` by
:mod:`app.ingest.dashboard_reference`.

**Direction.**  Chronic absenteeism and suspension are judged in reverse: a low
rate is the good outcome.  Level 5 is always the best outcome and level 1 the
worst, whichever way the underlying number runs.

**Variants.**  A cut point is only meaningful together with the table it came
from.  Suspension is published as six tables keyed by the file's ``type``
column — ``ED``, ``HD`` and ``UD`` for elementary, high school and unified
districts; ``ES``, ``MS`` and ``HS`` for schools — and the academic indicators
as two, split by the ``hscutpoints`` flag at grade 11.  The same 4.0% suspension
rate is *High* for an elementary school and *Medium* for a high school.

**Small denominators.**  An entity with fewer than 150 students is judged on a
reduced grid.  For chronic absenteeism, suspension and college/career the five
change bands collapse to three — "increased significantly" folds into
"increased", "declined significantly" into "declined" — while the cut points
themselves are unchanged.  Graduation keeps five change bands but uses its own
colours.  The state does not publish these reduced grids as tables anywhere;
they are derived from the published files and cross-checked against the tables
wherever the two overlap.

**Overrides.**  A row flagged ``dataerrorflag`` carries a colour the state
assigned by hand because the local agency submitted data known to be wrong.
Fifty-seven rows in the 2025 files are flagged.  These are stored as published
and never reproduced by the rules.

Together these reproduce every ``statuslevel``, ``changelevel`` and ``color``
in the 2024–25 files exactly — 1,381,722 classifications across all eight
indicators, with no disagreements.  ``tests/service/test_dashboard_projection``
holds that to account.

Groups the state does not rate
----------------------------------------------------------------

Six student groups are reported for information and never receive a colour, no
matter how large they are: ``ELO`` (English learners only), ``RFP``
(reclassified fluent English proficient), ``EO`` (English only), and the
assessment-type groups ``SBA``, ``CAA`` and ``CAST``.  Statewide these cover
hundreds of thousands of students, so "no colour" here means *not rated*, not
*too few students*, and reports must say which.

Vocabularies that are deliberately not shared
----------------------------------------------------------------

Two code sets look joinable and are not:

``student_group_code``
   The Dashboard uses short strings — ``ALL``, ``AA``, ``EL``, ``SED`` — while
   the research files use numeric CAASPP and ELPAC group ids.  They come from
   different publishers and only partly overlap; the Dashboard set includes
   assessment types that are not demographics at all.

``first_test_year`` / ``last_test_year``
   These record the years an entity sat a test.  The Dashboard is not an
   administration, so a Dashboard file never widens them.  An entity that
   appears only in Dashboard files — 124 of them, schools that have never
   tested — carries neither.

Importing
----------------------------------------------------------------

.. code-block:: console

   $ uv run app/scripts/ingest_dashboard_files.py --year 2025

With no ``--source`` the importer reads directly from the state's web server;
pass a directory or an ``s3://`` prefix to load from a local copy.  ``--only``
narrows to one indicator, ``--year`` is repeatable, and ``--force`` reloads
files whose fingerprint has not changed.

The load is idempotent: everything stored for the ``(reporting_year,
indicator_code)`` pairs a file covers is deleted and replaced inside one
transaction, so re-running converges rather than duplicating.
