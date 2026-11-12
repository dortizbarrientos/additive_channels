# Can noisy height measurements recover a fitness relationship?

A plant's height measurements and offspring count are observable; its breeding value is not. This example uses repeated measurements to estimate that uncertainty, then asks how much variation in log expected reproduction a linear term can describe. Because the data are simulated, you can compare the estimated share with its known generating value.

[View the observed counts and fitted relationship](results/case1_relationship.pdf).

**[Read the worked example](worked_example.pdf)** or use the Shiny app to change the observations and model assumptions. Both call the same [estimation code](model.py).

## Launch the app on your computer

Download and unzip the repository, or clone it. With Python 3.11 or newer installed, open a terminal in the repository root and run:

```bash
bash run_shiny.sh
```

The launcher installs missing dependencies, including Shiny for Python, in a local environment. The first installation needs an internet connection. The app then runs locally; no R installation or hosted account is needed. A browser should open at **http://127.0.0.1:8000**. If it does not, open that address yourself. Keep the terminal running while you use the app and press **Ctrl-C** there to stop it.

If port 8000 is already in use, choose another:

```bash
SHINY_PORT=8001 bash run_shiny.sh
```

Then open **http://127.0.0.1:8001**. The app's **Read the worked example** link opens the accompanying PDF; **Download this case** saves the displayed data, settings, simulation truth, estimates and completed bootstrap draws.

## Try three questions

1. **How much does uncertain measurement matter?** Begin with the default case, then increase environmental variance or reduce the number of height measurements. Press **Generate and estimate** after changing a setting. In **Fit the mean**, compare measurement uncertainty; in **Calculate the share**, compare the two absolute variance components as well as their ratio. The naive analysis treats predicted breeding values as exact.
2. **How uncertain is the estimate under the fitted model?** In **Quantify uncertainty**, use 20 bootstrap replicates for a quick demonstration and press **Calculate intervals**. Use 500 to reproduce the reference interval. Every replicate repeats both stages of estimation. Generating a new dataset clears its old intervals.
3. **Can a narrow interval hide a poor model?** Select the fourth-order option, generate again, and open **Check the model**. The local quadratic share remains 2/3 for the generating parameters, but the linear fit to the complete log mean has an R² of about 0.2424. Compare the fitted curves and diagnostics; a bootstrap interval conditional on the quadratic model does not remove that mismatch.

The status banner identifies the displayed case and warns when changed settings have not yet been applied. A simulation seed reproduces the same data under the recorded software versions.

## What the default example represents

The simulation gives 800 unrelated plant genotypes three noisy measurements of height and one count of surviving offspring. The repeated measurements estimate breeding-value uncertainty; the count likelihood averages over it. Zero offspring counts remain in the analysis: the estimator does not take their logarithms.

Height is wholly additive in this teaching model, with independent measurement environments and an independent reproductive assay. Real clonal variation can include nonadditive and permanent environmental effects. These observations alone would not identify additive variance without the stated assumptions. The analysis describes the current population; it does not model inheritance or predict offspring breeding values.

## Check against the saved result

The default dataset contains 88 zero counts. Its estimated linear share is about **0.6107**, compared with the generating value **2/3**. The 500-replicate model-conditional 95% interval is approximately **0.5330–0.6857**. The component estimates and uncertainty record are supplied alongside that ratio.

| Reference file | Contents |
|---|---|
| [Observed data](results/observed_data.csv) | Genotype ID, one offspring count and three height deviations in centimetres: the estimator's inputs. |
| [Simulation truth](results/simulation_truth.csv) | True breeding value by ID, kept separate from the estimator. |
| [Estimates](results/estimates.csv) | Generating values, estimates, intervals and the comparison that treats predicted breeding values as exact. |
| [Bootstrap draws](results/bootstrap_draws.csv) | The 500 refits underlying the conditional interval. |
| [Numerical record](results/summary.json) | Settings, numerical integration checks, software versions and the data checksum. |

## Reproduce without the app

From the repository root:

```bash
bash run_estimation.sh
```

The default analysis writes a new result set to `outputs/estimation/`. For a quick demonstration with 20 bootstrap draws, use:

```bash
bash run_estimation.sh --bootstrap 20 --output outputs/demo
```

Twenty draws illustrate the procedure but are too few for a stable interval. The default seeds are 20261005 for the observations and 20261006 for the bootstrap. The [batch analysis](run_case.py) and [app](app.py) share `model.py`; the [numerical checks](test_model.py) compare the implementation with Gaussian moments, closed-form expected output and independent integration.

For the population-weighting ideas behind the estimator, return to the [visual walkthrough](../../tutorials/one_trait_visual/README.md) or [follow individual parents under reproductive weights](../../tutorials/parental_weighting/README.md).
