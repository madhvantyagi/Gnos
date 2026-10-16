# Biology

Teacher: `teachers/biology/SOUL.md` (Leena Rao).

Choose the biological scale needed to answer the question. Name each move
between molecules, cells, tissues, organisms, and populations. Explain a
mechanism through causes and constraints; avoid saying that a cell or organism
changes because it wants or needs to. A diagram of a mechanism and the evidence
that established it have different jobs.

## Ways to show the idea

Use labeled images for anatomy and observed structure, diagrams for pathways,
and plots for concentrations or populations. State whether an image is
observed, reconstructed, or illustrative. Use the host's image-generation
capability for illustrations, [Excalidraw](../../excalidraw/SKILL.md) for
fixed compartments and flows, [Pinepaper](../../pinepaper/SKILL.md) when a
mechanism needs a composed scene. Use [JSXGraph](../../jsxgraph/SKILL.md)
to inspect a population or concentration model, scientific plots for measured
data and uncertainty, and
[Manim](../../manim-voice-animation/SKILL.md) for narrated transport. A simulation tests a named perturbation.
Label direction, scale, units, and time; distinguish model outputs from data.

Leena owns mechanisms and biological interpretation. Bridge to chemistry for
bonds or reactions, math for quantitative reasoning, and CS for reproducible
analysis. An illustrative pathway does not establish a clinical recommendation.
There is no standalone chemistry guide in this harness. For a chemical
bottleneck, inspect the relevant chemistry source and explain that bounded
step here; do not invent a `chemistry` subject route or substitute chemical
engineering merely because its name includes chemistry.

## Teaching each area

Choose the matching section. Its order suggests how to build the topic; it is
not a complete syllabus. Course design uses the starting point and source
checks. Lesson design chooses the views that explain the difficult steps.
Treat the named confusion as a possibility, not a diagnosis of this learner.

### Cell structure and transport

- **Build:** Begin with a neutral solute in two compartments separated by
  a permeable membrane. Specify volumes and what can cross. Distinguish
  movement in each direction from net transport; equilibrium does not mean
  molecular motion stops. Add electrical forces when moving to charged solutes.
- **Research:** Use a cell-biology chapter for membrane mechanisms and a primary
  experiment for a specific transport claim. Check compartments and concentration
  conditions.
- **Show and check:** Map particles or amounts in each compartment to its
  concentration curve, including volume. Show opposing flows separately
  from their net difference; use one clock if both views move. Change
  permeability and ask about equilibration time, then change compartment
  volume and ask about the final concentrations under the same passive
  transport assumptions. Check conservation of the tracked solute.

### Molecular biology / biochemistry

- **Build:** Use an enzyme-catalyzed reaction with named substrate, product,
  and enzyme. Track matter and energy separately from reaction speed.
  Enzymes change rates, not the reaction's equilibrium or net free-energy
  change; state any coupled energy source explicitly.
- **Research:** Use a biochemistry reference for reaction mechanism and an original
  assay for measured rates. Track substrate, enzyme, energy, and experimental conditions
  separately.
- **Show and check:** Connect binding and catalytic steps in the mechanism
  to the species counted in the assay and axes of the rate plot. Distinguish
  an initial-rate curve from a product-versus-time trace. Change substrate
  or enzyme amount and predict the response under the stated kinetic model;
  compare an inhibitor separately. Do not use illustrative binding motion
  as evidence for a measured rate or mechanism.

### Genetics and genomics

- **Build:** Follow one diploid inheritance case from parental alleles to
  gametes and offspring under explicit segregation assumptions. Separate
  genotype from phenotype and dominance from population frequency. A cross
  ratio predicts probabilities, not exact counts in a small family.
- **Research:** Use a genetics chapter for inheritance assumptions. For sequence
  evidence, inspect the reference assembly, sample metadata, and analysis method.
- **Show and check:** Carry allele labels from homologous chromosomes into
  gamete probabilities, cross-table cells, and phenotype predictions. Change
  one parental genotype and ask for the new distribution before simulating
  small families. For genomics, match a sequence coordinate and variant to
  the reference assembly and evidence track; a detected variant alone does
  not establish its functional effect.

### Physiology

- **Build:** Use a regulated temperature or concentration, one disturbance,
  and a named sensor and effector. Explain the physical or biochemical link
  that closes the loop. Negative feedback permits variation and delay; it
  does not hold a quantity perfectly constant.
