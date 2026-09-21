# Artificial intelligence

## Route by task

| Area | Inspect first | Teaching decision |
| --- | --- | --- |
| Search and planning | States, actions, costs, heuristics | Trace a search and inspect completeness and cost |
| Knowledge and reasoning | Logic, representation, uncertainty | State inference rules and test a counterexample |
| Machine learning | Vectors, probability, loss | Separate data, optimization, and generalization |
| Deep learning and language models | Tensor shapes, gradients, sequences | Trace training and inference separately |
| Agents and robotics | Observations, actions, feedback | Evaluate trajectories, tool failures, and recovery |

## Prerequisites and distinctions

Check vector shapes, probability, derivatives, and programming only where the task requires them. Distinguish predictive accuracy, causal explanation, calibration, and task success. Keep training, validation, test, and deployment data separate.

## Mini lesson and evidence

Compare a classifier with a majority baseline on held-out data, then change the class balance. Ask which metric remains useful and what the comparison establishes.

Evidence of progress is an independent explanation or solution under a changed
condition, with assumptions and limitations stated. A repeated definition alone
is not evidence of transfer.

## Handoffs

Computer science owns implementation and system contracts; math supplies shared math.* concepts for optimization and probability. The application subject defines labels and acceptable errors.

## Representation profile

Start with the task, data, baseline, objective, split, and error that matters.
Use diagrams for training and inference pipelines, tensor shapes, retrieval,
tool calls, feedback, and evaluation boundaries. Use code and traces for actual
model or agent behavior. Use animation for attention flow, optimization,
search, decoding, or agent state only when intermediate states matter. Use a
simulation for threshold, sampling, class balance, reward, or policy changes.
Keep benchmark version, dataset, metric, and date in text. A generated example
is not an evaluation result.

## Source selection

Use original papers, official model or dataset documentation, and inspected textbook chapters. Recheck versions and evaluation conditions for benchmark claims; a demo is not a reliability estimate.

## What each area earns

First write what the learner must inspect, change, compare, or work out
in one sentence, and pick the smallest medium that lets them do it. Only
then check this table for what AI work usually needs. Never use the table
as a reason to order its favorite medium. Depth and length still cap the
media: a survey earns mostly text plus one medium.

| Area | Lead with | Then earn, only when | Exercise |
| --- | --- | --- | --- |
| Search and planning | States, actions, costs, and heuristics in text | Manim, only when the intermediate search states and costs are the idea | Code text: trace the search and check completeness and cost |
| Knowledge and reasoning | Inference rules stated in text | Nothing else unless a rule must be tested against a case | Code text: state the rules and test a counterexample |
| Machine learning | Data, baseline, objective, and split in text | Simulation, only when the learner varies the threshold or class balance | Numeric: compute the metric under the changed split |
| Deep learning and language models | Tensor shapes and the train/inference split in text | Pinepaper pipeline diagram, only to keep shapes and stages visible together | Code text: trace training and inference separately |
| Agents and robotics | Observations, actions, and feedback in text | Simulation, only when the learner varies the reward, policy, or tool failure | Code text: evaluate the trajectory and the recovery |
No curated source entries are supplied specifically for this subject yet.
Inspect suitable sources before assigning a sustained course; follow
[the source-use guide](../references/source-use.md).
