# Find and reproduce a scientific result

This page maps the four main figures, mathematical results, Appendices S1–S7, the mathematics guide and the worked estimation example to their calculations. It also covers the additional visual tutorials and Shiny app. The [machine-readable catalogue](reference/result_catalog.json) supplies 53 result records with assumptions, expected values, code, inputs, outputs and exact commands.

All paths and commands below start at the repository root. Follow [REPRODUCING.md](REPRODUCING.md) to prepare the numerical Python environment. The shell launchers prepare it when needed; individual `python` commands assume it is active.

```bash
bash run_all.sh             # Figures, mathematics, archived diagnostics and 500 bootstrap refits
bash run_all.sh --quick     # Same figure/mathematics checks, without the bootstrap analysis
bash run_all.sh --visuals   # Rebuild the visual tutorials and their numerical records
```

The numerical target is variation in **log expected reproductive output conditional on breeding value**. Its first-order share describes the linear contribution under a specified population distribution. Expected reproductive weights determine a selected-parent mean. Offspring predictions require an additional inheritance model.

## Main figures

One command regenerates all four figures and writes their parameters and results to `outputs/figure_results.json`:

```bash
python code/figures.py
```

The inputs are the parameters and random seeds recorded in [the generator](code/figures.py). [reference/figures.json](reference/figures.json) provides the comparison values. PDFs and PNGs are written to `outputs/figures/`.

| Figure | Calculation and numerical landmark | Output stem |
|---|---|---|
| **1. Construct conditional expected fitness** | Average a Gaussian phenotype-fitness function over environmental deviations, then take the logarithm. With environmental variance 0.49 and fitness width 0.36, breeding-value slope is 1.1764705882 and curvature is −1.1764705882 at the specified mean. The plotted individual values are assigned phenotype-dependent fitness, not offspring-count draws. | `figure1_conditional_fitness` |
| **2. Check the Gaussian projection identity** | 360 parameter combinations, in dimensions 2, 4 and 8, each use 20,000 sampled breeding-value vectors. Median absolute discrepancy between the Gaussian expression and sample squared correlation is 0.0023672601; the 95th percentile is 0.0103264192. | `figure2_projection_identity` |
| **3. Change covariance on a fixed surface** | Replacing G by 0.11G changes the components from 0.7515 and 0.4928 to 0.082665 and 0.00596288. The share rises from 0.603954 to 0.932720. Both absolute components decrease. | `figure3_covariance_contraction` |
| **4. Follow the specified covariance closure** | The scalar fixed point is 0.4723532349. With the gradient maintained, the share rises from 0.581395 to 0.921639 by generation 40. The gradient subsequently decreases according to a separately specified schedule; the share reaches 0.00870449 at generation 100. | `figure4_fixedB_trajectory` |

The covariance closure in Figure 4 does not calculate the changing mean or gradient. Its gradient schedule is an input. The finite Gaussian samples in Figure 2 illustrate the identity; sampling error is expected.

## Mathematical results and their numerical checks

Two scripts provide complementary checks:

```bash
python code/verify_mathematics.py
python code/reproduce_result_checks.py
```

[verify_mathematics.py](code/verify_mathematics.py) checks 30 matrix cases in dimensions 2, 4 and 8, coordinate invariance, proportional covariance scaling, selection bounds, an anisotropic counterexample and scalar trajectories. It writes `outputs/mathematics_checks.json`.

[reproduce_result_checks.py](code/reproduce_result_checks.py) uses deterministic Gaussian quadrature, adaptive integration, weighted population regression and small matrix calculations. It writes `outputs/result_checks.json`. The group names in the table below identify the corresponding records in that file. Neither script replaces an analytical proof. The [mathematics guide](tutorials/mathematics/guide.pdf) develops the derivations and their assumptions.

