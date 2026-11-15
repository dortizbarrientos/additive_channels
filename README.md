# Additive channels

Code, simulated data and explanations for **[Additive Channels in Curved Fitness Landscapes](https://doi.org/10.64898/2026.03.21.713332)** by Daniel Ortiz-Barrientos and Mark Cooper.

## Read the argument

1. **[From fitness variation to selection](tutorials/companion/companion.pdf)** explains the choices behind the calculations. It asks what each model describes, why a particular mathematical approach helps, and which biological assumptions are needed for the next result.
2. **[Supplementary File 1: mathematics guide](tutorials/mathematics/guide.pdf)** supplies the worked calculations. The short companion points to the relevant sections, so it is possible to follow one question without reading the whole guide.
3. **[Supplementary File 3: worked estimation](examples/estimating_variance_share/worked_example.pdf)** develops the observation model, parameter estimates and uncertainty for a simulated example. Use it when moving from the theoretical quantities to data.

The short companion is additional exposition by Daniel Ortiz-Barrientos for this repository. The numbered supplementary files accompany the paper.

If you prefer to work with adjustable examples, use the **[interactive study guide](tutorials/interactive/README.md)**. Its six lessons follow the argument through figures, calculations and exercises. The **[teaching collection](tutorials/README.md)** also contains introductory notes, a worksheet, slides, the geometry and parental-contribution explorers, and editable figures. Each can be used on its own.

For changes between preprint versions, see **[Reading versions 2 and 3](docs/VERSION_GUIDE.md)**. It identifies the current claims and the earlier material that remains useful.

## Reproduce the results

With Python 3.11 or newer and Bash installed, run this command from the repository directory:

```bash
bash run_all.sh
```

The first run installs missing Python dependencies if needed. The command regenerates the four main figures, checks the mathematical calculations, summarises the archived SLiM diagnostics and reproduces the worked estimation example, including 500 bootstrap refits. New results are written to `outputs/` and compared with the supplied reference records.

For a shorter run that skips the estimation example, use `bash run_all.sh --quick`.

The **[reproduction instructions](REPRODUCING.md)** give the dependencies, commands and expected outputs. The **[result catalogue](RESULTS.md)** connects each paper result to its source, inputs and numerical check.

## Find the files

| Purpose | Location |
|---|---|
| Main figures and mathematical checks | [code/](code/) |
| Reference values and result catalogue | [reference/](reference/) |
| Population simulations and archived diagnostics | [slim/](slim/) |
| Estimation data, analysis, tests and optional local app | [examples/estimating_variance_share/](examples/estimating_variance_share/) |
| Short companion, interactive guide, teaching materials and Appendix S7 figure sources | [tutorials/](tutorials/README.md) |

All supplied observations are simulated or generated from specified mathematical populations.

## Cite the paper

> Ortiz-Barrientos, D. and Cooper, M. (2026). *Additive Channels in Curved Fitness Landscapes*. bioRxiv. https://doi.org/10.64898/2026.03.21.713332

For a calculation, also record the exact repository release or commit used. The paper is the preferred citation in [CITATION.cff](CITATION.cff); a comparison with a particular preprint revision should identify that revision. Code and documentation use the [MIT licence](LICENSE).
