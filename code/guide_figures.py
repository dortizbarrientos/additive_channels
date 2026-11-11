#!/usr/bin/env python3
"""Generate the five teaching figures for the mathematics guide."""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np








RESULTS: dict[str, dict[str, Any]] = {
    "math_guide_fig1": {
        "main_text_labels": [
            "eq:target",
            "eq:fitness_model",
            "eq:environmental_average",
        ],
        "result": (
            "Construct W_A(a)=E[W|A=a] by averaging realized fitness at fixed "
            "breeding value, then construct ell_A(a)=log W_A(a)."
        ),
        "parameters": {
            "W_max": 1.0,
            "theta": 4.0,
            "omega_squared": 1.0,
            "V_E": 1.0,
        },
    },
    "math_guide_fig2": {
        "main_text_labels": [
            "eq:centered_terms",
            "eq:vlin",
            "eq:vquad",
            "eq:Ag",
        ],
        "result": (
            "For centered Gaussian A, compare L=bA with "
            "Q_c=(H/2)(A^2-G); their variances are b^2G and H^2G^2/2."
        ),
        "parameters": {"b": 2.0, "H": -0.5, "G": 1.0},
    },
    "math_guide_fig3": {
        "main_text_labels": ["eq:selected_mean", "eq:selected_covariance"],
        "result": (
            "Gaussian log-quadratic selection gives selected mean "
            "(G^{-1}+Gamma)^{-1}b and selected covariance "
            "(G^{-1}+Gamma)^{-1}."
        ),
        "parameters": {"b": 2.0, "Gamma": 0.5, "G": 1.0},
    },
    "math_guide_fig4": {
        "main_text_labels": ["eq:scalar_recursion", "eq:scalar_root"],
        "result": (
            "The scalar fixed-baseline update is "
            "g_next=(1-rho)B+rho*g/(1+gamma*g), with the positive root given "
            "by eq:scalar_root."
        ),
        "parameters": {"B": 1.0, "gamma": 0.5, "rho": 0.5, "g0": 1.0},
    },
    "math_guide_fig5": {
        "main_text_labels": [
            "eq:LA_moments",
            "eq:LA_selected_mean",
            "eq:LA_selected_cov",
            "eq:LA_conversion",
        ],
        "result": (
            "Gaussian moments turn a compatible relative-fitness regression "
            "into selected breeding-value moments; matching those moments "
            "gives b and H on the log conditional-fitness scale."
        ),
        "parameters": {"P": 1.5, "beta": 0.4, "gamma": -0.2, "G": 0.5},
    },
}


ROOT = Path(__file__).resolve().parents[1] / "tutorials" / "mathematics"
FIGURE_DIR = ROOT / "figures"
SEED = 20_260_903




BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
DARK = "#243746"
MID_GREY = "#6B737B"
LIGHT_GREY = "#E2E6E9"
PALE_BLUE = "#DCECF5"
PALE_ORANGE = "#F7E4DC"
PALE_GREEN = "#DCEFE8"


plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans"],
        "mathtext.fontset": "dejavusans",
        "font.size": 9.0,
        "axes.titlesize": 10.0,
        "axes.labelsize": 9.2,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "legend.fontsize": 8.0,
        "axes.linewidth": 0.7,
        "lines.linewidth": 1.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
    }
)


def _style_axis(ax: plt.Axes, *, grid_axis: str | None = None) -> None:
    """Remove nonessential ink while retaining an interpretable scale."""

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(width=0.65, length=3)
    if grid_axis is not None:
        ax.grid(
            True,
            axis=grid_axis,
            color=LIGHT_GREY,
            linewidth=0.55,
            zorder=0,
        )


def _panel_label(ax: plt.Axes, label: str) -> None:
    """Place a panel letter consistently outside the plotting field."""

    ax.text(
        -0.12,
        1.05,
        label,
        transform=ax.transAxes,
        fontsize=10.5,
        fontweight="bold",
        va="top",
        ha="left",
    )


