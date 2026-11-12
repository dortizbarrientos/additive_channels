# Reproducing a result

Run `bash run_all.sh` from the root. A successful run ends with the checks of the four figure records and the 500 bootstrap refits. The commands below use only files in this repository. New numerical outputs go to `outputs/`; the saved reference data are left intact.

| Result | Code and inputs | What to compare |
|---|---|---|
| 1. From phenotype-dependent fitness to a conditional mean | [Figure code](code/figures.py), function `make_figure_1`; fixed seed and a specified environmental distribution | [Figure 1](reference/figures/figure1_conditional_fitness.pdf). Filled points are phenotype-dependent fitness values from sampled environmental deviations, open circles are sample means and the curve is the conditional mean. Offspring counts are not simulated in this figure. |
| 2. Gaussian projection identity | Same script, `make_figure_2`; 360 parameter combinations, 20,000 breeding-value vectors per combination | [Figure 2](reference/figures/figure2_projection_identity.pdf). The population identity is exact; the median absolute difference in the samples is about 0.00237. |
| 3. Proportional covariance contraction | Same script, `make_figure_3`; fixed slope and curvature, same mean, covariance G versus 0.11G | [Figure 3](reference/figures/figure3_covariance_contraction.pdf). The linear share rises from 0.604 to 0.933. Both absolute variance components fall. |
| 4. Covariance across generations | Same script, `make_figure_4`; scalar covariance recursion, fixed genic baseline and imposed gradient history | [Figure 4](reference/figures/figure4_fixedB_trajectory.pdf). The covariance fixed point is 0.472353. The linear share rises from 0.581 to 0.922 while the gradient is maintained, then falls as the imposed gradient declines. |
| Appendix A1: three one-trait populations | [Figure and independent integration checks](tutorials/one_trait_visual/make_figure.py); run `python3 tutorials/one_trait_visual/make_figure.py` | Fixed curve `ell(a)=a−a²/2`; shares 2/3, 20/21 and 0 for broad, narrow and peak-centered populations. [Exact components](tutorials/one_trait_visual/values.json). |
| Appendix A2: rotation on a fixed surface | [Geometry module](tutorials/geometry/README.md); run `bash tutorials/geometry/run.sh` | Page 1 of the [geometry PDF](tutorials/geometry/figures/geometry_of_additive_channels.pdf); shares 0.910626, 0.839276 and 0.203012. [Parameters and checks](tutorials/geometry/values.json). |
| A good fit can overestimate selection | [Quadrature check](tutorials/introduction/check_examples.py); [worked derivation, p. 4](tutorials/introduction/notes.pdf) | At G = 1, b = 2 and H = −½, the linear share is 32/33. Expected-output weighting gives a selected-parent shift of 4/3. Ignoring curvature gives 2. |
| Matrix identities and limits | [Mathematical checks](code/verify_mathematics.py) | Coordinate invariance, covariance scaling, the displacement bound and the scalar fixed point; results in `outputs/mathematics_checks.json`. |
| Finite-population simulation | [SLiM model and diagnostic tables](slim/), [aggregation code](code/summarize_simulation.py) | Across 4,000 replicate-generation rows, the median absolute difference between the Gaussian share and empirical squared correlation is 0.0156678857. This checks the approximation, not the fixed-baseline inheritance model. |
| Estimating the share from observations | [Count model and simulated data](examples/estimating_variance_share/), `bash run_estimation.sh` | Generating share 0.6667; estimate 0.6107; 95% parametric bootstrap interval 0.5330–0.6857. Each replicate refits the measurement and fitness models. |

[reference/figures.json](reference/figures.json) lists the numerical parameters and results for each panel. The fresh record is `outputs/figure_results.json`. The checks compare underlying values, not PDF bytes: fonts, metadata and renderers can change a figure file without changing its calculation. The worked-example checks compare the observations, true simulated breeding values, estimates and the individual bootstrap draws. Small numerical differences are allowed for floating-point calculations.

To repeat the long simulation, install **SLiM 5.2** and run `bash run_all.sh --simulate`. Set `SLIM_BIN` to an executable path if `slim` is not on your PATH. This writes raw breeding values, optima, diagnostic tables and comparisons to `outputs/simulation/`. The [simulation guide](slim/README.md) explains the records and the comparison tolerance. The shorter default calculation starts from the included diagnostics.

For the numerical functions used by the app and the estimator, run the independent integration and simulation tests with:

    python -m unittest discover -s examples/estimating_variance_share -p 'test_*.py' -v

Use the Python interpreter containing the dependencies (for example `.venv/bin/python` if the launcher created that environment).

## Visual companions

Run `bash tutorials/build_visuals.sh` to regenerate all three visual modules using NumPy, SciPy, pandas and Matplotlib. These optional outputs are saved beside their module sources; they are separate from the default numerical reproduction under `outputs/`. Editable PowerPoint exports are supplied; rebuilding them additionally requires the dependencies listed in each module's README.

The [parental-weighting module](tutorials/parental_weighting/README.md) refits the exported simulated parent table and compares unweighted, expected-output-weighted and recorded-count-weighted summaries. Its saved observations and simulation truth are the same files used by the worked estimation example. The geometry module independently checks the Gaussian moments by numerical quadrature. Physical rotation of a population and rotation in the whitened parameter representation are distinguished in its guide.
