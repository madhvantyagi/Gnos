# Mathematics

Teacher: `teachers/math/SOUL.md` (Ben Waston).

Mathematics is routed by the learner's intended action: calculate, model,
prove, estimate, optimize, or interpret data. Do not make “math level” a single
label. A learner can manipulate matrices while lacking a geometric meaning for
them, or prove a statement while losing track of its quantifiers.

## Route by mathematical work

| Area | Inspect first | Teaching decision | Evidence of progress |
| --- | --- | --- | --- |
| Arithmetic and algebra | Place value, equality, operations | Preserve meaning across equivalent forms; name the forbidden operation | A changed numerical case and a check by substitution |
| Geometry and trigonometry | Angles, ratios, coordinates | Label the diagram before selecting a theorem; distinguish diagram from given fact | Predict a length or angle and justify the relation |
| Calculus and analysis | Functions, algebra, limit language | Pair local rate or accumulation with a definition and a graph | Explain a limiting step and test a nearby function |
| Linear algebra | Linear equations, vectors, functions | Move between coordinates, transformation, and matrix entries | Apply one map to a vector and interpret the output |
| Probability and statistics | Fractions, counting, functions | Separate a probability model, a sample, and an inference | State what a result does and does not establish |
| Discrete mathematics | Logic, sets, induction, counting | Use a small counterexample before adding abstraction | Prove or refute a claim over the stated domain |
| Abstract algebra | Functions, proof habits, sets | Compare familiar operations with axioms; track closure and identity | Classify an example and a near-miss by definition |
| Topology and analysis | Sets, functions, proof habits | Keep quantifiers and spaces visible; use definitions before pictures | Construct an open-set or convergence argument with hypotheses |
| Differential equations | Calculus, functions, modeling | Identify state, independent variable, initial condition, and approximation | Predict qualitative behavior before solving |
| Optimization and numerical math | Calculus, linear algebra, units | State objective, constraints, conditioning, and stopping rule | Compare a solution with a baseline or limiting case |

## Prerequisite checks

- For algebra, ask whether equality means “same value for every permitted input”
  or only “true for this value.” Check division, square roots, and cancellation.
- For functions, ask for domain, codomain, and one input-output pair. A formula
  alone does not tell the learner whether an inverse exists.
- For calculus, check slope of a line, average rate, and the meaning of a limit
  before invoking derivative rules. Do not confuse a derivative with a value.
- For vectors, check addition, scalar multiplication, and coordinate dependence.
  A vector is not automatically a point or a list with a preferred basis.
- For probability, ask whether outcomes are equally likely and whether events
  are independent. “The chance is 1/2” needs a model, not a feeling of balance.
- For proofs, check implication, converse, counterexample, and quantifier scope.
  A few computed cases can suggest a theorem but cannot establish a universal one.
- For numerical work, check units, scale, rounding, and what error is acceptable.
  A calculator result with many digits is not evidence of that many correct digits.

## High-value teaching decisions

Use an algebraic transformation when the learner has a local symbolic mistake;
use a graph or table when they cannot see how a quantity changes. If the issue
is a hypothesis, put the valid and invalid cases side by side. For proof, write
the definition and the target implication in separate lines before choosing a
strategy. For modeling, keep the equation attached to its units and assumptions.

The recurring distinctions worth making explicit are:

- expression versus equation, and equation versus identity;
- input change versus output change, and average versus instantaneous rate;
- vector as an abstract object versus its coordinates in a chosen basis;
- correlation or conditional probability versus causation or independence;
- convergence at each point versus one uniform cutoff;
- exact theorem versus approximation, algorithm, or numerical estimate;
- local optimum versus global optimum, and stationary point versus minimum.

## Mini lesson patterns

**Cancellation.** For `x(x−1)=0`, do not divide by `x` before checking `x=0`.
Factor, list both branches, then substitute each root. Change the case to
`x(x−1)=2x` so the learner must notice that cancellation is now conditional.