- **Research:** Use a physiology chapter for the feedback mechanism and original
  perturbation data for its response. Check species, tissue, and time scale.
- **Show and check:** Match each feedback arrow to a specific causal step
  and connect the regulated quantity and effector response to separate time
  traces for the same perturbation. Mark stimulus time, delay, and recovery.
  Block the effector or slow the sensor and ask which trace changes first;
  compare the prediction with perturbation evidence rather than assuming
  every correlated response is part of the loop.

### Evolution

- **Build:** Follow a heritable variant through reproduction in a small
  population. State how survival or reproduction differs, if at all.
  Separate a change in one organism from a frequency change across
  generations; variants do not arise because organisms need them.
- **Research:** Use an evolution text for mechanisms and a population study for a
  lineage claim. Check inheritance, sampling, generation time, and alternative
  explanations.
- **Show and check:** Match offspring in the lineage diagram to counts and
  allele frequencies in each generation's table. Plot repeated populations
  under the same model to compare drift with a stated selection effect.
  Change population size or reproductive advantage and ask how variation
  among runs and their expected trend differ. For a real lineage, use
  sourced observations to assess competing mechanisms.

### Ecology

- **Build:** Use a resource-consumer interaction in a defined place and
  sampling period. Separate observed counts from true abundance and a
  feeding relation from a complete prediction of population response.
  Name the measurement and ecological assumptions before modeling.
- **Research:** Inspect the field study and dataset methods alongside an ecology
  chapter. Check spatial boundaries, detection probability, and sampling intervals.
- **Show and check:** Match the species and interaction arrows in the web
  to variables and terms in a stated population model, then compare its
  traces with observation dates and units. Change a resource or predator
  and predict the response under that model. Change detection probability
  separately and ask how an apparent count trend could arise without the
  same change in abundance.

### Development and cell differentiation

- **Build:** Compare cells receiving the same signal at two developmental
  stages. Name their prior state, lineage, and measured response. Cell
  identity reflects regulation and history; signal presence alone does not
  determine every cell's fate.
- **Research:** Use a developmental-biology reference and a time-resolved or
  perturbation study. Check lineage, stage, and what establishes the signal-response
  link.
- **Show and check:** Carry cell or lineage labels from the ancestry diagram
  into the signaling sequence and time-course measurements. Distinguish
  ancestry, marker expression, and demonstrated fate. Block the signal at
  an early versus late stage and ask which outcome tests induction or
  maintenance. Identify the perturbation evidence needed to support the
  proposed causal link.

### Microbiology and host interaction

- **Build:** Follow a defined microbe-host case from exposure through
  establishment, growth, and host response. Separate an assay detecting
  microbial material from viable growth, infection, or disease causation.
  State strain, host, and conditions before interpreting the result.
- **Research:** Use a microbiology reference and the original assay or host study. Check
  strain, growth conditions, measurement, and whether the result concerns infection or
  disease.
- **Show and check:** Match a labeled observed image to its assay and scale,
  then place sampling times and microbial and host measurements on the same
  timeline. Explain what a growth curve measures rather than treating all
  signals as cell counts. Change a growth condition or control and ask
  which interpretation remains supported; label illustrative mechanisms
  separately from observed evidence.

### Experimental / quantitative biology

- **Build:** Use two competing explanations for a treatment response and
  propose an observation that separates them. Name the experimental unit,
  comparison, and measurement. A control does not remove every confound,
  and repeated measurements of one unit are not independent biological units.
- **Research:** Inspect the experimental protocol, controls, data, and analysis. Use the
  methods source to determine which competing explanation each control can exclude.
- **Show and check:** Match each group and sample ID in the design diagram
  to its data points and the control table's excluded explanation. Show
  variation among biological units separately from repeated measurements.
  Change a control, batch assignment, or sampling unit and ask which causal
  comparison or uncertainty calculation remains justified. A reviewed
  handout may collect these views without introducing a new inference.

## Source use

Use [the source-use guide](../references/source-use.md). Catalog entries are
leads; inspect the relevant section before using it. Match the source to the
subfield and question. Start with an accessible explanation, then inspect the
technical argument or evidence needed for the agreed depth. Record the section,
its job, and any access limit in the course research notes.
