"""Draw the home-page illustration from the one-trait model.

The fitness curve and Gaussian populations are the same as in the one-trait
tutorial. The two rows separate log expected reproduction from population
frequency. All three variance shares are checked against the saved tutorial
values before the PNG and SVG are written. No images or fonts are downloaded.

Run ``python code/build_readme_visuals.py`` from any directory.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "docs" / "images"
INK, MUTED, PALE = "#173c48", "#5c7380", "#b7cbd1"
BACKGROUND = "#f6faf9"


def build() -> None:
    """Compare population-fitted lines, densities and variance shares."""
    saved = json.loads((ROOT / "tutorials/one_trait_visual/values.json").read_text())["cases"]
    cases = [
        ("A", "Broader variation", 0.0, 1.0, "#176780"),
        ("B", "Less variation, same mean", 0.0, 0.1, "#ba572a"),
        ("C", "Same narrow range, at the peak", 1.0, 0.1, "#80608f"),
    ]
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "text.color": INK, "axes.labelcolor": MUTED,
        "axes.edgecolor": PALE, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.spines.top": False, "axes.spines.right": False,
        "svg.fonttype": "none", "svg.hashsalt": "additive-channels-overview",
    })
    figure = plt.figure(figsize=(13.5, 6.2), facecolor=BACKGROUND)
    grid = figure.add_gridspec(2, 3, left=0.080, right=0.975, bottom=0.23,
        top=0.78, height_ratios=[2.2, 1.0], hspace=0.20, wspace=0.28)
    figure.text(0.080, 0.935, "One fitness curve. Different populations.",
                fontsize=23, weight="bold")
    figure.text(0.080, 0.882,
                "Which breeding values are common changes the linear description.",
                fontsize=12, color=MUTED)
    x = np.linspace(-2.3, 2.7, 1000)
    curve = x - x * x / 2
    for column, (key, title, mean, variance, colour) in enumerate(cases):
        # For A = mean + X, the affine fit is E[ell(A)] + (1-mean)X.
        # Its intercept includes the average curvature contribution.
        slope = 1 - mean
        fitted_at_mean = mean - mean * mean / 2 - variance / 2
        linear, quadratic = slope * slope * variance, variance * variance / 2
        share = linear / (linear + quadratic)
        np.testing.assert_allclose([linear, quadratic, share],
            [saved[key]["V_linear"], saved[key]["V_quadratic"], saved[key]["linear_share"]],
            rtol=1e-13, atol=1e-14)
        fitted = fitted_at_mean + slope * (x - mean)
        low, high = norm.ppf([0.025, 0.975], loc=mean, scale=np.sqrt(variance))
        central = (x >= low) & (x <= high)
        upper = figure.add_subplot(grid[0, column], facecolor=BACKGROUND)
        upper.set_title(title, fontsize=12, weight="bold", loc="left", pad=13)
        upper.plot(x, curve, color=INK, alpha=0.24, lw=1.5)
        upper.plot(x[central], curve[central], color=INK, lw=2.5)
        upper.plot(x[central], fitted[central], color=colour, lw=2.2, ls="--")
        upper.axvline(mean, color=PALE, lw=0.9, ls=":")
        upper.set(xlim=(-2.3, 2.7), ylim=(-5.2, 2.4), yticks=[-4, -2, 0, 2])
        upper.tick_params(axis="x", bottom=False, labelbottom=False)
        if column == 0:
            upper.set_ylabel("Log expected\nreproductive output", fontsize=11)
        else:
            upper.tick_params(axis="y", labelleft=False)
        lower = figure.add_subplot(grid[1, column], facecolor=BACKGROUND, sharex=upper)
        density = norm.pdf(x, loc=mean, scale=np.sqrt(variance))
        lower.fill_between(x, density, color=colour, alpha=0.17)
        lower.plot(x, density, color=colour, lw=2)
        lower.axvline(mean, color=PALE, lw=0.9, ls=":")
        lower.set(ylim=(0, 1.4), yticks=[0, 1], xticks=[-2, -1, 0, 1, 2],
                  xlabel="Breeding value for height")
        if column == 0:
            lower.set_ylabel("Population\ndensity", fontsize=11)
        else:
            lower.tick_params(axis="y", labelleft=False)
        position = lower.get_position()
        figure.text(position.x0, 0.105, f"{share:.1%}", fontsize=25,
                    color=colour, weight="bold")
        figure.text(position.x0 + 0.103, 0.112, "linear share", fontsize=12, color=MUTED)
    legend = [Line2D([0], [0], color=INK, lw=2, label="Same fitness curve"),
              Line2D([0], [0], color=MUTED, lw=2, ls="--", label="Population-fitted line")]
    figure.legend(handles=legend, loc="lower left", bbox_to_anchor=(0.075, 0.015),
                  ncol=2, frameon=False, fontsize=10)
    figure.text(0.575, 0.042,
                "Dark curves span 95% of each population; calculations use all values.",
                fontsize=8.5, color=MUTED)
    DESTINATION.mkdir(parents=True, exist_ok=True)
    figure.savefig(DESTINATION / "additive_channels_overview.png", dpi=160)
    figure.savefig(DESTINATION / "additive_channels_overview.svg", metadata={"Date": None})
    plt.close(figure)
    print("Built the home-page visual; all three shares match the tutorial record.")


if __name__ == "__main__":
    build()