| Scientific result | Calculation or counterexample | Code or result-check group |
|---|---|---|
| **Average output before taking its logarithm** | Independently integrate Gaussian environmental deviations; compare log mean output with mean log output. A group with outputs 0 and 2 has log mean 0 but no finite mean of logged counts. Changing the frequency of a class with twice the output changes its reproductive fraction from 0.4 to 6/7 in the two specified populations. | `conditional_mean_and_log` |
| **Gaussian linear and quadratic variances** | Integrate a correlated two-trait quadratic with off-diagonal terms. Recover bᵀGb, ½tr(HGHG), the centred-quadratic mean, and zero linear–quadratic covariance. | `gaussian_projection` |
| **Population affine regression** | Fit the intercept and slopes independently by weighted least squares. Recover the curvature-adjusted intercept and the first-order share as the fitted R². A tangent at the mean generally has a different intercept. | `gaussian_projection`; [introductory checks](tutorials/introduction/check_examples.py) |
| **Ratio of noisy linear and quadratic R² values** | Independent multiplicative lognormal noise gives a constant log-mean gap and finite log-error variance. With noise variance 4, the R² values are 32/65 and 33/65; their ratio is 32/33. | `noisy_regression_ratio` |
| **Proportional covariance scaling** | With mean, slope and curvature fixed, G → sG gives linear variance sL and quadratic variance s²Q. The share is L/(L+sQ); the omitted fraction is sQ/(L+sQ). Strict improvement under contraction requires L and Q both positive. | [verify_mathematics.py](code/verify_mathematics.py); `gaussian_projection` |
| **Arbitrary covariance reduction need not improve the share** | For b=(1,0) and H=−I, changing G from I to diag(0.1,0.9) reduces the share from 0.5 to 0.196078. | `anisotropic_contraction_shares` in `mathematics_checks.json` |
| **Coordinate invariance and trait units** | Transform G, b and H together under invertible changes of coordinates. The guide's tenfold unit change gives G=100, b=0.2 and H=−0.005, leaving component variances 4 and 0.125. | [verify_mathematics.py](code/verify_mathematics.py); `gaussian_projection` |
| **Whitening, orientation and the Rayleigh quotient** | Hold the whitened gradient length and curvature spectrum fixed: the share remains constant while eigenaligned displacement errors can be 0.1 or 0.8. A separate calculation holds the gradient's Euclidean norm fixed in the original trait coordinates and checks the covariance eigenvalue bounds. | `orientation_and_absolute_scale` |
| **Zero components and singular covariance** | Check shares 0 and 1 at the appropriate boundaries. Record the constant-target share and zero-gradient correlation as undefined. Restrict a rank-one covariance to its varying support before calculating selected moments. | `boundaries_and_non_gaussian_cases` |
| **Limits of Gaussian moments** | An asymmetric two-point population has nonzero linear–quadratic covariance and actual regression R²=1, while the Gaussian expression is 0.8. A symmetric two-point population retains orthogonality but has a different fourth moment. | `boundaries_and_non_gaussian_cases` |
| **Exact selected-parent moments** | Reweight the original Gaussian quadrature nodes by expected output. Compare the resulting mean and covariance with the completed-square formulas for stabilising curvature and an integrable saddle. Identify a nonintegrable combined precision. | `selected_parent_moments` |
| **A close linear fit does not guarantee an accurate parental shift** | With b=2, H=−0.5 and G=1, the share is 32/33, the exact shift is 4/3, and ignoring curvature predicts 2: a 50% relative error. Increasing b to 10 raises the share to 0.998752 without reducing that relative error. A specified pair in the distribution's tail also reverses rank. | `selected_parent_moments`; [introductory checks](tutorials/introduction/check_examples.py) |
| **Relative displacement bound** | Use the G-inverse norm for both displacement and error. Check the spectral-norm bound and its upper bound √(2V_quadratic), including equality along curvature eigenvectors. These are exact-quadratic-model results. | `selected_parent_moments`, `orientation_and_absolute_scale`; [verify_mathematics.py](code/verify_mathematics.py) |
| **Fixed effects versus a fixed genic baseline** | A locus with effect 1 contributes variance 0.50 at allele frequency 0.5 and 0.32 at frequency 0.8. Fixed effects alone do not hold the baseline fixed. | `inheritance_matrix_and_limits` |
| **Matrix inheritance interval and fixed-point bounds** | For noncommuting positive-definite baseline and stabilising-curvature matrices, test 12 covariances in the order interval and find one fixed point within its bounds. | `inheritance_matrix_and_limits` |
| **Scalar inheritance and convergence** | Check the positive fixed point, the exact scalar contraction inequality, starts at 0, 0.1 and 4, and the zero-curvature/zero-retention boundaries. A low initial variance can increase. | `inheritance_matrix_and_limits`; [verify_mathematics.py](code/verify_mathematics.py) |
| **Retention equal to one** | Compare repeated updates with Gₜ=(G₀⁻¹+tΓ)⁻¹. Positive curvature removes variation in every direction. A correlated example with singular curvature retains null-space variance 1.84, rather than its initial marginal variance 2. | `inheritance_matrix_and_limits` |
| **Prediction shrinkage** | Keep b and H on the true breeding-value scale and replace only G by 0.6G. The naive share becomes 0.981595 instead of 0.969697. This is a specific covariance substitution, not a general bias correction. | `prediction_shrinkage` |
| **Phenotype-regression conversion** | Fit relative-fitness regressions by quadrature for positive fitness functions in one and two traits. Convert their selected moments and compare b and H with independent environmental averaging. The guide's moment example gives α=1.15, selected variance 0.41, b=0.487805 and H=−0.439024. | `phenotype_regression_conversion` |
| **Local quadratic share versus a complete nonquadratic curve** | Add −0.08a⁴ to the worked example. Its local quadratic share remains 2/3, while the complete log-mean curve has linear R²=0.242406. | `local_quadratic_and_full_curve`; [estimation checks](examples/estimating_variance_share/test_model.py) |

