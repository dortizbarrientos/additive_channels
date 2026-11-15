#!/usr/bin/env python3
"""Reproduce the four figures and write their parameters and numerical results to outputs/.

Run python code/figures.py from the repository root. The random seed is fixed.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np









SCIENTIFIC_RESULTS = {
    "conditional_fitness": (
        "Definition: W_A(a) = E[W | A=a].  Average individual fitness at a "
        "fixed breeding value before taking the logarithm."
    ),
    "log_conditional_fitness": (
        "Definition: ell_A(a) = log W_A(a), not E[log W | A=a]."
    ),
    "local_expansion": (
        "Local result: ell_A is approximated by ell_0 + b^T X + "
        "(1/2) X^T H X around the current breeding-value mean."
    ),
    "variance_share": (
        "Gaussian current-state result: V_lin = b^T G b, "
        "V_quad = (1/2) tr[(H G)^2], and A_g = V_lin/(V_lin+V_quad)."
    ),
    "projection_identity": (
        "Gaussian projection result: for positive linear variance, A_g = Corr(L, L+Q_c)^2, with "
        "L=b^T X and Q_c=[X^T H X-tr(HG)]/2."
    ),
    "selected_covariance": (
        "Within-generation result under Gaussian stabilizing selection: "
        "G_sel = (G^{-1} + Gamma)^{-1}, Gamma=-H."
    ),
    "fixed_B_recursion": (
        "Across-generation conditional closure: "
        "G_{t+1}=(1-rho)B + rho G_sel.  B is a fixed genic covariance "
        "baseline, not mutational input."
    ),
    "scalar_dynamics": (
        "Isotropic special case: g_{t+1}=(1-rho)B + "
        "rho g_t/(1+gamma g_t).  With a maintained gradient, V_lin scales "
        "as g and V_quad as g^2."
    ),
    "scaling": (
        "Proportional-covariance result: replacing G by sG while b and H "
        "remain fixed multiplies V_lin by s and V_quad by s^2, so the "
        "first-order share A_g increases as covariance contracts when both components are positive."
    ),
}




EQUATION_LABELS = {
    "conditional_fitness": "eq:target",
    "log_conditional_fitness": "eq:target",
    "local_expansion": "eq:taylor",
    "variance_share": "eq:vlin, eq:vquad, eq:Ag",
    "projection_identity": "eq:r2_identity",
    "selected_covariance": "eq:selected_covariance",
    "fixed_B_recursion": "eq:fixedB_recursion",
    "scalar_dynamics": "eq:scalar_recursion",
    "scaling": "eq:scaling",
}


ROOT = Path(__file__).resolve().parents[1] / "outputs"
FIGURE_DIR = ROOT / "figures"
RESULTS_PATH = ROOT / "figure_results.json"
SEED = 20_260_903




BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
PURPLE = "#CC79A7"
SKY = "#56B4E9"
DARK = "#263746"
MID_GREY = "#66717E"
LIGHT_GREY = "#D9DEE3"


plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 8.5,
        "axes.titlesize": 9.5,
        "axes.labelsize": 9,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.2,
        "axes.linewidth": 0.7,
        "lines.linewidth": 1.7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
    }
)


def _jsonable(value: Any) -> Any:
    """Convert NumPy scalars and arrays to ordinary JSON values."""

    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def _style_axis(ax: plt.Axes, *, grid: bool = True) -> None:
    """Apply a restrained journal style; this function changes no data."""

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid:
        ax.grid(True, color="#E7EAED", linewidth=0.55, zorder=0)
    ax.tick_params(width=0.65, length=3)


def _save_figure(fig: plt.Figure, stem: str) -> dict[str, str]:
    """Save one scientific figure as vector PDF and a PNG preview."""

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURE_DIR / f"{stem}.pdf"
    png_path = FIGURE_DIR / f"{stem}.png"
    pdf_tmp = FIGURE_DIR / f".{stem}.tmp.pdf"
    png_tmp = FIGURE_DIR / f".{stem}.tmp.png"
    fig.savefig(
        pdf_tmp,
        format="pdf",
        bbox_inches="tight",
        metadata={
            "Title": stem,
            "Author": "Ortiz-Barrientos and Cooper",
            "Subject": "Population fitness, genetic covariance and selection",
            "Creator": "figures.py",
        },
    )
    fig.savefig(png_tmp, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    if b"%%EOF" not in pdf_tmp.read_bytes()[-32:]:
        raise OSError(f"Incomplete PDF generated for {stem}")
    if png_tmp.read_bytes()[-12:-4] != b"\x00\x00\x00\x00IEND":
        raise OSError(f"Incomplete PNG generated for {stem}")
    os.replace(pdf_tmp, pdf_path)
    os.replace(png_tmp, png_path)
    return {
        "pdf": str(pdf_path.relative_to(ROOT)),
        "png": str(png_path.relative_to(ROOT)),
    }







def conditional_expected_fitness(
    a: np.ndarray | float,
    *,
    theta: float,
    omega: float,
    environmental_variance: float,
) -> np.ndarray:
    """Evaluate the conditional mean used in Figure 1.

    Main-text result
    ----------------
    ``conditional_fitness``: W_A(a)=E[W|A=a].  In the illustrative model
    Z=A+E, E~N(0,V_E), and W(Z)=exp[-(Z-theta)^2/(2 omega^2)].  Integrating
    over E gives the expression below.  This is a breeding-value-to-expected-
    fitness relationship after residual variation has been averaged; it is not
    a genotype-to-phenotype map.
    """

    a_array = np.asarray(a, dtype=float)
    omega2 = omega**2
    broadened_variance = omega2 + environmental_variance
    normalization = math.sqrt(omega2 / broadened_variance)
    return normalization * np.exp(
        -((a_array - theta) ** 2) / (2.0 * broadened_variance)
    )


def log_conditional_expected_fitness(
    a: np.ndarray | float,
    *,
    theta: float,
    omega: float,
    environmental_variance: float,
) -> np.ndarray:
    """Take log *after* evaluating E[W|A=a], as defined in the main text.

    Main-text result
    ----------------
    ``log_conditional_fitness``: ell_A=log(E[W|A]), not E[log W|A].  Keeping
    this operation in its own function makes the order explicit in the code as
    well as in Figure 1.
    """

    return np.log(
        conditional_expected_fitness(
            a,
            theta=theta,
            omega=omega,
            environmental_variance=environmental_variance,
        )
    )


def variance_components(
    b: np.ndarray, H: np.ndarray, G: np.ndarray
) -> tuple[float, float]:
    """Compute the two population-weighted terms in the revised diagnostic.

    Main-text result
    ----------------
    ``variance_share``: for centered Gaussian breeding values X~N(0,G),
    V_lin=b^T G b and V_quad=(1/2)tr[(H G)^2].  The latter is the variance of
    Q_c=[X^T H X-tr(HG)]/2, not a variance component in the
    genotype-to-phenotype map.
    """

    b = np.asarray(b, dtype=float)
    H = np.asarray(H, dtype=float)
    G = np.asarray(G, dtype=float)
    v_lin = float(b @ G @ b)
    HG = H @ G
    v_quad = float(0.5 * np.trace(HG @ HG))
    return v_lin, v_quad


def first_order_share(v_lin: float, v_quad: float) -> float:
    """Return A_g, with the boundary convention for the variance-share calculation.

    Main-text result
    ----------------
    ``variance_share``: A_g=V_lin/(V_lin+V_quad).  It is undefined if both
    variances vanish.  If V_lin=0 and V_quad>0 it equals zero, although the
    correlation representation is then undefined because L is constant.
    """

    denominator = v_lin + v_quad
    if denominator <= 0.0:
        raise ValueError("The first-order share is undefined when both variances vanish.")
    return float(v_lin / denominator)


def selected_parent_covariance(G: np.ndarray, Gamma: np.ndarray) -> np.ndarray:
    """Apply the within-generation Gaussian selection operator.

    Main-text result
    ----------------
    ``selected_covariance``: G_sel=(G^{-1}+Gamma)^{-1}.  This operation uses
    the current breeding-value covariance and stabilizing curvature of log
    conditional expected fitness.  The directional gradient changes the selected mean but not
    this covariance formula.
    """

    G = np.asarray(G, dtype=float)
    Gamma = np.asarray(Gamma, dtype=float)
    return np.linalg.inv(np.linalg.inv(G) + Gamma)


def fixed_baseline_update(
    G_selected: np.ndarray, B: np.ndarray, rho: float
) -> np.ndarray:
    """Apply the conditional across-generation covariance closure.

    Main-text result
    ----------------
    ``fixed_B_recursion``: G_next=(1-rho)B+rho G_sel.  The fixed matrix B is
    an additional short-timescale closure.  It is not inferred from fixed
    allelic effects and it is not a per-generation mutation term.
    """

    if not 0.0 <= rho <= 1.0:
        raise ValueError("rho must lie in [0, 1].")
    return (1.0 - rho) * np.asarray(B, dtype=float) + rho * np.asarray(
        G_selected, dtype=float
    )







def make_figure_1() -> dict[str, Any]:
    """Build Figure 1: average fitness first, then take its logarithm.

    Panels and scientific results
    -----------------------------
    A. ``conditional_fitness``.  Repeated residual outcomes at the same
       breeding value are averaged to construct W_A(a).
    B. ``log_conditional_fitness`` and ``local_expansion``.  The occupied
       breeding-value distribution marks the range over which the tangent and
       curved descriptions are compared.

    Biology
    -------
    Individuals with the same breeding value need not have the same phenotype
    or fitness.  The figure therefore begins with conditional expected fitness,
    not a deterministic genotype-to-fitness surface.
    """

    rng = np.random.default_rng(SEED + 1)
    theta = 1.0
    omega = 0.60
    environmental_variance = 0.49
    G = 0.49
    population_mean = 0.0

    broadened_variance = omega**2 + environmental_variance
    b = (theta - population_mean) / broadened_variance
    H = -1.0 / broadened_variance

    
    
    
    check_a = np.array([-1.5, -0.5, 0.0, 1.0, 2.0])
    check_e = rng.normal(
        0.0,
        math.sqrt(environmental_variance),
        size=(check_a.size, 200_000),
    )
    check_w = np.exp(
        -((check_a[:, None] + check_e - theta) ** 2) / (2.0 * omega**2)
    )
    monte_carlo_mean = check_w.mean(axis=1)
    analytic_mean = conditional_expected_fitness(
        check_a,
        theta=theta,
        omega=omega,
        environmental_variance=environmental_variance,
    )
    conditional_mean_max_error = float(
        np.max(np.abs(monte_carlo_mean - analytic_mean))
    )
    assert conditional_mean_max_error < 0.004

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.35, 3.15))

    
    
    a_stacks = np.linspace(-1.7, 2.2, 14)
    residuals = rng.normal(
        0.0,
        math.sqrt(environmental_variance),
        size=(a_stacks.size, 28),
    )
    z = a_stacks[:, None] + residuals
    individual_w = np.exp(-((z - theta) ** 2) / (2.0 * omega**2))
    ax_a.scatter(
        np.repeat(a_stacks, individual_w.shape[1]),
        individual_w.ravel(),
        s=8,
        facecolor=SKY,
        edgecolor="none",
        alpha=0.32,
        zorder=2,
        label="individual fitness values",
    )
    a_grid = np.linspace(-1.8, 2.3, 500)
    w_curve = conditional_expected_fitness(
        a_grid,
        theta=theta,
        omega=omega,
        environmental_variance=environmental_variance,
    )
    ax_a.plot(
        a_grid,
        w_curve,
        color=BLUE,
        linewidth=2.4,
        zorder=4,
        label=r"conditional mean $W_A(a)$",
    )
    ax_a.plot(
        a_stacks,
        individual_w.mean(axis=1),
        linestyle="none",
        marker="o",
        markersize=3.2,
        markerfacecolor="white",
        markeredgecolor=DARK,
        markeredgewidth=0.7,
        zorder=5,
        label="sample means",
    )
    ax_a.set(
        xlim=(-1.8, 2.3),
        ylim=(-0.02, 1.02),
        xlabel=r"breeding value $a$",
        ylabel="fitness",
        title=r"a. Average fitness at each $a$",
    )
    _style_axis(ax_a)
    ax_a.legend(frameon=False, loc="upper left", handlelength=2.0)

    
    
    
    ell_curve = log_conditional_expected_fitness(
        a_grid,
        theta=theta,
        omega=omega,
        environmental_variance=environmental_variance,
    )
    ell_at_mean = float(
        log_conditional_expected_fitness(
            population_mean,
            theta=theta,
            omega=omega,
            environmental_variance=environmental_variance,
        )
    )
    tangent = ell_at_mean + b * (a_grid - population_mean)
    ax_b.plot(
        a_grid,
        ell_curve,
        color=BLUE,
        linewidth=2.4,
        label=r"$\ell_A(a)$ = second order (exact here)",
        zorder=4,
    )
    ax_b.plot(
        a_grid,
        tangent,
        color=ORANGE,
        linewidth=2.0,
        linestyle=(0, (5, 2.5)),
        label="first-order approximation",
        zorder=3,
    )
    ax_b.axvline(population_mean, color=MID_GREY, linestyle=":", linewidth=1.0)
    ax_b.scatter(
        [population_mean],
        [ell_at_mean],
        s=26,
        facecolor="white",
        edgecolor=DARK,
        linewidth=0.8,
        zorder=6,
    )

    y_floor = min(float(ell_curve.min()), float(tangent.min())) - 0.20
    pop_density = np.exp(-0.5 * (a_grid - population_mean) ** 2 / G)
    pop_density /= pop_density.max()
    density_top = y_floor + 0.72 * pop_density
    ax_b.fill_between(
        a_grid,
        y_floor,
        density_top,
        color=SKY,
        alpha=0.32,
        linewidth=0,
        zorder=1,
    )
    ax_b.plot(a_grid, density_top, color=SKY, linewidth=0.9, zorder=2)
    ax_b.text(
        -1.68,
        y_floor + 0.15,
        r"current $A$ distribution (scaled)",
        color=DARK,
        fontsize=7.1,
    )
    ax_b.set(
        xlim=(-1.8, 2.3),
        ylim=(y_floor, max(float(tangent.max()), float(ell_curve.max())) + 0.15),
        xlabel=r"breeding value $a$",
        ylabel=r"log conditional expected fitness $\ell_A(a)$",
        title="b. Then take the logarithm",
    )
    _style_axis(ax_b)
    ax_b.legend(frameon=False, loc="upper left", handlelength=2.5)

    fig.subplots_adjust(wspace=0.34)
    paths = _save_figure(fig, "figure1_conditional_fitness")
    return {
        "scientific_results": [
            SCIENTIFIC_RESULTS["conditional_fitness"],
            SCIENTIFIC_RESULTS["log_conditional_fitness"],
            SCIENTIFIC_RESULTS["local_expansion"],
        ],
        "parameters": {
            "theta": theta,
            "omega": omega,
            "environmental_variance": environmental_variance,
            "breeding_value_variance_G": G,
            "population_mean": population_mean,
        },
        "results": {
            "b": b,
            "H": H,
            "conditional_mean_monte_carlo_max_abs_error": conditional_mean_max_error,
        },
        "outputs": paths,
    }







def _random_orthogonal(rng: np.random.Generator, n: int) -> np.ndarray:
    """Draw an orthogonal basis used only to vary current geometry."""

    q, r = np.linalg.qr(rng.normal(size=(n, n)))
    signs = np.sign(np.diag(r))
    signs[signs == 0.0] = 1.0
    return q @ np.diag(signs)


def _draw_current_state(
    rng: np.random.Generator, n: int, stabilizing: bool
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Draw one positive-definite G, symmetric H, and nonzero b.

    This generator samples *current-state triples*.  It does not simulate an
    inheritance process.  Stabilizing and saddle-shaped Hessians are both used
    because the projection identity concerns a quadratic random variable; it
    does not require exponentiating that quadratic into an integrable fitness
    weight.
    """

    basis_G = _random_orthogonal(rng, n)
    eigen_G = np.exp(rng.uniform(np.log(0.08), np.log(2.5), size=n))
    G = basis_G @ np.diag(eigen_G) @ basis_G.T

    basis_H = _random_orthogonal(rng, n)
    magnitude_H = np.exp(rng.uniform(np.log(0.03), np.log(0.9), size=n))
    if stabilizing:
        signs_H = -np.ones(n)
    else:
        signs_H = np.ones(n)
        signs_H[: max(1, n // 2)] = -1.0
        rng.shuffle(signs_H)
    H = basis_H @ np.diag(signs_H * magnitude_H) @ basis_H.T

    b = rng.normal(size=n)
    b /= np.linalg.norm(b)
    b *= float(np.exp(rng.uniform(np.log(0.08), np.log(1.5))))
    return b, H, G


def make_figure_2() -> dict[str, Any]:
    """Build Figure 2: a Gaussian-only numerical check of the identity.

    Main-text result
    ----------------
    ``projection_identity``.  For Gaussian X, odd central moments vanish, so
    Cov(L,Q_c)=0 and the population squared correlation of L with L+Q_c equals
    the analytic first-order variance share.

    Scope
    -----
    This panel checks that identity and finite-sample implementation only.  It
    does not test rank recovery, selected-mean response, non-Gaussian genetic
    architectures, or a multi-generation recursion.
    """

    rng = np.random.default_rng(SEED + 2)
    dimensions = (2, 4, 8)
    triples_per_dimension = 120
    sample_size = 20_000

    records: list[dict[str, Any]] = []
    for n in dimensions:
        for replicate in range(triples_per_dimension):
            stabilizing = replicate % 2 == 0
            b, H, G = _draw_current_state(rng, n, stabilizing)
            v_lin, v_quad = variance_components(b, H, G)
            share = first_order_share(v_lin, v_quad)

            
            
            
            X = rng.standard_normal(size=(sample_size, n)) @ np.linalg.cholesky(G).T
            linear_term = X @ b
            
            quadratic_term = 0.5 * (
                np.einsum("ni,ij,nj->n", X, H, X) - np.trace(H @ G)
            )
            local_log_fitness = linear_term + quadratic_term
            empirical_r2 = float(np.corrcoef(linear_term, local_log_fitness)[0, 1] ** 2)

            records.append(
                {
                    "dimension": n,
                    "curvature": "stabilizing" if stabilizing else "saddle",
                    "A_g": share,
                    "empirical_R2": empirical_r2,
                    "absolute_error": abs(share - empirical_r2),
                }
            )

    errors = np.array([record["absolute_error"] for record in records])
    median_error = float(np.median(errors))
    p95_error = float(np.quantile(errors, 0.95))
    max_error = float(np.max(errors))

    
    
    assert median_error < 0.01
    assert p95_error < 0.03
    assert all(0.0 <= record["A_g"] <= 1.0 for record in records)
    assert all(0.0 <= record["empirical_R2"] <= 1.0 for record in records)

    fig, ax = plt.subplots(figsize=(3.65, 3.45))
    marker_by_dimension = {2: "o", 4: "s", 8: "^"}
    color_by_dimension = {2: BLUE, 4: GREEN, 8: ORANGE}
    for n in dimensions:
        subset = [record for record in records if record["dimension"] == n]
        ax.scatter(
            [record["A_g"] for record in subset],
            [record["empirical_R2"] for record in subset],
            s=16,
            marker=marker_by_dimension[n],
            facecolor=color_by_dimension[n],
            edgecolor="white",
            linewidth=0.25,
            alpha=0.56,
            label=rf"$n={n}$",
            zorder=3,
        )
    ax.plot([0, 1], [0, 1], color=DARK, linestyle=(0, (5, 3)), linewidth=1.15, zorder=2)
    ax.text(
        0.04,
        0.96,
        "Gaussian breeding values\n"
        rf"median $|\mathcal{{A}}_g-R^2|={median_error:.3f}$"
        "\n"
        rf"95th percentile $={p95_error:.3f}$",
        transform=ax.transAxes,
        ha="left",
        va="top",
        bbox={"boxstyle": "round,pad=0.3", "fc": "white", "ec": LIGHT_GREY},
    )
    ax.set(
        xlim=(-0.02, 1.02),
        ylim=(-0.02, 1.02),
        xlabel=r"analytical first-order share $\mathcal{A}_g$",
        ylabel=r"empirical $\mathrm{Corr}^2(L,L+Q_c)$",
        title="Gaussian projection identity",
    )
    ax.set_aspect("equal", adjustable="box")
    _style_axis(ax)
    ax.legend(frameon=False, loc="lower right", ncol=1)
    paths = _save_figure(fig, "figure2_projection_identity")

    return {
        "scientific_results": [
            SCIENTIFIC_RESULTS["variance_share"],
            SCIENTIFIC_RESULTS["projection_identity"],
        ],
        "parameters": {
            "random_seed": SEED + 2,
            "dimensions": dimensions,
            "triples_per_dimension": triples_per_dimension,
            "number_of_current_state_triples": len(records),
            "sample_size_per_triple": sample_size,
            "curvature_classes": ["stabilizing", "saddle"],
            "G_eigenvalue_range": [0.08, 2.5],
            "absolute_H_eigenvalue_range": [0.03, 0.9],
            "b_norm_range": [0.08, 1.5],
        },
        "results": {
            "median_absolute_error": median_error,
            "p95_absolute_error": p95_error,
            "maximum_absolute_error": max_error,
        },
        "outputs": paths,
    }







def _covariance_ellipse(
    ax: plt.Axes,
    covariance: np.ndarray,
    *,
    edgecolor: str,
    linestyle: str,
    linewidth: float,
) -> Ellipse:
    """Draw the 95% ellipse for the current G in Equation ``eq:scaling``."""

    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    scale_95 = math.sqrt(5.991464547107979)  
    width, height = 2.0 * scale_95 * np.sqrt(eigenvalues)
    angle = math.degrees(math.atan2(eigenvectors[1, 0], eigenvectors[0, 0]))
    ellipse = Ellipse(
        (0.0, 0.0),
        width=width,
        height=height,
        angle=angle,
        edgecolor=edgecolor,
        facecolor="none",
        linestyle=linestyle,
        linewidth=linewidth,
        zorder=3,
    )
    ax.add_patch(ellipse)
    return ellipse


def make_figure_3() -> dict[str, Any]:
    """Build Figure 3: covariance contraction raises the first-order share.

    Exact main-text links
    ---------------------
    ``eq:taylor`` supplies the single log conditional expected-fitness surface.
    ``eq:scaling`` states that replacing G by sG at fixed b and H multiplies
    V_lin by s and V_quad by s^2.  ``eq:Ag`` converts those two variances to the
    two values printed beside the covariance ellipses.  Thus every graphical
    element serves one result: contraction makes the quadratic term diminish
    faster and raises A_g while the gradient and curvature are maintained.

    The figure compares two current covariance states on the same surface.  It
    does not depict the across-generation recursion, population types,
    equilibria, or mutation.
    """

    G_broad = np.array([[1.0, 0.3], [0.3, 0.6]])
    scale = 0.11
    G_narrow = scale * G_broad
    b = np.array([0.75, 0.30])
    gamma = 0.80
    Gamma = gamma * np.eye(2)
    H = -Gamma

    broad_v_lin, broad_v_quad = variance_components(b, H, G_broad)
    narrow_v_lin, narrow_v_quad = variance_components(b, H, G_narrow)
    broad_share = first_order_share(broad_v_lin, broad_v_quad)
    narrow_share = first_order_share(narrow_v_lin, narrow_v_quad)

    
    
    assert math.isclose(narrow_v_lin, scale * broad_v_lin, rel_tol=1e-13)
    assert math.isclose(narrow_v_quad, scale**2 * broad_v_quad, rel_tol=1e-13)
    assert math.isclose(
        narrow_share,
        (scale * broad_v_lin)
        / (scale * broad_v_lin + scale**2 * broad_v_quad),
        rel_tol=1e-13,
    )
    assert math.isclose(broad_share, 0.603954030378526, rel_tol=1e-12)
    assert math.isclose(narrow_share, 0.9327200424967854, rel_tol=1e-12)

    x = np.linspace(-3.0, 3.0, 301)
    y = np.linspace(-3.0, 3.0, 301)
    xx, yy = np.meshgrid(x, y)
    ell = b[0] * xx + b[1] * yy - 0.5 * gamma * (xx**2 + yy**2)
    levels = np.linspace(float(np.min(ell)), float(np.max(ell)), 8)

    fig, ax = plt.subplots(figsize=(3.65, 3.35))
    
    
    ax.contour(xx, yy, ell, levels=levels, colors="#C3C9CF", linewidths=0.45, zorder=1)
    
    
    _covariance_ellipse(
        ax,
        G_broad,
        edgecolor=BLUE,
        linestyle="-",
        linewidth=1.9,
    )
    _covariance_ellipse(
        ax,
        G_narrow,
        edgecolor=ORANGE,
        linestyle=(0, (4, 2.2)),
        linewidth=1.8,
    )
    
    
    ax.text(
        -2.82,
        -2.43,
        rf"broad $\mathbf{{G}}$: $\mathcal{{A}}_g={broad_share:.3f}$",
        color=BLUE,
        ha="left",
        va="center",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.2, "alpha": 0.94},
        zorder=5,
    )
    ax.text(
        0.40,
        -2.43,
        rf"narrow $\mathbf{{G}}$: $\mathcal{{A}}_g={narrow_share:.3f}$",
        color=ORANGE,
        ha="left",
        va="center",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.2, "alpha": 0.94},
        zorder=5,
    )
    ax.set(
        xlim=(-3.0, 3.0),
        ylim=(-3.0, 3.0),
        xlabel=r"breeding value $a_1$",
        ylabel=r"breeding value $a_2$",
    )
    ax.set_aspect("equal", adjustable="box")
    _style_axis(ax, grid=False)
    paths = _save_figure(fig, "figure3_covariance_contraction")

    return {
        "scientific_results": [
            SCIENTIFIC_RESULTS["local_expansion"],
            SCIENTIFIC_RESULTS["variance_share"],
            SCIENTIFIC_RESULTS["scaling"],
        ],
        "parameters": {
            "b": b,
            "H": H,
            "Gamma": Gamma,
            "G_broad": G_broad,
            "narrow_scale": scale,
            "G_narrow": G_narrow,
        },
        "results": {
            "broad": {
                "trace_G": np.trace(G_broad),
                "V_lin": broad_v_lin,
                "V_quad": broad_v_quad,
                "A_g": broad_share,
            },
            "narrow": {
                "trace_G": np.trace(G_narrow),
                "V_lin": narrow_v_lin,
                "V_quad": narrow_v_quad,
                "A_g": narrow_share,
            },
            "verified_scaling_ratios": {
                "V_lin_narrow_over_broad": narrow_v_lin / broad_v_lin,
                "V_quad_narrow_over_broad": narrow_v_quad / broad_v_quad,
            },
        },
        "outputs": paths,
    }







