# Motion and models

Use motion when order, change, or a mechanism is the question. State the
governing rule, initial condition, boundary, clock, and units beside the
scene. A moving object with no stated rule can teach the wrong mechanism.

Use a relation for motion constrained by another object or path. Use
keyframes or a named sequence when the lesson depends on discrete stages.
Avoid adding many hand-placed frames for a rule that a relation or expression
can state. Keep one visual reference fixed so direction and size changes can
be judged. Pause at the moment the learner needs to predict the next state.

For mechanics, `pinepaper_physics` can give canvas objects bodies, gravity,
forces, collisions, and joints. Its force and gravity values use canvas
coordinates. Translate the lesson's physical units and sign convention
explicitly. Check a simple limiting case, such as zero force or equal and
opposite forces. Show force arrows, trajectory, and a position or velocity
trace only when each adds information. A particle animation is a model of
the chosen assumptions, not footage of an experiment.

For waves, keep propagation direction separate from local oscillation. A
snapshot in space and a trace at one location answer different questions.
Tie both to the same phase, speed, and boundary condition. For feedback or
compartment models, show the stock, flow, delay, and measured output as
separate quantities. Check that arrows and time plots use the same sign and
units.

For heat transfer or another field model, begin with the domain, boundary
temperatures or fluxes, material assumptions, and update rule. A color field
or heatmap is a display, not a thermal solver. Calculate or verify the values
with an appropriate model before mapping them to color. Keep a numeric scale
and a time or spatial profile beside the field. Test an equilibrium or
conservation case and state when the model does not apply. Do not use a
decorative fire or glow effect to stand for temperature.

Inspect playback at the start, a transition, and the end. Compare any plotted
quantity with the displayed state at the same time. If the lesson needs
narration synchronized to a rendered sequence, follow the Manim skill instead.
