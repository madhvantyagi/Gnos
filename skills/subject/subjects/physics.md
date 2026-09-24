# Physics

Teacher: `teachers/physics/SOUL.md` (Mira Sen).

Choose the branch by the physical question. Name the system, frame, quantities,
and approximation before calculating. Develop a qualitative prediction, then
check units, sign, and a limiting case. Distinguish a model prediction from a
measurement and state when the approximation fails.

## Ways to show the idea

Use diagrams for setup, graphs for quantities, and equations for their relation.
Use [Excalidraw](../../excalidraw/SKILL.md) for boundaries or apparatus,
[Manim](../../manim-voice-animation/SKILL.md) for narrated motion, and
[Pinepaper](../../pinepaper/SKILL.md) for linked visual states. A simulation
lets the learner test a changed condition. Keep the same units and initial
state across views. Generated motion is a model illustration.

Read [the physics reference](../references/physics.md) for detailed examples
and visual conventions. Mira owns the physical meaning; math and CS support
only the calculation or implementation needed for this question.

## Teaching each area

Choose the matching section. Its order suggests how to build the topic; it is
not a complete syllabus. Course design uses the starting point and source
checks. Lesson design chooses the views that explain the difficult steps.
Treat the named confusion as a possibility, not a diagnosis of this learner.

### Mechanics

- **Build:** Start with an object, its interactions, and a prediction before equations.
  Velocity and acceleration can point differently. Force is not needed to maintain
  constant velocity.
- **Research:** Use an introductory mechanics chapter with a worked force or energy
  argument. Check the frame and approximations before adopting a formula.
- **Show and check:** Draw the fixed free-body diagram with Excalidraw. Use
  Pinepaper when position, velocity, and moving body must share one clock.
  Label the force rule and units. Test mass, force, or initial velocity against
  a limiting case.

### Oscillations and waves

- **Build:** Start with one oscillator, then coupled locations. A wave transports a
  disturbance without carrying each particle along its full path.
- **Research:** Inspect a waves chapter for the relation between the oscillator and
  propagation. Check the boundary conditions and whether the model is dispersive.
- **Show and check:** Pair a spatial snapshot with a time trace at one marked
  point. Use Pinepaper when motion must keep phase aligned across both views.
  Separate local oscillation from propagation. Change frequency or boundary
  conditions and explain the result.

### Thermodynamics

- **Build:** Start with a bounded system and an energy transfer before naming the law.
  Heat and work describe transfers. Temperature is not stored heat.
- **Research:** Use a thermodynamics chapter and any needed property table. Check sign
  conventions, process assumptions, and the range of the data.
- **Show and check:** An Excalidraw boundary diagram names heat and work
  transfers. An energy ledger checks the balance. Use Pinepaper for a state
  path or temperature profile that changes with the same stated process.
  Compare two paths with the same endpoints.

### Electricity and magnetism

- **Build:** Start with sources and a test charge or simple circuit before a field
  formula. Field, force, potential, and potential energy are different quantities.
- **Research:** Use an electromagnetism or circuits chapter that defines the quantities.
  Inspect apparatus documentation when interpreting a real measurement.
- **Show and check:** A field map shows directions. Equipotentials explain work. A
  circuit diagram tracks connections. A simulation compares charge, geometry, or
  resistance.

### Optics

- **Build:** Start with a light source, an obstacle, a scale, and an observation. A ray
  model and a wave model explain different features of the setup.
- **Research:** Choose a geometrical- or wave-optics source to match the scale. Inspect
  the approximation before applying a ray or diffraction formula.
- **Show and check:** A ray diagram locates an image. Wavefront motion explains
  interference. An intensity plot connects to observations. Controls test aperture or
  wavelength.

### Relativity

- **Build:** Start with two observers describing the same events and measurements. A
  coordinate difference need not be a difference in an invariant quantity.
- **Research:** Use a relativity text that defines clocks, synchronization, frames, and
  the transformation. Check the physical assumptions before using a diagram.
- **Show and check:** Use a spacetime diagram with labeled events. Work through one
  transformation. Use Manim to coordinate observers when sequence matters. Compare an
  invariant across both descriptions.

### Quantum physics

- **Build:** Start with a preparation, a measurement, and the distribution of possible
  outcomes. An amplitude is not a probability, and a state is not a hidden classical
  trajectory.
- **Research:** Use a quantum text for the state, observable, and probability rule.
  Inspect the original experimental setup when explaining an empirical result.
- **Show and check:** Pair an apparatus diagram with an outcome distribution and a
  worked amplitude calculation. Simulate repeated measurements under stated assumptions.
  Distinguish this teaching model from measured evidence.

### Experimental physics

- **Build:** Start with a measurement question and an instrument reading. A fitted line
  can hide bias. Precision does not establish accuracy.
- **Research:** Inspect the instrument manual, calibration method, and original
  measurements. Use a laboratory-methods source to assess uncertainty and fit quality.
- **Show and check:** An apparatus diagram explains measurement. Data with uncertainty
  and residual plots test the fit. Compare calibration or sampling choices.

### Computational physics

- **Build:** Start with a simple physical rule and a finite numerical step. A smooth
  computed trajectory can still be unstable or physically wrong.
- **Research:** Use a numerical-methods source plus a known analytic or limiting case.
  Check discretization, solver tolerances, and conservation error.
- **Show and check:** A step table connects the rule to code. A plot compares
  analytic and numerical results. Use Pinepaper only when the computed state
  and plot must move together. Vary the time step and inspect conservation error.

## Source use

Use [the source-use guide](../references/source-use.md). Catalog entries are
leads; inspect the relevant section before using it. Match the source to the
subfield and question. Start with an accessible explanation, then inspect the
technical argument or evidence needed for the agreed depth. Record the section,
its job, and any access limit in the course research notes.
