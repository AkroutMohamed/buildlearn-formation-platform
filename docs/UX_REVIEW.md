# BuildLearn application UX review

Date: 2026-09-27

## Scope and evidence

Reviewed the public homepage/catalog, account entry points, shared workspace navigation, administrator product screens, instructor course management, and student dashboard/course/lesson/quiz flows. This is a source review with public-browser smoke checks, not a complete authenticated end-to-end or accessibility certification. RAG implementation, ranking, validators, prompts, feature flags, indexing, and Qdrant were outside scope and were not changed. No database records were modified.

## Corrections

| Area | Observed problem | Result |
| --- | --- | --- |
| Public homepage | Sample courses had invented details and every course button opened the general catalog. | Available trainings now come from the existing published-course API, with actual course-detail links and loading/error/empty states. |
| Public discovery | Homepage course links sent anonymous visitors to protected student routes. | Hero, categories, and final call to action open the public catalog. |
| Catalog | Older filter requests could overwrite newer results; controls lacked accessible names. | Both catalogs ignore responses from obsolete request generations, reset pending pagination on filter changes, and label search/category/level/language controls. |
| Enrollment | Errors were rethrown without user feedback; the action appeared before account checks finished. | Inline failure feedback, account-loading indication, and an explanation for non-student accounts. |
| Student dashboard | Request failures were swallowed, causing indefinite loading or a misleading empty progress state. | Separate error/loading states and retry actions; completed courses are excluded from Continue learning. |
| Lesson player | Completion errors replaced the whole lesson; navigation wrapped poorly and cancelled sessions still offered Join. | Inline save errors preserve content, saving feedback, wrapping controls, inactive links removed from keyboard order, and Join limited to upcoming/live sessions. |
| Student quiz | Submission failure hid the quiz and selected answers; progress represented page position without showing answered coverage. | Preserved answers and retryable submission, answered count/progress, unanswered warning, loading retry, accessible answer groups, and disabled controls while submitting. Scoring and submission payload semantics remain unchanged. |
| Course navigation | Leaving Overview removed course tabs and made adjacent management screens difficult to reach. | A course layout preserves navigation on subpages, including a link back to My courses. |
| Lesson authoring | Lessons could be created without any UI to edit their content, duration, or publication status. | A labeled editor uses the existing lesson-update API with validation and failure feedback. |
| Module/lesson actions | Mutations lacked pending/error feedback; list length could reuse order indices after deletion. | Pending controls, inline failures, trimmed titles, explicit deletion warnings, and next order index based on existing maximum. |
| Instructor quizzes | Opening Questions did not fetch existing questions; answer options had no authoring UI. | Existing questions load, creation/deletion errors are visible, and options can be added/deleted and marked correct using existing APIs. A warning highlights incomplete options. |
| Course editing | Duration/language errors were insufficiently checked and no cancel link existed. | Non-negative integer duration and language checks, trimmed submitted fields, alert feedback, and Cancel. |
| Shared navigation | A fake unread indicator was always shown; administrator notifications had no action; menu breakpoint differed from sidebar visibility. | Removed fabricated indicators/inactive control, aligned breakpoint, Escape closes account menu, and redundant shell user fetches removed. |
| Administrator sidebar | Parent and child links could both be active. | The most specific matching destination is active. |
| Dialogs/drawers | Dialog focus escaped behind the overlay and tall dialogs could overflow. | Dialog focus containment/restoration, body scroll lock, and bounded scrolling. Admin/instructor mobile drawers support Escape and scroll locking. |
| Administrator product pages | Initial loading effects failed React lint checks. | Stable load callbacks with scheduled initial loading; full-source lint has no errors. |

## Validation

- TypeScript: `tsc --noEmit --incremental false` passed.
- Full frontend ESLint: `eslint src` passed with zero errors and seven existing warnings (instructor product hooks/images and an unused registration import).
- Production build: `npm.cmd run build` passed after the final changes, including TypeScript and generation of 31 static pages.
- Existing URL sanitization tests: `node --test src/lib/sanitizeUrl.test.mjs`, 3 passed, 0 failed. These tests validate the existing URL utility, not the new interactive flows.
- Browser smoke check: anonymous homepage displays actual API courses; Explore courses reaches the public catalog without login; labeled search for `briks` returns that course.
- Read-only database check confirmed that records titled `Archived Catalog Course` and one titled `Draft Catalog Course` are actually marked PUBLISHED. The repository filters by PUBLISHED correctly; course titles are not publication status. These records were left unchanged.

