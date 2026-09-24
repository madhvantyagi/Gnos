# Chemical engineering

Choose the process boundary, basis, units, composition, and conserved quantities
before algebra. Distinguish steady state from equilibrium, and conversion from
selectivity. Supply chemistry only where bonding, reactions, or equilibrium
blocks the explanation.

## Ways to show the idea

Use [Excalidraw](../../excalidraw/SKILL.md) for fixed streams and control volumes,
[Pinepaper](../../pinepaper/SKILL.md) when a process state and its graph must
change together, and property tables for exact values.
Use [Manim](../../manim-voice-animation/SKILL.md) for narrated transient change
and a simulation to test flow, temperature, residence time, or controller
settings. Match stream names and units across the picture and balance.
Keep property ranges, assumptions, and physical limits visible. A teaching
simulation does not validate equipment or an operating procedure.

Chemical engineering owns process assumptions and feasibility. Math, physics,
and CS support the needed equation, mechanism, or implementation. No chemical
engineering teacher is assigned by default.

## Teaching each area

Choose the matching section. Its order suggests how to build the topic; it is
not a complete syllabus. Course design uses the starting point and source
checks. Lesson design chooses the views that explain the difficult steps.
Treat the named confusion as a possibility, not a diagnosis of this learner.

### Material and energy balances

- **Build:** Start with a chosen boundary and named streams on a stated basis. Steady
  state does not mean no flow or no reaction.
- **Research:** Use an engineering balances chapter and a stated process case. Check
  units, basis, composition, and which quantities are conserved.
- **Show and check:** Draw streams and a control volume in Excalidraw. A balance
  table tracks each term. Use Pinepaper if varying an inlet must update the
  accumulation and outlet trace together. Check the worked equation against
  the boundary and a steady case.

### Thermodynamics

- **Build:** Start with a material, its state, and the proposed change. Equilibrium,
  steady state, and a chosen process path are different conditions.
- **Research:** Use thermodynamic property references and the relevant model
  documentation. Check phase, composition, reference state, and validity range.
- **Show and check:** A phase diagram shows allowed states. A property table
  supplies values and ranges. Use Pinepaper for a changing process path only
  when its point, phase label, and energy calculation share the same state.

### Transport phenomena

- **Build:** Start with a gradient across a small region and the resulting flux. A flux
  law alone does not specify the boundary or initial conditions.
- **Research:** Use a transport text for constitutive laws and boundary conditions.
  Inspect measured property data before assigning numerical values.
- **Show and check:** Pair a spatial profile with flux arrows. Use Pinepaper
  for a transient temperature or concentration field only after stating the
  boundary conditions and update rule. Keep a numeric scale and matching
  profile. Compare a steady or conservation case.

### Reaction engineering

- **Build:** Start with a reaction in a defined volume and the time material spends
  there. Conversion, selectivity, and reaction rate answer different questions.
- **Research:** Use a reaction-engineering chapter plus measured kinetic data for the
  stated reaction. Check rate units, temperature range, and mixing assumptions.
- **Show and check:** A reactor sketch shows mixing assumptions. A concentration
  trace shows progress. Use Pinepaper if changing residence time or
  temperature must update both the reactor state and trace. Check the result
  with a balance.

### Separations

- **Build:** Start with a mixture, a target composition, and a physical basis for
  separation. Equilibrium feasibility does not establish how fast separation occurs.
- **Research:** Use a separations text with equilibrium and mass-transfer data. Check
  composition range, stage assumptions, and the definition of the target purity.
- **Show and check:** A phase plot shows the limit. A stage diagram tracks composition.
  A worked balance connects stages. Vary a rate or operating condition.

### Process design and control

- **Build:** Start with a process at a stated condition and one disturbance. A
  controller can correct one variable while reaching another constraint.
- **Research:** Use process-dynamics and control references with stated equipment
  limits. Teaching models do not establish safe operating procedures.
- **Show and check:** A flowsheet locates feedback. Time plots show response and delay.
  A simulation tests settings. Mark physical constraints and distinguish a teaching
  model from equipment validation.

## Source use

Use [the source-use guide](../references/source-use.md). Catalog entries are
leads; inspect the relevant section before using it. Match the source to the
subfield and question. Start with an accessible explanation, then inspect the
technical argument or evidence needed for the agreed depth. Record the section,
its job, and any access limit in the course research notes.
