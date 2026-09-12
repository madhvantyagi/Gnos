# Research ledger · From slope to a working optimizer

Checked 2026-09-12. This is an example course, not a record of a real learner.

| Chapters | Source | Verified | Decision |
| --- | --- | --- | --- |
| 1 | [OpenStax Calculus 1](https://openstax.org/details/books/calculus-volume-1) | Publisher landing page only | Use as a source seed; inspect the derivative section before assigning reading |
| 2–3 | [MIT 18.02SC, Unit 2](https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/pages/2.-partial-derivatives/) | Unit includes partial derivatives and a chain-rule/gradient/directional-derivative sequence | Add the vector bridge; keep advanced multivariable topics outside this short route |
| 4–6 | [MIT 6.390, §§3.1–3.2](https://introml.mit.edu/notes/gradient_descent.html) | One- and multidimensional updates, termination choices, and learning-rate cautions | Teach a small quadratic; defer stochastic and minibatch variants |
| Coding | [Python Tutorial](https://docs.python.org/3/tutorial/) | The tutorial expects prior programming knowledge | Keep basic Python as an assumption and diagnose if it fails |

The course's numerical examples and success criteria are original, hand-checked
quadratic problems. At (1,1), the gradient of x²+2y² is (2,4); a step of 0.1
gives (0.8,0.6), with loss 1.36. The y update has multiplier 1−4η, so η=0.6
diverges from nonzero y. This narrow example does not establish a convergence
guarantee for arbitrary losses.

Open questions before teaching a real learner: their scalar derivative fluency,
comfort with vectors, available time, and whether implementation is the desired
destination. The sample has no completed learner evidence.