## Remaining limitations

- Published test records and placeholder descriptions remain in the database. Content cleanup requires deciding which records should remain published; the UI does not silently filter by suspicious titles.
- Instructor Settings and Messages accurately report unavailable backend functionality. This review does not invent settings or messaging APIs.
- The support email shown by the footer has not been verified as an operational service.
- Authenticated authoring, failed-network retries, enrollment, keyboard focus, and mobile layouts still need manual checks with the appropriate role accounts. No live enrollments, quiz submissions, uploads, or deletions were performed during this review.
- Seven existing lint warnings remain. This work is not a claim that every screen or backend authorization path has been exhaustively validated.

## Files changed in this review

Under `frontend/src/`:

- `app/admin/layout.tsx`
- `app/admin/products/[id]/page.tsx`
- `app/admin/products/[id]/instructors/page.tsx`
- `app/formations/page.tsx`
- `app/instructor/courses/[courseId]/layout.tsx` (new)
- `app/student/dashboard/page.tsx`
- `app/student/formations/page.tsx`
- `app/student/layout.tsx`
- `components/home/FeaturedFormations.tsx`
- `components/home/Hero.tsx`
- `components/home/Categories.tsx`
- `components/home/CTA.tsx`
- `components/instructor/CourseForm.tsx`
- `components/instructor/CourseNavigation.tsx` (new)
- `components/instructor/InstructorCourseViews.tsx`
- `components/instructor/InstructorShell.tsx`
- `components/layout/WorkspaceNavbar.tsx`
- `components/student/formations/FormationFilter.tsx`
- `components/student/learning/PublicCourseDetailsPage.tsx`
- `components/student/learning/LessonPlayer.tsx`
- `components/student/learning/QuizExperience.tsx`
- `components/ui/Modal.tsx`

The build also regenerates `.next` output; generated build files are not source implementation changes.

## Final journey regression — 27 September 2026

The final pass exercised actual application routes and services with an isolated SQLite database, role-specific test users, and a temporary upload directory. It did not create courses, enrollments, quiz attempts, or uploaded files in the production database. These are API journey checks, not a claim that every authenticated browser interaction has been tested.

| Journey | Verified behavior |
| --- | --- |
| Course authoring | Instructor creates a course, module and lesson, edits the lesson, and publishes the course; the published course is available through the public catalog. |
| Student learning | Enrollment grants lesson access; completion reaches 100% and issues one certificate; repeated completion does not duplicate the certificate. An unenrolled student cannot access the lesson. |
| Multiple uploads | Two PDFs and two additional videos remain distinct and visible in student lesson resources. Deleting one video removes its file and preserves the other video. Student upload requests are rejected before files are created. |
| Quizzes | Student question responses omit correct-answer flags. Partial submissions are rejected, a complete correct submission scores 100%, and a duplicate submission is rejected. |
| RAG conversations | The existing frozen eight-case conversation set was replayed against the live adapter/providers without persisting conversations or overwriting earlier evaluation artifacts. All eight outcomes and accepted support IDs matched the previous results; no technical failures occurred. |

### Reproducible problems fixed

- The student quiz UI allowed incomplete submission despite the backend requiring every question to be answered. Submission now stays disabled until all answers are selected, and the warning states that requirement accurately. Scoring rules remain unchanged.
- Uploaded lesson download links used the frontend origin for `/uploads/` paths. They now use the backend API origin, as uploaded video playback already did.
- Deleting an additional video used only the filename and left files under `uploads/videos/` behind. Resource cleanup now resolves the complete upload-relative path and checks that it remains within the upload directory before deleting it.

Files for this pass: `frontend/src/components/student/learning/QuizExperience.tsx`, `frontend/src/components/student/learning/LessonPlayer.tsx`, `backend/app/services/resource_service.py`, and the new `backend/tests/test_learning_journeys.py`, plus this report.

