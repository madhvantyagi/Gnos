# Mathematics depth and visual patterns

Read this reference when a mathematics lesson needs detailed prerequisite
checks, examples, source selection, or a substantial diagram or animation. The
concise route remains in [the subject guide](../subjects/math.md).

Use the guide's representation profile first, then apply
`skills/course-design/references/representation-choices.md`. This reference
defines mathematical content and visual grammar; it does not order media by
itself.

## Prerequisite checks

- Algebra: equality for all permitted inputs versus equality at one value;
  conditions on division, roots, logarithms, and cancellation.
- Functions: domain, codomain, one input-output pair, composition, and whether
  an inverse is actually defined.
- Calculus: slope, average rate, limit, and units before derivative rules;
  accumulation before antiderivative shortcuts.
- Vectors: addition, scalar multiplication, basis, and coordinate dependence.
- Probability: sample space, equal-likelihood assumptions, conditioning, and
  independence.
- Proof: implication, converse, counterexample, and quantifier scope. Computed
  cases can suggest a theorem but do not prove a universal claim.
- Numerical work: scale, units, conditioning, rounding, convergence criterion,
  and acceptable error.

## Teaching patterns

**Cancellation.** For `x(x-1)=0`, preserve the `x=0` branch before division.
Change the equation to `x(x-1)=2x` so cancellation becomes a condition the
learner must defend.

**Chain rule.** Set `u=3x`, `y=u^2`, and attach each derivative factor to one
stage. Replace the inner function with `x^2+1` to test composition rather than
the phrase “outside times inside.”

**Linear maps.** Apply the map to basis vectors, then assemble a general input
from those images. Contrast the transformation with a coordinate change.

**Probability.** Compare two draws without replacement with two coin flips.
Make the sample space and conditional information visible. A simulation checks
a chosen model; it does not choose the model.

**Proof and counterexample.** Ask for the domain in “every continuous function
is bounded.” Compare a closed bounded interval with `(0,1)` and the real line.
The picture supports the hypotheses; it does not replace them.

**Gradient descent.** Keep parameters `theta`, objective `L(theta)`, gradient,
step size, and stopping rule fixed in notation. Vary the step size and connect
overshoot to curvature or conditioning.

## Pinepaper patterns

Read [the Pinepaper workflow](pinepaper.md) before using the MCP tools.

### Transformation

For a linear map, keep the original basis and grid faintly visible while the
mapped basis, grid, and vector move together. Display the matrix and connect
each column to the corresponding basis image. Pause at the initial, halfway,
and final states; do not imply that every matrix interpolation preserves the
property being studied.

### Function and derivative

Place the point, secant or tangent, local slope, and relevant difference
quotient in one visual grammar. If a secant approaches a tangent, animate the
parameter and equation together. Preserve axis scale so apparent steepness does
not change for cosmetic reasons.

### Optimization

Show level sets, current point, gradient direction, update vector, and next
point. Keep the update equation visible. Compare at least two step sizes from
the same start and mark divergence or slow progress without calling either a
general property of the optimizer.

### Differential equations and dynamical systems

Tie every moving state to the differential equation, initial condition, time
scale, and numerical method. A smooth path is not evidence of numerical
stability. When useful, show a phase portrait beside the time series.

### Probability and statistics

Use motion to reveal sampling, conditioning, or accumulation, not to dramatize
randomness. Keep population, sample, statistic, model, and interval visually
separate. For repeated sampling, fix the data-generating assumption and show
how the statistic's distribution is built.

### Proof-supporting diagrams

Mark given facts, constructed objects, and conclusions differently. Use the
visual to expose a relation or counterexample; keep the quantifiers and
hypotheses in text. Never let a generic-looking picture stand in for an exact
or exceptional case.

## Handoffs, artifacts, and sources

Ben leads mathematical meaning. Physics owns measured-system assumptions; CS
owns algorithms and implementation; economics or biology owns the domain model.
Carry one notation and the last valid claim across the bridge. Use stable IDs
such as `math.vector`, `math.derivative`, `math.chain-rule`, and
`math.gradient`.

Use a PDF for a reusable derivation, theorem sheet, or worked-example packet.
Use Pinepaper for interactive or animated vector explanation and Manim for a
narrated rendered lesson.

Catalog starting points include `openstax-calculus-1`, `mit-linear-algebra`,
`mit-multivariable`, `mit-gradient-descent`, and `mit-algorithms`. Inspect the
relevant unit before assigning it. Select topic-specific academic sources for
probability, statistics, abstract algebra, topology, differential equations,
or numerical analysis.
