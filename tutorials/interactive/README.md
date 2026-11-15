# Interactive guide to additive channels

**[Download the HTML guide](Additive_channels_interactive_guide.html?raw=1)** and open the saved file in a browser. If GitHub displays its source, choose **Download raw file**. The explanations, controls and embedded records work without an internet connection. External source links need a connection.

The six lessons cover expected reproduction, the linear share, population variation, selection, estimation and inheritance. This is additional repository material, separate from the paper and its numbered supplementary files. The [short companion](../companion/companion.pdf) explains the main argument. The [reproduction instructions](../../REPRODUCING.md) and [result catalogue](../../RESULTS.md) identify the paper's calculations. [Reading versions 2 and 3](../../docs/VERSION_GUIDE.md) explains changes between preprint versions and the role of earlier material.

## Calculations and saved records

The sliders calculate the stated mathematical examples. The estimation lesson displays 12 rows from the archived simulated observations and all 500 saved bootstrap refits. Selecting a row or changing a teaching example does not rerun the estimator. The [Python estimation app](../../examples/estimating_variance_share/README.md) provides that separate function.

[reference_sources.json](src/reference_sources.json) identifies each source file by its path and SHA-256 hash. The [embedded reference record](src/scientific_reference.json) contains the scientific values, assumptions and source information. Its baseline hash confirms that these scientific records are unchanged from the preceding six-lesson guide. The mathematical model file is also checked by hash.

Source links open the current public repository paths. Their contents can be compared with the recorded hashes; a link to the main branch alone does not identify an exact version. Keep the downloaded guide and record the repository release or commit when reusing it, following the [citation instructions](../../README.md#cite-the-paper).

## Rebuild and check the guide

The editable lessons, styles, drawing code and numerical functions are in [src/](src/). The guide check also requires Node.js. From the repository root:

```bash
python -m pip install -r tutorials/interactive/requirements.txt
python tutorials/interactive/build_guide.py
python tutorials/interactive/src/validate_guide.py
```

The build checks the supplied source files before embedding the records. It works from a downloaded source tree or a new Git repository, without any earlier Git objects. It does not refit an analysis or install a browser framework.

To recreate the reference record and check the browser calculations, use the repository's numerical Python environment and Node.js:

```bash
python tutorials/interactive/src/extract_scientific_reference.py
python tutorials/interactive/src/validate_models.py
python tutorials/interactive/build_guide.py
python tutorials/interactive/src/validate_guide.py
```

The extractor reads only files whose bytes match the source manifest. It checks the saved observations, calibration, component identities, bootstrap percentiles and reference trajectories without refitting. The model checks use separate Gaussian quadrature, adaptive integration, matrix calculations and bracketed root finding. The guide check covers embedded data, local links, lesson structure and JavaScript syntax. These checks do not prove the analytical results.

If a source hash changes, review what changed before updating the manifest. Changes to numerical records or model assumptions also require review of the lesson text and the scientific baseline; the extractor does not silently replace saved estimates with new fits.

## Authorship

Daniel Ortiz-Barrientos prepared this additional guide with assistance from ChatGPT, using the [paper by Daniel Ortiz-Barrientos and Mark Cooper](https://doi.org/10.64898/2026.03.21.713332) and its documented calculations. Cite the paper for the scientific work and identify the repository version when reusing code or data. The lessons distinguish constructed examples, saved simulated results and proposed empirical work.
