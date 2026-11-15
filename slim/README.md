# Finite-population check of the Gaussian variance share

Twenty independent SLiM 5.2 replicates use seeds 42–61. Each follows a diploid population of 2,000 individuals for 200 generations. There are four traits, 50 loci per trait, no new mutations and a recombination rate of 0.5. The optimum moves along the first trait axis for 40 steps and then remains fixed. [The model](slim_sim_n_traits.slim) and [runner](run_simulations.sh) specify the initialisation, fitness function, parameters and seeds.

The [diagnostic tables](diagnostics/) contain **one row per generation in each replicate**. No external dataset is required for the default reproduction run. The Gaussian calculation uses the breeding-value covariance in that generation. The empirical squared correlation is evaluated over the simulated individuals. Allele frequencies can change; the simulation does not test the inheritance model with a fixed genic baseline.

| Column | Meaning |
|---|---|
| `gen`, `N` | Generation and population size |
| `a_bar_i`, `z_opt_i`, `b_i` | Trait i’s mean breeding value, optimum and local log-fitness slope |
| `G_ii`, `eig_G_i` | Trait variance and covariance eigenvalues; their sum gives total variance |
| `mu_i` | Eigenvalues of ΓG, with Γ = −H the stabilising curvature and G the breeding-value covariance |
| `V_lin`, `V_quad`, `A_g` | Gaussian linear variance, quadratic variance and their linear share |
| `R2_empirical`, `Ag_minus_R2` | Empirical squared correlation and signed difference from the Gaussian calculation |

`bash run_all.sh --simulate` regenerates raw individual breeding values and the optimum history, reconstructs every diagnostic table, then compares all 20 tables and their summary with the reference files. Use a location with room for **8 million individual-generation records**. [The comparison](../code/compare_simulations.py) uses a default absolute tolerance of 10⁻¹² for the same seeds and simulator version; [the diagnostic code](compute_diagnostics.py) records how each quantity is calculated.
