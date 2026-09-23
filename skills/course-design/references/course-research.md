# Research the course route

Search for the material needed to build each step of the course. Do not copy
one syllabus or assign one book to every topic. A source can help with the
order of ideas, the first explanation of one concept, a precise derivation,
or an exercise. Say which job it does.

## Match the source to the step

For each topic, write down the question the learner should be able to answer
and the knowledge needed before it. Look for a readable explanation of that
step. Open the section and check its prerequisites. If it begins with symbols
or terms the learner has not met, find an earlier explanation or give that
idea its own topic.

Use a technical chapter or paper when its exact method, evidence, or limits
matter. A course that ends at a research method may use a paper near the end
without teaching the opening concepts from that paper. Explain the paper's
terms before asking the learner to read its derivation.

The course depth changes how far you check an idea, not how hard the first
source must be:

| Depth | Check while planning |
| --- | --- |
| `survey` | Find a sound first explanation and check the order of the central ideas. |
| `working` | Also check an example or exercise that requires the learner to use each main idea. |
| `mastery` | Also inspect the derivation, assumptions, limits, and a case where the method needs care. |

Choose the few sources that do these jobs well. Add another only when it
answers a question the existing sources leave open. A short course should
cover fewer steps fully; a longer course can give difficult steps their own
topics. Do not use a source count as a proxy for depth.

## Search and verify

Start with books, open course pages, official documentation, primary records,
and papers suited to the subject. `skills/subject/references/resources.json`
is a list of leads, not a preselected bibliography. For changing software,
check the installed version. For a research claim, open the original work.

Record the actual section you read, what it establishes, and its audience.
A landing page may confirm a title but not a chapter's teaching content. A
search snippet is a lead, not proof. If a page is inaccessible, mark it that
way and use a source you can inspect.

## Save the useful notes

Keep `RESEARCH.md` beside `course.json`. A small table is enough:

| Topic or concept | Source and section | Job in the course | What you checked | Gap |
| --- | --- | --- | --- | --- |
| First encounter with probability | Introductory chapter, named section | Explain chance through a small case | Read the example and its prerequisites | Conditional cases come later |

Use `course-research.json` when structured notes help. Keep `used_in` tied to
topic IDs and state what the source contributes. For example:

```json
{
  "goal": "compare uncertain outcomes",
  "sources": [
    {
      "id": "openstax-expected-value",
      "title": "OpenStax Introductory Statistics 2e",
      "url": "https://openstax.org/books/introductory-statistics-2e/pages/4-2-mean-or-expected-value-and-standard-deviation",
      "opened_sections": ["4.2 Mean or Expected Value and Standard Deviation"],
      "role": "Introduce a probability-weighted average through a small table",
      "trust": "opened",
      "used_in": ["expected-return"]
    }
  ],
  "open_questions": ["Learner's fluency with probability is unverified"]
}
```

The `id` must match `course.json/sources`. Only sources used by the route
belong in that course record. Its topic `resource_ids` select the sources for
that topic. Give each recorded source its real section and verification note.
Do not describe unopened material as checked.
