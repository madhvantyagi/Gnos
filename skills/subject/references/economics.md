# Economics depth and visual patterns

Read this reference when an economics lesson needs deeper branch guidance,
source selection, a substantial example, or an advanced diagram or animation.
The concise route remains in [the subject guide](../subjects/economics.md).

## Branch guidance

**Microeconomics.** Name the agent, feasible alternatives, objective or
preference, constraints, and margin. Start with a numerical table. A price
change causes movement along a fixed demand curve unless another condition
changes the relationship.

**Macroeconomics.** Label stocks, flows, accounting identities, behavioral
assumptions, equilibrium conditions, and empirical claims separately. Ask
whether a value is nominal or real, aggregate or per person, adjusted how, and
measured over which dates.

**Econometrics.** Start with whose outcome, which treatment, which comparison,
and which time window. Then inspect selection, confounding, interference,
measurement, missingness, and the identification assumption. A regression
coefficient needs units and a comparison group before policy interpretation.

**Game theory.** Put players, timing, information, actions, and payoffs in the
same model. Solve best responses before naming equilibrium. Change information
or commitment and test whether the equilibrium changes.

**Labor, public, and development.** Ask who receives the benefit, pays the
cost, or has bargaining power. Separate statutory assignment from incidence,
and efficiency from the stated distributional criterion.

**Behavioral economics.** Use a meaningful baseline, then distinguish changes
in preference, belief, attention, framing, learning, and implementation. Check
population, incentives, treatment, replication, and external validity.

**Economic history.** Put model mechanisms beside dated evidence about law,
organizations, technology, labor, and distribution. A counterfactual model does
not establish what historical actors knew or which institutions existed.

## Teaching patterns

Compare a nonrefundable ticket with a resalable ticket to separate sunk cost
from opportunity cost. Compare a randomized offer with an observational wage
gap to expose the identification assumption. In a policy example, show total
surplus or output alongside incidence and distribution rather than collapsing
them into one “better” result.

## Pinepaper patterns

Read [the Pinepaper workflow](pinepaper.md) before using the MCP tools.

### Curves and comparative statics

Begin with a table and a labeled static graph. Animate either movement along a
fixed curve or a shift of the whole relationship, never both without explicit
labels. Preserve the original curve faintly, mark the changed condition, and
show the old and new equilibrium values with units.

### Dynamic adjustment and feedback

For inflation, inventories, expectations, debt, growth, or cobweb dynamics,
show the stock-flow structure, update rule, time step, and lag. Animate one
period at a time and place the time series beside the mechanism. A simulated
path is conditional on the assumed equations and parameters.

### Games and strategic interaction

Use a game tree for sequence and information, a payoff matrix for simultaneous
choice, and a network only when relationships among many actors matter. Let the
learner choose an action or information change, then update best responses and
payoffs from the same model.

### Causal and policy diagrams

Keep causal assumptions, observed variables, selection, and policy
implementation stages distinct. Animate the proposed mechanism as a hypothesis,
then place the empirical comparison or missing evidence beside it. Do not use
motion to imply causation that the research design does not identify.

### Distribution

When an aggregate changes, keep totals and group outcomes visible together.
Flows between groups should balance when they represent transfers. Label whose
welfare criterion is being applied.

## Sources and handoffs

`openstax-economics` and `core-economy` are introductory starting points. For US
data, inspect the exact FRED, BLS, or BEA series, including units, frequency,
seasonal adjustment, coverage, revisions, and dates. For causal or theoretical
claims, inspect the paper's methods and data rather than relying on the title or
abstract alone.

Nadia leads incentives, equilibrium, identification, evidence, and the
positive/normative boundary. Ben supports algebra, calculus, probability, or
uncertainty; Theo supports data and simulation; history owns chronology and
source context. Carry the economic quantity, comparison, units, and unresolved
assumption through the handoff.

Use Pinepaper for interactive models or animated vector explanation, Manim for
a narrated rendered lesson, and a PDF for a reusable model-and-evidence sheet.
