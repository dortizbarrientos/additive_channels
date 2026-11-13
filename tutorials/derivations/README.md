# Follow each result from assumptions to biological meaning

**[Download the derivation companion](derivations.pdf)** · **[Find a result](RESULT_MAP.md)** · **[Find an equation](EQUATION_MAP.md)** · **[Editable LaTeX](derivations.tex)**

Why does a Gaussian population separate slope and curvature so cleanly? Why does that separation fail to determine the response to selection? What extra assumptions are needed to predict the covariance in offspring? This companion follows those questions through the calculations, then connects the resulting quantities to observations.

It expands the intermediate steps behind the analytical results, numerical examples and estimation procedures in *Additive channels in curved fitness landscapes* and its supplementary materials. Each substantial derivation names the mathematical concepts it uses, states its assumptions, shows the algebra and explains the biological interpretation. The existing [mathematics guide](../mathematics/guide.pdf) provides a gentler introduction with checkpoints; this document supplies the fuller proof and calculation reference.

## What is derived

| Chapter | Mathematical development | Biological question |
|---|---|---|
| **1. Expected reproduction and conditioning** | Conditional expectation, population reweighting, covariance selection differential, Jensen's inequality and environmental integration. | What does averaging reproduction at a breeding value describe, and which parents contribute? |
| **2. Gaussian variation and projection** | Taylor remainders, Gaussian moment contractions, linear and quadratic variances, affine normal equations, nested regression fits and non-Gaussian corrections. | What does a large linear share establish about fitness variation in this population? |
| **3. Geometry and changes in variation** | Proportional scaling, coordinate invariance, whitening, eigenvalues, Rayleigh quotients and projection angles. | How do the amount and direction of genetic variation change the description? |
| **4. Selection under an exact quadratic log mean** | Integrability, completing the square, normalisation, selected moments and the displacement-error bound, including equality cases. | When does ignoring curvature mispredict the selected-parent mean? |
| **5. Inheritance and covariance** | Genic and association covariance, the stated inheritance closure, matrix order, fixed-point existence and bounds, scalar contraction, and singular-curvature limits. | Under which inheritance assumptions can variation persist, and what converges? |
| **6. Estimation from noisy observations** | Repeated-measurement calibration, Gaussian conditioning, integrated Poisson likelihood, quadrature, predictions, bootstrap construction, model comparison and the quartic example. | How can the share be estimated while retaining uncertainty in breeding values? |
| **7. Phenotype-regression conversion** | Gaussian regression moments, selected covariance, the order of matrix products, inversion and exact versus moment-matched parameters. | When do phenotype-selection regressions identify breeding-value fitness parameters? |
| **8. Worked results** | Parameter substitutions, all four main figures, visual examples, guide checkpoints, estimation benchmarks and simulation diagnostics. | How do the reported numerical results follow from the stated models and algorithms? |

The appendices connect results to precise derivations and explain the role of the foundational references. The linked contents and equation references work within the PDF.

## Find a particular calculation

- [RESULT_MAP.md](RESULT_MAP.md) connects all **53 records** in the repository's result catalogue to their mathematical concepts, biological questions and derivation chapters. Several records refer to the same result in different resources; they are not 53 separate theorems.
- [EQUATION_MAP.md](EQUATION_MAP.md) connects the stable equation identifiers in the main account, visual appendix, mathematics guide and estimation example to the detailed derivations. Identifiers are qualified by source, because an identifier can occur in more than one document.
- [RESULTS.md](../../RESULTS.md) and [reference/result_catalog.json](../../reference/result_catalog.json) identify the numerical inputs, code, reference outputs and reproduction commands.

The proofs establish analytical statements under their stated assumptions. Reported estimates, bootstrap endpoints and simulation discrepancies are computational outputs. Chapter 8 explains their calculations and reproduction routes; agreement in numerical examples is not presented as a proof of a general result.

## Build only this companion

From the repository root:

```bash
bash tutorials/derivations/build.sh
```

Install Python 3 and TeX Live or MacTeX with pdfLaTeX, latexmk, BibTeX, the extra/science packages and Latin Modern fonts. This standalone build needs no numerical Python packages, Node.js, LibreOffice, R or SLiM. It checks the coverage maps, compiles the bibliography and cross-references, and writes `tutorials/derivations/derivations.pdf`. Temporary TeX files remain in the ignored `build/` directory. The one-trait figure used in Chapter 8 is already supplied in the repository.

To check the result and equation navigation without building a PDF:

```bash
python3 tutorials/derivations/check_coverage.py
```

To regenerate the readable maps after editing their JSON sources, add `--write`. The check verifies coverage and link targets; it does not assess mathematical correctness. The complete teaching build, `bash run_all.sh --tutorials`, also includes this companion.

## Sources and version scope

[derivations.tex](derivations.tex) assembles the [chapter sources](chapters/), [references.bib](references.bib) and [foundations.bib](foundations.bib). The [result map](result_map.json) and [equation map](equation_map.json) are machine-readable. The build does not require manuscript or editorial files.

The scientific calculations correspond to the public archive at [05c75c6](https://github.com/dortizbarrientos/additive_channels/tree/05c75c6ee4335513b217f3026bf6e43ccbd0f62b). The catalogue and expanded numerical checks used to prepare this companion are those at [c860f6a](https://github.com/dortizbarrientos/additive_channels/tree/c860f6a1373be310a59502e244effe75e0e622be). The companion adds derivations and explanation without changing the generating models or reference results.
