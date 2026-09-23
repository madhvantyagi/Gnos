# Finished artifact registry

Treat `manifest.json` as the course portal's publication boundary. Creating a
file does not publish it. Register an artifact only after its usable output has
been produced and checked; set it to `ready` only when a learner should see it.

The lesson coordinator is the only manifest writer. A block worker returns a
finished file and a complete artifact record. It does not run the registration
command and does not edit `manifest.json`. This prevents concurrent workers
from overwriting one another or publishing an unchecked result.

## What belongs in the manifest

Each artifact has a stable ID, type, learner-facing title and purpose, related
concept IDs, chapter/topic/lesson placement, one local path or HTTPS URL, MIME
type, metadata, timestamps, and a status. Use metadata for facts the renderer
can state honestly, such as duration, page count, dimensions, registered
captions, a registered transcript, or a thumbnail. Renderer hints are display
preferences, never permission to weaken portal safety.

Use `draft` while the final output is still being checked, `ready` to publish,
`failed` to retain an honest record of an unavailable result, and `archived` to
remove an older item from ordinary views without deleting its file or history.
Updating a stable artifact ID requires a later timestamp and preserves the old
manifest entry in history.

Register only final teaching material. Do not register render frames, temporary
audio clips, generation logs, MCP calls, tool output, creation progress, or a
raw transcript merely because it exists. A transcript or caption file becomes
visible only when it is intentionally finished and registered as its own usable
artifact or explicit companion metadata.

## Paths and presentation

Local paths are relative to the validated course workspace and remain inside
it. Reject absolute paths, traversal, protocol-relative URLs, `file:` URLs, and
symbolic-link escapes. An external artifact uses HTTPS. Do not scan the
`artifacts/` directory to discover content; the current ready manifest entries
are the complete public set.

Images, audio, and video may receive inline viewers. Interactive HTML runs only
in the portal's restricted sandbox. PDFs and unknown formats still receive an
accurate title, purpose, metadata, and safe Open or Download action. A missing
preview must not make the manifest claim disappear or expose neighboring files.

For a simulation, record the HTML's intended canvas in
`metadata.dimensions`, for example `{"width": 1280, "height": 800}`. The
width must be a whole number from 320 to 2400 pixels and the height from 480
to 1600 pixels. The registry rejects dimensions outside those limits. The
viewer uses those values to size its iframe, with a 1280 by 800 fallback for
older artifacts that lack them.
The HTML must also resize its own content; frame dimensions alone cannot fix
a fixed-width chart or controls that overflow on a phone. Inspect the result
inside the portal at wide and narrow widths before registering it.

## Mutation workflow

Before registering a worker result, the coordinator checks that its artifact
ID matches the lesson block, its concept and placement match `course.json`, its
path is the worker's assigned path, and its declared metadata is true. Register
worker results one at a time. Refresh the manifest fingerprint between writes.

Register a finished artifact:

```bash
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  register <learner-id> <course-id> --file artifact.json
```

List the public set:

```bash
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  list <learner-id> <course-id> --ready
```

Archive with the manifest fingerprint returned by the latest read or write:

```bash
python3 skills/course-design/scripts/manage_artifact.py --learners-root learners \
  archive <learner-id> <course-id> --artifact-id <artifact-id> \
  --fingerprint <sha256>
```

The fingerprint is an optimistic concurrency boundary. If it is stale, refresh
and decide again; never overwrite a newer manifest silently. Archive is the
ordinary removal action. Permanent file deletion and learner-evidence
retraction are separate explicit operations.

Do not ask workers to retry a stale manifest write. They do not own the
manifest. The coordinator refreshes, checks the returned artifact record
against the current lesson, and performs the next write.
