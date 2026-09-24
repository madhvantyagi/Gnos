# Mathematics: difficult steps and worked representations

Read the [subject guide](../subjects/math.md) to choose the subfield and
starting point. Use the matching section below when a lesson needs a deeper
example, a proof, or several views of the same mathematical object. These
patterns apply with any suitable producer. Choose one through
[lesson design](../../lesson-design/references/representation-choices.md).

## From an operation to a rule

Work a small case and name the condition that permits each operation. For
$x(x-1)=0$, dividing by $x$ discards the solution $x=0$. Keep that branch
visible, solve the other branch, and substitute both answers into the original
equation. A graph can locate the roots; the algebra explains why they are roots.
Change the right side to $2x$ to check whether the learner preserves the condition.

For the chain rule, use $u=3x$ and $y=u^2$. Track a small change through both
stages before multiplying their rates. Label each factor with its input and
output. Connect the composition diagram to the equation, then replace $3x$
with $x^2+1$ so the inner rate also varies.

## From values to graphs and limits

Start with values the learner can compute. Put the same values in a table,
on a graph, and in the difference quotient. Explain what is held fixed and
what approaches a limit. Preserve axis scale during motion so the apparent
slope does not change for a visual reason.

Use [Pinepaper](../../pinepaper/SKILL.md) when the secant, interval, and
displayed value must change from one parameter. Use Manim when a narrated
approach to a tangent or accumulation is the deliverable.
State what the visual suggests and which limit argument establishes the result.
For differential equations, connect a local slope to one numerical step, then
to the trajectory. Keep the equation, initial state, time scale, and numerical
method visible. Compare step sizes against an analytic or limiting case.

## From coordinates to a linear map

Apply the map to basis vectors before assembling a general input from their
images. Match each matrix column to the corresponding basis image. Retain the
original grid or vectors when comparing before and after. Contrast changing
the vector with changing the coordinates used to describe it.

Use an [Excalidraw](../../excalidraw/SKILL.md) still for comparing fixed
bases and Pinepaper motion when following a transformation.
Do not imply that an interpolation between matrices preserves invertibility,
length, or another property unless it does. Check dimensions, a simple vector,
and a degenerate case before accepting the visual.

## From outcomes to uncertainty

Compare two draws without replacement with two independent coin flips. List
outcomes and explain which information changes the second probability. Connect
the tree branches to table entries and equation terms before simulating trials.
The simulation samples a chosen model; it does not establish that the model
fits a real population.

For inference, distinguish population, sample, statistic, and sampling
distribution. Build the distribution from repeated samples under fixed
assumptions. Explain why one observed estimate can differ from the parameter.
A changed sampling rule should lead to a discussion of assumptions, not just
a different curve.

## From examples to proof

State the domain and quantifier order before evaluating a universal claim.
For “every continuous function is bounded,” compare a closed bounded interval,
$(0,1)$, and the real line. Use a counterexample to expose the missing
hypothesis, then explain how the proof uses the corrected one.

Mark given facts, constructed objects, and conclusions separately in diagrams.
A typical-looking figure can hide an exceptional case. For convergence or
topology, work through actual bounds or neighborhoods so the learner can see
which choice depends on which earlier choice.

## From an update to convergence

Connect the objective, current point, gradient, update, and next point in one
worked calculation. Use contours or a graph to explain direction, then an
iteration trace to compare step sizes from the same start. Show when curvature,
conditioning, constraints, or numerical error changes the reasoning. One
converging example does not establish a general convergence guarantee.

## Research the missing step

Use an accessible worked example to introduce the object, then inspect the
precise theorem or method for its hypotheses. Catalog leads include
`openstax-calculus-1`, `mit-linear-algebra`, and `mit-multivariable`; they do not
cover every branch. Choose a dedicated source for probability, analysis,
topology, or numerical error. Record the exact section and any convention that
differs from the lesson. In an applied lesson, keep the domain's variables and
units while explaining the mathematical step.
