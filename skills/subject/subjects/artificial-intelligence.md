# Artificial intelligence

Choose the branch by the task and the claim about the system. Separate data,
objective, optimization, evaluation, and deployment. Check probability,
vector shapes, derivatives, or code only where they enter the explanation.
Keep training, validation, and test data separate. A generated example is not
an evaluation result; date benchmark claims and state their conditions.

## Ways to show the idea

Use [Excalidraw](../../lesson-design/references/excalidraw.md) for data paths and boundaries,
[Manim](../../manim-voice-animation/SKILL.md) for narrated updates or state
changes, and [Pinepaper](../../lesson-design/references/pinepaper.md) for linked diagrams.
Use plots for distributions, error, and optimization; use tables and code for
exact computations. Simulations should reveal the effect of a meaningful
choice, such as a threshold, policy, sample, or step size.

No AI teacher is assigned by default. CS supports implementation; math supports
the needed derivation; the application subject defines labels and acceptable
errors. Keep the AI explanation responsible for the model and its evidence.

## Teaching each area

Choose the matching section. Its order suggests how to build the topic; it is
not a complete syllabus. Course design uses the starting point and source
checks. Lesson design chooses the views that explain the difficult steps.
Treat the named confusion as a possibility, not a diagnosis of this learner.

### Search and planning

- **Build:** Start with a small route problem. Follow available moves before naming a
  search method. A promising heuristic does not guarantee the cheapest path.
- **Research:** Use an introductory search chapter with pseudocode and guarantee
  conditions. Check heuristic assumptions and what the cost measures.
- **Show and check:** A graph shows choices. A frontier table explains selection.
  Animate expansion when order is hard to follow. Compare costs after changing an edge.

### Knowledge and reasoning

- **Build:** Start with a few facts and one inference. Then state the rule that permits
  it. A valid inference can start from a false premise. Missing evidence is not always
  falsity.
- **Research:** Use a logic or knowledge-representation text with explicit semantics.
  Check whether the system treats missing facts as false or unknown.
- **Show and check:** An inference tree makes dependencies visible. A truth table or
  counterexample tests the rule. Code can trace a larger rule set.

### Machine learning

- **Build:** Start with a real prediction task, a simple baseline, and one mistake.
  Build toward loss and fitting. Lower training loss does not establish better
  predictions on new data.
- **Research:** Use an accessible ML chapter for the first model and loss. Inspect
  dataset documentation and evaluation procedures before using performance claims.
- **Show and check:** A small data table grounds the task. A fitted curve shows errors.
  A threshold control exposes different kinds of error. Code traces one update.

### Neural networks and optimization

- **Build:** Start with one input, prediction, and error before explaining parameter
  updates. Activations, parameters, and gradients play different roles.
- **Research:** Use a deep-learning chapter for the operation and official framework
  documentation for implementation. Inspect tensor shapes and the assumptions behind the
  update.
- **Show and check:** Use a shape diagram and one numeric forward pass. Use Manim for a
  narrated gradient path and a graph for loss or step size. Trace the same quantities in
  code and compare training with held-out errors.

### Language models and transformers

- **Build:** Start with a short token sequence and the next-token task before attention
  or generation. Training probabilities, sampling choices, and factual reliability are
  different questions.
- **Research:** Use an accessible transformer explanation, then the architecture paper
  and official model documentation. Check tokenizer, masks, objective, and evaluation
  conditions.
- **Show and check:** Use a token and shape diagram, an attention matrix, and one worked
  weighted sum. Animate the dependency or decoding order with Manim. Vary sampling in a
  small model. Explain why the displayed weights alone do not establish a causal
  explanation.

### Reinforcement learning foundations

- **Build:** Start with a choice and its later consequences. Compare episodes before
  return, policy, and value. One successful episode does not establish a good policy.
  Immediate reward differs from return.
- **Research:** Use an introductory RL text or course section that develops episodes and
  decision rules. Bring in probability when comparing uncertain outcomes, with an
  inspected explanation of expectation.
- **Show and check:** Use an episode trace, state diagram, and reward table for the same
  case. Simulate choices before deriving expected return. Later, connect a Bellman term
  to its branch in the diagram and show what is being averaged.

### Policy optimization and language-model post-training

- **Build:** Start with a policy that generates choices, then how evaluated outcomes
  change its parameters. A reward, value baseline, advantage estimate, and probability
  ratio are different quantities.
- **Research:** Read the relevant policy-gradient derivation before PPO or GRPO. Inspect
  each original method paper and implementation for objectives, sampling, normalization,
  and differences from earlier methods.
- **Show and check:** Work through a small batch in a table before the objective. Use
  graphs for clipping or reward sensitivity, code for one update, and motion for
  sampling-to-update flow. State which parts are a simplified teaching example.

### Agents and robotics

- **Build:** Start with a task, an observation, an action, and feedback from the
  environment. A planned action may not execute. A plausible tool response may not
  establish success.
- **Research:** Inspect tool or robot interface documentation and the evaluation
  protocol. Use original results for claims about reliability or physical performance.
- **Show and check:** A sequence diagram separates observation and action. A real or
  labeled toy trace exposes failure. A simulation varies delays or failed actions.
  Compare recovery policies.

## Source use

Use [the source-use guide](../references/source-use.md). Catalog entries are
leads; inspect the relevant section before using it. Match the source to the
subfield and question. Start with an accessible explanation, then inspect the
technical argument or evidence needed for the agreed depth. Record the section,
its job, and any access limit in the course research notes.
