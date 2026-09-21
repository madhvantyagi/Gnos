# Mathematics

Teacher: `teachers/math/SOUL.md` (Ben Waston).

Route by the learner's intended action: calculate, model, prove, estimate,
optimize, or interpret data. Diagnose the representation that failed rather
than assigning one global “math level.”

| Area | Inspect first | Evidence of progress |
| --- | --- | --- |
| Arithmetic and algebra | Equality, operations, permitted values | Transform and verify a changed case |
| Geometry and trigonometry | Angles, ratios, coordinates | Justify a relation from labeled givens |
| Calculus and differential equations | Functions, limits, rate, accumulation | Explain a limiting step and predict behavior |
| Linear algebra | Vectors, functions, coordinate systems | Apply a map and interpret its output |
| Probability and statistics | Sample space, dependence, sampling | State what an inference establishes |
| Discrete and abstract mathematics | Logic, sets, proof habits | Prove or refute over the stated domain |
| Analysis and topology | Quantifiers, spaces, convergence | Construct an example with all hypotheses |
| Optimization and numerical math | Objective, constraints, conditioning | Compare against a baseline or limiting case |

Keep expression, equation, identity, theorem, approximation, and numerical
estimate distinct. Put hypotheses beside every result; coordinates are not the
abstract vector; a stationary point is not automatically a minimum.

Write mathematics as LaTeX with `$...$` (inline) or `$$...$$` (display)
delimiters so the course page renders it with KaTeX: `$\mathbb{R}^n$`,
`$[v]_B$`, `$P^{-1}$`, `$\operatorname{diag}(2, 0.5)$`. Bare ASCII such
as `R^(m x n)` or `P^(-1)` is never acceptable lesson text.

Use algebra for a local symbolic break, a table or graph for variation, and a
diagram for geometry or transformation. For deeper prerequisites, teaching
patterns, sources, or an advanced visual, read
[the mathematics reference](../references/math.md). When animation or polished
vector graphics are useful, also read
[the Pinepaper workflow](../references/pinepaper.md).

## Representation profile

Start with exact notation and a worked step. Add a table or graph when a
quantity varies, and a labeled diagram when geometry, coordinates, or a mapping
must be inspected. Use a simulation when the learner should change a parameter,
test a conjecture, or compare repeated samples. Use Manim or Pinepaper for a
limit, transformation, orbit, sampling process, or algorithm whose intermediate
states carry the idea. Keep hypotheses and quantifiers in text; a picture does
not prove the theorem. Math can use many simulations and animations across a
sustained course, but each one must expose a distinct change.

Load those references only when the task needs them. Ben owns definitions,
derivations, proof structure, and mathematical meaning. A domain teacher owns
what the variables represent and what counts as evidence.

## What each area earns

First write what the learner must inspect, change, compare, or work out
in one sentence, and pick the smallest medium that lets them do it. Only
then check this table for what mathematics usually needs. Never use the
table as a reason to order its favorite medium. Depth and length still
cap the media: a survey earns mostly text plus one medium.

| Area | Lead with | Then earn, only when | Exercise |
| --- | --- | --- | --- |
| Arithmetic and algebra | Exact equations in text | Nothing else; a picture adds no new action | Numeric: transform and verify a changed case |
| Geometry and trigonometry | Labeled diagram (Pinepaper) of givens and coordinates | Nothing else unless a shape moves | Short text: justify the relation from the givens |
| Calculus and differential equations | Worked limit step in text | Manim, only when the middle steps of a limit or accumulation carry the idea | Numeric: predict the behavior |
| Linear algebra | Diagram (Pinepaper) of the map and coordinate systems | Manim, only when the transformation itself must be watched | Numeric: apply the map and read the output |
| Probability and statistics | Definitions and sample space in text | Simulation, only when the learner changes a parameter or compares repeated samples | Numeric: state what the inference establishes |
| Discrete and abstract mathematics | Logic and proof steps in text | Nothing else; the proof burden is words and symbols | Long text: prove or refute over the stated domain |
| Analysis and topology | Quantifiers and hypotheses in text | Nothing else; a picture does not prove convergence | Long text: build an example that meets every hypothesis |
| Optimization and numerical math | Objective, constraints, and baseline in text | Simulation, only when the learner varies the objective or constraints and compares against the baseline | Numeric: compare against the baseline or limiting case |

Applied areas earn motion and simulation more often on average, and
theory areas earn exact text more often. That is an observation about
averages, never a rule for this lesson: a theory lesson on limits can
earn motion, and an applied lesson on reading one fitted number earns
only text and a small table.
