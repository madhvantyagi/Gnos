# GNOS implementation plan

Goal: turn the supplied sketches and existing Manim library into an operable,
compact teaching harness in this repository.

1. Write the learning router, six teacher souls, subject maps, course-design
   guidance, and evidence model. Review examples for distinct decisions and
   variable depth; remove repeated general instructions.
2. Implement local state and context scripts. Verify learner isolation, path
   validation, retry behavior, and that passive coverage cannot imply mastery.
3. Add valid tiny and multi-subject course examples. Validate graph ordering,
   teacher assignments, outcomes, and assessment coverage.
4. Add a structured PDF builder and an illustrated sample lesson. Extract text
   and inspect every rendered page for typography, equations, and collisions.
5. Repair Manim paths, timing, failure handling, and output selection. Keep
   templates and visual components. Test media operations with real FFmpeg and
   render a sample if Manim is available.
6. Validate links, skills, records, and examples. Run behavioral scenarios
   against the instructions; document concrete limitations and quickstart.

Use standard-library Python for the core. Media dependencies are optional.
Do not write personal learner state during development, install global tools,
or claim learning outcomes from synthetic fixtures.
