"""Calculate and verify the geometry teaching examples.

All populations in this module are specified Gaussian models. The dots in the
figures are simulated illustrations; they are not empirical observations and
do not enter these population calculations.

Write the log-fitness Hessian as H. In these examples that matrix is
-H_STRENGTH * I, and its sign-reversed stabilising curvature is
Gamma = H_STRENGTH * I. Naming the scalar explicitly avoids confusing it with
H itself or with the genic covariance matrix B.

Run from this module's directory with ``python3 code/geometry.py``. The script
writes values.json and checks each analytic result by Gaussian quadrature.
"""
from pathlib import Path
import json

import numpy as np
from numpy.polynomial.hermite import hermgauss

ROOT = Path(__file__).resolve().parents[1]
H_STRENGTH = 0.8
PEAK = np.array([0.9375, 0.375])
PEAK_DISTANCE = float(np.linalg.norm(PEAK))
GRADIENT_NORM = H_STRENGTH * PEAK_DISTANCE
PRINCIPAL_VARIANCES = np.array([0.20, 0.005])  # Variances, not standard deviations.
BASELINE_COVARIANCE = np.array([[1.0, 0.3], [0.3, 0.6]])

# Each entry gives (label, covariance multiplier, distance-to-peak multiplier).
# Cases A and B reproduce the covariance comparison in Figure 3 of the accompanying paper.
# Cases C and D are additional teaching examples on the same fixed surface.
COMPARISONS = [
    ("A", 1.0, 1.0),
    ("B", 0.11, 1.0),
    ("C", 0.11, 0.0),
    ("D", 1.0, 1.0 / np.sqrt(0.11)),
]


def rotation(angle_degrees):
    """Return an orthonormal rotation, which preserves ordinary distances."""
    angle = np.deg2rad(angle_degrees)
    return np.array([[np.cos(angle), -np.sin(angle)],
                     [np.sin(angle), np.cos(angle)]])


def logfit(breeding_values, peak):
    """Log expected reproductive output, up to an irrelevant additive constant.

    The function is exactly quadratic. Exponentiating it gives positive
    expected output, not a draw of an individual's realised offspring count.
    """
    return -0.5 * H_STRENGTH * np.sum((breeding_values - peak) ** 2, axis=-1)


def analyse(mean, covariance, peak):
    """Compute variance components, the fitted plane and parental mean shifts.

    For X=A-mean, b=H_STRENGTH*(peak-mean) and H=-H_STRENGTH*I.
    Under Gaussian population weighting:
        V_linear = b' G b
        V_quadratic = trace((H G)^2) / 2
    Their ratio is the first-order variance share.

    The population least-squares plane has slope b and an intercept lowered by
    H_STRENGTH*trace(G)/2 relative to the surface at the population mean.
    Multiplying the Gaussian density by exp(logfit) gives a selected-parent
    mean shift (I + H_STRENGTH*G)^(-1) G b. Omitting curvature gives G b.
    Both concern weighted parental means. An inheritance model would be
    needed to calculate the offspring distribution.
    """
    gradient = H_STRENGTH * (peak - mean)
    linear = float(gradient @ covariance @ gradient)
    quadratic = float(H_STRENGTH**2 * np.trace(covariance @ covariance) / 2)
    curved_shift = np.linalg.solve(
        np.eye(2) + H_STRENGTH * covariance, covariance @ gradient
    )
    plane_shift = covariance @ gradient
    # At linear=0, the 90-degree value is a limiting triangle angle. The
    # ordinary angle with a zero fitted component is undefined.
    projection_angle = float(np.degrees(np.arctan2(np.sqrt(quadratic), np.sqrt(linear))))
    return {
        "L": linear,
        "Q": quadratic,
        "Ag": linear / (linear + quadratic),
        "alpha": float(logfit(mean, peak) - H_STRENGTH * np.trace(covariance) / 2),
        "curved_shift": curved_shift.tolist(),
        "plane_shift": plane_shift.tolist(),
        "angle": projection_angle,
        "mean": mean.tolist(),
        "covariance": covariance.tolist(),
        "gradient": gradient.tolist(),
    }