The matrix inheritance proof establishes existence and bounds under fixed B, fixed stabilising curvature and scalar retention below one. The numerical matrix example does not assert general uniqueness or convergence. Those stronger conclusions apply to the scalar result. Likewise, the phenotype-regression conversion requires joint Gaussianity, phenotype-mediated selection, compatible coordinates, the stated quadratic-coefficient convention and positive selected covariance. Without exact log-quadraticity, a valid moment conversion gives moment-matched parameters, not arbitrary point derivatives.

## Appendices S1–S7

| Appendix | Complete calculation coverage | Reproduction route |
|---|---|---|
| **S1: Gaussian moments and projections** | Linear and quadratic variances; third-moment orthogonality; fitted intercept and slopes; nested R² ratio; invertible coordinate changes; whitened curvature; Rayleigh quotient; zero terms and singular support. | The two mathematics scripts above. Figure 2 supplies the finite-sample comparison; guide Sections 4 and 9 supply derivations. |
| **S2: Selection and the displacement bound** | Gaussian selected mean/covariance; integrability; stabilising covariance contraction; displacement norm and eigenvector equality; environmental convolution. | `conditional_mean_and_log`, `selected_parent_moments`, `orientation_and_absolute_scale`, `phenotype_regression_conversion`; Figure 1. |
| **S3: Fixed-baseline inheritance** | Order-interval invariance; fixed-point bounds; scalar root and contraction; retention-one precision update and null-space limit; distinction between fixed effects and fixed baseline. | `inheritance_matrix_and_limits`, `verify_mathematics.py`; Figure 4. |
| **S4: Forward-time simulation** | All 20 replicate tables, 4,000 generation records, Gaussian-share identities and the reported discrepancy. | Archive summary or a fresh SLiM run, as separated below. |
| **S5: Phenotype-regression conversion** | Relative-fitness intercept and selected moments; covariance correction; inverse conversion to b and H; factor-of-two convention; distinction from raw-polynomial log derivatives. | `phenotype_regression_conversion`; guide Figure 5. |
| **S6: Interpretation and limits** | All 11 questions map to the result records in the [JSON catalogue](reference/result_catalog.json): target, historical context, log order, gene-action limits, non-Gaussian moments, estimation, zero terms, ranking/selection accuracy, orientation, inheritance and covariance scaling. | The mathematical and estimation checks verify the stated calculations. Historical attribution and interpretive qualifications are conceptual statements, not additional numerical results. |
| **S7: Visual explanation** | All three one-trait populations, their fitted-line intercepts and component variances; all three two-trait rotations and their full-population fits. | The one-trait and geometry generators below; both use Gaussian quadrature. |

