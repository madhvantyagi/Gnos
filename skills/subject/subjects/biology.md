# Biology subject map

Teacher: `teachers/biology/SOUL.md` (Leena Rao).

Use this file after routing a learner to biology. Select the smallest biological
scale that can answer the question, then make any cross-scale move explicit.
“Why does this treatment work?” may need molecular binding, cell signaling,
physiology, and evidence about organisms; do not flatten those into one story.

## Entry routes and prerequisites

| Route | Inspect first | First observable outcome |
| --- | --- | --- |
| Cell structure and transport | atoms, polarity, concentration, energy | Label a membrane and predict one blocked transport step |
| Molecular biology / biochemistry | bonds, reactions, molecular shape | Trace matter or information through one mechanism |
| Genetics and genomics | meiosis, probability, DNA/RNA vocabulary | Interpret a cross or a small sequence comparison |
| Physiology | cells, transport, feedback, basic graphs | Perturb one variable and predict compensation |
| Evolution | variation, inheritance, reproduction, time | Explain a frequency change across generations |
| Ecology | populations, sampling, energy, time series | Bound a food web or population model and test it |
| Development and cell differentiation | gene regulation, signaling, time | Link a signal to a changed cell state |
| Microbiology and host interaction | cell structure, growth, transmission, sampling | Distinguish exposure, infection, growth, and disease |
| Experimental / quantitative biology | controls, units, uncertainty, statistics | Design a discriminating experiment with a measurable outcome |

If polarity, pH, logarithms, or probability blocks the lesson, give a short
chemistry or `math.*` bridge. If chemistry becomes the actual destination,
route a named supporting module and say that GNOS has no chemistry teacher
listed in the subject router. CS can support sequence analysis or data work;
it does not replace biological interpretation.

## Branch guidance

**Cell biology.** Start with compartments, barriers, gradients, and energy
coupling. Keep “the cell wants” out of explanations: ask which molecules can
cross, what changes concentration, and where ATP or a gradient is spent. A good
check changes membrane permeability or an ion concentration and asks for the
local consequence before the whole-cell consequence. Use OpenStax Biology 2e
(`openstax-biology-2e`, introductory; landing page verified, chapter content
not inspected) for a broad route. NCBI Bookshelf's *Molecular Biology of the
Cell* is a free, searchable higher-level reference at
https://www.ncbi.nlm.nih.gov/books/NBK21054/; the current access page exposed
the contents, but individual chapters may be searchable rather than browsable.

**Molecular biology and biochemistry.** Separate substrate, enzyme, product,
energy, and regulation. Track atoms and electrons separately from genetic
information. For transcription and translation, ask what is copied, what is
read, and what is assembled; do not treat DNA as a literal blueprint. A useful
mini-lesson compares an enzyme inhibitor with a substrate shortage and predicts
which measured quantities change. For a deep mechanism, pair a reviewed source
with the primary paper or method that established the claim; a textbook diagram
is a model, not direct evidence.

**Genetics and genomics.** Make the inheritance assumptions visible: ploidy,
random segregation, linkage, penetrance, population, and environment. Repair
“dominant means common” and “one gene means one trait” by changing allele
frequency or adding a second locus. Begin with a small cross, then compare it
with a pedigree or a short sequence alignment. NCBI SRA at
https://www.ncbi.nlm.nih.gov/sra/ is an accessible official raw-read archive
for advanced data work; its landing page and documentation links resolved, but
an archive record still needs metadata, quality checks, and a stated analysis
pipeline before it can support a biological conclusion.

**Physiology.** Define the regulated variable, sensor, controller, effector,
and time scale. Distinguish negative feedback from “the body keeps everything
constant”; a response can overshoot, trade against another variable, or fail.
Use a perturbation such as exercise, dehydration, or a blocked receptor, then
ask which observation would distinguish neural, hormonal, and local control.
Never infer a human clinical recommendation from an illustrative pathway.

**Evolution.** Put variation, heritability, differential reproduction, and
generations in the same causal chain. “Need causes adaptation” is a repair
target: need may change selection, but it does not manufacture a directed
variant. Compare natural selection, drift, gene flow, and mutation in a tiny
population model. A claim about a particular lineage needs a dated dataset or
primary study; the broad OpenStax route is not evidence for every evolutionary
specialty.

**Ecology.** State the boundary, units, sampling frame, and time horizon before
drawing a food web or growth curve. Separate energy flow from matter cycling,
and correlation from interaction. A changed case might add a predator, remove a
resource, or alter detection probability; the learner should predict what the
measured series would do and what it cannot tell us. Use a real dataset only
after identifying its sampling and missingness; a generated curve is a model
illustration.

**Development, microbiology, and experimental biology.** Treat cell state as a
history of signals and regulation, not a permanent “cell type switch.” In
microbiology distinguish culture growth from abundance in a host and from
pathogenic effect. For any experiment, name the independent variable, outcome,
control, randomization or blocking choice, measurement error, and stopping
rule. Ask for a competing hypothesis and the result that would change the
learner's mind.

## Course design, evidence, and repair

Translate a broad goal into an action: predict a perturbation, interpret a
figure, compare mechanisms, design a controlled experiment, or argue from a
primary result. Order modules by dependency rather than by textbook chapter;
insert a five-minute bridge when the first real task exposes a gap in chemistry,
graphs, or probability. Before fixing a sustained sequence, use
`skills/course-design/references/course-research.md` to check scope,
prerequisites, source fit, and assessment. Keep one main source per module and
record the exact chapter or dataset only after inspecting it.

Evidence of biology learning is an independent prediction in a changed case,
an accurate labeled diagram, a justified interpretation of data, or a design
whose controls fit the claim. Exposure to a pathway and assisted recall are
not mastery. Record corrected misconceptions and delayed recall separately;
never invent a learner's response to fill a course record. If the learner says
“I know the steps,” test one local perturbation before adding more vocabulary.

## Representations and media

Start with the biological scale, named structures, and the measured outcome.
Use labeled images for anatomy, cells, molecules, organisms, and experimental
setups; state what is observed, reconstructed, or illustrative. Use diagrams
for compartments, pathways, inheritance, food webs, and feedback. Label
direction, scale, concentration, and time. Use animation for diffusion,
transport, signaling, development, action-potential propagation, population
change, or feedback under a changed condition. Use a simulation when the
learner should vary permeability, binding, genotype, population size, or a
sampling rule. Show original and changed states and check a limiting case. A
PDF is useful for a source-backed mechanism sheet or figure-analysis packet;
do not make a decorative pathway atlas.

## Teacher selection and handoffs

Leena remains the lead for mechanisms, levels of organization, perturbations,
and biological evidence. Hand to math when probability, rates, uncertainty, or
statistical inference is the actual bottleneck; hand to CS for reproducible
sequence or dataset operations. A physics bridge may own diffusion, forces, or
energy only for the named mechanism. The supporting teacher supplies one
bounded explanation, then Leena resumes with the biological variable and claim.
Carry the learner's last sound step, notation, and unresolved misconception
across every handoff.

## Source discipline

Existing catalog entries are starting points, not proof of coverage. Refresh
the relevant content before teaching, label access limits, and distinguish a
review, textbook model, database record, and primary experiment. For a specialty
not listed here, search PubMed or NCBI Bookshelf for the field's review and then
the cited primary study; do not imply that OpenStax Biology 2e covers advanced
immunology, structural biology, ecology, or genomics in sufficient depth.