### Final checks

- Relevant retrieval, RAG, safety, identity, endpoint, runtime, upload and learning-journey tests: **365 passed**, zero failures, 48 deprecation warnings.
- Legacy chat tests in a separate process: **18 passed**, zero failures, 23 deprecation warnings. Separate execution avoids their embedding-model environment side effects. Total unique backend tests in this pass: **383 passed**.
- Focused journey/upload run: 20 passed; these are included in the 365 above and are not counted again.
- Frontend production build, including TypeScript: passed; 31 static pages generated.
- Full frontend ESLint: zero errors, seven existing warnings.
- Existing URL sanitization tests: three passed, zero failures.
- A targeted collection-only check confirmed two existing limitations: `tests/ai/test_chunking.py` imports the unavailable `BaseChunker`, and `tests/ai/test_extraction.py` requires unavailable `fitz`/PyMuPDF. The schema tests collected 35 cases in that check. The 383 count is the relevant executable suite, not a claim that unrestricted repository-wide discovery succeeds.

### RAG and manual-testing limitations

The live replay returned one supported answer and seven insufficient/clarification outcomes, matching the earlier artifact. C01 and C02 retain the previously documented consumption/weight false abstentions; C05 still rejects the proposed unsupported claim. The replay is regression evidence, not a fresh accuracy estimate. C07 preserved its accepted support ID and cited evidence. Ambiguous follow-ups and incomplete multi-fact questions continue to abstain conservatively. Retrieval ranking, prompts, support validation and answer semantics were not changed in this pass.

Authenticated browser checks remain necessary for file-picker clarity, drag-and-drop, keyboard focus, mobile layouts and network-failure feedback. The automated journeys verify server behavior but do not replace those visual/manual checks. Existing demo content and unavailable messaging/settings functionality also remain as documented above.

No Qdrant writes or indexing/checkpoint changes were made by this work. The live RAG calls used the existing read-only retrieval path. This pass did not change the feature flag or its current default.

## Mixed quiz questions and teacher review — 27 September 2026

The course Quizzes screen now lets an instructor choose each question's type: Yes/No, written answer, or existing multiple choice. Yes/No questions create their two options and chosen answer key atomically. Written questions have no answer options. The author selects the question's maximum points. Existing multiple-choice authoring remains available; automatically graded single-choice questions must have exactly one correct option before submission.

Students answer every question before submitting. Automatic corrections show the student's selection and the correct answer after submission, including when reopening the quiz. Written responses display “Submitted — awaiting teacher review”; the overall score and pass/fail remain unset until every written response has been graded. A refresh control checks for published grades. The instructor's Student submissions panel on the Quizzes screen shows submitted responses and accepts bounded points and optional feedback for every written question. Publishing produces a final score; students can reopen the quiz to see that score and feedback.

### Persistence and access control

- New `quiz_attempts` rows store a snapshot of question text/type/points, submitted responses, automatic corrections and teacher feedback. Subsequent edits to a quiz do not change a saved submission's grading basis.
- Pending attempts do not create `QuizResult` records and therefore do not lower final-score analytics with an artificial zero. Completed attempts create their final result in the same transaction as their grading state. Scores use earned points divided by available points; the existing 50% pass threshold is retained. Existing saved result scores are not recalculated.
- Students can read only their own enrolled-course results; correct-answer flags are not returned in the pre-submission question payload. Only active instructors assigned to the course can list or grade submissions. Manual grades may target only that attempt's written question snapshots.
- Duplicate attempts and duplicate final results are guarded by database uniqueness; grading uses a PostgreSQL row lock and checks the pending state. Invalid, incomplete, nonfinite or excessive grades are rejected. These checks do not imply that live concurrent browser grading was load-tested.
- The additive Alembic migration `b2c3d4e5f6a8` creates the new table without rewriting existing quizzes/results. It was applied successfully to the configured local PostgreSQL database. Other deployments need `python -m alembic upgrade head` before running the updated backend.

### Verification and limits

