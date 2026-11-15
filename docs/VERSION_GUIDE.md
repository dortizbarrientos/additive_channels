# Reading versions 2 and 3

*Additive Channels in Curved Fitness Landscapes* - Daniel Ortiz-Barrientos and Mark Cooper

This note compares [bioRxiv v2, posted on 7 June 2026](https://www.biorxiv.org/content/10.64898/2026.03.21.713332v2), with the manuscript prepared for v3. It was checked on 15 November 2026. The [paper DOI](https://doi.org/10.64898/2026.03.21.713332) identifies the preprint record.

## Changes in v3

Version 3 retains the Gaussian linear-quadratic variance partition and its regression interpretation. It makes the target explicit: log expected reproductive output conditional on breeding value, evaluated across the current population. “First-order variance share” replaces the broader “additivity index” to identify what the ratio measures. Proportional covariance change is treated as a controlled comparison, with the mean and fitness relationship held fixed.

Several changes correct claims in v2. A large share does not guarantee accurate rankings or selected-parent displacement, and it does not establish a general ceiling on gains from epistatic genomic prediction. V3 separates these questions. Its example has a 97% linear share but a 50% displacement error when curvature is omitted; a separate bound assesses that error (Section 4, Equations 18-20). The broader interpretations in v2 are superseded.

V3 also corrects the interpretation of gradient orientation after whitening: rotating the gradient leaves the share unchanged when its standardised length and the curvature eigenvalues are fixed. A proper selected distribution requires the combined precision, G⁻¹ + Γ, to be positive definite; stabilising curvature is sufficient but not necessary. Conversion from phenotype regressions proceeds through selected moments under explicit assumptions, replacing the shortcut that identified regression coefficients with local log-fitness derivatives (Section 3.4; Section 4; Section 6.1 and Appendix S5).

The inheritance analysis holds genic covariance fixed and separates selected parents from offspring. It establishes matrix fixed-point existence and bounds, with uniqueness and convergence proved for the scalar case. It does not establish mutation-selection balance or general predictions distinguishing breeding and natural populations. The retention parameter summarises a specified inheritance model; there is no universal conversion from selfing or recombination rates (Section 5 and Appendix S3). The broader GCA/SCA analogy and effective-dimension heuristic in v2 are not carried forward as established results.

V3 adds a worked estimation example using simulated measurements and offspring counts, including uncertainty in breeding values (Section 6 and Supplementary File 3).

## Useful material in v2

- **Gaussian phenotype-selection calculations:** Appendix S2, p. 20, “Level 2 derivation” and “Convergence of Level 2 to Level 1”. The matrix derivation remains useful under its stated Gaussian assumptions. V3 introduces conditional expected fitness directly and retains a scalar environmental-averaging example (Section 2; Appendix S2, Equation 45).
- **Historical reading pointers:** Appendix S7, pp. 27-28. V3 places the relevant foundations beside the results and summarises them in Appendix S6, Q2.
- **Extended replicate and covariance-spectrum plots:** Appendix S5, pp. 23-26. These remain archival explorations. Use v3, Appendix S4 and its reproduction files for the current simulation check. The broader validation claims are superseded; the older numerical summaries are outside the current validated results.

Use v3 for the current formulas, assumptions and scientific claims. The [short companion](../tutorials/companion/companion.pdf) explains the mathematical choices, and the [teaching collection](../tutorials/README.md) provides figures, exercises and interactive examples.
