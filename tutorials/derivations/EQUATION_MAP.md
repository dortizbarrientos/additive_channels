# Equation-by-equation derivation map

This map covers **106 source-qualified equation labels** in the main text, its mathematical appendices, the visual walkthrough, the mathematics guide and the worked estimation example. Each points to a definition, analytical derivation or worked calculation in the companion.

The identifiers are stable `eq:` labels in the source, rather than equation numbers that can change with formatting. The label `eq:Ag` occurs in two documents, so source identifiers distinguish those entries. The map records the versions inspected; it does not copy their prose or equation bodies.

Open [the PDF](derivations.pdf) for the linked equation map in Appendix A. The links below open editable chapter sources; each listed label locates the precise equation, proposition or section within its source.

## Treatment of the mapped material

- **Definition:** A definition, coefficient convention or explicitly stated model assumption; it is not an empirical theorem.
- **Proof:** An analytical derivation under stated assumptions. A scalar specialisation or immediate algebraic corollary may share its parent proof.
- **Calculation:** A stated numerical substitution, worked example, direct differentiation or fitted-model calculation. Numerical values are not substituted for proof.

## Source versions and coverage

| Source | Equation labels | Source basename | SHA-256 |
|---|---:|---|---|
| Main text and mathematical appendices | 37 | `manuscript_body.tex` | `316db758371dc5e28aca0af6df0557eb6bf97b3b6430fd0825b4f46dd4972715` |
| Appendix S7: visual walkthrough | 5 | `visual_walkthrough.tex` | `6dbddb4283e74186ea3c96d85060df81e5dd113f34d1b7bfa9f5ea605d19505f` |
| Supplementary File 1: mathematics guide | 49 | `Supplementary_File_1_Mathematics_Guide.tex` | `e164c77a9e27c1e6cd31408106fb00231648f51b949449ae951e8b723999e86c` |
| Supplementary File 3: worked estimation | 15 | `Supplementary_File_3_Worked_Estimation.tex` | `a63dbcb19f84da2554c64159239101b1d44589ba216003fa3df283aa45806b62` |

The source versions were inspected on **2026-11-13**. The navigation checker validates this recorded inventory and its companion targets; it does not re-read external source documents or prove the results.

## Main text and mathematical appendices

