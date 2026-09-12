# Economics subject map

Teacher: `teachers/economics/SOUL.md` (Nadia Vale).

Route by the decision or claim the learner wants to make. Keep the decision
maker, alternatives, constraints, comparison, and held-constant conditions
visible. A graph is a compact model of a choice or relationship; it is not a
photograph of an economy and does not settle the value judgment by itself.

## Entry routes and prerequisites

| Route | Inspect first | First observable outcome |
| --- | --- | --- |
| Microeconomics | ratios, graphs, opportunity cost | Compare a choice after changing one constraint |
| Macroeconomics | stocks/flows, accounting, time horizon | Distinguish nominal, real, per-person, and aggregate measures |
| Econometrics / causal inference | probability, statistics, data structures | State an estimand and identification assumption |
| Game theory | conditional reasoning, payoffs | Find best responses and separate prediction from preference |
| Labor economics | micro, institutions, measurement | Compare wage, employment, incidence, and bargaining outcomes |
| Public economics | externalities, incidence, welfare criteria | Compare policy alternatives and distributional effects |
| Development economics | micro, institutions, measurement | Separate mechanism, context, and evidence across settings |
| Behavioral economics | baseline model, experiments | Specify the departure and competing explanations |
| Economic history / institutions | chronology, sources, models | Put a mechanism beside evidence of historical conditions |
| Finance and monetary economics | present value, risk, accounting | Track claims, timing, and units without treating prices as welfare |

If slope, percentages, probability, or logarithms blocks the first task, route
a short `math.*` bridge. If the learner needs reproducible data cleaning or a
model implementation, CS supports the operation; Nadia still owns the economic
estimand and interpretation. History owns archival context and chronology.

## Branch guidance

**Microeconomics.** Name the agent, feasible alternatives, objective or
preference, constraints, and margin of choice. Distinguish a movement along a
curve from a change in the relationship: a price change is not automatically a
demand shift. Start with a small numerical table before adding curves. A useful
mini-lesson compares a nonrefundable ticket with a resalable ticket so sunk cost
and opportunity cost become a changed condition, not a slogan.

**Macroeconomics.** Label stocks, flows, accounting identities, behavioral
assumptions, equilibrium conditions, and empirical claims separately. Ask
whether a value is nominal or real, aggregate or per person, seasonally adjusted,
and measured over what dates. GDP growth can coexist with unequal gains, price
changes, or unmeasured household production. Have the learner explain what a
model predicts before adding a limitation, then identify the observation that
would discriminate between competing mechanisms.

**Econometrics and causal inference.** Start with the estimand: whose outcome,
which treatment, which comparison, and which time window? Then inspect selection,
confounding, interference, measurement, missing data, and the identification
assumption. Correlation, prediction, and causal effect are different products.
A mini-lesson can compare a randomized offer with an observational wage gap and
ask which assumptions make each estimate interpretable. Do not let a regression
coefficient become a policy conclusion without units and a comparison group.

**Game theory.** Put players, timing, information, actions, and payoffs on one
page. Solve best responses before naming an equilibrium and distinguish a model's
prediction from a player's moral preference. Change one information or commitment
condition to show why an equilibrium can change. In repeated or mechanism
settings, state what is assumed about rationality and common knowledge rather
than presenting a strategy as universal advice.

**Labor, public, and development economics.** Ask who receives a benefit, pays
a cost, or has bargaining power. Separate incidence from statutory assignment,
and efficiency from a stated distributional criterion. Institutions, race,
gender, geography, informality, and historical power can change the mechanism;
they are not decorative context. Compare a policy to a specified alternative,
show transfers and behavioral responses, and say which outcome is measured.

**Behavioral economics.** Teach the baseline optimizing or equilibrium model
first when it is a real comparison, then describe the observed departure and the
experimental design. Separate preference, belief, attention, framing, learning,
and implementation failure. A single lab result is not a universal law; check
population, incentive, treatment, replication, and external validity.

**Economic history and institutions.** Put model mechanisms beside dated sources
about law, organizations, technology, labor, and distribution. Economics can
clarify a counterfactual; history must establish which conditions and actors
existed. Ask whether a series is comparable across time and whose records were
excluded. Never use a modern equilibrium diagram as a substitute for archival
evidence or assume historical actors held the modeler's information.

**Money, finance, and environment.** Track timing, units, risk, default,
liquidity, and the accounting identity before discussing returns or policy.
For environmental questions, identify property rights, physical limits,
externalities, and whose welfare enters the objective. A market price is an
observation of exchange conditions, not a complete measure of social value.

## Source routes and verification status

`openstax-economics` (Principles of Economics 3e) is an introductory textbook
route; its landing page was verified, while chapter content was not inspected.
`core-economy` is an open-access introductory route pairing models with data
activities; the official home page was verified. Neither is a specialized
econometrics text, current policy forecast, or guarantee that a module fits the
learner's level.

For observed US series, FRED at https://fred.stlouisfed.org/ was accessible and
exposes source, release, frequency, and observation metadata. Cite the series,
not only the chart, and record vintage when revisions matter. BLS data at
https://www.bls.gov/data/ was accessible and lists CPI, employment, wages,
productivity, and API routes. Check definitions, seasonal adjustment, coverage,
and breaks before comparing values. BEA's data landing page at
https://www.bea.gov/data resolved but returned little readable content in the
current check; verify the table and methodology directly before assigning it.

For causal or theoretical claims, use a paper's abstract and methods, then
inspect the cited data and identification. NBER's papers landing page was not
readable in the current check, so do not promise access to a particular working
paper without reopening it. A data portal is evidence about measurement; it is
not evidence that a model or policy caused the observed movement.

## Course design and learner evidence

State outcomes as actions: solve a constrained choice, draw and explain a
shift, derive an equilibrium, audit an estimate, compare policy incidence, or
write a conditional recommendation. Build each module around one comparison
and one changed assumption. Before fixing a sustained sequence, use
`skills/course-design/references/course-research.md` to check scope,
prerequisites, source fit, and assessment. Choose a main source at the starting
level, inspect the relevant chapter or series, and reserve time for retrieval
and repair. Date current figures and policy claims.

Evidence is a correctly scoped model, a transparent calculation, a valid graph
with causes labeled, an estimand with assumptions, or a policy comparison that
shows totals and distribution. A fluent definition or copied curve is exposure;
independent transfer to a new shock is stronger evidence. Record whether the
learner confused demand with quantity demanded, sunk with opportunity cost,
accounting with causality, or positive with normative claims.

## Representations and media

Use a numerical table before a graph when the choice is new. On every graph label
axes, units, direction of movement, and which condition changed. Use Manim when
one parameter changes over time or a dynamic adjustment is the object; keep the
original and changed states visible, show the update rule, and include a limiting
case. A graph generated from assumed equations is a model illustration, not
empirical data. A PDF is useful for a model sheet with assumptions, algebra,
figure, data definition, and a short “what would change the answer?” prompt.

## Teacher selection and handoffs

Nadia leads models, incentives, equilibrium, identification, evidence, and the
positive/normative boundary. Hand to math when algebra, probability, calculus,
or statistical uncertainty is the bottleneck; return with the economic quantity
and comparison intact. Hand to CS for data or simulation operations, and to
history for institutions, archival sources, and chronology. A support teacher
gets one named bridge, not a second running lecture. Carry the learner's last
sound step, notation, units, and unresolved assumption across the handoff.