### Figure A1: a fixed curve and three populations

```bash
python tutorials/one_trait_visual/make_figure.py
```

The [generator](tutorials/one_trait_visual/make_figure.py) supplies all inputs and writes [values.json](tutorials/one_trait_visual/values.json) plus PDF, PNG and SVG versions of `one_trait_additive_channel` in the module's `figures/` directory.

| Population | Mean | Variance | Linear variance | Quadratic variance | Linear share |
|---|---:|---:|---:|---:|---:|
| A: broad, on the slope | 0 | 1 | 1 | 0.5 | 2/3 |
| B: narrow, same mean | 0 | 0.1 | 0.1 | 0.005 | 20/21 |
| C: narrow, at the peak | 1 | 0.1 | 0 | 0.005 | 0 |

Every population uses ℓ(a)=a−a²/2. The fitted values at the population means are −0.5, −0.05 and 0.45. All calculations use the complete Gaussian distributions; the central 95% highlighted in the drawing is a visual guide.

### Figure A2: turn the population distribution

```bash
python tutorials/geometry/code/geometry.py   # Numbers and quadrature checks
bash tutorials/geometry/run.sh              # Also rebuild figures and explorer
```

The [geometry source](tutorials/geometry/code/geometry.py) specifies the fixed surface and principal variances 0.20 and 0.005. [values.json](tutorials/geometry/values.json) records all cases. **Figure A2 is page one** of [geometry_of_additive_channels.pdf](tutorials/geometry/figures/geometry_of_additive_channels.pdf).

| Long-axis direction | Linear variance | Quadratic variance | Linear share |
|---|---:|---:|---:|
| 0° | 0.1305 | 0.012808 | 0.910626 |
| 45° | 0.06688125 | 0.012808 | 0.839276 |
| 90° | 0.0032625 | 0.012808 | 0.203012 |

These comparisons rotate the population in fixed trait coordinates. They do not relabel the axes. The small perpendicular variance still contributes to the full fitted plane at 90°.

## Forward-time population simulation

To check the archived calculation:

```bash
python code/summarize_simulation.py
```

Inputs are the 20 [archived diagnostic tables](slim/diagnostics/). The script verifies generations 1–200, finite records, component/share identities and the reference summary. It writes `outputs/simulation_summary.json`. The median absolute difference between the Gaussian share and sample squared correlation is **0.015667885704792002**, from 4,000 replicate-generation rows.

To regenerate those diagnostics from individual populations:

```bash
bash run_all.sh --simulate
```

This separate route requires **SLiM 5.2**. [The model](slim/slim_sim_n_traits.slim) and [driver](slim/run_simulations.sh) supply the settings and seeds 42–61. [compute_diagnostics.py](slim/compute_diagnostics.py) reconstructs the quantities from breeding-value and optimum records. [compare_simulations.py](code/compare_simulations.py) compares all regenerated tables and the summary with the archive. Fresh outputs go to `outputs/simulation/`; the simulation produces eight million individual-generation records.

The finite-population comparison assesses the Gaussian current-population approximation in this design. It does not test selected-parent displacement or the separate fixed-B inheritance model.