The relevant backend regression suite passed **379 tests**, including 18 isolated learning-journey cases (14 additional cases for this change). A separate legacy-chat run passed **18 tests**, bringing this pass to **397 unique passing backend tests**. The focused upload/journey run's 34 cases are already included in that count. The frontend production build and TypeScript checks passed, and ESLint passed for the changed quiz components/services/types.

The regression cases cover automatic correct/wrong feedback, mixed and written-only quizzes, persisted results, immutable grading snapshots, zero/partial teacher credit, duplicate submissions/reviews, invalid grades, answer-type checks, and student/unassigned-teacher access rejection. Tests use isolated data and temporary uploads. The new local database table and its uniqueness constraint were verified without creating live student submissions. Authenticated browser checks remain a manual follow-up.

Older completed quizzes have aggregate results only: their original answers were never saved, so the interface shows their existing final score without inventing per-question corrections. This implementation keeps one submission per student/quiz, requires all written grades before publishing, and does not add retakes or grade revisions. Student notification of grading is currently through reopening/refreshing the quiz; no email is sent. Existing unrelated test-discovery limitations remain as recorded above. RAG behavior, Qdrant data, indexing/checkpoints and the RAG feature flag were not changed.

### Implementation files

- Backend: `app/models/quiz_attempt.py`, model registration, `app/services/quiz_attempt_service.py`, student/question/answer services, student/question schemas, instructor routes, `alembic/versions/b2c3d4e5f6a8_quiz_attempts.py`, and `tests/test_learning_journeys.py`.
- Frontend: `InstructorCourseViews.tsx`, `QuizExperience.tsx`, instructor/student-learning services, and instructor/learning types.

## Local database cleanup and realistic learning catalog — 27 September 2026

At the user's explicit request, the configured PostgreSQL learning database was backed up and cleaned. Users decreased from 224 to exactly three: `admin@buildlearn.local` (admin), `mo@gmail.com` (instructor), and `akrout@gmail.com` (student). Their original account IDs, password hashes and roles were verified unchanged. The retained accounts' existing conversation and two messages were preserved. Other accounts and their chat records were removed.

The 26 old courses and two placeholder products were replaced with three published products and three French courses grounded in already-acquired manufacturer documents:

| Product | Course focus | Source PDF |
| --- | --- | --- |
| LIKA PAP2 | Identify the projected interior plaster, distinguish its characteristics, prepare documentary checks and storage. | `fiche_technique_pap2.pdf` |
| HYDRO-FAÇADE | Understand surface water repellency, support preparation, consumption and application limits. | `HYDRO%20FAçADE1.pdf` |
| EMTOP EBPK20021 | Identify the 20 V / 4.0 Ah battery and verify documented P20S compatibility. | `EBPK20021%20Technical%20Data.pdf` |

The catalog now contains six modules, 18 published lessons, three downloadable source PDFs, three quizzes and nine questions (six Yes/No and three written). Each course is assigned to `mo@gmail.com`, as is its product. Duration is calculated from lesson durations. The student can enroll through the normal application flow; no enrollments, completions, certificates or grades were fabricated. Old learning activity and demo notifications were cleared with the old courses. No fake videos, schedules, prices, warranties or official manufacturer accreditation were added.

These are authored educational courses based on the project's source material, not manufacturer-approved training or a substitute for current site prescriptions. Technical claims were limited to the inspected documents; exercises are labeled pedagogical estimates. Topics lacking evidence are explicitly described as requiring verification. The unchanged RAG corpus still covers its broader existing document inventory; this three-product teaching catalog does not narrow that corpus.

### Backup, execution and validation

- A PostgreSQL custom-format backup was created before mutation at `backend/.local_backups/catalog-reset-20260927_155227_573218/database.dump`. Its readability was checked with `pg_restore --list`; a full restore rehearsal was not performed. The backup contains private account data and is ignored by Git.
- `backend/scripts/reset_learning_catalog.py` defaults to a read-only preview. Its explicit `--apply` path validates the required accounts/roles and source identities, requires a verified backup, rejects unexpected tables, acquires table locks and executes cleanup/seeding in one transaction. It does not run at application startup.
- Actual source PDFs were copied into a new upload subdirectory and their SHA-256 hashes verified. Original PDFs and old upload files were not deleted.
- The isolated learning-journey suite passed **20 tests**, including new cleanup checks for account/password/role preservation, retained chats, realistic course structure and refusal to delete anything when required accounts are missing. The suite's test data uses SQLite and temporary uploads, not the cleaned live database.
- Live read-only checks confirmed exactly three published courses in `/public/courses` and successful downloads of all three PDF resources.
- All **2,586 indexing/identity files** retained their exact SHA-256 hashes. Both Qdrant collections retained their counts and configuration: legacy `buildlearn_products` has 624 points; hierarchical `buildlearn_products_hierarchical_v1` has 2,637. No Qdrant writes were performed, and no retrieval/RAG behavior or feature flag changed.

