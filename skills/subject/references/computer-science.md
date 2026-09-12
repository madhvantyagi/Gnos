# Computer science

Teacher: `teachers/computer-science/SOUL.md` (Theo Park).

| Subfield | Prerequisites to inspect | Productive representation / check |
| --- | --- | --- |
| Programming | State, expressions, control flow | Small execution trace; predict before running |
| Algorithms / data structures | Invariants, recursion, discrete math | Trace plus correctness argument and cost model |
| Systems / architecture | Memory, representation, concurrency | Follow data across a concrete boundary |
| Networks / distributed systems | Processes, messages, failures | Timeline; distinguish delay from failure |
| Databases | Sets, queries, consistency | Example data; transactions and failure cases |
| Theory / languages | Logic, proofs, automata | Formal rule beside a minimal accepted/rejected example |
| AI / machine learning | Linear algebra, probability, calculus | Shapes, objective, data split, baseline, evaluation |
| Software engineering / security | Contracts, testing, system boundaries | Reproduce a failure and verify a bounded repair |

Resource seeds: `cs50` for introductory programming/CS; `python-tutorial` for
programmers learning Python (not a novice's complete first course);
`mit-algorithms` for algorithms and analysis. Read installed-version official
documentation for libraries and research papers for model-specific claims.

Bridges: math supplies shared concepts; application subjects define what counts
as a useful answer. Distinguish a toy implementation from a production design.

Media: animate pointer movement or state transitions when a static trace loses
the order. Prefer runnable code plus a trace for debugging. Keep visual nodes
linked to actual state; do not move arrows independently of the algorithm.