| Source equation label | Mathematical concept | Treatment | Companion derivation |
|---|---|---|---|
| `eq:target` | Conditional expected reproduction and its logarithm | definition | `conditioning:target` ([source](chapters/01_conditioning.tex)); `conditioning:log_target` ([source](chapters/01_conditioning.tex)) |
| `eq:selection_weight` | Normalised reproductive weighting of parental frequencies | proof + definition | `conditioning:selection_weight` ([source](chapters/01_conditioning.tex)); `conditioning:selected_density` ([source](chapters/01_conditioning.tex)) |
| `eq:log_ratio` | Log differences as proportional changes in conditional mean output | proof | `conditioning:log_ratio` ([source](chapters/01_conditioning.tex)) |
| `eq:jensen` | Noncommutation of averaging and taking logarithms | proof | `conditioning:jensen` ([source](chapters/01_conditioning.tex)); `conditioning:jensen_inequality` ([source](chapters/01_conditioning.tex)) |
| `eq:taylor` | Local quadratic expansion of log conditional expected output | definition + proof | `gaussian:quadratic_definition` ([source](chapters/02_gaussian_projection.tex)); `gaussian:taylor_derivation` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:centered_terms` | Mean-centred quadratic component | definition + proof | `gaussian:terms` ([source](chapters/02_gaussian_projection.tex)); `gaussian:quadratic_mean` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:vlin` | Variance of the linear component | proof | `gaussian:linear_variance` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:vquad` | Gaussian variance of the quadratic component | proof | `gaussian:four_index_variance` ([source](chapters/02_gaussian_projection.tex)); `gaussian:quadratic_variance` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:Ag` | First-order share of quadratic log-target variance | definition | `gaussian:share` ([source](chapters/02_gaussian_projection.tex)); `gaussian:variance_partition` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:affine_projection` | Population affine projection and curvature-adjusted intercept | proof | `gaussian:affine_projection` ([source](chapters/02_gaussian_projection.tex)); `gaussian:fitted_affine` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:r2_identity` | Regression and squared-correlation interpretations of the share | proof | `gaussian:regression_share` ([source](chapters/02_gaussian_projection.tex)); `gaussian:correlation_identity` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:nested_r2` | Ratio of nested fit statistics and the complementary fraction | proof | `gaussian:nested_r2` ([source](chapters/02_gaussian_projection.tex)); `gaussian:nested_ratio` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:scaling` | Linear and quadratic components under proportional covariance scaling | proof | `geometry:scaling_proposition` ([source](chapters/03_geometry.tex)); `geometry:component_scaling` ([source](chapters/03_geometry.tex)) |
| `eq:whitening` | Gradient and Hessian in population-standardised coordinates | definition + proof | `geometry:whitened_coefficients` ([source](chapters/03_geometry.tex)); `geometry:spectral_components` ([source](chapters/03_geometry.tex)) |
| `eq:log_quadratic_weight` | Exact quadratic reproductive-weight model | definition | `selection:model` ([source](chapters/04_selection.tex)); `selection:log_quadratic_weight` ([source](chapters/04_selection.tex)) |
| `eq:selected_mean` | Exact selected-parent mean displacement | proof | `selection:selected_moments` ([source](chapters/04_selection.tex)); `selection:moment_formulas` ([source](chapters/04_selection.tex)) |
| `eq:selected_covariance` | Exact covariance under parental reproductive weights | proof | `selection:selected_moments` ([source](chapters/04_selection.tex)); `selection:moment_formulas` ([source](chapters/04_selection.tex)) |
| `eq:counterexample` | Large variance share with a one-half displacement overestimate | calculation | `selection:97_50_example` ([source](chapters/04_selection.tex)); `worked:guide` ([source](chapters/08_worked_results.tex)) |
| `eq:T` | Population-scaled stabilising curvature | definition | `selection:T` ([source](chapters/04_selection.tex)); `selection:precision_factorisation` ([source](chapters/04_selection.tex)) |
| `eq:response_bound` | Covariance-scaled relative displacement-error bound | proof | `selection:relative_bound` ([source](chapters/04_selection.tex)); `selection:full_bound` ([source](chapters/04_selection.tex)) |
| `eq:fixedB_recursion` | Covariance update under fixed genic baseline and association retention | definition + proof | `inheritance:retention-assumption` ([source](chapters/05_inheritance.tex)); `inheritance:recursion` ([source](chapters/05_inheritance.tex)) |
| `eq:genic_baseline` | Genic covariance from allele frequencies and fixed allelic effects | proof | `inheritance:genic-formula` ([source](chapters/05_inheritance.tex)); `inheritance:association-decomposition` ([source](chapters/05_inheritance.tex)) |
| `eq:loewner_interval` | Invariant order interval for the covariance map | definition + proof | `inheritance:interval` ([source](chapters/05_inheritance.tex)); `inheritance:invariance` ([source](chapters/05_inheritance.tex)) |
| `eq:fixedpoint_bounds` | Bounds on every positive covariance fixed point | proof | `inheritance:existence` ([source](chapters/05_inheritance.tex)); `inheritance:fixed-bounds` ([source](chapters/05_inheritance.tex)) |
| `eq:scalar_recursion` | One-trait or isotropic covariance update | definition + proof | `inheritance:scalar-map` ([source](chapters/05_inheritance.tex)); `inheritance:scalar` ([source](chapters/05_inheritance.tex)) |
| `eq:scalar_root` | Unique positive scalar covariance fixed point | proof | `inheritance:scalar-quadratic` ([source](chapters/05_inheritance.tex)); `inheritance:positive-root` ([source](chapters/05_inheritance.tex)) |
| `eq:rho_one` | Precision accumulation with complete association retention | proof | `inheritance:precision-iteration` ([source](chapters/05_inheritance.tex)); `inheritance:rho-one` ([source](chapters/05_inheritance.tex)) |
| `eq:log_error_model` | Observation model with a constant conditional log gap | definition + proof | `conditioning:constant_gap` ([source](chapters/01_conditioning.tex)); `gaussian:noise_model` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:ebv_inflation` | Share after substituting shrunken prediction covariance | proof | `estimation:shrinkage_formula` ([source](chapters/06_estimation.tex)); `estimation:shrinkage_share` ([source](chapters/06_estimation.tex)) |
| `eq:LA_regression` | Raw relative-fitness phenotype regression and quadratic convention | definition | `conversion:regression_model` ([source](chapters/07_phenotype_conversion.tex)); `conversion:coefficient_convention` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:LA_conversion` | Conversion of selected moments into log-quadratic parameters | proof | `conversion:selected_formula` ([source](chapters/07_phenotype_conversion.tex)); `conversion:conversion_formula` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:fitness_model` | Phenotype-fitness model with independent Gaussian environment | definition | `conditioning:phenotype_fitness` ([source](chapters/01_conditioning.tex)); `conditioning:environmental_average` ([source](chapters/01_conditioning.tex)) |
| `eq:environmental_average` | Gaussian environmental convolution of the fitness curve | proof | `conditioning:environment_formula` ([source](chapters/01_conditioning.tex)); `conditioning:environmental_average` ([source](chapters/01_conditioning.tex)) |
| `eq:precision_order` | Inverse-order covariance contraction under stabilising curvature | proof | `inheritance:inverse-order` ([source](chapters/05_inheritance.tex)); `inheritance:selection-order` ([source](chapters/05_inheritance.tex)) |
| `eq:LA_moments` | Phenotype-regression normalisation and selected moments | proof | `conversion:regression_moments` ([source](chapters/07_phenotype_conversion.tex)); `conversion:phenotype_moment_formula` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:LA_selected_mean` | Selected breeding-value mean from phenotype regression | proof | `conversion:selected_breeding_moments` ([source](chapters/07_phenotype_conversion.tex)); `conversion:selected_formula` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:LA_selected_cov` | Selected breeding-value covariance from phenotype regression | proof | `conversion:selected_breeding_moments` ([source](chapters/07_phenotype_conversion.tex)); `conversion:selected_formula` ([source](chapters/07_phenotype_conversion.tex)) |

## Appendix S7: visual walkthrough

| Source equation label | Mathematical concept | Treatment | Companion derivation |
|---|---|---|---|
| `eq:visual_model` | Fixed one-trait curve and Gaussian populations | definition | `worked:one_trait` ([source](chapters/08_worked_results.tex)) |
| `eq:visual_variances` | Variance components for the three one-trait populations | calculation + proof | `worked:one_trait` ([source](chapters/08_worked_results.tex)); `gaussian:variance_formulas` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:visual_line` | Population-fitted line for the one-trait walkthrough | calculation + proof | `worked:one_trait` ([source](chapters/08_worked_results.tex)); `gaussian:fitted_affine` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:visual_rotation_surface` | Two-trait surface expressed along and across the gradient | definition + calculation | `worked:rotation` ([source](chapters/08_worked_results.tex)); `geometry:rotation_formula` ([source](chapters/03_geometry.tex)) |
| `eq:visual_rotation_variances` | Full-population components under physical covariance rotation | calculation + proof | `worked:rotation` ([source](chapters/08_worked_results.tex)); `geometry:rotation_formula` ([source](chapters/03_geometry.tex)) |

## Supplementary File 1: mathematics guide

| Source equation label | Mathematical concept | Treatment | Companion derivation |
|---|---|---|---|
| `eq:guide-target` | Conditional expected reproductive output | definition | `conditioning:target` ([source](chapters/01_conditioning.tex)) |
| `eq:guide-log-target` | Logarithm of conditional expected output | definition | `conditioning:log_target` ([source](chapters/01_conditioning.tex)) |
| `eq:guide-jensen` | Averaging versus logging individual outputs | proof | `conditioning:jensen` ([source](chapters/01_conditioning.tex)); `conditioning:jensen_inequality` ([source](chapters/01_conditioning.tex)) |
| `eq:guide-selection-weight` | Normalised reproductive weighting of breeding values | proof + definition | `conditioning:selection_weight` ([source](chapters/01_conditioning.tex)); `conditioning:selected_density` ([source](chapters/01_conditioning.tex)) |
| `eq:guide-phenotype-fitness` | The guide's Gaussian phenotype-fitness example | definition + calculation | `conditioning:phenotype_fitness` ([source](chapters/01_conditioning.tex)); `worked:guide` ([source](chapters/08_worked_results.tex)) |
| `eq:guide-environmental-average` | Conditional mean for the guide's environmental parameters | proof + calculation | `conditioning:environment_formula` ([source](chapters/01_conditioning.tex)); `worked:guide` ([source](chapters/08_worked_results.tex)) |
| `eq:guide-quadratic-example` | Expansion of the guide's exact quadratic log mean | calculation | `worked:guide` ([source](chapters/08_worked_results.tex)); `conditioning:environment_derivatives` ([source](chapters/01_conditioning.tex)) |
| `eq:guide-finite-slope` | Symmetric finite-difference estimate of slope | calculation + proof | `worked:guide` ([source](chapters/08_worked_results.tex)); `gaussian:taylor_derivation` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-finite-curvature` | Symmetric second difference for curvature | calculation + proof | `worked:guide` ([source](chapters/08_worked_results.tex)); `gaussian:taylor_derivation` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-local-description` | One-trait quadratic approximation | definition + proof | `gaussian:quadratic_definition` ([source](chapters/02_gaussian_projection.tex)); `gaussian:taylor_derivation` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-environmental-integral` | Integral over environmental deviations in the guide example | definition + proof | `conditioning:environment_integral` ([source](chapters/01_conditioning.tex)); `conditioning:environmental_average` ([source](chapters/01_conditioning.tex)) |
| `eq:guide-general-completing-square` | Completing the environmental square | proof | `conditioning:environmental_average` ([source](chapters/01_conditioning.tex)) |
| `eq:guide-environmental-average-general` | General Gaussian environmental convolution | proof | `conditioning:environment_formula` ([source](chapters/01_conditioning.tex)); `conditioning:environmental_average` ([source](chapters/01_conditioning.tex)) |
| `eq:guide-normal-moments` | Centred Gaussian moments through order four | proof | `gaussian:mgf_derivatives` ([source](chapters/02_gaussian_projection.tex)); `gaussian:fourth_moment` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-centered-Q` | Centred scalar quadratic component | definition + proof | `gaussian:terms` ([source](chapters/02_gaussian_projection.tex)); `gaussian:quadratic_mean` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-vlin-one` | Scalar linear variance | proof | `gaussian:linear_variance` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-vquad-one` | Scalar quadratic variance | proof | `gaussian:quadratic_variance` ([source](chapters/02_gaussian_projection.tex)); `gaussian:fourth_moment` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-correlation` | Squared correlation between the linear term and full quadratic target | proof | `gaussian:correlation_identity` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:Ag` | First-order variance share | definition | `gaussian:share` ([source](chapters/02_gaussian_projection.tex)); `gaussian:singular_support` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-projection` | Population affine-regression R-squared equals the share | proof | `gaussian:regression_share` ([source](chapters/02_gaussian_projection.tex)); `gaussian:affine_projection` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-one-trait-slope` | Scalar least-squares slope equals the local slope under Gaussian quadratic conditions | proof | `gaussian:normal_equations` ([source](chapters/02_gaussian_projection.tex)); `gaussian:affine_projection` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-nested-r2` | Ratio of noisy affine and quadratic fit statistics | proof | `gaussian:nested_r2` ([source](chapters/02_gaussian_projection.tex)); `gaussian:nested_ratio` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-scaling` | Proportional covariance scaling of the two components | proof | `geometry:component_scaling` ([source](chapters/03_geometry.tex)); `geometry:scaling_proposition` ([source](chapters/03_geometry.tex)) |
| `eq:guide-selected-moments` | Scalar selected-parent variance and mean shift | proof | `selection:scalar_moments` ([source](chapters/04_selection.tex)); `selection:selected_moments` ([source](chapters/04_selection.tex)) |
| `eq:guide-response-bound-one` | One-dimensional curvature bound on relative displacement error | proof + calculation | `selection:scalar_relative_error` ([source](chapters/04_selection.tex)); `selection:full_bound` ([source](chapters/04_selection.tex)) |
| `eq:guide-recursion` | Scalar fixed-baseline inheritance closure | definition + proof | `inheritance:scalar-map` ([source](chapters/05_inheritance.tex)); `inheritance:retention-assumption` ([source](chapters/05_inheritance.tex)) |
| `eq:guide-scalar-bounds` | Numerical endpoints of the scalar invariant interval | calculation + proof | `inheritance:fixed-bounds` ([source](chapters/05_inheritance.tex)); `inheritance:scalar-boundaries` ([source](chapters/05_inheritance.tex)) |
| `eq:guide-general-fixedpoint-quadratic` | Polynomial satisfied by the scalar equilibrium | proof | `inheritance:scalar-quadratic` ([source](chapters/05_inheritance.tex)) |
| `eq:guide-scalar-root` | Positive scalar equilibrium root | proof | `inheritance:positive-root` ([source](chapters/05_inheritance.tex)); `inheritance:rationalised-root` ([source](chapters/05_inheritance.tex)) |
| `eq:guide-contraction` | Exact distance formula and scalar contraction inequality | proof | `inheritance:contraction` ([source](chapters/05_inheritance.tex)); `inheritance:contraction-bound` ([source](chapters/05_inheritance.tex)) |
| `eq:guide-rho-one` | Scalar precision after repeated updates with full retention | proof | `inheritance:precision-iteration` ([source](chapters/05_inheritance.tex)); `inheritance:rho-one` ([source](chapters/05_inheritance.tex)) |
| `eq:guide-LA` | Scalar phenotype regression of relative fitness | definition | `conversion:regression_model` ([source](chapters/07_phenotype_conversion.tex)); `conversion:coefficient_convention` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:guide-intercept` | Relative-fitness intercept and its numerical value | proof + calculation | `conversion:phenotype_moment_formula` ([source](chapters/07_phenotype_conversion.tex)); `conversion:scalar_example` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:guide-first-moment` | First selected phenotype moment | proof | `conversion:regression_moments` ([source](chapters/07_phenotype_conversion.tex)); `conversion:phenotype_moment_formula` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:guide-second-moment` | Second selected phenotype moment | proof | `conversion:regression_moments` ([source](chapters/07_phenotype_conversion.tex)); `conversion:phenotype_moment_formula` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:guide-conditional-A-one` | Breeding-value mean and variance conditional on phenotype | proof | `conversion:conditional_moments` ([source](chapters/07_phenotype_conversion.tex)); `conversion:conditional_formula` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:guide-BV-moments` | Selected breeding-value moments in one trait | proof | `conversion:selected_formula` ([source](chapters/07_phenotype_conversion.tex)); `conversion:scalar_example` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:guide-conversion-one` | Scalar inversion from selected moments to log-quadratic parameters | proof + calculation | `conversion:conversion_formula` ([source](chapters/07_phenotype_conversion.tex)); `conversion:scalar_numbers` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:guide-ebv` | Share under fixed-coefficient prediction-variance substitution | proof + calculation | `estimation:shrinkage_share` ([source](chapters/06_estimation.tex)); `estimation:shrinkage` ([source](chapters/06_estimation.tex)) |
| `eq:guide-trace-reduction` | Four-index reduction of quadratic variance to a trace | proof | `gaussian:four_index_variance` ([source](chapters/02_gaussian_projection.tex)); `gaussian:quadratic_variance` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-multi-variances` | Multivariate linear variance, quadratic variance and orthogonality | proof | `gaussian:variance_formulas` ([source](chapters/02_gaussian_projection.tex)); `gaussian:orthogonality` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:guide-multi-selected` | Multivariate selected-parent mean and covariance | proof | `selection:selected_moments` ([source](chapters/04_selection.tex)); `selection:moment_formulas` ([source](chapters/04_selection.tex)) |
| `eq:guide-whitened-full` | Exact selected displacement in covariance-scaled coordinates | proof | `selection:whitened_error_identity` ([source](chapters/04_selection.tex)); `selection:precision_factorisation` ([source](chapters/04_selection.tex)) |
| `eq:guide-whitened-error` | Displacement error in covariance-scaled coordinates | proof | `selection:whitened_error_identity` ([source](chapters/04_selection.tex)) |
| `eq:guide-multi-bound` | Relative displacement bound and Frobenius upper bound | proof | `selection:relative_bound` ([source](chapters/04_selection.tex)); `selection:full_bound` ([source](chapters/04_selection.tex)) |
| `eq:guide-genic-baseline` | Multitrait genic covariance from loci | proof | `inheritance:genic-formula` ([source](chapters/05_inheritance.tex)); `inheritance:genic` ([source](chapters/05_inheritance.tex)) |
| `eq:guide-matrix-interval-map` | Invariance of the covariance order interval | proof | `inheritance:invariance` ([source](chapters/05_inheritance.tex)); `inheritance:existence` ([source](chapters/05_inheritance.tex)) |
| `eq:guide-multi-conditioning` | Multivariate breeding-value conditioning on phenotype | proof | `conversion:conditional_moments` ([source](chapters/07_phenotype_conversion.tex)); `conversion:conditional_second` ([source](chapters/07_phenotype_conversion.tex)) |
| `eq:guide-multi-raw-derivatives` | Derivatives of the logged phenotype-regression polynomial | proof | `conversion:raw_derivatives` ([source](chapters/07_phenotype_conversion.tex)); `conversion:raw_log` ([source](chapters/07_phenotype_conversion.tex)) |

