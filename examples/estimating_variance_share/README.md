# Estimate a variance share from offspring counts

[Read the worked example](worked_example.pdf) or run **`bash run_shiny.sh`** from the repository root. The app opens on your computer (normally `http://127.0.0.1:8000`). Stop it with Ctrl-C; use `SHINY_PORT=8001 bash run_shiny.sh` to choose another port. The launcher installs Shiny for Python when needed. No R installation is required.

The simulation gives each of 800 unrelated plant genotypes three noisy measurements of height and one count of surviving offspring. Repeated measurements estimate how uncertain the breeding values are. The count model integrates over that uncertainty; it does not take logarithms of individual counts. Height is wholly additive in this teaching example. In real clonal data, among-genotype differences can include nonadditive and persistent environmental effects.

| Reference file | Contents |
|---|---|
| [Observed data](results/observed_data.csv) | Genotype ID, one offspring count and three height deviations in centimetres. These are the estimator inputs. |
| [Simulation truth](results/simulation_truth.csv) | True breeding value by ID, kept separate from the estimator. |
| [Estimates](results/estimates.csv) | Generating values, estimates, intervals and the comparison that treats predicted breeding values as exact. |
| [Bootstrap draws](results/bootstrap_draws.csv) | The 500 refits underlying the model-conditional 95% interval. |
| [Numerical record](results/summary.json) | Generation settings, numerical integration checks, software versions and data checksum. |

**Reproduce:** `bash run_estimation.sh`. New files are written to `outputs/estimation/`. For a quick demonstration, use `bash run_estimation.sh --bootstrap 20 --output outputs/demo`; 20 draws are too few for a stable interval. The default seeds are 20261005 for the observations and 20261006 for the bootstrap.

**Explore:** change the measurement error or add a fourth-order term, then press **Generate and estimate**. A fourth-order term can change the fit over the population without changing the slope and curvature at the mean. The uncertainty interval is conditional on the fitted quadratic model. The [estimator](model.py), [batch analysis](run_case.py) and [app](app.py) share the same model code.
