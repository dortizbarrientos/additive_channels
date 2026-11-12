"""Draw the one-trait walkthrough used in Appendix S7 of the paper.

The same exactly quadratic log expected-fitness function is used in every
panel. Only the mean or variance of the Gaussian breeding values changes.
The figure separates the fitness function (upper row) from the population
density (middle row). Thus a curve's horizontal extent is not mistaken for
the frequency of the breeding values that contribute to the calculation.

Run from any directory with ``python3 path/to/make_figure.py``. Outputs are
written next to this script. Dependencies: NumPy, SciPy and Matplotlib.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
from scipy.integrate import quad
from scipy.stats import norm

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

BLUE = "#176780"
ORANGE = "#bd4e24"
INK = "#20343d"
GRAY = "#6f7f86"
LIGHT = "#b6c4ca"


def log_expected_fitness(a):
    """Log of conditional expected reproductive output; maximum at a = 1."""
    return a - 0.5 * np.asarray(a) ** 2


def case_values(mean, variance):
    """Calculate the affine population fit and its variance partition.

    Write A = mean + X, with E[X] = 0 and Var(X) = variance. Expanding the
    quadratic gives a linear component (1 - mean) X and a centred residual
    -(X**2 - variance)/2. Gaussian third moments vanish, so the two are
    uncorrelated. The fitted intercept is E[ell(A)], not ell(mean).
    """
    slope = 1.0 - mean
    fit_at_mean = float(log_expected_fitness(mean) - 0.5 * variance)
    linear_variance = slope**2 * variance
    quadratic_variance = 0.5 * variance**2
    total = linear_variance + quadratic_variance
    share = linear_variance / total

    # Independently integrate the squared fitted and residual deviations.
    # These integrals check the stated Gaussian moment calculation using
    # the complete distribution, rather than the visible plotting window.
    sd = np.sqrt(variance)
    fitted = lambda a: fit_at_mean + slope * (a - mean)
    density = lambda a: norm.pdf(a, loc=mean, scale=sd)
    integrated_linear = quad(
        lambda a: (fitted(a) - fit_at_mean)**2 * density(a),
        -np.inf, np.inf, epsabs=1e-11)[0]
    integrated_residual = quad(
        lambda a: (log_expected_fitness(a) - fitted(a))**2 * density(a),
        -np.inf, np.inf, epsabs=1e-11)[0]
    assert np.isclose(integrated_linear, linear_variance, atol=1e-10)
    assert np.isclose(integrated_residual, quadratic_variance, atol=1e-10)

    return dict(mean=mean, variance=variance, slope=slope,
                fitted_value_at_mean=fit_at_mean,
                V_linear=linear_variance, V_quadratic=quadratic_variance,
                total_variance=total, linear_share=share,
                quadrature_V_linear=integrated_linear,
                quadrature_V_quadratic=integrated_residual)


def main():
    cases = [
        ("A", "Broad population\non the slope", 0.0, 1.0),
        ("B", "Narrow population\non the same slope", 0.0, 0.1),
        ("C", "Narrow population\ncentered at the peak", 1.0, 0.1),
    ]
    values = [case_values(mean, variance) for _, _, mean, variance in cases]
    (ROOT / "values.json").write_text(json.dumps({
        "model": "ell(a) = a - a^2/2; A is Gaussian",
        "fitness_scale": "natural logarithm of conditional expected reproductive output",
        "units": "the same arbitrary breeding-value units in all panels",
        "cases": {label: value for (label, *_), value in zip(cases, values)},
    }, indent=2) + "\n")

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "text.color": INK, "axes.labelcolor": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": LIGHT, "xtick.color": GRAY, "ytick.color": GRAY,
        "pdf.fonttype": 42, "svg.fonttype": "none",
    })
    fig = plt.figure(figsize=(7.2, 5.95), facecolor="white")
    grid = fig.add_gridspec(3, 3, left=0.105, right=0.985, top=0.835,
                           bottom=0.155, height_ratios=[2.5, 1.05, 0.78],
                           hspace=0.50, wspace=0.27)
    xmin, xmax = -2.3, 2.7
    a = np.linspace(xmin, xmax, 700)
    for col, ((label, title, mean, variance), result) in enumerate(zip(cases, values)):
        sd = np.sqrt(variance)
        lo, hi = norm.ppf([0.025, 0.975], loc=mean, scale=sd)
        local = np.linspace(lo, hi, 250)
        fitted = lambda x: result["fitted_value_at_mean"] + result["slope"] * (x - mean)

        top = fig.add_subplot(grid[0, col])
        top.set_title(f"{label}  {title}", loc="left", fontweight="bold",
                      fontsize=9.4, pad=19, linespacing=1.25)
        top.text(0.0, 1.015, f"Mean {mean:g}; variance {variance:g}",
                 transform=top.transAxes, fontsize=8, color=GRAY)
        # Full curves are pale; the darker part spans the central 95% of
        # each population. This is a visual guide, not a truncation of the
        # distribution used to calculate any number.
        top.plot(a, log_expected_fitness(a), color=INK, alpha=0.20, lw=1.2)
        top.plot(a, fitted(a), color=BLUE, alpha=0.20, lw=1.1, ls="--")
        top.plot(local, log_expected_fitness(local), color=INK, lw=2)
        top.plot(local, fitted(local), color=BLUE, lw=1.6, ls="--")
        top.axvline(mean, color=LIGHT, lw=0.6, ls=":")
        # Equal quantile positions indicate equal-probability groups of
        # individuals. The vertical segments are prediction errors on the
        # log scale; the fitness function itself has not changed.
        aq = norm.ppf(np.linspace(0.05, 0.95, 15), loc=mean, scale=sd)
        top.vlines(aq, fitted(aq), log_expected_fitness(aq),
                   color=ORANGE, alpha=0.80, lw=0.8)
        top.scatter(aq, log_expected_fitness(aq), s=6, color=INK, zorder=3)
        top.set(xlim=(xmin, xmax), ylim=(-5.3, 2.5), xticks=[-2, -1, 0, 1, 2],
                yticks=[-4, -2, 0, 2])
        top.tick_params(labelbottom=False)
        if col == 0:
            top.set_ylabel("Log expected reproductive output")
        else:
            top.tick_params(labelleft=False)

        density = fig.add_subplot(grid[1, col], sharex=top)
        p = norm.pdf(a, loc=mean, scale=sd)
        density.fill_between(a, 0, p, color=BLUE, alpha=0.17)
        density.plot(a, p, color=BLUE, lw=1.5)
        density.axvline(mean, color=LIGHT, lw=0.6, ls=":")
        density.set(ylim=(0, 1.38), yticks=[0, 0.6, 1.2])
        if col == 0:
            density.set_ylabel("Population\ndensity")
        else:
            density.tick_params(labelleft=False)
        density.set_xlabel("Breeding value")

        bars = fig.add_subplot(grid[2, col])
        share = result["linear_share"]
        bars.barh(0.58, share, height=0.29, color=BLUE)
        bars.barh(0.58, 1-share, left=share, height=0.29, color=ORANGE)
        bars.text(0, 1.02, f"{100*share:.1f}% linear share", fontsize=10,
                  color=INK, fontweight="bold")
        bars.text(0, 0.10,
                  f"Linear variance: {result['V_linear']:g}\n"
                  f"Curvature variance: {result['V_quadratic']:g}",
                  fontsize=8, linespacing=1.4, va="top")
        bars.set(xlim=(0, 1), ylim=(0, 1.25))
        bars.axis("off")

    legend = [Line2D([0], [0], color=INK, lw=2, label="Same fitness curve"),
              Line2D([0], [0], color=BLUE, lw=1.6, ls="--", label="Population-fitted line"),
              Line2D([0], [0], color=ORANGE, lw=0.8, label="Residual difference")]
    fig.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.53, 0.985),
               ncol=3, frameon=False, fontsize=8, handlelength=2.3,
               columnspacing=1.4)
    fig.text(0.105, 0.035,
             "The density supplies the weights. Bars divide total variance within each population;\n"
             "equal bar lengths do not imply equal total variance. All panels use the same axes.",
             fontsize=8, color=GRAY, linespacing=1.45)
    for extension in ["pdf", "png", "svg"]:
        fig.savefig(FIGURES / f"one_trait_additive_channel.{extension}", dpi=190)
    plt.close(fig)
    print("Three analytic variance partitions verified by independent integration.")


if __name__ == "__main__":
    main()