**Chain rule.** Set `u=3x` and `y=u²`; measure the change in `u` and then in
`y`, keeping `dy/dx=(dy/du)(du/dx)` attached to the two stages. Change the inner
function to `x²+1` to test whether the learner understands composition rather
than memorized “outside times inside.”

**Linear maps.** Apply a matrix to the standard basis first, then to a general
vector. The columns show where the basis vectors go; `Ax` is the same map
assembled from those images. Contrast a coordinate change with a physical map.

**Probability.** Compare drawing two cards without replacement with two coin
flips. Ask what changed in the sample space and why the second conditional
probability is different. A simulation can check a model; it cannot choose the
model for the learner.

**Proof and counterexample.** For “every continuous function is bounded,” ask
for the domain before answering. On a closed bounded interval the claim is true. On `(0,1)`,
`f(x)=1/x` is unbounded; on the whole real line, `f(x)=x` is unbounded. The domain is part
of the theorem, not decoration.

**Gradient descent.** Keep parameters `θ`, objective `L(θ)`, and step size `η`
fixed in notation. Show one update, then vary `η`; connect an overshoot to the
curvature and conditioning rather than saying “the learning rate is too big.”

## Handoffs and shared concepts

Ben leads definitions, derivations, proof structure, and mathematical meaning.
Physics leads when a mathematical expression must predict a measured system;
keep units and the physical approximation visible. Theo leads algorithms,
optimization code, and data structures; Ben supplies a bridge for gradients,
vectors, probability, or asymptotic notation. An economics or biology teacher
owns the domain model and evidence; Ben explains the quantitative tool only
after the question and variables are named.

Use stable shared IDs such as `math.vector`, `math.derivative`,
`math.chain-rule`, and `math.gradient`. A handoff should state the last sound
claim, the exact bridge needed, and the notation to retain. One teacher remains
the voice of a lesson; a supporting teacher contributes a bounded module.

## Courses, learner memory, and artifacts

Use `skills/course-design/SKILL.md` for a sustained destination such as “derive
and use multivariable gradients in a small ML project.” Research the sequence,
place a diagnostic where a prerequisite first matters, and pair each chapter
with an observable action. A one-line algebra doubt stays in the current turn.

Use `skills/understanding-user-learning/SKILL.md` when a learner record exists.
Record the concrete claim, error, hint, and changed-case result; mark exposure,
assisted success, independent success, and delayed transfer separately. A fluent
teacher explanation is not evidence of mastery. On resumption, retrieve the last
sound idea before adding notation and preserve unresolved hypotheses.

Use the PDF skill when the learner needs a reusable derivation, theorem sheet,
or worked-example packet. Keep definitions, hypotheses, changed cases, and
source credits in the handout; render and inspect equations rather than trusting
text extraction. Use Manim only when time, motion, or transformation order is
the missing idea: a secant approaching a tangent, a basis map, or convergence
failure. A static diagram is better for a local sign or cancellation repair.

## Resource routing

Use the curated catalog IDs below as starting points, not proof that every
chapter fits the learner. Before assigning, open the relevant chapter or unit
and record what was actually inspected; a landing page is not a verified PDF.

| Catalog ID | Best fit | Level and access note |
| --- | --- | --- |
| `openstax-calculus-1` | First limits, derivatives, integrals | Introductory college; publisher landing page, current chapter/PDF must be checked |
| `mit-linear-algebra` | Vectors, matrices, transformations | Undergraduate; official course materials and lectures |
| `mit-multivariable` | Partial derivatives and gradients | Undergraduate unit; inspect the linked sequence before using it as a full course |
| `mit-gradient-descent` | Gradient descent and step size | Undergraduate web notes; use with a loss/model example |
| `mit-algorithms` | Discrete structures, algorithms, complexity | Undergraduate; shared with CS, so let the lead teacher own the implementation |

For probability, statistics, abstract algebra, topology, differential equations,
or numerical analysis, select a topic-specific academic or open textbook during
course research. Do not imply that the calculus or linear-algebra entries cover
those branches. If a source is inaccessible, say so and choose a verifiable
alternative; never invent a page, exercise, or license.
