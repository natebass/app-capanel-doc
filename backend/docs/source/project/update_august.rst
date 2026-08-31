.. meta::
   :description lang=en: What changed in August 2026, what we learned about the state's accountability data, and where the project is going next.

August 2026 Update
================================================================

This records a single large change -- the addition of the California School
Dashboard accountability layer -- together with what we learned building it,
the decisions we took and why, and what we deliberately did not do.  It is
written for whoever picks this up next, including us in six months.

Where the project stood
----------------------------------------------------------------

The application ingested CAASPP and ELPAC research files well.  Thirteen
million assessment rows, a clean entity dimension keyed on CDS codes, a
reporting API, and a working ``/dashboard`` route.  That part was in good shape
and none of it changed.

What it could not do was be the thing it was modelled on.
``caschooldashboard.org`` is not an assessment site; it is an **accountability**
site.  Of the state's seven Dashboard measures, five -- chronic absenteeism,
suspension, graduation, college/career, and English learner progress -- have no
assessment-file source at all.  The application had no table for any of them.

The one piece of code that reached toward them, ``app/service/color_calculator.py``,
was orphaned: nothing imported it, no route exposed it, no test covered it, and
there was no data for it to read.

What changed
----------------------------------------------------------------

A third data layer, alongside the assessment one.  See :doc:`../data/dashboard`
for how it works; this section is about what it consists of.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Thing
     - Result
   * - Indicator rows loaded
     - 4,459,363, covering 2018 through 2025
   * - Entities discovered that had never tested
     - 708
   * - Rows carrying indicator-specific columns as JSON
     - 2,901,599
   * - Cut points and grid cells transcribed
     - 150 and 515
   * - State classifications reproduced exactly
     - 1,381,722 (100%)
   * - Backend tests
     - 158 passing

Coverage has real holes, and they are the state's, not ours.  No Dashboard was
published for 2020 or 2021 -- graduation and college/career files exist for
those years but carry no colours, and the other five indicators have no file at
all.  Science files begin in 2024.  Reports must render these as breaks rather
than as missing data, which is why the trend endpoint returns an explicit
``missingYears`` list.

What the state does not write down
----------------------------------------------------------------

This is the part worth reading.  The Dashboard's published documentation
describes most of how a colour is decided, and we transcribed it faithfully --
and still only reproduced about 60% of the state's own chronic absenteeism
change levels on the first pass.  Four rules had to be recovered from the data.

**The small-denominator grid.**  An entity with fewer than 150 students is
judged on a reduced grid.  For chronic absenteeism, suspension and
college/career the five change bands collapse to three: "increased
significantly" folds into "increased" and "declined significantly" into
"declined", while the cut points themselves are unchanged.  Graduation keeps
five change bands but assigns different colours.  The state publishes the
five-by-five tables as fifteen HTML tables; it publishes these reduced grids
nowhere.  All 140 small-denominator cells in ``dashboard_color_cells`` were
derived from the published files themselves and cross-checked against the
tables wherever the two overlap.

**Suspension has six variants.**  The suspension file carries a ``type`` column
-- ``ED``, ``HD``, ``UD`` for elementary, high school and unified districts;
``ES``, ``MS``, ``HS`` for schools -- and each has its own cut points.  The same
4.0% suspension rate is *High* for an elementary school and *Medium* for a high
school.  The six tables on the CDE page are captioned but not keyed, so the
mapping was confirmed by classifying every published row and checking the
result against the state's own ``statuslevel``.

**Some rows carry a hand-assigned override.**  A row flagged ``dataerrorflag``
has a colour the state set by hand because the local agency submitted data known
to be wrong -- 57 rows in 2025, 250 in 2023.  These are stored as published and
excluded from anything that derives or verifies a colour.  They are the reason
the first grid derivation reported ambiguous cells.

**Six student groups are never rated.**  ``ELO``, ``RFP``, ``EO``, ``SBA``,
``CAA`` and ``CAST`` are reported for information and never receive a colour, no
matter how large.  Statewide they cover hundreds of thousands of students.
"No colour" here means *not rated*, not *too few students*, and an interface
that conflates the two is actively misleading -- our first draft of the footnote
did exactly that and had to be corrected.

