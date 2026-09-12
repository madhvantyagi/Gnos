# Research ledger · From slope to a working optimizer

Checked 2026-09-12. This is a planning example, not evidence about a real
learner. Its course file keeps one current topic and leaves later chapters
provisional until conversation and attempts justify the route.

| Course route | Source | What was checked | Planning decision |
| --- | --- | --- | --- |
| `local-change` → `local-change` | [OpenStax Calculus 1](https://openstax.org/details/books/calculus-volume-1) | Publisher landing page and catalog only | Use as a source seed for the ready introductory lesson; inspect the exact derivative section before assigning it as reading |
| `multivariable-change` → `directional-change`, `gradient` | [MIT 18.02SC, Unit 2](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/2.-partial-derivatives/) | The official unit places chain rule, gradient, and directional derivatives in one sequence | Preserve a vector-and-dot-product bridge before treating the gradient as a descent direction; keep the chapter provisional |
| `optimizer-loop` → `update-rule`, `step-size`, `optimizer-diagnostics` | [MIT 6.390, §§3.1–3.2](https://introml.mit.edu/notes/gradient_descent.html) | Official notes cover one- and multidimensional updates, termination choices, and learning-rate cautions | Move from one hand-traced update to implementation and diagnosis; omit stochastic and minibatch variants from this goal |
| `optimizer-loop` implementation | [Python Tutorial](https://docs.python.org/3/tutorial/) | Official tutorial material for functions and control flow; it assumes prior programming | Treat basic Python as an assumption and diagnose it in chat if implementation work exposes a gap |

Only `slope-introduction` is authored and ready. Its explanation, equation,
worked comparison, source note, and numeric check form one lesson composition;
the table of contents is not permission to pre-generate the remaining lessons.

The numerical examples and success criteria are original, hand-checked
quadratic problems. At (1,1), the gradient of x²+2y² is (2,4); a step of 0.1
gives (0.8,0.6), with loss 1.36. The y update has multiplier 1−4η, so η=0.6
diverges from nonzero y. That controlled example does not establish a
convergence guarantee for arbitrary losses.

Before using this route for a real learner, establish scalar derivative fluency,
comfort with vectors, available time, and whether implementation is the desired
destination. If any answer changes the dependency route, revise the provisional
topics rather than rewriting old evidence.
