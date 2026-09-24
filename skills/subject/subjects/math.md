# Mathematics

Teacher: `teachers/math/SOUL.md` (Ben Waston).

Choose the branch by the task: calculate, model, prove, estimate, or optimize.
Check the needed operation or assumption at the point of use. Keep expressions,
equations, identities, approximations, and theorems distinct. Put hypotheses
beside the claim and state the permitted inputs.

## Ways to show the idea

Use graphs for variation, diagrams for structure, and worked notation for the
argument. Use [Excalidraw](../../excalidraw/SKILL.md) for a quick labeled figure,
[Pinepaper](../../pinepaper/SKILL.md) when a curve and geometric state must
change together, and [Manim](../../manim-voice-animation/SKILL.md) for narrated change.
Use a plotting library when exact data or numerical curves matter. A picture
can suggest a theorem; it does not replace a proof.

Write lesson math as LaTeX with `$...$` or `$$...$$`, such as `$\mathbb{R}^n$`
and `$P^{-1}$`. Read [the math reference](../references/math.md) for detailed
prerequisite checks and visual patterns. Ben owns the mathematical argument;
a domain teacher keeps responsibility for what the variables mean.

## Teaching each area

Choose the matching section. Its order suggests how to build the topic; it is
not a complete syllabus. Course design uses the starting point and source
checks. Lesson design chooses the views that explain the difficult steps.
Treat the named confusion as a possibility, not a diagnosis of this learner.

### Arithmetic and algebra

- **Build:** Start with a quantity or equality and a concrete operation. Use that
  example to explain the symbolic rule. An expression is not an equation. An operation
  may exclude some values.
- **Research:** Use an introductory algebra section with worked operations and excluded
  cases. Check the permitted number system and operation.
- **Show and check:** A number line or area model explains the operation. A value table
  exposes a pattern. Worked equations justify the general step and test an excluded
  value.

### Geometry and trigonometry

- **Build:** Start with a labeled figure and the relation to determine. A drawing's
  appearance does not establish a length, angle, or theorem.
- **Research:** Inspect a geometry or trigonometry chapter that states the givens and
  proves the relation. A labeled figure should match those hypotheses.
- **Show and check:** Compare labeled figures with changed givens. Use Pinepaper
  when moving a point must update an angle, length, or graph from the same
  coordinates. Derive the relation beside the labels. The motion tests a
  conjecture before a proof.

### Calculus

- **Build:** Start with a changing quantity or accumulating amount. Compare finite
  differences or sums before taking limits. A quantity differs from its rate, and a
  picture of a limit does not prove convergence.
- **Research:** Use a calculus chapter that develops the limit before the rule. Check
  domains, units, and a worked example. Use analysis for a requested rigorous
  justification.
- **Show and check:** Connect a value table to secants or area strips. Use Pinepaper
  when the changing interval must update both the construction and its
  numerical value. Use Manim for a narrated approach to a limit. Translate
  each visual quantity into the equation.

### Differential equations and dynamics

- **Build:** Start with a local rule for change and an initial state before a solution
  method. An equation describes allowed change. Initial and boundary conditions select a
  solution.
- **Research:** Inspect a differential-equations text for existence assumptions and
  solution methods. Use a numerical-methods source when discretization affects the
  example.
- **Show and check:** Pair a slope field or phase portrait with a time plot. Use
  Pinepaper if one initial condition must drive both views; keep the equation
  and solver stated. Use Manim to narrate a trajectory or a simulation to vary
  initial conditions. Compare with an analytic or limiting case.

### Linear algebra

- **Build:** Start with a vector as an object and one operation on it. Introduce
  coordinates and a general map from that example. Coordinates depend on a basis.
  Matrix entries do not explain the transformation by themselves.
- **Research:** Use a linear-algebra chapter that connects maps, bases, and matrices.
  Check dimensions and whether the argument depends on a chosen basis.
- **Show and check:** An Excalidraw figure labels input and output vectors. A
  worked product connects entries to movement. Use Pinepaper if changing the
  basis must move the vectors and update coordinates together. Code tests a
  larger case.

### Probability

- **Build:** Start with possible outcomes and what information is known before a
  calculation. Conditioning changes what is counted. Expected value need not occur on
  one trial.
- **Research:** Use a probability text with explicit sample spaces and model
  assumptions. Inspect the counting argument or derivation before reusing its formula.
- **Show and check:** Use outcome tables and trees for counting, graphs for
  distributions, and simulation for repeated trials. Keep the same event across views
  and distinguish the model probability from an observed frequency.

### Statistics and inference

- **Build:** Start with a question about a population and how the observed sample was
  obtained. A sample estimate, its uncertainty, and a causal claim require different
  arguments.
- **Research:** Use an introductory statistics chapter for the estimator and an original
  study or dataset guide for the sampling process. Check missingness, dependence, and
  the inferential assumptions.
- **Show and check:** Plot data before fitting. Compare estimates across simulated
  samples. Show intervals on repeated estimates. Use code to reproduce a calculation,
  then explain what changing the sampling process would invalidate.

### Discrete and abstract mathematics

- **Build:** Start with a small structure or claim. Test examples before stating the
  definition and proof. Several examples do not prove a universal claim. Reversing an
  implication changes it.
- **Research:** Use a discrete-math or algebra text with the exact structure and proof.
  Check the domain before reusing a familiar theorem.
- **Show and check:** A graph, truth table, or operation table makes the structure
  inspectable. A proof tree shows dependencies. A counterexample tests a weakened
  assumption.

### Analysis and topology

- **Build:** Start with the question a definition solves, then a concrete example and
  near-miss. Changing quantifier order changes the claim. A picture can hide an
  exceptional point.
- **Research:** Inspect the definition, hypotheses, proof, and a counterexample in an
  analysis or topology text. Compare conventions when sources differ.
- **Show and check:** Annotated graphs suggest the distinction. Explicit choices of
  bounds or neighborhoods expose the quantifiers. A proof establishes what the picture
  cannot.

### Optimization and numerical math

- **Build:** Start with a quantity to improve and one attempted update under stated
  constraints. A stationary point may not be a minimum. A numerical result depends on
  conditioning and tolerance.
- **Research:** Use an optimization or numerical-analysis chapter for assumptions and
  error bounds. Check a reference implementation only after the mathematical rule is
  clear.
- **Show and check:** Contours connect direction to change. A worked update and
  iteration table explain the rule. Use Pinepaper only when a changed step size
  must update both the path and loss trace. Compare conditioning or constraints.

## Source use

Use [the source-use guide](../references/source-use.md). Catalog entries are
leads; inspect the relevant section before using it. Match the source to the
subfield and question. Start with an accessible explanation, then inspect the
technical argument or evidence needed for the agreed depth. Record the section,
its job, and any access limit in the course research notes.