Smaller things that cost time
----------------------------------------------------------------

* The Dashboard files are **UTF-8**, not the Windows code page 1252 the research
  files use.  ``sources.py`` now carries the encoding per source rather than as
  a module constant.
* The chronic absenteeism file spells ``changeLevel`` with a capital L; every
  other file uses ``changelevel``.  Columns are matched case-insensitively.
* The state's web server answers ``HEAD`` with a **303 redirect loop**.
  Existence and fingerprint are probed with a ranged ``GET`` whose body is never
  read.
* The ``indicator`` column was only added in 2023, and English learner progress
  files had no ``studentgroup`` column before 2024.  Both are recovered from the
  file name, which is why the first full import failed on every pre-2023 year.
* Files are **revised in place** after release.  The 2024-25 academic files were
  reissued four months later at the same URL.  Fingerprinting by entity tag and
  size is what catches this.

Decisions, and why
----------------------------------------------------------------

**One fact table, not seven.**  Every indicator file shares the same record
envelope; only the measure columns differ.  Seven tables would have meant seven
of every query.  The columns that do not fit -- two dozen ``curr_prep_*``
pathway columns in college/career, a dozen ``currprogressed*`` in English
learner progress -- go into a ``source_extras`` JSONB column rather than
becoming columns that are null six times out of seven.  Nothing is discarded.

**Ingest the state's colours; do not recompute them.**  Every published figure
is stored exactly as the state printed it.  On a public accountability site,
disagreeing with ``caschooldashboard.org`` reads as a bug regardless of who is
right.  The rules engine exists to *project* figures the state has not published
yet, and to hold our transcription to account against the ones it has.

**The projection has to earn the right to exist.**  ``tests/service/test_dashboard_projection``
replays real published rows -- one for every distinct combination of status
band, change band, variant and grid -- hides the levels and the colour, and
checks the rules put them back.  It passes at 100% on 1,381,722 classifications.
If it ever fails, the projection must not ship for an unknown year.

**Two vocabularies stay separate.**  The Dashboard uses short student-group
strings (``ALL``, ``SED``, ``EL``); the research files use numeric CAASPP and
ELPAC ids.  They come from different publishers, overlap only partly, and the
Dashboard set includes assessment types that are not demographics at all.
Unifying them would have invented equivalences the state does not assert.  If a
report ever needs to join across the two layers, that is a crosswalk table, not
a shared key.

**No foreign key from results onto the colour grid.**  The colour on a published
row is whatever the state printed.  It has to survive our transcription being
wrong or a variant not yet being seeded.

**The Dashboard never widens ``first_test_year``.**  It is not an administration
of a test.  An entity that appears only in Dashboard files -- 708 of them,
schools that have never tested -- carries neither test year, and an entity that
already exists is left alone rather than having its charter status or year range
rewritten from a different publication.

**``is_projected`` is a column, not a separate table.**  Every read path filters
on it explicitly, and every API response carries it.  It is also the seam for a
later district-contributed layer: the same row shape, marked provisional, with
``projection_basis`` saying where it came from.

Corrections to earlier work
----------------------------------------------------------------

**A retracted claim: there was no syntax error.**  An earlier draft of this
page reported ``except InvalidTokenError, ValidationError:`` in
``app/api/deps.py`` as a committed syntax error stopping the application from
booting.  That was wrong.  :pep:`758` made unparenthesised exception tuples
valid in **Python 3.14**, which is the version this project targets and runs.
The mistake was verifying with the system interpreter -- 3.12, where it really
is a syntax error -- instead of the project's own.  The "Fix IntelliJ lint
warnings" commit was modernising to 3.14 syntax and was correct to do so.
Nothing was ever broken, and the form is now used deliberately.  When checking
syntax in this project, use ``uv run python``; ``python3`` is a different
interpreter with different rules.

