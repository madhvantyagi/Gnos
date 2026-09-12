# Physics depth and visual patterns

Read this reference when a physics lesson needs detailed prerequisite checks,
examples, source selection, or a substantial diagram or animation. The concise
route remains in [the subject guide](../subjects/physics.md).

## Prerequisite checks

- Mechanics: vectors, graph slopes, units, reference frame, and which object
  each force acts on. Action-reaction forces act on different objects.
- Energy: stored energy versus transfer by work or heat; what crosses the
  chosen system boundary.
- Waves: amplitude, phase, frequency, wavelength, and the distinction between
  a wave profile and one material point's motion.
- Fields: source, field at a location, force on a test object, superposition,
  and inverse-square scaling.
- Thermodynamics: state variables, path dependence, equilibrium, and sign
  convention. Heat is not a substance stored in a body.
- Relativity and quantum physics: operationally measured quantities,
  probability notation, and the danger of importing a classical trajectory.
- Experiments: calibration, scale, uncertainty, residuals, and systematic
  error. A fit does not erase instrument bias.

## Teaching patterns

**Thrown object.** At the top of a trajectory, vertical velocity is momentarily
zero while acceleration remains approximately `-g`. Change the frame or add
drag and ask which statements survive.

**Falling bodies.** Derive equal gravitational acceleration from `F=ma` and
`F=mg` only after naming assumptions. Add different shapes and drag so the
learner distinguishes acceleration in the model from observed fall time.

**Pendulum.** Show angle, tangent velocity, and acceleration on one clock. Use
the small-angle solution only within its approximation and compare a larger
swing or numerical solution.

**Circuit.** Trace charge and energy through a loop while keeping current,
potential difference, and resistance distinct. Change one component and predict
before calculating.

**Heat and work.** Compare adiabatic compression with a heated path reaching the
same final state. Track transfer across the boundary and preserve the chosen
sign convention.

**Measurement.** Fit a line, inspect residuals, and vary a plausible calibration
offset. Separate random scatter from systematic bias.

## Pinepaper patterns

Read [the Pinepaper workflow](pinepaper.md) before using the MCP tools.

### Mechanics and free-body diagrams

Begin with a correct static free-body diagram: one object, interaction forces,
axes, frame, and scale convention. Animate motion in a second layer driven by
the same initial conditions and model. Force arrows should change only when the
modeled interaction changes; velocity and acceleration need distinct styles.

### Waves and oscillations

Use a shared clock for the source, one medium point, the spatial profile, and
the graph of displacement versus time. Motion should reveal phase and
propagation. Do not animate every point as though it travels with the wave.

### Fields

Separate source objects, field samples, field lines, and the force on a test
object. If the test object moves, update the field-derived vector consistently.
Field-line density is qualitative unless the construction explicitly encodes a
scale.

### Thermodynamics

Keep the system boundary visible. Animate state variables, work, and heat with
distinct channels; show a path on the state diagram beside the apparatus.
Equal endpoints do not imply equal work or heat.

### Relativity and quantum physics

Use worldlines, events, frames, state amplitudes, or outcome distributions with
carefully named axes and observers. Motion is explanatory geometry, not footage
of an unobserved classical mechanism.

### Simulation integrity

Place equations, parameters, units, initial conditions, approximation, and
numerical step beside the scene. Compare with a conservation law, analytic
case, or limit. A smooth animation is not validation.

## Handoffs, artifacts, and sources

Mira leads system choice and physical interpretation. Ben supplies derivatives,
vectors, differential equations, or probability; Theo supplies numerical
methods and software behavior. Carry the system, frame, last sound prediction,
and approximation through the handoff.

Use Pinepaper for interactive or animated vector explanations, Manim for a
narrated rendered lesson, and a PDF for apparatus notes, derivations, or
uncertainty tables.

Catalog starting points include `openstax-physics-1`, `mit-mechanics`,
`openstax-calculus-1`, and `mit-multivariable`. Inspect the relevant chapter or
lecture. Use topic-specific university courses, open texts, or primary papers
for thermodynamics, E&M, optics, relativity, quantum physics, experiments, and
computational physics.
