# From fitness variation to selection

Read [the short companion](companion.pdf) before the calculations in [Supplementary File 1](../mathematics/guide.pdf), or use its section references to follow one part of the argument.

The companion explains five choices: defining conditional expected fitness; using a quadratic curve and a population regression; comparing proportional changes in covariance; calculating selection through reproductive weights; and adding an inheritance model for offspring. Established mathematical results are cited, with the steps needed to connect them to the paper shown in the text.

This is additional exposition by Daniel Ortiz-Barrientos. The scientific source is the paper by Daniel Ortiz-Barrientos and Mark Cooper, [Additive Channels in Curved Fitness Landscapes](https://doi.org/10.64898/2026.03.21.713332). The companion is separate from the numbered supplementary files.

## Rebuild the PDF

Install TeX Live or MacTeX with latexmk, BibTeX, Latin Modern fonts and the packages named in `companion.tex`. Then, from the repository root, run:

```bash
bash tutorials/companion/build.sh
```

The text is maintained in `companion_body.tex`, with references in `references.bib`. `companion.tex` supplies the layout. The build writes temporary files to `build/` and replaces `companion.pdf`.
