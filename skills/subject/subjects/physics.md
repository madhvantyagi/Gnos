# Physics

Teacher: `teachers/physics/SOUL.md` (Mira Sen).

Route physics by the physical prediction the learner wants to make: describe a
motion, account for energy, infer a field, explain a measurement, or compare
models. Every equation belongs to a system, reference frame, approximation, and
measured quantity. Do not let an elegant formula replace the apparatus.

## Route by physical work

| Area | Inspect first | Teaching decision | Evidence of progress |
| --- | --- | --- | --- |
| Mechanics | Vectors, graphs, units | Name object, frame, interactions, and sign convention before equations | Predict direction and acceleration before calculating |
| Oscillations and waves | Periodic functions, mechanics | Keep phase, amplitude, frequency, and propagation separate | Read or sketch two quantities on one clock |
| Thermodynamics | Energy, systems, probability | Draw the system boundary; separate state, work, heat, and entropy | Account for energy and identify the process assumption |
| Electricity and magnetism | Vectors, fields, calculus | Distinguish source, field, force, potential, and flux | Use signs, symmetry, units, and a limiting case |
| Optics | Geometry, waves | Choose ray or wave model from scale and question | Predict image or interference behavior under a changed setup |
| Relativity | Frames, algebra, spacetime | State observers and measured intervals before transforming them | Compare invariant and frame-dependent quantities |
| Quantum physics | Probability, complex numbers, linear algebra | Keep state, measurement rule, and outcome distribution distinct | Predict probabilities without treating a state as a trajectory |
| Experimental physics | Units, uncertainty, estimation | Treat instrument limits and residuals as part of the result | Report fit, uncertainty, and a plausible error source |
| Computational physics | Equations, programming, numerical error | State discretization, initial conditions, and stability condition | Compare numerical output with analytic or limiting behavior |
| Biophysics | Physics model plus biological constraints | Choose scale and effective variables; label what is simplified | Connect a measurable biological quantity to the model |

## Prerequisite checks

- For mechanics, check vectors, slopes, graphs, and unit conversion. Ask what
  object each arrow acts on; action-reaction pairs belong to different objects.
- For energy, distinguish a system's stored energy from energy transferred by
  work or heat. Ask what crosses the chosen boundary and what remains inside.
- For waves, check sinusoid parameters and phase. Amplitude is not frequency,
  and a wave's shape is not automatically the motion of one material point.
- For fields, check vector direction, superposition, and inverse-square scaling.
  A field is defined at a location; it is not the force arrow on every object.
- For thermodynamics, check state variables, path dependence, and equilibrium.
  Heat is not a substance stored in a body.
- For relativity and quantum mechanics, check algebra and probability notation,
  then name which quantity is operationally measured. Avoid classical pictures
  that smuggle in an unsupported trajectory.
- For experiments, check significant scale, calibration, uncertainty, and graph
  axes. A best-fit line does not erase systematic error.

## High-value teaching decisions

Ask for a qualitative prediction before calculation when sign, direction, or
scale distinguishes models. After calculating, check units, sign, limiting case,
and whether the result answers the stated quantity. Restore an approximation
when the learner silently extends it: small angle, negligible drag, constant
field, equilibrium, or nonrelativistic speed.

Keep these distinctions visible:

- position, velocity, and acceleration are different derivatives of motion;
- net force is not an individual force, and zero acceleration is not no forces;
- mass is not weight, and weight depends on the gravitational field;
- energy is a conserved accounting quantity, while work and heat describe modes
  of transfer across a system boundary;
- electric field is not electric force, and potential is not potential energy;
- a model's fit to data is not the same as a causal explanation;
- deterministic evolution of a state is not deterministic prediction of every
  measurement outcome.

## Mini lesson patterns

**Thrown object.** At the top of a trajectory, vertical velocity is zero for an
instant while acceleration remains approximately `−g`. Draw both vectors and
change the frame or add drag to show which statement survives.

**Mass and falling.** Start from `F=ma` and `F=mg`; cancel mass only after naming
the assumptions. Then change shape and include air resistance so the learner can
see why equal gravitational acceleration is not a universal statement about fall
time.

**Pendulum.** Show angle, tangent velocity, and acceleration on one clock. Use
`θ(t)=θ₀ cos(√(g/L)t)` only under the small-angle approximation; compare a large
swing or a numerical solution rather than calling the approximation exact.

**Circuit model.** Trace charge flow through a simple loop and distinguish
potential difference from current. Change one resistance and predict which
quantity changes before using Ohm's law; keep the circuit boundary explicit.

**Heat and work.** Compress a gas and ask which energy crosses the boundary and
with what sign convention. Compare an adiabatic path with a heated path reaching
the same final state to expose path dependence.

**Measurement.** Fit a line to data, inspect residuals, and ask whether the
intercept is physically expected. Vary one plausible systematic offset; the
learner should distinguish a noisy estimate from a biased instrument.

## Handoffs and shared concepts

Mira leads system choice, physical assumptions, diagrams, units, and predictions.
Ben supplies derivatives, vectors, differential equations, or probability when
the mathematics blocks the physical reasoning. Theo leads simulation code,
numerical methods, and data pipelines; Mira defines which state and observable
the code must represent. Biology owns the biological mechanism in biophysics;
Mira supplies the force, diffusion, energy, or transport model.

A handoff names the object or system, the last sound prediction, the exact
mathematical bridge, and the approximation to preserve. Keep a single notation
for time, position, field, and energy. One teacher owns the explanation while a
supporting teacher contributes only the needed bridge.

## Courses, learner memory, and artifacts

Use `skills/course-design/SKILL.md` for a sustained goal such as “model a damped
oscillator from data” or “explain satellite motion.” Research the sequence,
schedule a vector or calculus bridge where it first matters, and assess with a
prediction plus a changed physical situation. A local unit mismatch does not
need a mechanics course.

Use `skills/understanding-user-learning/SKILL.md` to record the learner's actual
system choice, diagram, prediction, correction, and transfer case. Preserve
whether the learner can identify a force, use a formula with help, predict
independently, or explain a limit after delay. Never convert one wrong sign into
an enduring ability label.

Use the PDF skill for apparatus notes, derivation sheets, uncertainty tables, or
lab-ready worked examples. Include system boundaries, units, assumptions, and
source credits; render every page and inspect equations and diagrams. Use Manim
when time or spatial change is the target: trajectories, phase, field lines, or
wave propagation. Tie every moving object to the same equations and initial
conditions; a visually smooth simulation is not validation. For a force balance,
circuit, or measurement table, a labeled still is usually clearer.

## Resource routing

These catalog entries are starting points. Inspect the relevant chapter, lecture,
or exercise before assigning it and state whether access was to a landing page,
course materials, or a verified PDF. Do not infer coverage from a title.

| Catalog ID | Best fit | Level and access note |
| --- | --- | --- |
| `openstax-physics-1` | Introductory mechanics and waves | Introductory college; publisher landing page, current chapter/PDF must be checked |
| `mit-mechanics` | Classical mechanics sequence and exercises | Undergraduate; official course materials and problem resources |
| `openstax-calculus-1` | Calculus bridge for changing quantities | Introductory college; use only for the needed calculus section |
| `mit-multivariable` | Partial derivatives in fields or thermodynamics | Undergraduate unit; not a complete physics text |

For thermodynamics, E&M, optics, relativity, quantum physics, experimental
methods, or computational physics, choose a topic-specific university course,
open textbook, or primary paper during course research. Check the level and the
actual relevant content. If a source page or PDF cannot be opened, report that
limit and route to a verifiable alternative rather than inventing an exercise or
claiming that a landing page was read.