def scalar_fixed_point(B: float, gamma: float, rho: float) -> float:
    """Return the positive fixed point of the scalar fixed-B recursion.

    Main-text result
    ----------------
    ``scalar_dynamics``.  For gamma>0 the positive quadratic root is used.
    For gamma=0 there is no covariance compression and g*=B.  The function is
    restricted to rho<1 because rho=1 is the separate collapse boundary
    G_t=(G_0^{-1}+t Gamma)^{-1} for complete retention.
    """

    if B <= 0.0 or gamma < 0.0 or not 0.0 <= rho < 1.0:
        raise ValueError("Require B>0, gamma>=0, and 0<=rho<1.")
    if gamma == 0.0:
        return B
    linear = (1.0 - rho) * (1.0 - gamma * B)
    discriminant = linear**2 + 4.0 * gamma * B * (1.0 - rho)
    return float((-linear + math.sqrt(discriminant)) / (2.0 * gamma))


def make_figure_4() -> dict[str, Any]:
    """Build Figure 4: fixed-B covariance dynamics and a prescribed b_t.

    Exact main-text links
    ---------------------
    Panel A normalizes the covariance trajectory generated by
    ``eq:scalar_recursion`` and places it beside the externally prescribed
    gradient history.  The gradient is an input, not an output of the
    recursion.  Panel B evaluates ``eq:Ag`` at each current state.  The
    assertions below verify ``eq:scaling`` during the maintained-gradient
    interval: V_lin follows g_t and V_quad follows g_t squared.

    Biology
    -------
    This is a conditional short-timescale illustration.  It does not contain a
    mutation term and therefore does not represent a mutation-selection
    equilibrium or a natural-versus-breeding population comparison.
    """

    n_dimensions = 4
    g_initial = 4.0
    B = 1.0
    gamma = 0.30
    rho = 0.90
    maintained_until = 40
    gradient_initial = 1.0
    gradient_decay = 0.06
    final_generation = 100

    generations = np.arange(final_generation + 1)
    gradient_norm = np.where(
        generations <= maintained_until,
        gradient_initial,
        gradient_initial * np.exp(-gradient_decay * (generations - maintained_until)),
    )

    g = np.empty_like(generations, dtype=float)
    g[0] = g_initial
    for index in range(final_generation):
        
        
        g_selected = g[index] / (1.0 + gamma * g[index])
        g[index + 1] = (1.0 - rho) * B + rho * g_selected

    
    
    v_lin = gradient_norm**2 * g
    v_quad = 0.5 * n_dimensions * gamma**2 * g**2
    share = v_lin / (v_lin + v_quad)

    fixed_point = scalar_fixed_point(B, gamma, rho)
    fixed_point_residual = abs(
        fixed_point - ((1.0 - rho) * B + rho * fixed_point / (1.0 + gamma * fixed_point))
    )
    assert fixed_point_residual < 1e-13
    assert abs(g[-1] - fixed_point) < 1e-10
    assert (1.0 - rho) * B <= fixed_point <= B
    assert np.all(g > 0.0)
    
    
    asserted_next_g = (1.0 - rho) * B + rho * g[:-1] / (1.0 + gamma * g[:-1])
    assert np.allclose(g[1:], asserted_next_g, rtol=1e-13, atol=1e-14)
    
    assert np.allclose(share, v_lin / (v_lin + v_quad), rtol=1e-14, atol=1e-15)
    assert np.all((share >= 0.0) & (share <= 1.0))
    
    
    maintained_slice = slice(0, maintained_until + 1)
    normalized_g_maintained = g[maintained_slice] / g[0]
    assert np.allclose(
        v_lin[maintained_slice] / v_lin[0],
        normalized_g_maintained,
        rtol=1e-13,
        atol=1e-14,
    )
    assert np.allclose(
        v_quad[maintained_slice] / v_quad[0],
        normalized_g_maintained**2,
        rtol=1e-13,
        atol=1e-14,
    )

    
    
    
    for index in (0, maintained_until, final_generation):
        b_vector = np.zeros(n_dimensions)
        b_vector[0] = gradient_norm[index]
        H_matrix = -gamma * np.eye(n_dimensions)
        G_matrix = g[index] * np.eye(n_dimensions)
        matrix_v_lin, matrix_v_quad = variance_components(b_vector, H_matrix, G_matrix)
        assert math.isclose(matrix_v_lin, v_lin[index], rel_tol=1e-13)
        assert math.isclose(matrix_v_quad, v_quad[index], rel_tol=1e-13)

    normalized_g = g / g[0]
    normalized_gradient = gradient_norm / gradient_norm[0]

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(7.20, 2.70))

    
    
    ax_a.plot(generations, normalized_g, color=BLUE)
    ax_a.plot(
        generations,
        normalized_gradient,
        color=ORANGE,
        linestyle=(0, (5, 2.5)),
    )
    ax_a.set(
        xlim=(0, final_generation),
        ylim=(0, 1.05),
        xlabel="generation",
        ylabel="proportion of initial value",
        title="a. Covariance and imposed gradient",
    )
    _style_axis(ax_a, grid=False)
    
    ax_a.text(
        17,
        0.955,
        r"$\|\mathbf{b}_t\|/\|\mathbf{b}_0\|$",
        color=ORANGE,
        ha="left",
        va="top",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.8, "alpha": 0.92},
    )
    ax_a.text(
        18,
        0.20,
        r"$g_t/g_0$",
        color=BLUE,
        ha="left",
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.8, "alpha": 0.92},
    )

    
    ax_b.plot(generations, share, color=GREEN)
    ax_b.set(
        xlim=(0, final_generation),
        ylim=(0, 1.0),
        xlabel="generation",
        ylabel=r"first-order share $\mathcal{A}_g(t)$",
        title="b. First-order variance share",
    )
    _style_axis(ax_b, grid=False)

    
    
    for ax in (ax_a, ax_b):
        ax.axvline(maintained_until, color="#AEB5BC", linestyle=":", linewidth=0.75, zorder=0)
    ax_a.text(
        maintained_until + 1.5,
        0.045,
        r"$t=40$",
        color=MID_GREY,
        fontsize=7.1,
        ha="left",
        va="bottom",
    )

    fig.subplots_adjust(wspace=0.32)
    paths = _save_figure(fig, "figure4_fixedB_trajectory")
    return {
        "scientific_results": [
            SCIENTIFIC_RESULTS["variance_share"],
            SCIENTIFIC_RESULTS["fixed_B_recursion"],
            SCIENTIFIC_RESULTS["scalar_dynamics"],
            SCIENTIFIC_RESULTS["scaling"],
        ],
        "parameters": {
            "n_dimensions": n_dimensions,
            "g_initial": g_initial,
            "B": B,
            "gamma": gamma,
            "rho": rho,
            "maintained_gradient_through_generation": maintained_until,
            "gradient_norm_initial": gradient_initial,
            "gradient_decay_after_maintenance": gradient_decay,
            "final_generation": final_generation,
        },
        "results": {
            "scalar_fixed_point": fixed_point,
            "fixed_point_residual": fixed_point_residual,
            "g_at_final_generation": g[-1],
            "A_g_initial": share[0],
            "A_g_at_end_of_maintained_gradient": share[maintained_until],
            "A_g_final": share[-1],
            "V_lin_initial": v_lin[0],
            "V_quad_initial": v_quad[0],
            "V_lin_at_end_of_maintained_gradient": v_lin[maintained_until],
            "V_quad_at_end_of_maintained_gradient": v_quad[maintained_until],
            "verified_max_abs_scalar_recursion_error": float(
                np.max(np.abs(g[1:] - asserted_next_g))
            ),
            "verified_max_abs_V_lin_scaling_error": float(
                np.max(
                    np.abs(
                        v_lin[maintained_slice] / v_lin[0]
                        - normalized_g_maintained
                    )
                )
            ),
            "verified_max_abs_V_quad_scaling_error": float(
                np.max(
                    np.abs(
                        v_quad[maintained_slice] / v_quad[0]
                        - normalized_g_maintained**2
                    )
                )
            ),
        },
        "outputs": paths,
    }


def main() -> None:
    """Generate all figures, then write the values used by their captions."""

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "provenance": {
            "script": Path(__file__).name,
            "random_seed": SEED,
            "purpose": (
                "Numerical record for the four study figures. "
                "Every scientific calculation is linked to a named main-text result."
            ),
        },
        "result_map": SCIENTIFIC_RESULTS,
        "equation_labels": EQUATION_LABELS,
        "figure1": make_figure_1(),
        "figure2": make_figure_2(),
        "figure3": make_figure_3(),
        "figure4": make_figure_4(),
    }
    with RESULTS_PATH.open("w", encoding="utf-8") as stream:
        json.dump(_jsonable(results), stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
