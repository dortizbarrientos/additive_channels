# Parental frequencies and reproductive weights

This companion makes the population weighting in *Additive Channels in Curved Fitness Landscapes* visible. It follows a fixed set of simulated parents under equal frequency weights, expected reproductive weights from a curved surface, and weights predicted by a fitted plane. A separate example uses the saved simulated offspring counts from Supplementary File 3.

These are **teaching figures**. The article's four main figures retain their numbering. The one-trait 97%/50% example in the abstract is a different calculation and should not be used to label the two-trait cloud here.

## Open the materials

| Resource | Use |
| --- | --- |
| [Parental-weighting figure](figures/parental_weighting.pdf) | Three views of the same parental points and a comparison of weighted means. |
| [Offline parent explorer](explore_parental_cloud.html) | Inspect any of the 20,000 simulated parents and switch its displayed weight. Download the HTML and open it in a browser. |
| [Recorded-count teaching figure](figures/tutorial_cloud_recorded_offspring.pdf) | Compare equal, expected and realised-count weights in the saved one-trait simulation. |
| [Editable parental-weighting figure](figures/parental_weighting.pptx) and [count figure](figures/tutorial_cloud_recorded_offspring.pptx) | Native text labels and embedded SVG artwork. |
| [Numerical results](data/results.json) and [all parental values](data/parent_cloud.csv.gz) | Full-precision calculations and a row for every simulated parent. |
| [Caption fragment](captions.tex) | Text for reuse in a separate teaching document. |

SVG and PNG versions accompany each PDF. The [geometry companion](../geometry/) explains covariance orientation, fitted planes and the variance-share projection.

## Where the two-trait population came from

The module replays the Figure 2 Gaussian validation generator with seed 20260905 and selects its 25th two-trait scenario, using one-based indexing. Each of its 20,000 parents has two simulated breeding values. The curvature is stabilising. The example was chosen because it combines a high sample linear fit with a substantial discrepancy in the predicted selected-parent displacement. This is a selected illustration, not an estimate of how frequently that combination occurs.

The generator's ordered random draws are preserved. Replaying all 360 scenarios reproduces the archived median, 95th percentile and maximum absolute discrepancies within 1e-10. The frozen generator snapshot in `code/manuscript_figures.py` is byte-identical to `code/figures.py` at manuscript repository commit `10a865c`. `data/manuscript_figure_results.json` supplies the reference values for that check.

These individuals come from the Gaussian validation experiment. They are not SLiM individuals or measured plants. The print figure shows 600 parents sampled uniformly without replacement, with display seed 2511. All 20,000 determine the means, percentages and fit; the displayed subset does not enter the calculations. The explorer can display either the subset or everyone.

## What is fitted

For each simulated parent i, evaluate its known quadratic log expected fitness, ℓ_i. Fit a plane with an intercept to these log values by ordinary least squares. Its prediction is ℓ̂_i.

The **sample plane explains 90.2095%** of variation in these log values. The **population Gaussian share is 90.3601%** for the generating parameters. These are different quantities: the former is an empirical least-squares fit to this finite cloud; the latter uses the specified Gaussian distribution. The manuscript's empirical squared-correlation diagnostic is also recorded separately in `data/results.json`.

The map colours are shifted by a constant separately for each surface, giving zero at the starting mean. Such a constant cancels from normalised reproductive weights. It does not alter any mean or percentage.

## Three weighting rules

For the same parental values a_i:

\[
w_i^{\rm equal}=1/N,\qquad
w_i^{\rm curved}=\frac{\exp(\ell_i)}{\sum_j\exp(\ell_j)},\qquad
w_i^{\rm plane}=\frac{\exp(\hat\ell_i)}{\sum_j\exp(\hat\ell_j)}.
\]

Summing weights over a specified group gives its contribution. Summing weighted breeding values over all parents gives the selected-parent mean. Parents with trait 1 below one starting-population standard deviation make up 15.9% of the population. They contribute 28.4668% of expected output under the curved surface and 34.1268% under the plane.

Dot area is proportional to expected contribution, and radius is proportional to its square root. The average area is the same under all three weightings before subsampling. Each point remains at its original breeding-value coordinates. Only its contribution changes.

For the reported displacement length, subtract the sample mean and divide each trait by its own starting-population standard deviation. The curved and plane-weighted shifts are approximately (-0.473, +0.429) and (-0.593, +0.580). Their lengths are 0.638049 and 0.829949, giving a **30.0759% overestimate of length**.

This is Euclidean distance after marginal trait standardisation. It is not full covariance whitening. The displayed percentage compares displacement lengths; it is not the norm of the vector prediction error in the manuscript's covariance-scaled bound. The two-trait weights are expected reproductive contributions, not realised offspring counts. Predicting offspring breeding values would also require an inheritance model.

## The one-trait companion with recorded simulated counts

The files `data/simulation_truth.csv` and `data/observed_data.csv` are copied from the worked-estimation example in Supplementary File 3 and match it byte for byte. Genotype IDs connect known simulated breeding values with simulated counts of surviving offspring. The 800 records include 88 zero counts and 2,862 offspring in total.

The count-weighted mean is

\[
\frac{\sum_i W_i a_i}{\sum_i W_i}.
\]

The high group contains 122 parents with breeding value more than one standard deviation above the sample mean. Their recorded simulated counts total 585 offspring. Thus their count-weighted contribution is 585/2,862 = 20.4403%, compared with 15.25% of the parents. Parents with zero offspring remain in the initial population and contribute zero to the count-weighted mean.

The figure also shows expected weights from the generating quadratic relationship and its fitted linear description. It uses the known simulated breeding values to explain weighting. It does not re-estimate those values from noisy height measurements or repeat the measurement-error analysis in Supplementary File 3. The high group is the upper tail in this example; selection favours the lower tail of trait 1 in the two-trait example. The group definitions therefore differ deliberately.

## Reproduce

From this directory, with Python 3 available:

```bash
python3 -m pip install -r requirements.txt
bash run.sh
```

The first command needs a network connection if dependencies are missing. Once installed, the module runs offline. `PYTHON_BIN` can select a specific interpreter.

| Script | Operation |
| --- | --- |
| `code/calculate.py` | Replays the Figure 2 random stream; checks the archived validation summaries; fits the selected plane; computes weights, group contributions and mean shifts; writes `data/results.json` and `data/parent_cloud.csv.gz`. |
| `code/draw.py` | Draws both teaching figures from the checked data and writes PDF, SVG and PNG files to `figures/`. |
| `code/export_interactive.py` | Builds the self-contained `explore_parental_cloud.html` from the same parent table and template. |
| `code/manuscript_figures.py` | Frozen Figure 2 generator snapshot; imported by the calculation script. |
| `code/export_pptx.py` | Optional export of the existing SVG figures to editable PowerPoint files. Requires python-pptx, Pillow, lxml and Inkscape. |

Regeneration replaces derived results and figures in this folder. It does not overwrite the saved height observations or simulation truth. The prebuilt figures and HTML are supplied for readers who only want to inspect or teach the examples.

## Provenance

The primary numerical definitions are the manuscript's conditional selection weight, Gaussian variance share and selected-parent moments, with derivations in Appendices S1–S2. The saved-count companion reuses the Supplementary File 3 teaching data. All numerical results here concern these specified model populations. Neither the visual similarity of a plane nor a high variance share establishes additive gene action or an offspring response.