**``color_calculator.py`` was less wrong than it looked, and more wrong than it
mattered.**  Checked against the CDE tables, its academic, chronic, graduation,
English learner progress and college/career cut points were all correct, and so
were all five of its colour grids.  What it lacked entirely was the
small-denominator rule and the six suspension variants, whose cut points were an
unimplemented stub.  Between them those cover **38% of the 2025 rows that carry
a performance colour** -- 120,307 of 314,890 -- so it would have disagreed with
the official Dashboard on well over a third of everything it touched, while
looking authoritative.  Its ``convert_mean_scale_to_dfs`` was also unsound:
Distance From Standard is a per-student average, so it is recoverable at a
single grade but not from an aggregate mean scale score, and the module's own
comments admitted the "all grades" thresholds were approximations.  It has been
replaced by ``app/service/dashboard_projection.py``, which reads cut points and
grids from seeded tables rather than module constants.

**The plan this replaced.**  An earlier proposal had the project abandon the
research-file model, adopt a Drizzle ORM schema with slowly-changing dimensions
and monthly range partitioning, and integrate with district student information
systems over Ed-Fi, Clever or nightly SFTP.  It is recorded here so it is not
re-litigated.  It was wrong on the facts -- the ELPAC research files are
aggregate, not student-level, and California does not run Ed-Fi statewide -- and
wrong on the architecture, since published state data is annual aggregate and
revisions are handled by re-ingesting a year, which the loader already did.  Had
we followed it we would have thrown away the best code in the repository.

Where this is going
----------------------------------------------------------------

**The calendar gap is the point.**  The underlying data is certified in CALPADS
by 31 July.  The Dashboard is not published until mid-November -- 15 November
for the 2025 release.  For roughly three months every year the facts exist and
the state's judgement does not.  Publishing a clearly-labelled provisional
colour in that window is something ``caschooldashboard.org`` does not do, needs
no private data, and is now a small amount of work: the rules engine is built
and proven, and nothing is running only because the state has published through
2024-25 and there is nothing yet to project.

What a projection cannot capture, and what any interface must say: the state's
academic denominator counts only *continuously enrolled* students and applies a
participation-rate penalty by substituting the lowest obtainable scale score for
untested students.  The research files expose neither.  Rate indicators --
absenteeism, suspension, graduation -- have no such adjustment and project
exactly from the same underlying counts.

**The third layer is next.**  The CDE `downloadable data files
<https://www.cde.ca.gov/ds/ad/downloadabledata.asp>`_ at ``/ds/ad/`` carry the
counts underneath the Dashboard -- absenteeism, discipline, graduates and
dropouts, enrolment, English learners, free and reduced-price meals, staff --
on their own release cadence, often earlier and with more disaggregation than
the Dashboard files.  They are what a projection would actually be computed
from, and they are worth having on their own.  This is the natural next
increment.

**District data is a partnership problem, not an engineering one.**  Real-time
figures mean student-level records from a district's student information system:
FERPA-covered personal data, per-district data-sharing agreements, and a
security posture this project does not have and should not casually acquire.
The schema is shaped so a single willing district could contribute interim data
behind a feature flag without a migration rewrite -- that is what ``is_projected``
and ``projection_basis`` are for -- but nothing should be built there until an
agreement exists.  Until then, everything the site shows is public data.

Second phase: the local half of the Dashboard
----------------------------------------------------------------

A local archive of files downloaded by hand from the CDE accountability site
turned out to contain four datasets the importer did not know about.  The
important one was seven ``Pr*.xlsx`` files: the **LCFF Local Indicators**,
which are the entire Local Measures half of the Dashboard.  Having built the
state half, the application had been showing one side of a two-sided document.

That half is now ingested and on the page.  See :doc:`../data/local-indicators`.

.. list-table::
   :header-rows: 1
   :widths: 55 45

   * - Thing
     - Result
   * - Local indicator rows loaded
     - 75,533, across 49 files
   * - Years covered
     - 2018, 2019 and 2021 through 2025
   * - LEAs reporting
     - ~2,295, of which 2,293 already existed as entities
   * - Backend tests
     - 193 passing