def _save(fig: plt.Figure, stem: str) -> dict[str, Path]:
    """Write and validate one vector figure and one review image atomically."""

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURE_DIR / f"{stem}.pdf"
    png_path = FIGURE_DIR / f"{stem}.png"
    pdf_tmp = FIGURE_DIR / f".{stem}.tmp.pdf"
    png_tmp = FIGURE_DIR / f".{stem}.tmp.png"
    metadata = {
        "Title": stem,
        "Author": "Ortiz-Barrientos and Cooper",
        "Subject": "Teaching figure linked to named GENETICS manuscript results",
        "Creator": Path(__file__).name,
    }
    fig.savefig(pdf_tmp, format="pdf", bbox_inches="tight", metadata=metadata)
    fig.savefig(png_tmp, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    
    
    
    
    if pdf_tmp.stat().st_size == 0 or b"%%EOF" not in pdf_tmp.read_bytes()[-32:]:
        raise OSError(f"Incomplete PDF generated for {stem}")
    if png_tmp.stat().st_size == 0 or png_tmp.read_bytes()[-12:-4] != b"\x00\x00\x00\x00IEND":
        raise OSError(f"Incomplete PNG generated for {stem}")
    os.replace(pdf_tmp, pdf_path)
    os.replace(png_tmp, png_path)
    return {"pdf": pdf_path, "png": png_path}







def conditional_expected_fitness(
    a: np.ndarray | float,
    *,
    W_max: float = 1.0,
    theta: float = 4.0,
    omega_squared: float = 1.0,
    environmental_variance: float = 1.0,
) -> np.ndarray:
    """Evaluate ``eq:target`` using ``eq:fitness_model`` and
    ``eq:environmental_average`` from the main text.

    With Z=A+E, E~N(0,V_E), and
    W(Z)=W_max*exp[-(Z-theta)^2/(2 omega^2)], integrating over E gives

        W_A(a)=W_max*sqrt[omega^2/(omega^2+V_E)]
               * exp[-(a-theta)^2/{2(omega^2+V_E)}].

    This function performs the averaging before any logarithm is taken.
    """

    a = np.asarray(a, dtype=float)
    total_variance = omega_squared + environmental_variance
    return W_max * math.sqrt(omega_squared / total_variance) * np.exp(
        -((a - theta) ** 2) / (2.0 * total_variance)
    )


def log_conditional_expected_fitness(a: np.ndarray | float) -> np.ndarray:
    """Evaluate ell_A(a)=log E[W|A=a] from ``eq:target`` in that order."""

    return np.log(conditional_expected_fitness(a))


def normal_pdf(x: np.ndarray, mean: float, variance: float) -> np.ndarray:
    """Normal density used only to display population weighting or selection."""

    return np.exp(-0.5 * (x - mean) ** 2 / variance) / math.sqrt(
        2.0 * math.pi * variance
    )


def first_order_components(
    x: np.ndarray, *, b: float = 2.0, H: float = -0.5, G: float = 1.0
) -> dict[str, np.ndarray | float]:
    """Compute ``eq:centered_terms``--``eq:Ag`` in one trait.

    The centered curvature piece is Q_c=(H/2)(X^2-G).  Under X~N(0,G),
    ``eq:vlin`` gives V_lin=b^2G and ``eq:vquad`` gives
    V_quad=H^2G^2/2.  Their ratio is the share in ``eq:Ag``.
    """

    linear = b * x
    quadratic_centered = 0.5 * H * (x**2 - G)
    v_lin = b**2 * G
    v_quad = 0.5 * H**2 * G**2
    share = v_lin / (v_lin + v_quad)
    return {
        "L": linear,
        "Q_c": quadratic_centered,
        "sum": linear + quadratic_centered,
        "V_lin": v_lin,
        "V_quad": v_quad,
        "share": share,
    }


def selected_gaussian(
    *, b: float = 2.0, Gamma: float = 0.5, G: float = 1.0
) -> tuple[float, float]:
    """Return ``eq:selected_mean`` and ``eq:selected_covariance`` in 1D."""

    selected_variance = 1.0 / (1.0 / G + Gamma)
    selected_mean = selected_variance * b
    return selected_mean, selected_variance


def scalar_update(g: np.ndarray | float, *, B: float, gamma: float, rho: float):
    """Evaluate the fixed-baseline update in ``eq:scalar_recursion``."""

    g = np.asarray(g, dtype=float)
    return (1.0 - rho) * B + rho * g / (1.0 + gamma * g)


def scalar_positive_root(*, B: float, gamma: float, rho: float) -> float:
    """Evaluate the positive fixed point stated in ``eq:scalar_root``."""

    if gamma == 0.0:
        return B
    discriminant = (1.0 - rho) ** 2 * (1.0 - gamma * B) ** 2
    discriminant += 4.0 * gamma * B * (1.0 - rho)
    numerator = -(1.0 - rho) * (1.0 - gamma * B) + math.sqrt(discriminant)
    return numerator / (2.0 * gamma)


def moment_conversion(
    *, P: float = 1.5, beta: float = 0.4, gamma: float = -0.2, G: float = 0.5
) -> dict[str, float]:
    """Evaluate ``eq:LA_moments``, ``eq:LA_selected_mean``,
    ``eq:LA_selected_cov``, and ``eq:LA_conversion`` in one trait.

    The first step uses the Gaussian moment identity in ``eq:LA_moments`` to
    set the mean-one intercept.  The second forms selected breeding-value
    moments.  Matching those moments to ``eq:selected_mean`` and
    ``eq:selected_covariance`` gives the b and H formula in
    ``eq:LA_conversion``.
    """

    alpha = 1.0 - 0.5 * gamma * P
    selected_mean = G * beta
    selected_variance = G + G * (gamma - beta**2) * G
    b = selected_mean / selected_variance
    H = 1.0 / G - 1.0 / selected_variance
    return {
        "alpha": alpha,
        "selected_mean": selected_mean,
        "selected_variance": selected_variance,
        "b": b,
        "H": H,
    }







def make_figure_1() -> dict[str, Path]:
    """Illustrate ``eq:target`` using the model and average in
    ``eq:fitness_model`` and ``eq:environmental_average``."""

    rng = np.random.default_rng(SEED)
    fixed_a = np.arange(-2.0, 5.0, 1.0)
    replicates = 28
    residuals = rng.normal(0.0, 1.0, size=(fixed_a.size, replicates))
    realized = np.exp(-0.5 * (fixed_a[:, None] + residuals - 4.0) ** 2)
    jitter = rng.uniform(-0.115, 0.115, size=realized.shape)

    a_curve = np.linspace(-2.35, 4.35, 500)
    conditional = conditional_expected_fitness(a_curve)

    fig, (ax_raw, ax_log) = plt.subplots(1, 2, figsize=(7.35, 3.05))

    ax_raw.scatter(
        fixed_a[:, None] + jitter,
        realized,
        s=8,
        facecolor=MID_GREY,
        edgecolor="none",
        alpha=0.30,
        label="individual outcomes",
        rasterized=True,
        zorder=1,
    )
    ax_raw.plot(
        a_curve,
        conditional,
        color=DARK,
        linewidth=2.0,
        label=r"average at fixed $a$: $W_A(a)$",
        zorder=3,
    )
    ax_raw.set(
        xlim=(-2.4, 4.4),
        ylim=(-0.03, 1.03),
        xlabel="Breeding value, $a$",
        ylabel="Realized fitness",
        title="1  Average at each breeding value",
    )
    ax_raw.legend(frameon=False, loc="upper left", handlelength=2.2)
    _style_axis(ax_raw)
    _panel_label(ax_raw, "a")

    ell = log_conditional_expected_fitness(a_curve)
    ax_log.plot(a_curve, ell, color=BLUE, linewidth=2.1)
    ax_log.axvline(0.0, color=LIGHT_GREY, linewidth=0.8, zorder=0)
    ax_log.text(
        0.04,
        0.07,
        r"$\ell_A(a)=\log W_A(a)$",
        transform=ax_log.transAxes,
        color=BLUE,
        ha="left",
        va="bottom",
    )
    ax_log.set(
        xlim=(-2.4, 4.4),
        ylim=(-10.8, -0.1),
        xlabel="Breeding value, $a$",
        ylabel="Log conditional expected fitness",
        title="2  Take the logarithm of that mean",
    )
    _style_axis(ax_log)
    _panel_label(ax_log, "b")

    fig.subplots_adjust(wspace=0.36)
    return _save(fig, "math_guide_fig1")







def make_figure_2() -> dict[str, Path]:
    """Show ``eq:centered_terms`` and its variance share visually."""

    x = np.linspace(-3.0, 3.0, 500)
    pieces = first_order_components(x)
    density = normal_pdf(x, mean=0.0, variance=1.0)

    fig = plt.figure(figsize=(7.2, 4.0))
    grid = fig.add_gridspec(2, 1, height_ratios=[4.3, 1.0], hspace=0.06)
    ax = fig.add_subplot(grid[0])
    ax_weight = fig.add_subplot(grid[1], sharex=ax)

    ax.axhline(0.0, color=LIGHT_GREY, linewidth=0.7, zorder=0)
    ax.plot(
        x,
        pieces["sum"],
        color=DARK,
        linewidth=2.2,
        label=r"together: $L+Q_c$",
        zorder=3,
    )
    ax.plot(
        x,
        pieces["L"],
        color=BLUE,
        linestyle="--",
        linewidth=1.7,
        label=r"first-order piece: $L=2A$",
        zorder=2,
    )
    ax.plot(
        x,
        pieces["Q_c"],
        color=ORANGE,
        linestyle=":",
        linewidth=2.0,
        label=r"centered curvature: $Q_c=-0.25(A^2-1)$",
        zorder=1,
    )
    ax.set(
        xlim=(-3.0, 3.0),
        ylim=(-8.5, 6.6),
        ylabel="Contribution to log expected fitness",
        title="The same local surface, separated into two pieces",
    )
    ax.legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=3,
        columnspacing=1.25,
        handlelength=2.5,
    )
    ax.text(
        0.025,
        0.08,
        "First-order variance = 4\n"
        "Curvature variance = 0.125\n"
        "First-order share = 0.970",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.7,
        linespacing=1.35,
        bbox={"boxstyle": "round,pad=0.32", "facecolor": "white", "edgecolor": LIGHT_GREY},
    )
    _style_axis(ax)
    ax.tick_params(labelbottom=False)

    ax_weight.fill_between(x, density, color=PALE_BLUE, linewidth=0)
    ax_weight.plot(x, density, color=BLUE, linewidth=1.45)
    ax_weight.text(
        0.985,
        0.60,
        "More common breeding values\nreceive more weight",
        transform=ax_weight.transAxes,
        ha="right",
        va="center",
        color=DARK,
        fontsize=8.4,
    )
    ax_weight.set(
        xlim=(-3.0, 3.0),
        ylim=(0.0, 0.45),
        xlabel=r"Breeding value relative to the mean, $A$",
        ylabel="Population\ndensity",
    )
    ax_weight.set_yticks([])
    _style_axis(ax_weight)

    return _save(fig, "math_guide_fig2")