## Supplementary File 3: worked estimation

| Source equation label | Mathematical concept | Treatment | Companion derivation |
|---|---|---|---|
| `eq:A` | Gaussian latent breeding-value population in the estimation example | definition | `estimation:model` ([source](chapters/06_estimation.tex)); `estimation:measurement_model` ([source](chapters/06_estimation.tex)) |
| `eq:measurement` | Repeated noisy trait measurements | definition | `estimation:measurement_model` ([source](chapters/06_estimation.tex)); `estimation:model` ([source](chapters/06_estimation.tex)) |
| `eq:count` | Conditional Poisson reproductive-count model | definition | `estimation:count_model` ([source](chapters/06_estimation.tex)); `estimation:model` ([source](chapters/06_estimation.tex)) |
| `eq:surface` | Quadratic log conditional expected count | definition | `estimation:count_model` ([source](chapters/06_estimation.tex)) |
| `eq:linear` | Generating linear variance in the worked example | calculation + proof | `estimation:components` ([source](chapters/06_estimation.tex)); `gaussian:linear_variance` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:quadratic` | Generating quadratic variance in the worked example | calculation + proof | `estimation:components` ([source](chapters/06_estimation.tex)); `gaussian:quadratic_variance` ([source](chapters/02_gaussian_projection.tex)) |
| `eq:share` | Generating variance share in the worked example | calculation | `estimation:components` ([source](chapters/06_estimation.tex)); `worked:estimation` ([source](chapters/08_worked_results.tex)) |
| `eq:Ehat` | Unbiased within-genotype measurement-variance calibration | proof | `estimation:anova_calibration` ([source](chapters/06_estimation.tex)); `estimation:calibration_estimators` ([source](chapters/06_estimation.tex)) |
| `eq:Ghat` | Unbiased between-genotype variance calibration | proof | `estimation:anova_calibration` ([source](chapters/06_estimation.tex)); `estimation:calibration_estimators` ([source](chapters/06_estimation.tex)) |
| `eq:shrink` | Calibrated prediction reliability and centred conditional mean | proof + calculation | `estimation:posterior` ([source](chapters/06_estimation.tex)); `estimation:reliability_identities` ([source](chapters/06_estimation.tex)) |
| `eq:posterior` | Normal latent distribution conditional on repeated measurements | proof | `estimation:posterior_formula` ([source](chapters/06_estimation.tex)); `estimation:posterior` ([source](chapters/06_estimation.tex)) |
| `eq:likelihood` | Poisson likelihood integrated over uncertain breeding value | proof | `estimation:mixture_likelihood` ([source](chapters/06_estimation.tex)); `estimation:likelihood` ([source](chapters/06_estimation.tex)) |
| `eq:derivatives` | Slope and curvature of the fitted quadratic log mean | proof + calculation | `estimation:components` ([source](chapters/06_estimation.tex)) |
| `eq:quarticvar` | Complete even-part variance with a quartic term | proof | `estimation:quartic_variance` ([source](chapters/06_estimation.tex)); `estimation:quartic_full_r2` ([source](chapters/06_estimation.tex)) |
| `eq:quarticR2` | Full-curve affine R-squared for the quartic generating function | proof + calculation | `estimation:quartic_full_r2` ([source](chapters/06_estimation.tex)); `estimation:quartic` ([source](chapters/06_estimation.tex)) |

## Unlabelled intermediate displays

The review also covered **87 unlabelled displays**. Reviewed top-level equation/align/gather/multline and display-bracket blocks without an eq: label; repeated and intermediate displays are grouped by concept below. TeX linebreaks followed by bracketed spacing are excluded.

| Mathematical concept | Companion labels | Coverage note |
|---|---|---|
| Basic variance/covariance definitions; linear and centred quadratic terms | `gaussian:terms` ([source](chapters/02_gaussian_projection.tex)); `gaussian:linear_variance` ([source](chapters/02_gaussian_projection.tex)); `gaussian:product_covariance` ([source](chapters/02_gaussian_projection.tex)) | Definitions are used explicitly in the component and product-covariance expansions. |
| Environmental square completion and scalar guide parameters | `conditioning:environmental_average` ([source](chapters/01_conditioning.tex)); `worked:guide` ([source](chapters/08_worked_results.tex)) | Both the general integral and its scalar numerical substitutions are covered. |
| Gaussian product moments, odd-moment cancellation and variance addition | `gaussian:fourth_moment` ([source](chapters/02_gaussian_projection.tex)); `gaussian:product_covariance` ([source](chapters/02_gaussian_projection.tex)); `gaussian:orthogonality` ([source](chapters/02_gaussian_projection.tex)) | All intermediate moment identities belong to the detailed variance proof. |
| Affine normal equations and intercept adjustment | `gaussian:normal_equations` ([source](chapters/02_gaussian_projection.tex)); `gaussian:fitted_affine` ([source](chapters/02_gaussian_projection.tex)) | The projection proof supplies the minimisation argument as well as the coefficients. |
| Noisy fit statistics and complementary explained fraction | `gaussian:nested_ratio` ([source](chapters/02_gaussian_projection.tex)); `gaussian:noisy_response` ([source](chapters/02_gaussian_projection.tex)) | The numerical example and ratio complement follow from the shared variance denominator. |
| Trait-unit transformations, spectral components and Rayleigh bounds | `geometry:coordinate_invariance` ([source](chapters/03_geometry.tex)); `geometry:spectral_components` ([source](chapters/03_geometry.tex)); `geometry:rayleigh_bound` ([source](chapters/03_geometry.tex)) | Coordinate changes, physical orientation and equality conditions are distinguished. |
| Combined precision, square completion and selected-parent displacement | `selection:combined_precision` ([source](chapters/04_selection.tex)); `selection:completed_square` ([source](chapters/04_selection.tex)); `selection:scalar_moments` ([source](chapters/04_selection.tex)) | The exact distribution is normalised before its moments are read off. |
| Whitened full displacement, error vector and matrix norms | `selection:whitened_error_identity` ([source](chapters/04_selection.tex)); `selection:full_bound` ([source](chapters/04_selection.tex)) | The general bound and scalar equality case are derived. |
| Covariance interval, every-fixed-point bounds and scalar equilibrium steps | `inheritance:invariance` ([source](chapters/05_inheritance.tex)); `inheritance:existence` ([source](chapters/05_inheritance.tex)); `inheritance:scalar-quadratic` ([source](chapters/05_inheritance.tex)) | All unlabelled intermediate algebra is expanded in the inheritance proof. |
| Scalar guide iterations and complete-retention precision updates | `inheritance:scalar-boundaries` ([source](chapters/05_inheritance.tex)); `inheritance:precision-iteration` ([source](chapters/05_inheritance.tex)) | Exact rational iterates and the no-restoration boundary are included. |
| Regression-selected moments and inverse parameter conversion | `conversion:phenotype_moment_formula` ([source](chapters/07_phenotype_conversion.tex)); `conversion:selected_formula` ([source](chapters/07_phenotype_conversion.tex)); `conversion:conversion_formula` ([source](chapters/07_phenotype_conversion.tex)) | The conditional-variance term and matrix multiplication order are retained. |
| Logged raw-regression derivatives and numerical checkpoint | `conversion:raw_derivatives` ([source](chapters/07_phenotype_conversion.tex)); `conversion:scalar_example` ([source](chapters/07_phenotype_conversion.tex)) | The two conversion targets are explicitly separated. |
| Multivariate component example and finite-difference checkpoint arithmetic | `worked:main3` ([source](chapters/08_worked_results.tex)); `worked:guide` ([source](chapters/08_worked_results.tex)) | Numerical substitutions are shown separately from the population proofs. |

## Notation between resources

- The one-trait visual calculation uses m and v in the companion where S7 uses mu and g.
- The estimation chapter distinguishes centred latent X from the population mean; SF3 uses A in its zero-mean generating model and Z for the centred fitted latent value.
- Prediction reliability is R_pred in the companion; reproductive count is R_i. This separates the two meanings represented by r and W in SF3.
- The inheritance scalar gamma and the phenotype-regression gamma belong to different models; their definitions are retained locally.

The [JSON map](equation_map.json) retains the individual qualifications and the source metadata. The [result map](RESULT_MAP.md) adds biological questions and reproduction resources.