**What the archive was actually worth.**  Not access -- discovery.  Every file
in it is downloadable from the same ``www3.cde.ca.gov`` URL pattern the
importer already used; all were probed and all returned 200.  What the archive
supplied was the *names*.  The local copies had also already drifted: the local
``eladownload2025.xlsx`` carried 176,042 rows against 176,088 live, though
every statewide value still matched, so the drift was added rows rather than
corrections.  HTTP stays the source of truth; the archive is now useful for
offline runs, a pinned corpus, and fixtures.

**The real decision was format, not location.**  Both ``.txt`` and ``.xlsx``
are downloadable, and the choice is settled by one measurement: a Priority 3
narrative is 2,035 characters in both, with ten paragraph breaks in the
spreadsheet and none in the text export.  Numeric files are equivalent in
either format; narrative files are not.  So the state indicators keep reading
``.txt`` and the local indicators read ``.xlsx``.  ``openpyxl`` was already a
declared and unused dependency, so this cost nothing.

**Why the local indicators get their own table.**  They have no colour, no cut
points and no five-by-five grid -- only ``Met``, ``Not Met`` or ``Not Met For
Two or More Years`` -- and the grain is the LEA rather than the school.
Folding them into ``dashboard_indicator_results`` would have implied an
equivalence the state does not make.  The API and the interface both refuse the
Dashboard palette here for the same reason.

**Why almost everything lives in JSON.**  These files have no stable schema.
The delimiter changes (2022 and 2023 are tab-delimited, every other year is
pipe-delimited), the columns are renamed across years (``CDSCode`` /
``cdsCode`` / ``cdscode``; ``PriorityNumber`` / ``priorityId``; ``Performance``
/ ``countyPerformance``), and the column sets are restructured -- Priority 3
has been published with 8, 21, 27 and 28 columns.  Only a small envelope gets
columns; everything else is kept verbatim under the name the state used that
year.  All 49 files load through one parser.

**A school is not an LEA.**  Local indicators are reported by the agency, so a
school inherits its district's answers and every response carries
``reportedBy`` naming the entity that actually answered.  A charter school is
its own LEA and reports directly -- a case a test caught by picking one and
finding it reported for itself.

Still to do from that archive
----------------------------------------------------------------

Three numeric datasets were found alongside the local indicators and are not
yet ingested.  All three extend the existing pipeline rather than needing a new
one:

**Growth Model** (``growthmodeldownload``, 249,095 rows a year) is the
valuable one.  Its grain is entity x subject x student group, with a
performance category of 1--5, and it answers a question status cannot: a
high-poverty school can sit Red on status and high on growth.  It has no
statewide row, and the state has not published its five-by-five categories yet
(due December 2026), so it must stay visibly informational until it does.

**Census enrolment rates** (``censusenrollratesdownload``, 119,961 rows) gives
total enrolment, subgroup size and rate.  It is the context the accountability
pages lack: it turns "Not rated" into "Not rated -- 18 students".

**Participation and DASS** (``elpacpart``, ``dass1yeargraduationrate``) are
small and explanatory -- the 95% testing rule behind participation penalties,
and the one-year graduation rate used for alternative schools.

Known gaps
----------------------------------------------------------------

* The ``/dashboard/children`` endpoint exists and is tested but has no interface;
  ranking the schools inside a district is an obvious next view.
* ``source_extras`` is stored and queryable but nothing reads it.  The
  college/career pathway breakdown is the most useful thing in there.
* Local indicator field names are shown as the state wrote them, typos and
  all -- ``CollaborationtInput`` renders as "Collaborationt Input".  Correcting
  the state's own column names would be inventing data; leaving them is ugly.
  Worth a display-name lookup eventually.
* The ``feature/`` documentation tree still describes seven components that do
  not exist and a stack (React 18, Chakra, Pandas, D3) that is not in use.  It
  needs rewriting against reality.
* This is the documentation repository.  Everything here has to be mirrored into
  ``opensacorg/app-capanel-web`` by hand; see
  :doc:`../developer-guide/documentation-repository-sync`.
