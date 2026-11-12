# Additive channels in curved fitness landscapes

**Daniel Ortiz-Barrientos and Mark Cooper**

How much of the variation in log expected reproductive output can a straight line describe across the breeding values in a population? The answer depends on the fitness curve **and** on which breeding values are common. A close fit need not predict how far selection shifts the parental mean: in one example, the linear term explains 97% of variation on the log scale, yet ignoring curvature overestimates the shift by 50%.

This repository contains the data, code and teaching materials for answering those questions. The examples use **log expected reproductive output at a breeding value**: average offspring counts first, then take the logarithm. The variance share concerns a quadratic description of that relationship. It does not measure how accurately we can predict an individual’s offspring count or their offspring’s breeding value.

## Start here

| If you want to… | Start with… |
|---|---|
| See the additive channel without matrices | [Three one-trait populations](tutorials/one_trait_visual/README.md) · [figure](tutorials/one_trait_visual/figures/one_trait_additive_channel.pdf) |
| Explore two traits and population orientation | [Geometry guide](tutorials/geometry/README.md) · [two-page visual guide](tutorials/geometry/figures/geometry_of_additive_channels.pdf) · [offline explorer](tutorials/geometry/rotate_the_cloud.html) |
| Compare population frequencies and reproductive contributions | [Parental-weighting guide](tutorials/parental_weighting/README.md) · [offline explorer](tutorials/parental_weighting/explore_parental_cloud.html) |
| Understand the idea in one sitting | [Four-page illustrated introduction](tutorials/introduction/notes.pdf) |
| Work through or teach the example | [Worksheet and answers](tutorials/introduction/worksheet.pdf) · [lecture slides](tutorials/introduction/slides.pdf) · [editable PowerPoint](tutorials/introduction/slides.pptx) |
| Follow the derivations, from one trait to several | [Mathematics guide](tutorials/mathematics/guide.pdf) |
| Estimate the share from noisy measurements and offspring counts | [Worked example](examples/estimating_variance_share/worked_example.pdf) · [data and Shiny app](examples/estimating_variance_share/) |
| Find the data and code behind a particular result | [Result-by-result reproduction guide](REPRODUCING.md) |

## What the repository contains

| Material | Location and purpose |
|---|---|
| Main calculations | `code/` and `reference/`: generation of Figures 1–4, their numerical records, and checks of the mathematical identities. |
| Forward simulation | `slim/`: model, seeds, driver and 20 archived diagnostic tables. The archived-data summary runs without a SLiM installation. |
| Estimation | `examples/estimating_variance_share/`: simulated measurements and offspring counts, estimation code, 500-bootstrap reference results and the Shiny app. |
| Reading and teaching | `tutorials/`: introductory notes, worksheet, slides, mathematics guide, the one-trait appendix figure, two-trait geometry and parental weighting. The visual modules include source code and saved numerical results. |

The examples are mathematical or simulated populations. The teaching modules make population weighting and the additive representation explicit; they do not add a test of the inheritance model. Download either HTML explorer and open it in a browser; both operate without a server or an internet connection. The [teaching index](tutorials/README.md) suggests a reading order.

## Reproduce the results

From a checkout of this repository, run:

    bash run_all.sh

This regenerates Figures 1–4, checks the mathematical results, summarises the 20 archived SLiM diagnostic tables, and refits the simulated observations and all 500 bootstrap samples. It checks the outputs against the supplied reference values and writes new results to **outputs/**. Python 3.11 or newer and Bash are required. If the numerical packages are missing, the launcher installs them in a local virtual environment; the first installation then requires internet access. The default run does not need TeX, R, Shiny or SLiM.

| Command | What it does |
|---|---|
| `bash run_all.sh --quick` | Figures, mathematical examples and the archived simulation summary; skips the 500 bootstrap refits. |
| `bash run_estimation.sh` | Rebuild only the worked example, its interval, tables and figures. |
| `bash run_shiny.sh` | Open the interactive worked example locally. Change a setting, then select **Generate and estimate**. |
| `bash run_all.sh --simulate` | Run 20 fresh SLiM 5.2 replicates and compare them with the archived diagnostics. Requires the SLiM executable. |
| `bash tutorials/build_visuals.sh` | Rebuild the one-trait appendix figure, geometry plates and both offline explorers; uses the numerical Python dependencies. |
| `bash run_all.sh --tutorials` | Rebuild the teaching PDFs and slide deck. [Optional build dependencies](tutorials/README.md). |

The numerical libraries used for the reference calculation are listed in [requirements-tested.txt](requirements-tested.txt). The [licence](LICENSE) covers the code and accompanying documentation.