## Supplementary File 1: mathematics guide

[Read the guide](tutorials/mathematics/guide.pdf). Its five figures share a recurring one-trait example and then introduce the phenotype-regression conversion. To regenerate them:

```bash
python code/guide_figures.py
```

The inputs are in [guide_figures.py](code/guide_figures.py). Each output is written as PDF and PNG under `tutorials/mathematics/figures/`.

| Guide figure | Output stem | Reproduced values or calculation |
|---|---|---|
| 1: conditional averaging | `math_guide_fig1` | Optimum 4, phenotype fitness width 1, environmental variance 1; conditional log slope 2 and curvature −0.5 at the mean. |
| 2: variance components | `math_guide_fig2` | b=2, H=−0.5, G=1; components 4 and 0.125, share 32/33. |
| 3: selected parents | `math_guide_fig3` | Selected mean 4/3 and variance 2/3. |
| 4: covariance iteration | `math_guide_fig4` | B=1, γ=0.5, ρ=0.5; g₁=0.833333, g₂=0.794118, g₃=0.784211, g₄=0.781664; fixed point (√17−1)/4. |
| 5: regression conversion | `math_guide_fig5` | P=1.5, β=0.4, γ=−0.2, G=0.5; α=1.15, selected G=0.41, b=0.487805, H=−0.439024. |

The [result checks](code/reproduce_result_checks.py) also cover every numerical checkpoint: log order (1), finite-difference slope/curvature (2), components and odd-product cancellation (3–4), trait units (5), selected moments and a steeper-gradient example (6–7), scalar updates and retention one (8–9), the simulation's scope (10), and phenotype conversion (11). The guide's noisy R² example, covariance-halving example, reliability substitution, multivariate calculations and inheritance limits are mapped in the catalogue as well. Check 10 is a scope distinction: agreement with a current-population calculation cannot validate a different inheritance recursion.

## Supplementary Files 2 and 3: reproduction and estimation

Supplementary File 2's scientific reproduction resources correspond to the code and reference data mapped throughout this page. The worked estimation example in Supplementary File 3 has a dedicated [source and results directory](examples/estimating_variance_share/) and [readable PDF](examples/estimating_variance_share/worked_example.pdf).

### Recreate the default estimation result

```bash
bash run_estimation.sh
```

[model.py](examples/estimating_variance_share/model.py) generates 800 genotypes, three measurements per genotype and one offspring count, then fits the two-stage latent-value model. [run_case.py](examples/estimating_variance_share/run_case.py) uses observation seed 20261005 and bootstrap seed 20261006. It writes the observations, separate simulation truth, estimates, all 500 bootstrap refits, numerical summary, generated tables and three figures to `outputs/estimation/`.

| Quantity | Generating value | Estimate | Model-conditional 95% interval |
|---|---:|---:|---:|
| Slope b | 0.7 | 0.682560 | 0.600334–0.778885 |
| Curvature H | −0.7 | −0.769799 | −0.916719–−0.630133 |
| Breeding-value variance G | 1 | 1.002149 | 0.876642–1.136257 |
| Linear variance | 0.49 | 0.466889 | 0.354749–0.599602 |
| Quadratic variance | 0.245 | 0.297570 | 0.195636–0.421178 |
| First-order share | 2/3 | 0.610744 | 0.533024–0.685713 |

The data contain **88 zero counts**, which remain in the count likelihood. Estimated measurement variance is 0.979881 and reliability is 0.754189. The naive analysis gives share 0.673984. All 500 reference bootstrap fits succeed, with no primary fit at a numerical bound. Increasing the quadrature order from 41 to 81 changes b, H and the share by less than 4×10⁻¹³ in this dataset. These values are recorded in [summary.json](examples/estimating_variance_share/results/summary.json).