def check(mean, covariance, peak, analytic):
    """Check analytic results against independent weighted integration.

    A tensor product of Gauss-Hermite nodes integrates over the specified
    Gaussian population. We fit the plane by weighted least squares at those
    nodes, then calculate the variance partition and reproductive means from
    the node weights. This check does not use the plotted point sample.
    """
    nodes, weights_1d = hermgauss(32)
    population_weights = np.outer(weights_1d, weights_1d).ravel() / np.pi
    grid = np.stack(np.meshgrid(nodes, nodes, indexing="ij"), -1).reshape(-1, 2)
    centred_values = grid * np.sqrt(2) @ np.linalg.cholesky(covariance).T
    log_output = logfit(centred_values + mean, peak)
    design = np.column_stack((np.ones(len(population_weights)), centred_values))
    square_root_weights = np.sqrt(population_weights)
    coefficients = np.linalg.lstsq(
        square_root_weights[:, None] * design,
        square_root_weights * log_output,
        rcond=None,
    )[0]
    fitted = design @ coefficients
    linear = population_weights @ (fitted - population_weights @ fitted) ** 2
    quadratic = population_weights @ (log_output - fitted) ** 2
    total = population_weights @ (log_output - population_weights @ log_output) ** 2
    np.testing.assert_allclose(
        [linear, quadratic, 1 - quadratic / total],
        [analytic["L"], analytic["Q"], analytic["Ag"]],
        atol=2e-12,
    )
    for log_weights, key in [(log_output, "curved_shift"), (fitted, "plane_shift")]:
        # A common additive constant cancels from normalised reproductive
        # weights. Subtract the maximum for numerical stability.
        reproductive_weights = population_weights * np.exp(log_weights - log_weights.max())
        shift = (reproductive_weights @ centred_values) / reproductive_weights.sum()
        np.testing.assert_allclose(shift, analytic[key], atol=2e-12)


def datasets():
    """Return the three orientation examples and four comparison populations."""
    rotations = {}
    for angle in [0, 45, 90]:
        transform = rotation(angle)
        covariance = (transform * PRINCIPAL_VARIANCES) @ transform.T
        mean = np.zeros(2)
        # These coordinates point towards/across the same fitness peak. This
        # orthonormal coordinate change is separate from rotating covariance.
        peak = np.array([PEAK_DISTANCE, 0.0])
        result = analyse(mean, covariance, peak)
        check(mean, covariance, peak, result)
        rotations[str(angle)] = result

    comparisons = {}
    for label, scale, distance_multiplier in COMPARISONS:
        mean = PEAK * (1 - distance_multiplier)
        covariance = scale * BASELINE_COVARIANCE
        result = analyse(mean, covariance, PEAK)
        check(mean, covariance, PEAK, result)
        comparisons[label] = result
    np.testing.assert_allclose(comparisons["B"]["Ag"], comparisons["D"]["Ag"], atol=1e-14)

    return {
        "model": {
            "population": "Gaussian model populations; plotted individuals are simulated",
            "peak_in_original_trait_coordinates": PEAK.tolist(),
            "hessian": (-H_STRENGTH * np.eye(2)).tolist(),
            "distance_metric": "Euclidean distance in the displayed trait units",
            "illustration_seed": 20261111,
            "illustrated_parents": 225,
            "ellipse_population_coverage": 0.90,
            "quadrature_points_per_axis": 32,
        },
        "rotations": rotations,
        "comparison_cases": comparisons,
    }


if __name__ == "__main__":
    (ROOT / "values.json").write_text(json.dumps(datasets(), indent=2) + "\n")
    print("Checked three rotations and four comparison populations; wrote values.json.")
