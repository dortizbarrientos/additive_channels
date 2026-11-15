# Reproducing the paper

The repository contains the code and reference records for *Additive Channels in Curved Fitness Landscapes*, including Appendices S1–S7 and the mathematics and estimation supplements. [RESULTS.md](RESULTS.md) maps the results to their calculations; [reference/result_catalog.json](reference/result_catalog.json) records the parameters, assumptions and expected values.

For an explanation before running code, read the [short companion](tutorials/companion/companion.pdf). The [mathematics guide](tutorials/mathematics/guide.pdf) develops the calculations in detail.

## Numerical reproduction

From the repository root, run:

```bash
bash run_all.sh
```

This regenerates the four main figures, runs the mathematical checks, summarises the archived SLiM diagnostics and repeats the worked estimation analysis with all 500 bootstrap refits. It compares the results with the supplied reference records. New outputs go to `outputs/`; the reference data are preserved.

Python 3.11 or newer is required. The launcher uses a compatible installed environment or creates `.venv/` and installs the numerical dependencies. The first installation needs internet access. To create the tested environment explicitly:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -c requirements-tested.txt
PYTHON_BIN=.venv/bin/python bash run_all.sh
```

The tested package versions are recorded in [requirements-tested.txt](requirements-tested.txt). Use `PYTHON_BIN` to select an interpreter for any of the shell launchers.

For a shorter run that omits the estimation and bootstrap calculation:

```bash
bash run_all.sh --quick
```

To run only the estimation example:

```bash
bash run_estimation.sh
```

## Outputs and reference values

| Output | Calculation |
|---|---|
| `outputs/figures/` and `outputs/figure_results.json` | Four main figures and their parameters and numerical values. |
| `outputs/mathematics_checks.json` | Coordinate invariance, covariance scaling, selected-parent displacement and fixed-point checks. |
| `outputs/result_checks.json` | Independent integration, regression and matrix checks for the analytical results and supplementary examples. |
| `outputs/simulation_summary.json` | Summary of 4,000 generation records in the 20 archived SLiM tables. |
| `outputs/estimation/` | Observations, separate simulation truth, fitted estimates, 500 bootstrap refits, intervals, tables and diagnostic figures. |

The Gaussian projection experiment has median absolute sample discrepancy **0.0023672601**. Proportional covariance contraction changes the Figure 3 share from **0.603954** to **0.932720**. The archived SLiM comparison has median absolute discrepancy **0.0156678857**. The worked estimate is **0.610744**, with model-conditional 95% interval **0.533024–0.685713**.

The main figure records are in [reference/figures.json](reference/figures.json). The complete estimation reference is in [examples/estimating_variance_share/results/](examples/estimating_variance_share/results/). The default comparison checks individual bootstrap draws as well as the final percentiles, allowing small floating-point differences. PDF bytes are not a numerical comparison: fonts and metadata can change without changing a scientific result.

## Visual figures and offline explorers

```bash
bash run_all.sh --visuals
```

This rebuilds the [one-trait figure](tutorials/one_trait_visual/README.md), [two-trait geometry module](tutorials/geometry/README.md), [parental-contribution module](tutorials/parental_weighting/README.md) and repository overview images. It checks the numerical records, draws PDF, PNG and SVG figures, and rebuilds the geometry and parental HTML explorers. Figure A2 in Appendix S7 is the first page of the geometry PDF.

The HTML explorers contain their own data and code. Download the files and open them in a browser; no server is needed.

## Teaching PDFs and slides

The supplied documents can be read without build tools. To regenerate the figures and compile the short companion, introductory notes and worksheet, Supplementary File 1, worked-estimation document and introductory slides:

```bash
bash run_all.sh --tutorials
```

This requires TeX Live or MacTeX with pdfLaTeX, latexmk, BibTeX, the extra/science packages and recommended fonts, plus Node.js, npm and LibreOffice. The first slide build installs the version of `pptxgenjs` recorded in [package.json](tutorials/introduction/package.json) if it is missing. Installation needs internet access; subsequent builds use the installed dependencies.

The editable PDF sources are [companion.tex](tutorials/companion/companion.tex), [notes.tex](tutorials/introduction/notes.tex), [worksheet.tex](tutorials/introduction/worksheet.tex), [guide.tex](tutorials/mathematics/guide.tex) and [worked_example.tex](examples/estimating_variance_share/worked_example.tex). [build_slides.js](tutorials/introduction/build_slides.js) creates the introductory PowerPoint, which LibreOffice converts to PDF.

The worked-estimation document uses the saved default tables in `examples/estimating_variance_share/results/`. Running a new analysis in `outputs/estimation/` does not replace those tables. To rebuild only the short companion, use `bash tutorials/companion/build.sh`.

## Interactive study guide

The [interactive study guide](tutorials/interactive/README.md) is a separate self-contained HTML file assembled from editable lessons and checked scientific records. Rebuild it with:

```bash
python3 -m pip install -r tutorials/interactive/requirements.txt
python3 tutorials/interactive/build_guide.py
```

The first command installs the additional build dependency, lxml. Node.js is needed for the independent JavaScript model checks in `tutorials/interactive/src/validate_models.py`. The generated guide runs offline in a browser.

## Editable teaching figures

Prebuilt PowerPoint files accompany the geometry and parental-contribution figures. To regenerate them after rebuilding the visual modules, install python-pptx, Pillow, lxml and Inkscape, then run:

```bash
python3 tutorials/geometry/code/export_pptx.py
python3 tutorials/parental_weighting/code/export_pptx.py
```

The exports preserve native text labels and SVG artwork for editing.

## Independent estimator checks and optional app

```bash
python3 -m unittest discover -s examples/estimating_variance_share -p 'test_*.py' -v
```

Use the interpreter containing the dependencies, such as `.venv/bin/python`. The checks compare the implementation with Gaussian moments, closed-form expected output, independent integration and simulated data. They also check bootstrap recalibration, the quartic example and explicit numerical failure conditions.

The optional Shiny app calls the same model functions as the batch analysis:

```bash
bash run_shiny.sh
```

The launcher installs the additional dependencies in [requirements-app.txt](requirements-app.txt) if needed, then opens a local page at `http://127.0.0.1:8000`. Set `SHINY_PORT=8001` to use another port. See the [worked-example README](examples/estimating_variance_share/README.md) for the model assumptions and controls. New app settings produce separate examples; the archived default remains the reproduction target.

## Fresh SLiM simulations

The default run uses the archived diagnostic tables. To regenerate them from individual populations:

```bash
bash run_all.sh --simulate
```

This requires **SLiM 5.2**. The [simulation instructions](slim/README.md), model and driver provide seeds 42–61 and all settings. The run produces eight million individual-generation records in `outputs/simulation/` and compares its diagnostics with the archive.

The simulation assesses the Gaussian current-population approximation in the specified multilocus design. It does not test the separate fixed-genic-baseline inheritance recursion or selected-parent displacement bound.

## Automated checks

The [workflow](.github/workflows/reproduce.yml) rebuilds and checks the interactive study guide, runs the complete numerical reproduction, rebuilds the visual modules and compares their numerical records. It also runs the independent estimator tests and checks that the optional Shiny app serves its example. PDF and slide compilation is separate from these automated checks.