def make_figure_3() -> dict[str, Path]:
    """Display the selected Gaussian from ``eq:selected_mean`` and covariance."""

    selected_mean, selected_variance = selected_gaussian()
    x = np.linspace(-3.5, 4.3, 700)
    before = normal_pdf(x, mean=0.0, variance=1.0)
    after = normal_pdf(x, mean=selected_mean, variance=selected_variance)

    fig, ax = plt.subplots(figsize=(7.15, 3.25))
    ax.fill_between(x, before, color=LIGHT_GREY, alpha=0.58, linewidth=0)
    ax.plot(
        x,
        before,
        color=MID_GREY,
        linestyle="--",
        linewidth=1.75,
        label="Before selection: mean 0, variance 1",
    )
    ax.fill_between(x, after, color=PALE_BLUE, alpha=0.88, linewidth=0)
    ax.plot(
        x,
        after,
        color=BLUE,
        linewidth=2.1,
        label=r"Selected contributors: mean $4/3$, variance $2/3$",
    )

    ax.vlines(0.0, 0.0, normal_pdf(np.array([0.0]), 0.0, 1.0)[0],
              color=MID_GREY, linestyle="--", linewidth=1.0)
    ax.vlines(
        selected_mean,
        0.0,
        normal_pdf(np.array([selected_mean]), selected_mean, selected_variance)[0],
        color=BLUE,
        linewidth=1.0,
    )
    ax.text(
        selected_mean,
        -0.033,
        r"$4/3$",
        color=BLUE,
        ha="center",
        va="top",
        clip_on=False,
    )
    ax.text(
        0.985,
        0.88,
        r"$b=2,\quad \Gamma=0.5,\quad G=1$",
        transform=ax.transAxes,
        ha="right",
        va="center",
        fontsize=9.0,
    )
    ax.set(
        xlim=(-3.5, 4.3),
        ylim=(0.0, 0.62),
        xlabel="Breeding value relative to the original mean",
        ylabel="Population density",
        title="Curved selection moves the mean and narrows the distribution",
    )
    ax.legend(frameon=False, loc="upper left", handlelength=2.5)
    _style_axis(ax)
    return _save(fig, "math_guide_fig3")