Implementation files for this operation: `.gitignore`, `backend/scripts/reset_learning_catalog.py`, `backend/scripts/data/buildlearn_catalog.json`, `backend/tests/test_learning_journeys.py`, and this report. Existing unrelated test-import limitations and RAG false abstentions remain as documented above. Refresh the application to load the replacement catalog.

## Visual refresh: BuildLearn technical studio — 27 September 2026

The visual direction now reflects a technical learning workspace: warm paper backgrounds, architectural navy, vermilion actions, restrained teal/amber category accents and more deliberate typography. It retains the existing routes and learning behavior. No data, authentication rules, quiz scoring/certificate conditions, RAG semantics or retrieval configuration were changed in this visual pass.

### What changed

- Homepage: an editorial headline, clearer calls to action and a custom isometric blueprint illustration replace the generic stack of information cards. The illustration is decorative, not a representation of a manufacturer's product specifications. It uses local SVG code, without external images, font downloads or new dependencies.
- Student, instructor and administrator workspaces: dark navigation surfaces, consistent line icons, stronger active states, translucent headers and coordinated spacing. Instructor/admin headers are offset from the fixed sidebar so they no longer cover its branding. Mobile drawers retain their existing actions.
- Student and instructor dashboards: a distinct welcome panel and more readable statistic cards. Values remain actual API data; no invented activity, progress, reviews or learner counts were added.
- Product/course discovery: category-specific artwork replaces blank BL placeholders across public cards, product lists, instructor product courses, student My courses and course detail pages. Actual uploaded thumbnails still take precedence where supported. Cards have more consistent rounded corners, subtle depth and restrained hover movement.
- Public catalog: a bounded content column and mobile gutters prevent headings and cards from touching the screen edges. Course details have one title/description, plus a Back to the catalog link, rather than repeating the same heading twice.
- Shared UI: stronger page hierarchy, illustrated empty states, matching sign-in styling and reduced-motion support. Student notification panels are bounded to the mobile viewport.

### Verification

- Final frontend production build passed, including TypeScript and generation of 31 static pages.
- Full-source ESLint passed with zero errors and seven pre-existing warnings. The final course-detail adjustment also passed its focused lint check.
- Existing URL sanitization tests: three passed, zero failures. These utility tests are not new browser-interaction coverage.
- Browser visual checks used desktop 1440×900 and mobile 375×812 viewports. Homepage and catalog had no horizontal overflow; the mobile navigation menu opened and reached the catalog. The course link opened the actual LIKA PAP2 public detail page. Its final mobile render had one H1 and no horizontal overflow. Temporary viewport overrides were reset afterward.
- Authenticated student/instructor/admin screens were checked by compilation and source review, not by signing into their accounts in this browser session. Role-specific visual checks, particularly on long tables and nested authoring screens, remain a manual follow-up. No user records, enrollments or uploads were created during visual testing.

Preview: [desktop homepage](ux-assets/design-homepage.png).

### Main implementation areas

- `frontend/src/app/globals.css` and root/workspace layouts.
- Public homepage, catalog and sign-in screen; student/instructor dashboard screens.
- Shared navigation headers and role sidebars.
- Product and course cards/lists/details for public, student, instructor and administrator routes.
- Shared PageHeader, StatCard and EmptyState components.
- New local `BlueprintArt.tsx` and `NavigationIcon.tsx` components.

This is a coordinated visual refresh, not a claim that every screen has been redesigned or every interactive state has been exhaustively tested. Existing functional/import limitations and RAG false abstentions remain as documented earlier.
