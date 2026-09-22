# Write mathematics without changing its meaning

Write new mathematics as LaTeX supported by the viewer's KaTeX renderer.
Use `$...$` for inline expressions and `$$...$$` for displayed expressions
inside prose. An `equation` block contains the LaTeX expression itself, without
outer delimiters. Never depend on the viewer to infer intended notation.

Introduce each symbol in the surrounding explanation. State units and relevant
assumptions before using an expression to make a prediction. Use `\text{...}`
for words inside mathematics and `\mathrm{...}` for upright units. Write a
long derivation as readable steps, using `aligned` when alignment helps.

Choose the symbol that states the operation. Multiplication may use `\cdot`
or `\times`; an optimum uses `x^*`, while a time derivative may use `\dot{x}`.
Those marks are not interchangeable. Preserve stars, punctuation within
`\text{}`, decimal points, and vector notation exactly.

For example, an optimization expression can be written as:

```latex
\min_{x\in\mathbb{R}^n} f(x)\quad\text{subject to}\quad x\in\mathcal{X},
\qquad x^*\in\operatorname*{arg\,min}_{x\in\mathcal{X}} f(x)
```

In a JSON string, escape each backslash once: `"\\frac{a}{b}"` decodes to
`\frac{a}{b}`. Use a JSON serializer when possible. Check the decoded value;
an accidental tab from `\t` or form feed from `\f` can destroy a command
before rendering begins.

Inspect the rendered lesson before publication. Check that equations parse,
superscripts and subscripts retain their meaning, units are readable, and long
expressions fit or scroll without covering adjacent text. Exercise prompts and
worked answers use the same notation rules. A successful JSON validation does
not establish that the mathematical notation rendered correctly.