def make_figure_4() -> dict[str, Path]:
    """Show iteration of ``eq:scalar_recursion`` toward ``eq:scalar_root``."""

    B, gamma, rho, g0 = 1.0, 0.5, 0.5, 1.0
    fixed = scalar_positive_root(B=B, gamma=gamma, rho=rho)
    generations = np.arange(0, 9)
    trajectory = np.empty(generations.size)
    trajectory[0] = g0
    for index in range(1, trajectory.size):
        trajectory[index] = scalar_update(
            trajectory[index - 1], B=B, gamma=gamma, rho=rho
        )

    g_grid = np.linspace(0.68, 1.04, 400)
    F_grid = scalar_update(g_grid, B=B, gamma=gamma, rho=rho)

    fig, (ax_map, ax_time) = plt.subplots(1, 2, figsize=(7.25, 3.25))

    ax_map.plot(g_grid, g_grid, color=MID_GREY, linestyle="--", label="no change")
    ax_map.plot(g_grid, F_grid, color=BLUE, linewidth=2.0, label="one update")

    
    
    
    current = g0
    for _ in range(4):
        updated = float(scalar_update(current, B=B, gamma=gamma, rho=rho))
        ax_map.plot([current, current], [current, updated], color=ORANGE, linewidth=1.05)
        ax_map.plot([current, updated], [updated, updated], color=ORANGE, linewidth=1.05)
        current = updated
    ax_map.scatter([fixed], [fixed], s=28, color=DARK, zorder=4)
    ax_map.annotate(
        f"balance = {fixed:.3f}",
        xy=(fixed, fixed),
        xytext=(0.705, 0.943),
        textcoords="data",
        arrowprops={"arrowstyle": "-", "color": DARK, "linewidth": 0.7},
        ha="left",
        va="bottom",
        fontsize=8.4,
    )
    ax_map.set(
        xlim=(0.68, 1.04),
        ylim=(0.68, 1.04),
        xlabel=r"Current variance, $g_t$",
        ylabel=r"Updated variance, $g_{t+1}$",
        title="Apply the same update repeatedly",
    )
    ax_map.legend(frameon=False, loc="lower right")
    _style_axis(ax_map)
    _panel_label(ax_map, "a")

    ax_time.axhline(fixed, color=MID_GREY, linestyle="--", linewidth=1.0)
    ax_time.plot(
        generations,
        trajectory,
        color=BLUE,
        marker="o",
        markersize=4.0,
        markerfacecolor="white",
        markeredgewidth=1.1,
    )
    ax_time.text(
        7.9,
        fixed + 0.006,
        f"balance {fixed:.3f}",
        ha="right",
        va="bottom",
        color=MID_GREY,
        fontsize=8.4,
    )
    ax_time.text(
        0.04,
        0.92,
        r"$B=1,\quad \gamma=0.5,\quad \rho=0.5$",
        transform=ax_time.transAxes,
        ha="left",
        va="top",
        fontsize=9.0,
    )
    ax_time.set(
        xlim=(-0.2, 8.2),
        ylim=(0.755, 1.015),
        xticks=np.arange(0, 9, 2),
        xlabel="Generation",
        ylabel="Breeding-value variance",
        title="The trajectory approaches the balance",
    )
    _style_axis(ax_time, grid_axis="y")
    _panel_label(ax_time, "b")

    fig.subplots_adjust(wspace=0.35)
    return _save(fig, "math_guide_fig4")







