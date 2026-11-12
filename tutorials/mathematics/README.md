# Why do slope and curvature contribute differently?

A linear term changes once with breeding value; a quadratic term changes with its square. To understand their variation, we need the distribution of breeding values as well as the fitness relationship. This guide derives the one-trait calculation before introducing vectors and matrices.

**[Read the mathematics guide](guide.pdf).** It includes worked numerical examples, checkpoints and answers. No prior calculus or linear algebra is required for the main reading path; optional sections develop the multivariate proofs.

## Follow the question through the calculations

1. **What is the fitness curve describing?** Start with average reproductive output at each breeding value, then take its logarithm. Distinguish this from the individual offspring count.
2. **How much does a line explain?** Derive the linear and quadratic variances under a Gaussian distribution. Compare populations on the same curve and include the fitted intercept.
3. **Does that fit justify dropping curvature for selection?** Calculate the selected-parent mean under reproductive weighting and examine the separate error bound.
4. **What happens in offspring?** Add the stated inheritance assumptions and follow the covariance recursion. Keep fixed allelic effects distinct from a fixed genic covariance.
5. **How does this connect to data?** Read the simulation and estimation sections, then use the [worked estimation example](../../examples/estimating_variance_share/README.md).
6. **What changes with several traits?** The final section explains covariance matrices, coordinate changes, orientation and the corresponding proofs.

The [result index](../../RESULTS.md) connects the scientific results to their code and numerical checks. The guide's section and equation numbers navigate its own derivations. Its appendix locators identify the corresponding formal results in *Additive Channels in Curved Fitness Landscapes*. The guide states the assumptions needed for each result; a local quadratic approximation is not automatically an exact selection model.

## Try a shorter route first

The [illustrated introduction and worksheet](../introduction/README.md) cover the central one-trait examples in a short class. The [one-trait visual walkthrough](../one_trait_visual/README.md) separates the curve, population density, fitted line and variance bars without matrices.

## Rebuild

From the repository root, `bash run_all.sh --tutorials` regenerates the guide figures and compiles the PDF along with the other teaching materials. See the [build requirements](../README.md#rebuild-the-materials). The editable source is [guide.tex](guide.tex), with [references.bib](references.bib) and the figures in [figures/](figures/).