| SF3 figure | Code and input | Generated output |
|---|---|---|
| **1: observed counts and conditional relationship** | `relationship_plot` in [plots.py](examples/estimating_variance_share/plots.py), using the generated observations and latent-value fit. | `outputs/estimation/case1_relationship.pdf` and PNG |
| **2: components and uncertainty** | `components_plot`, using generating settings, fitted parameters and the jointly recalibrated bootstrap draws. | `outputs/estimation/case2_components.pdf` and PNG |
| **3: observable-data diagnostics** | `diagnostics_plot`, using quadratic and quartic conditional predictions, bin summaries and zero-count probabilities. | `outputs/estimation/case3_diagnostics.pdf` and PNG |

The observations alone identify additive variance only under the specified teaching model: trait values are wholly additive, measurement environments are independent, and the reproductive assay is separate. Bootstrap intervals are conditional on that model. Diagnostic bars condition on fitted parameters and are not confidence bands for the fitness surface.

### Integration checks and a nonquadratic alternative

```bash
python -m unittest discover -s examples/estimating_variance_share -p test_model.py
python code/reproduce_result_checks.py
bash run_estimation.sh --quartic 0.08 --output outputs/estimation_quartic
```

The [eight estimation checks](examples/estimating_variance_share/test_model.py) cover Gaussian moments, simulation/truth separation, a closed expected-output formula, an independent adaptive likelihood integral, the known-value limit and repeated-seed recovery, bootstrap recalibration, quartic scope, and rejection of unresolved integration or failed calibration.

For the default quadratic data, quartic-minus-quadratic AIC is **3.410883**. The optional quartic generating case asks a different question: adding −0.08a⁴ preserves the generating local share 2/3 but reduces the full-curve linear R² to **0.242406**. The last command generates that exploratory case and its fitted analyses; the stated 0.242406 is the exact generating R², independently checked by quadrature. A model-conditional bootstrap interval does not repair a wrong functional form.

After a complete default reproduction, `python code/check_results.py default` compares the observations and every bootstrap draw with the saved records, as well as the main-figure and simulation values.

## Additional tutorials and interactive tools

| Resource | Inputs, outputs and command | Scientific purpose |
|---|---|---|
| [Introductory notes, worksheet and slides](tutorials/introduction/) | `python tutorials/introduction/check_examples.py` checks the stated examples. `python tutorials/introduction/make_figures.py` rebuilds the three figures from synthetic count groups and Gaussian populations. | Distinguish observed counts from conditional means; compare shares 2/3 and 8/9 under variances 1 and 0.25; calculate selected-parent shifts 4/3 and 2. |
| [Two-trait geometry](tutorials/geometry/) | `bash tutorials/geometry/run.sh` writes the numerical cases, two-page figure and `rotate_the_cloud.html`. No external dataset is required. | Rotate, narrow or move the population. Comparison cases B and D have the same share 0.932720 through different combinations of spread and distance from the peak. All seven fixed examples are quadrature-checked. |
| [Parental contributions](tutorials/parental_weighting/) | `bash tutorials/parental_weighting/run.sh` recovers a fixed 20,000-parent cloud and reads the supplied 800-genotype observation/truth tables. It writes `data/results.json`, the cloud, figures and `explore_parental_cloud.html`. | Compare frequency weights, expected-output weights, linear-approximation weights and realised count weights. The observed example has 2,862 offspring and 88 zero-count parents. These remain parental contributions, not offspring breeding-value distributions. |
| [Shiny estimation app](examples/estimating_variance_share/README.md) | `bash run_shiny.sh` launches the local app using the same `model.py` and `plots.py` as the batch calculation. Its download records the displayed settings, observations, estimates and completed bootstrap draws. | Change measurement uncertainty, replication and model shape; compare estimated components with known generating values. New scenarios are exploratory cases. |

For rebuilding the typeset teaching documents and slides, use the document-build commands and dependencies in [REPRODUCING.md](REPRODUCING.md). Numerical reproduction does not require rebuilding those documents.