def _add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    *,
    facecolor: str,
    heading: str,
    body: str,
) -> None:
    """Add one restrained box to the teaching flow diagram."""

    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.015",
        facecolor=facecolor,
        edgecolor=MID_GREY,
        linewidth=0.8,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2.0,
        y + height * 0.76,
        heading,
        ha="center",
        va="center",
        fontweight="bold",
        fontsize=8.4,
        linespacing=1.10,
    )
    ax.text(
        x + width / 2.0,
        y + height * 0.39,
        body,
        ha="center",
        va="center",
        fontsize=8.1,
        linespacing=1.35,
    )


def make_figure_5() -> dict[str, Path]:
    """Diagram the route from ``eq:LA_moments`` through
    ``eq:LA_selected_mean`` and ``eq:LA_selected_cov`` to
    ``eq:LA_conversion``."""

    converted = moment_conversion()
    assert math.isclose(converted["alpha"], 1.15, abs_tol=1e-12)
    assert math.isclose(converted["selected_mean"], 0.20, abs_tol=1e-12)
    assert math.isclose(converted["selected_variance"], 0.41, abs_tol=1e-12)
    assert math.isclose(converted["b"], 0.4878048780487805, abs_tol=1e-12)
    assert math.isclose(converted["H"], -0.4390243902439024, abs_tol=1e-12)

    fig, ax = plt.subplots(figsize=(7.35, 2.75))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    box_y, box_w, box_h = 0.24, 0.27, 0.56
    box_x = [0.01, 0.365, 0.72]
    _add_box(
        ax,
        (box_x[0], box_y),
        box_w,
        box_h,
        facecolor=PALE_ORANGE,
        heading="Relative-fitness\nregression",
        body=(
            r"$P=1.50,\ \beta=0.40$" "\n"
            r"$\gamma=-0.20,\ \alpha=1.15$"
        ),
    )
    _add_box(
        ax,
        (box_x[1], box_y),
        box_w,
        box_h,
        facecolor=PALE_GREEN,
        heading="Selected breeding-value\nmoments",
        body=(
            r"mean shift: $G\beta=0.20$" "\n"
            r"variance after selection: $0.41$"
        ),
    )
    _add_box(
        ax,
        (box_x[2], box_y),
        box_w,
        box_h,
        facecolor=PALE_BLUE,
        heading="Matched log-fitness\nsurface",
        body=(
            r"slope: $b=0.488$" "\n"
            r"curvature: $H=-0.439$"
        ),
    )

    for left, right, label in (
        (box_x[0] + box_w, box_x[1], "use\nmoments"),
        (box_x[1] + box_w, box_x[2], "match"),
    ):
        arrow = FancyArrowPatch(
            (left + 0.012, box_y + box_h / 2.0),
            (right - 0.012, box_y + box_h / 2.0),
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=1.0,
            color=DARK,
        )
        ax.add_patch(arrow)
        ax.text(
            (left + right) / 2.0,
            box_y + box_h / 2.0 + 0.075,
            label,
            ha="center",
            va="center",
            fontsize=7.2,
            color=DARK,
            linespacing=1.1,
        )

    ax.text(
        0.5,
        0.08,
        "The conversion uses compatible, unstandardized coordinates and the stated Gaussian conditions.",
        ha="center",
        va="center",
        fontsize=8.3,
        color=MID_GREY,
    )
    ax.set_title(
        "Use selected moments to connect an existing selection analysis to the paper's target",
        pad=4,
    )
    return _save(fig, "math_guide_fig5")


