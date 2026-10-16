# Teaching instruction probes

These four small scenarios test whether a reviewer applies the teaching instructions. They are synthetic evaluation data, not lessons or learner records. They intentionally omit the structural lesson schema so file validation cannot substitute for reading the explanation.

Give a reviewer `scenarios.json`, the subject skill and selected guides, and `skills/lesson-design/references/lesson-design.md`. Request one verdict and exact defects/repairs per case. Inspect the judgments against the checks below. Do not turn keyword presence or the number of paragraphs into an automatic teaching score.

| Case | Required judgment |
| --- | --- |
| thin-derivation | Reject the claimed derivation: no limit definition or intermediate argument; numeric exercise cannot demonstrate derivation. |
| bounded-division | Accept for this local question; do not demand a course, second medium, or extended glossary. |
| dp-contract-mismatch | Reject: private trace disagrees with public arithmetic; singleton behavior contradicts the stated domain; disclosed answer and numeric-only response cannot support justification. Do not call the visible C(2)=30 wrong. |
| source-overreach | Reject: one interested source cannot establish population unanimity or causal success; repair the claim and ask for an evidence comparison. |

A passing probe shows an instruction can guide these judgments in this run. It does not measure human understanding, long-term retention, or reliability across every subject/model. Repeat only after material instruction changes or a newly observed teaching failure.
