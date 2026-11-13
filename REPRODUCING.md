# Reproduce a result

Start with the question or result you want to check. The [complete result catalog](RESULTS.md) maps the four main figures, mathematical results, Appendices S1–S7, the mathematics guide and the worked estimation example to their sources and outputs. Its [machine-readable version](reference/result_catalog.json) records the same coverage.

## 1. Run the numerical reproduction

From the repository root:

```bash
bash run_all.sh
```

The launcher uses Python 3.11 or newer. It uses an installed compatible numerical environment when available, or creates `.venv/` and installs the dependencies. The first installation requires internet access. For the package versions used in the reference calculation:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -c requirements-tested.txt
PYTHON_BIN=.venv/bin/python bash run_all.sh
```

New numerical results go to `outputs/`. The saved observations, bootstrap draws and reference records remain available for comparison.

| Output | What it contains |
|---|---|
| `outputs/figures/` | Four main figures, in PDF and PNG formats. |
| `outputs/figure_results.json` | Parameters and numerical values for each figure panel. |
| `outputs/mathematics_checks.json` | Coordinate invariance, covariance scaling, selected-parent displacement and scalar fixed-point checks. |
| `outputs/result_checks.json` | Additional independent calculations for the mathematical results and supplementary examples. |
| `outputs/simulation_summary.json` | Summary of 4,000 replicate-generation rows from the 20 archived SLiM tables. |
| `outputs/estimation/` | Simulated observations, fitted models, all 500 bootstrap refits, interval estimates, tables and diagnostic figures. |

For a shorter run, use `bash run_all.sh --quick`. It performs the figure, mathematical and archived-diagnostic calculations and skips the 500 bootstrap refits. To run only the estimation example, use `bash run_estimation.sh`.

## 2. Compare the numbers

The launcher checks the regenerated values against the supplied records. These landmarks help you interpret a successful run:

| Calculation | Reference result |
|---|---|
| Gaussian projection experiment, Figure 2 | 360 parameter combinations, with 20,000 breeding-value vectors each; median absolute sample discrepancy approximately 0.00236726. |
| Covariance comparison, Figure 3 | Covariance changes from G to 0.11G; the linear share changes from 0.603954 to 0.932720. Both absolute variance components decrease. |
| Fixed-baseline scalar recursion, Figure 4 | Covariance fixed point 0.4723532349; the share changes from 0.581395 to 0.921639 while the gradient is maintained. |
| Close-fit selection example | Linear share 32/33; exact selected-parent shift 4/3; shift without curvature 2, an overestimate of 50%. |
| Archived finite-population diagnostic | 4,000 rows; median absolute difference between the Gaussian share and empirical squared correlation 0.0156678857. |
| Worked estimation example | Generating share 2/3; estimated share 0.610744; 95% parametric-bootstrap interval 0.533024–0.685713. |

[reference/figures.json](reference/figures.json) supplies the main figure comparisons. The estimation reference records are in [examples/estimating_variance_share/results/](examples/estimating_variance_share/results/). The checks compare individual bootstrap draws as well as final percentiles, allowing small floating-point differences.

Numerical agreement checks a calculation for the stated cases. The general proofs and their assumptions are developed in the [mathematics guide](tutorials/mathematics/guide.pdf) and the fuller [derivation companion](tutorials/derivations/README.md); the [result catalog](RESULTS.md) identifies both derivations and numerical checks. PDF bytes are not used as a scientific comparison, because font rendering and metadata can change without changing a result.

## 3. Rebuild the visual explanations

```bash
bash run_all.sh --visuals
```

This uses the numerical Python dependencies and writes the following outputs beside their sources:

| Module | Rebuilt resources and checks |
|---|---|
| [One trait](tutorials/one_trait_visual/) | Three-population figure and exact variance components, checked by numerical integration. |
| [Two-trait geometry](tutorials/geometry/) | Rotation and projection figures, numerical records and the offline rotation explorer. Gaussian quadrature checks the analytic components and selected-parent moments. |
| [Parental contributions](tutorials/parental_weighting/) | Equal-weight, expected-output-weight and recorded-count explanations; simulated data checks and the offline explorer. |
| [Home-page visual](code/build_readme_visuals.py) | The README comparison, checked against the one-trait numerical record. |

For the numerical functions used by the estimator and app, run:

```bash
python3 -m unittest discover -s examples/estimating_variance_share -p 'test_*.py' -v
```

Use the interpreter containing the dependencies; for example, replace `python3` with `.venv/bin/python` if the launcher created that environment. The independent tests use integration and simulated data to check the model functions.

## 4. Explore or teach

The two HTML explorers are self-contained. Download and open [rotate_the_cloud.html](tutorials/geometry/rotate_the_cloud.html) or [explore_parental_cloud.html](tutorials/parental_weighting/explore_parental_cloud.html) in a browser. A GitHub file page displays the source; the downloaded file runs the app.

The estimation app runs locally with:

```bash
bash run_shiny.sh
```

The launcher installs the extra Python Shiny dependencies if needed and opens a local browser page. Set `SHINY_PORT=8001` before the command to use another port. See the [worked-example guide](examples/estimating_variance_share/README.md) for the inputs, model assumptions and interpretation of its outputs.

The teaching PDFs and editable slides are ready to use. To rebuild them:

```bash
bash run_all.sh --tutorials
```

That optional build requires TeX Live or MacTeX with pdfLaTeX, latexmk, BibTeX, the extra/science packages and recommended fonts; Node.js with npm; and LibreOffice (`soffice`). See the [teaching index](tutorials/README.md). Rebuilding the optional PowerPoint versions of the geometry and parental-weighting figures uses the export dependencies listed in their module guides.

To rebuild only the detailed derivation companion, use:

```bash
bash tutorials/derivations/build.sh
```

This needs Python 3 and the TeX dependencies, but not the slide-building tools. The [companion guide](tutorials/derivations/README.md) explains its chapter sources and result/equation maps. `python3 tutorials/derivations/check_coverage.py` checks their coverage and navigation without TeX; it is also run by continuous integration.

## 5. Run new forward-time simulations

The default reproduction aggregates the included diagnostic tables. To generate a new set of 20 replicates, install **SLiM 5.2** and run:

```bash
bash run_all.sh --simulate
```

Set `SLIM_BIN` to the executable path if `slim` is not on your PATH. The runner writes raw breeding values, optima, diagnostic tables and comparisons to `outputs/simulation/`. The [simulation guide](slim/README.md) explains the model, fixed seeds and comparison tolerance.

The simulation diagnostic compares the Gaussian variance-share calculation with a finite-population projection calculation. The fixed-genic-baseline inheritance model is a separate mathematical analysis; the result catalog maps its checks separately.