def verify_numbers() -> None:
    """Fail before plotting if any displayed value departs from its equation."""

    
    
    assert math.isclose(float(conditional_expected_fitness(0.0)),
                        math.exp(-4.0) / math.sqrt(2.0), rel_tol=1e-12)
    components = first_order_components(np.array([0.0]))
    assert math.isclose(float(components["V_lin"]), 4.0, abs_tol=1e-12)
    assert math.isclose(float(components["V_quad"]), 0.125, abs_tol=1e-12)
    assert math.isclose(float(components["share"]), 4.0 / 4.125, abs_tol=1e-12)

    
    selected_mean, selected_variance = selected_gaussian()
    assert math.isclose(selected_mean, 4.0 / 3.0, abs_tol=1e-12)
    assert math.isclose(selected_variance, 2.0 / 3.0, abs_tol=1e-12)

    
    root = scalar_positive_root(B=1.0, gamma=0.5, rho=0.5)
    assert math.isclose(
        float(scalar_update(root, B=1.0, gamma=0.5, rho=0.5)),
        root,
        abs_tol=1e-12,
    )
    assert math.isclose(root, (math.sqrt(17.0) - 1.0) / 4.0, abs_tol=1e-12)

    
    
    converted = moment_conversion()
    assert math.isclose(converted["alpha"], 1.15, abs_tol=1e-12)
    assert math.isclose(converted["selected_mean"], 0.20, abs_tol=1e-12)
    assert math.isclose(converted["selected_variance"], 0.41, abs_tol=1e-12)
    assert math.isclose(converted["b"], 0.4878048780487805, abs_tol=1e-12)
    assert math.isclose(converted["H"], -0.4390243902439024, abs_tol=1e-12)


def main() -> None:
    """Verify all displayed numbers and generate the complete figure set."""

    verify_numbers()
    outputs = {
        "math_guide_fig1": make_figure_1(),
        "math_guide_fig2": make_figure_2(),
        "math_guide_fig3": make_figure_3(),
        "math_guide_fig4": make_figure_4(),
        "math_guide_fig5": make_figure_5(),
    }
    for stem, paths in outputs.items():
        label_text = ", ".join(RESULTS[stem]["main_text_labels"])
        print(f"{stem}: {paths['pdf'].name}, {paths['png'].name} [{label_text}]")


if __name__ == "__main__":
    main()
