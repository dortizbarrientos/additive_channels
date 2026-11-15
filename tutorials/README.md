# Reading and teaching

Start with **[From fitness variation to selection](companion/companion.pdf)**, the short companion explaining the argument and its assumptions. For a reading route with adjustable examples and exercises, use the **[interactive study guide](interactive/README.md)**. The two cover related questions in different formats; there is no need to work through both before reading the paper.

## Paper supplements

| Resource | Purpose |
|---|---|
| [Supplementary File 1: mathematics guide](mathematics/guide.pdf) | Worked calculations, derivations and answers. |
| [Supplementary File 3: worked estimation](../examples/estimating_variance_share/worked_example.pdf) | Repeated measurements, offspring counts, fitting and uncertainty. |

## Figures, exercises and slides

These resources can be used on their own for a particular question or a class.

| Resource | Purpose |
|---|---|
| [Illustrated introduction](introduction/README.md) | Four-page notes, a worksheet with solutions, slides, editable PowerPoint and speaker notes. |
| [One curve and three populations](one_trait_visual/README.md) | Compare the one-trait populations in Appendix S7, Figure A1. |
| [Parental contributions](parental_weighting/README.md) | Compare population frequencies, expected reproductive contributions and recorded simulated counts. Includes an offline explorer and editable figures. |
| [Two-trait geometry](geometry/README.md) | Rotate breeding-value variation on a fixed surface. Includes the source for Appendix S7, Figure A2, an offline explorer and editable figures. |

The [result catalogue](../RESULTS.md) connects the paper and teaching examples to their code and saved values.

## Rebuild the materials

The supplied PDFs, slides and downloaded HTML files can be opened without running the code. From the repository root, `bash run_all.sh --visuals` rebuilds the visual modules and their offline explorers. `bash run_all.sh --tutorials` also compiles the teaching PDFs and introductory slides. The interactive study guide has its own build command.

[REPRODUCING.md](../REPRODUCING.md) gives the dependencies and exact commands, including the optional editable-figure exports.
