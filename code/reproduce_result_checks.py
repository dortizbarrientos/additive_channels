#!/usr/bin/env python3
"""Numerical examples for the theoretical results and their scope conditions.

Run ``python code/reproduce_result_checks.py`` from the repository root. The
script writes ``outputs/result_checks.json`` and exits unsuccessfully if a
check fails. It uses deterministic integration and population least squares,
not simulated sample correlations. The examples check implementations and
illustrate statements; finite numerical checks do not prove general results.

In particular, a fit to log conditional expected fitness is distinct from
prediction of a reproductively weighted parental mean. No offspring response
is calculated without a separately specified inheritance rule.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.integrate import quad
from scipy.optimize import root
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = 2e-10


def close(actual, expected, *, atol=TOLERANCE, rtol=TOLERANCE):
    """Use an explicit tolerance and report both sides when a check fails."""
    np.testing.assert_allclose(actual, expected, atol=atol, rtol=rtol)


def symmetric_root(matrix):
    """Positive square root of a positive-definite covariance matrix."""
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    assert np.min(eigenvalues) > 0
    return (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T


def gaussian_grid(covariance, order=40):
    """Nodes and probabilities for integration under N(0, covariance).

    The tensor rule is deliberately confined to small illustrative examples.
    A singular covariance must first be restricted to its varying support.
    """
    covariance = np.atleast_2d(covariance)
    dimension = len(covariance)
    nodes, weights = hermgauss(order)
    grid = np.stack(np.meshgrid(*([nodes] * dimension), indexing="ij"), -1)
    weight_grid = np.stack(np.meshgrid(*([weights] * dimension), indexing="ij"), -1)
    probabilities = np.prod(weight_grid, axis=-1).ravel() / np.pi ** (dimension / 2)
    values = np.sqrt(2) * grid.reshape(-1, dimension) @ np.linalg.cholesky(covariance).T
    close(probabilities.sum(), 1)
    return values, probabilities


def variance(values, weights):
    centred = values - weights @ values
    return float(weights @ (centred * centred))


def fit(design, outcome, weights):
    """Population weighted least squares, including the supplied intercept."""
    square_root_weights = np.sqrt(weights)
    coefficients = np.linalg.lstsq(
        design * square_root_weights[:, None],
        outcome * square_root_weights, rcond=None,
    )[0]
    fitted = design @ coefficients
    residual = outcome - fitted
    total = variance(outcome, weights)
    r_squared = None if total == 0 else 1 - variance(residual, weights) / total
    return coefficients, fitted, r_squared


def components(b, H, G):
    """Closed Gaussian formulas used as the comparator, not as quadrature."""
    linear = float(b @ G @ b)
    quadratic = float(np.trace(H @ G @ H @ G) / 2)
    share = None if linear + quadratic == 0 else linear / (linear + quadratic)
    return linear, quadratic, share


def reproductive_moments(values, probabilities, log_output):
    """Reweight the original population by expected reproductive output.

    Subtracting the maximum log output stabilises exponentiation; its factor
    cancels on normalisation. These are selected-parent, not offspring, moments.
    """
    selected = probabilities * np.exp(log_output - np.max(log_output))
    selected /= selected.sum()
    mean = selected @ values
    centred = values - mean
    covariance = (centred.T * selected) @ centred
    return mean, covariance


def conditional_mean_and_log():
    """Environmental convolution, Jensen's inequality and population weights."""
    theta, width, environmental_variance = 4., 1., 1.
    cases = []
    for breeding_value in (-2., 0., 4.):
        # Directly integrate phenotype-dependent expected output over E.
        numerical = quad(
            lambda e: np.exp(-(breeding_value + e - theta) ** 2 / (2 * width))
            * norm.pdf(e, scale=np.sqrt(environmental_variance)),
            -np.inf, np.inf, epsabs=1e-13,
        )[0]
        exact = np.sqrt(width / (width + environmental_variance)) * np.exp(
            -(breeding_value - theta) ** 2 / (2 * (width + environmental_variance))
        )
        close(numerical, exact)
        mean_log = -((breeding_value - theta) ** 2 + environmental_variance) / (2 * width)
        gap = np.log(exact) - mean_log
        assert gap > 0
        cases.append(dict(a=breeding_value, conditional_mean=exact, log_mean=np.log(exact),
                          mean_log=mean_log, jensen_gap=gap))
    assert not np.isclose(cases[0]["jensen_gap"], cases[-1]["jensen_gap"])

    ell = lambda a: 2 * a - a * a / 4
    for step in (.2, .8, 1.7):
        close((ell(step) - ell(-step)) / (2 * step), 2)
        close((ell(step) - 2 * ell(0) + ell(-step)) / step ** 2, -.5)
    close([ell(.2), ell(-.2)], [.39, -.41])

    population_examples = []
    for upper_frequency in (.25, .75):
        p = np.array([1 - upper_frequency, upper_frequency])
        expected_output = np.array([1., 2.])
        selected = p * expected_output / (p @ expected_output)
        close(p * (3.7 * expected_output) / (p @ (3.7 * expected_output)), selected)
        population_examples.append(dict(upper_frequency=upper_frequency,
                                        mean_output=p @ expected_output,
                                        upper_reproductive_fraction=selected[1]))
    close([x["mean_output"] for x in population_examples], [1.25, 1.75])
    close([x["upper_reproductive_fraction"] for x in population_examples], [.4, 6 / 7])
    close(np.log(np.mean([1., 3.])), np.log(2))
    return dict(environmental_average=cases, finite_difference_slope=2.,
                finite_difference_curvature=-.5, population_examples=population_examples,
                zero_and_two_offspring=dict(log_mean=0., mean_log=None,
                                           reason="An individual zero count has no finite logarithm."))


def gaussian_projection():
    """Check the multivariate variance formulas by integration and regression."""
    G = np.array([[1., .3], [.3, .6]])
    b = np.array([.75, .3])
    H = np.array([[-.8, .25], [.25, .3]])  # A symmetric saddle, not just a diagonal Hessian.
    x, p = gaussian_grid(G)
    linear = x @ b
    quadratic = np.einsum("ni,ij,nj->n", x, H, x) / 2
    centred_quadratic = quadratic - p @ quadratic
    ell = 1.2 + linear + quadratic
    expected_linear, expected_quadratic, share = components(b, H, G)
    coefficients, fitted, r_squared = fit(np.column_stack((np.ones(len(x)), x)), ell, p)
    covariance = float(p @ (linear * centred_quadratic))
    close(p @ quadratic, np.trace(H @ G) / 2)
    close(covariance, 0)
    close([variance(linear, p), variance(quadratic, p)], [expected_linear, expected_quadratic])
    close(coefficients, np.r_[1.2 + np.trace(H @ G) / 2, b])
    close(r_squared, share)
    close(variance(ell - fitted, p), expected_quadratic)
    # The guide changes centimetres to units ten times smaller.
    close(components(np.array([.2]), np.array([[-.005]]), np.array([[100.]])),
          [4, .125, 32 / 33])
    close(components(np.array([2.]), np.array([[-.5]]), np.array([[.5]])),
          [2, .03125, 64 / 65])
    return dict(G=G, b=b, H=H, V_linear=expected_linear, V_quadratic=expected_quadratic,
                linear_quadratic_covariance=covariance, fitted_coefficients=coefficients,
                first_order_share=share, weighted_regression_R2=r_squared,
                guide_tenfold_unit_change=dict(b=.2, H=-.005, G=100., V_linear=4., V_quadratic=.125),
                guide_half_variance=dict(G=.5, V_linear=2., V_quadratic=.03125, share=64 / 65))


def noisy_regression_ratio():
    """A constant log-mean gap changes each R², while their ratio recovers A_g."""
    z, p = gaussian_grid(np.eye(2))
    x, independent_noise = z.T
    ell = 2 * x - .25 * x * x
    # U=exp(-2+2E) is independent lognormal noise with E[U]=1.
    # Hence E[W|A]=exp(ell) but E[log W|A]=ell-2.
    log_U = -2 + 2 * independent_noise
    close(p @ np.exp(log_U), 1)
    close([p @ log_U, p @ (log_U * log_U)], [-2, 8])
    outcome = ell + log_U
    _, _, linear_r2 = fit(np.column_stack((np.ones(len(x)), x)), outcome, p)
    _, _, full_r2 = fit(np.column_stack((np.ones(len(x)), x, x * x)), outcome, p)
    close([linear_r2, full_r2, linear_r2 / full_r2], [32 / 65, 33 / 65, 32 / 33])
    return dict(log_error_mean=-2., log_error_variance=4., log_error_second_moment=8.,
                linear_R2=linear_r2, quadratic_R2=full_r2, ratio=linear_r2 / full_r2,
                condition="Constant conditional log-mean gap and finite second moment of log error.")


def boundaries_and_non_gaussian_cases():
    """Zero terms, a singular covariance, and two limits of Gaussian formulas."""
    close(components(np.array([0.]), np.array([[-1.]]), np.eye(1))[2], 0)
    close(components(np.array([1.]), np.zeros((1, 1)), np.eye(1))[2], 1)
    assert components(np.array([0.]), np.zeros((1, 1)), np.eye(1))[2] is None

    # Work on the one-dimensional support, then embed it in two coordinates.
    G = np.diag([1., 0.])
    b, H = np.array([2., 5.]), np.array([[-.5, .8], [.8, -1.]])
    node, p = gaussian_grid([[1.]])
    x = np.column_stack((node[:, 0], np.zeros(len(node))))
    ell = x @ b + np.einsum("ni,ij,nj->n", x, H, x) / 2
    _, _, observed_share = fit(np.column_stack((np.ones(len(x)), x[:, 0])), ell, p)
    close(components(b, H, G), [4, .125, 32 / 33])
    close(observed_share, 32 / 33)
    selected_mean, selected_covariance = reproductive_moments(x, p, ell)
    close(selected_mean, [4 / 3, 0])
    close(selected_covariance, np.diag([2 / 3, 0]))

    # With only two support points every nonconstant response is affine there.
    # Skewness makes the linear and centred quadratic terms correlated.
    asymmetric_x, asymmetric_p = np.array([-1., 2.]), np.array([2 / 3, 1 / 3])
    asymmetric_q = -.25 * (asymmetric_x ** 2 - 2)
    asymmetric_y = asymmetric_x + asymmetric_q
    _, _, asymmetric_r2 = fit(np.column_stack((np.ones(2), asymmetric_x)), asymmetric_y, asymmetric_p)
    cov = float(asymmetric_p @ (asymmetric_x * asymmetric_q))
    close([asymmetric_p @ asymmetric_x ** 3, cov, variance(asymmetric_q, asymmetric_p), asymmetric_r2],
          [2, -.5, .125, 1])
    close(components(np.array([1.]), np.array([[-.5]]), np.array([[2.]]))[2], .8)

    # Symmetry restores orthogonality but not the Gaussian fourth moment.
    symmetric_x, symmetric_p = np.array([-1., 1.]), np.array([.5, .5])
    symmetric_q = -.5 * (symmetric_x ** 2 - 1)
    close(symmetric_p @ (symmetric_x * symmetric_q), 0)
    close(variance(symmetric_q, symmetric_p), 0)
    return dict(zero_gradient_share=0., zero_curvature_share=1., constant_target_share=None,
                zero_gradient_correlation=None,
                singular_support=dict(first_order_share=observed_share,
                                      selected_mean=selected_mean, selected_covariance=selected_covariance),
                asymmetric_distribution=dict(third_moment=2., linear_quadratic_covariance=cov,
                                             actual_quadratic_variance=.125,
                                             gaussian_quadratic_variance=.5,
                                             actual_regression_R2=asymmetric_r2,
                                             gaussian_expression=.8),
                symmetric_non_gaussian=dict(actual_quadratic_variance=0., gaussian_expression=.5))


def selected_parent_moments():
    """Integrate original Gaussian populations with stabilising or saddle weights."""
    G = np.array([[1., .2], [.2, .8]])
    b = np.array([.6, -.4])
    x, p = gaussian_grid(G, order=50)
    records = []
    for name, Gamma in (
        ("stabilising", np.array([[.4, .1], [.1, .3]])),
        ("integrable_saddle", np.array([[.4, .1], [.1, -.2]])),
    ):
        precision = np.linalg.inv(G) + Gamma
        assert np.min(np.linalg.eigvalsh(precision)) > 0
        ell = x @ b - np.einsum("ni,ij,nj->n", x, Gamma, x) / 2
        numerical_mean, numerical_covariance = reproductive_moments(x, p, ell)
        expected_covariance = np.linalg.inv(precision)
        expected_mean = expected_covariance @ b
        close(numerical_mean, expected_mean)
        close(numerical_covariance, expected_covariance)
        if name == "stabilising":
            assert np.min(np.linalg.eigvalsh(G - expected_covariance)) > 0
        else:
            assert np.max(np.linalg.eigvalsh(expected_covariance - G)) > 0
        inverse_G = np.linalg.inv(G)
        error = G @ b - expected_mean
        relative_error = np.sqrt((error @ inverse_G @ error) / (expected_mean @ inverse_G @ expected_mean))
        square_root_G = symmetric_root(G)
        T = square_root_G @ Gamma @ square_root_G
        spectral_bound, frobenius_bound = np.linalg.norm(T, 2), np.linalg.norm(T, "fro")
        assert relative_error <= spectral_bound + TOLERANCE
        assert spectral_bound <= frobenius_bound + TOLERANCE
        close(frobenius_bound, np.sqrt(2 * components(b, -Gamma, G)[1]))
        records.append(dict(case=name, G=G, Gamma=Gamma, b=b,
                            minimum_combined_precision_eigenvalue=np.min(np.linalg.eigvalsh(precision)),
                            selected_mean=numerical_mean, selected_covariance=numerical_covariance,
                            relative_error_G_inverse_norm=relative_error,
                            spectral_bound=spectral_bound, frobenius_bound=frobenius_bound))
    # This counterexample does not define a normalisable selected distribution.
    assert np.min(np.linalg.eigvalsh(np.eye(2) + np.diag([0., -1.2]))) < 0
    scalar_examples = []
    for slope in (2., 10.):
        V_linear, V_quadratic, share = components(np.array([slope]), np.array([[-.5]]), np.eye(1))
        full, linear = slope / 1.5, slope
        close(abs(linear - full) / abs(full), .5)
        scalar_examples.append(dict(b=slope, V_linear=V_linear, V_quadratic=V_quadratic,
                                    first_order_share=share, first_order_shift=linear,
                                    exact_shift=full, relative_error=.5))
    # Even the 32/33 example can reverse a pair's ranking beyond the optimum.
    # These are tail values of N(0,1), not a statement about frequent reversals.
    rank_values = np.array([4., 5.])
    rank_linear = 2 * rank_values - .25
    rank_curved = 2 * rank_values - .25 * rank_values ** 2
    assert rank_linear[0] < rank_linear[1] and rank_curved[0] > rank_curved[1]
    return dict(matrix_examples=records, scalar_examples=scalar_examples,
                tail_rank_reversal=dict(breeding_values=rank_values,
                                        linear_fit=rank_linear, log_expected_output=rank_curved),
                rejected_nonintegrable_precision_eigenvalues=[-.2, 1.])


def orientation_and_absolute_scale():
    """Equal variance shares need not imply equal displacement errors."""
    G = np.array([[1., .3], [.3, .6]])
    square_root_G = symmetric_root(G)
    inverse_square_root_G = np.linalg.inv(square_root_G)
    T = np.diag([.1, .8])
    Gamma = inverse_square_root_G @ T @ inverse_square_root_G
    records = []
    for angle in (0., 45., 90.):
        radians = np.deg2rad(angle)
        c = np.array([np.cos(radians), np.sin(radians)])
        b = inverse_square_root_G @ c
        linear, quadratic, share = components(b, -Gamma, G)
        full = np.linalg.solve(np.linalg.inv(G) + Gamma, b)
        error = G @ b - full
        relative = np.linalg.norm(inverse_square_root_G @ error) / np.linalg.norm(inverse_square_root_G @ full)
        close([linear, quadratic, share], [1, .325, 1 / 1.325])
        assert relative <= .8 + TOLERANCE
        records.append(dict(whitened_gradient_angle_degrees=angle,
                            first_order_share=share, relative_displacement_error=relative))
    close([records[0]["relative_displacement_error"], records[-1]["relative_displacement_error"]], [.1, .8])

    # Holding the gradient's Euclidean length fixed in the original coordinates
    # gives the separate Rayleigh-quotient result. It is not the rotation above.
    eigenvalues, eigenvectors = np.linalg.eigh(G)
    physical_linear_variances = []
    for angle in np.linspace(0, 2 * np.pi, 25):
        physical_b = np.array([np.cos(angle), np.sin(angle)])
        value = float(physical_b @ G @ physical_b)
        assert eigenvalues[0] - TOLERANCE <= value <= eigenvalues[-1] + TOLERANCE
        physical_linear_variances.append(value)
    close([eigenvectors[:, i] @ G @ eigenvectors[:, i] for i in (0, 1)], eigenvalues)
    return dict(G=G, whitened_curvature_eigenvalues=[.1, .8], V_linear=1., V_quadratic=.325,
                examples=records, fixed_euclidean_gradient_rayleigh_bounds=eigenvalues,
                condition="Whitened gradient length and curvature spectrum are held fixed.")


def inheritance_matrix_and_limits():
    """Test a noncommuting matrix interval and the distinct rho=1 limit."""
    B = np.array([[1., .25], [.25, .6]])
    Gamma = np.array([[.6, -.15], [-.15, .3]])
    rho = .65
    lower = (1 - rho) * B
    square_root_B = symmetric_root(B)

    def update(G):
        return lower + rho * np.linalg.inv(np.linalg.inv(G) + Gamma)

    minimum_lower_gap, minimum_upper_gap = np.inf, np.inf
    for angle in (0., .37, 1.1):
        rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        for eigenvalues in ((1 - rho, 1 - rho), (1 - rho, 1), (.5, .8), (1, 1)):
            G = square_root_B @ rotation @ np.diag(eigenvalues) @ rotation.T @ square_root_B
            next_G = update(G)
            minimum_lower_gap = min(minimum_lower_gap, float(np.min(np.linalg.eigvalsh(next_G - lower))))
            minimum_upper_gap = min(minimum_upper_gap, float(np.min(np.linalg.eigvalsh(B - next_G))))
    assert minimum_lower_gap >= -TOLERANCE and minimum_upper_gap >= -TOLERANCE

    def unpack(parameters):
        return np.array([[parameters[0], parameters[1]], [parameters[1], parameters[2]]])

    def residual(parameters):
        difference = update(unpack(parameters)) - unpack(parameters)
        return difference[[0, 0, 1], [0, 1, 1]]

    solution = root(residual, [.8, .2, .5])
    assert solution.success
    fixed = unpack(solution.x)
    close(update(fixed), fixed)
    assert np.min(np.linalg.eigvalsh(fixed - lower)) > 0
    assert np.min(np.linalg.eigvalsh(B - fixed)) > 0

    # Fixed effects alone do not fix the genic baseline: allele frequencies enter it.
    close([2 * .5 * .5, 2 * .8 * .2], [.5, .32])

    initial = np.array([[1., .4], [.4, 2.]])
    semidefinite_curvature = np.diag([.5, 0.])
    current = initial.copy()
    for generation in range(1, 7):
        current = np.linalg.inv(np.linalg.inv(current) + semidefinite_curvature)
        close(current, np.linalg.inv(np.linalg.inv(initial) + generation * semidefinite_curvature))
    far_future = np.linalg.inv(np.linalg.inv(initial) + 1e7 * semidefinite_curvature)
    # Correlation changes the retained null-space variance to a Schur complement.
    null_space_limit = initial[1, 1] - initial[0, 1] ** 2 / initial[0, 0]
    close(far_future, np.diag([0., null_space_limit]), atol=3e-7, rtol=3e-7)
    positive_curvature_limit = np.linalg.inv(np.linalg.inv(initial) + 1e7 * Gamma)
    assert np.max(np.linalg.eigvalsh(positive_curvature_limit)) < 1e-6
    close(np.linalg.inv(np.linalg.inv(initial) + np.zeros((2, 2))), initial)

    # The teaching scalar trajectory uses a different curvature and retention.
    trajectory = [1.]
    for _ in range(4):
        trajectory.append(.5 + .5 * trajectory[-1] / (1 + .5 * trajectory[-1]))
    guide_fixed = (np.sqrt(17) - 1) / 4
    close(.5 + .5 * guide_fixed / (1 + .5 * guide_fixed), guide_fixed)
    scalar_update = lambda g: .5 + .5 * g / (1 + .5 * g)
    for g, h in ((0., .2), (.1, 4.), (1., 12.)):
        observed_gap = abs(scalar_update(g) - scalar_update(h))
        exact_gap = .5 * abs(g - h) / ((1 + .5 * g) * (1 + .5 * h))
        close(observed_gap, exact_gap)
        assert observed_gap <= .5 * abs(g - h) + TOLERANCE
    for initial_g in (0., .1, 4.):
        current_g = initial_g
        for _ in range(80):
            current_g = scalar_update(current_g)
        close(current_g, guide_fixed)
    for g in (0., .2, 4.):
        # rho=0 restores the baseline immediately; gamma=0 has fixed point B.
        close((1 - 0) * 1 + 0 * g / (1 + .5 * g), 1)
    close((1 - .65) * 1 + .65 * 1 / (1 + 0 * 1), 1)
    return dict(B=B, Gamma=Gamma, rho=rho, interval_cases=12,
                minimum_lower_interval_gap=minimum_lower_gap, minimum_upper_interval_gap=minimum_upper_gap,
                example_fixed_point=fixed, fixed_point_residual=np.max(np.abs(update(fixed) - fixed)),
                matrix_scope="One checked fixed point; no general matrix uniqueness or convergence claim.",
                fixed_effect_genic_variances=[.5, .32], rho_one_initial=initial,
                rho_one_singular_curvature_limit=np.diag([0., null_space_limit]),
                guide_scalar_trajectory=trajectory, guide_scalar_fixed_point=guide_fixed,
                scalar_contraction_pairs=3, scalar_starting_values=[0., .1, 4.],
                scalar_rho_zero_next_variance=1., scalar_gamma_zero_fixed_variance=1.,
                guide_rho_one_variance_at_generation_four=1 / 3)


def prediction_shrinkage():
    """Check the specific rG substitution with coefficients kept on their true scale."""
    reliability = .6
    x, p = gaussian_grid([[reliability]])
    x = x[:, 0]
    ell = 2 * x - .25 * x * x
    _, _, observed = fit(np.column_stack((np.ones(len(x)), x)), ell, p)
    expected = 4 / (4 + reliability * .125)
    close(observed, expected)
    assert expected > 32 / 33
    return dict(reliability=reliability, true_share=32 / 33, naive_share=observed,
                condition="b and H are known on the true breeding-value scale; only G is replaced by rG.")


def phenotype_regression_conversion():
    """Recover conditional log curvature from population phenotype regressions.

    The first example independently integrates a positive Gaussian fitness
    function, fits its relative-fitness regression, and converts the resulting
    moments. The guide's separate polynomial example is moment algebra: its
    fitted polynomial need not be positive in the tails.
    """
    G, E, slope, curvature = .5, 1., .6, .4
    P = G + E
    z, p = gaussian_grid([[P]])
    z = z[:, 0]
    W = np.exp(slope * z - curvature * z * z / 2)
    w = W / (p @ W)
    coefficients, _, _ = fit(np.column_stack((np.ones(len(z)), z, .5 * z * z)), w, p)
    alpha, beta, gamma = coefficients
    close(alpha, 1 - .5 * gamma * P)
    selected_mean = G * beta
    selected_variance = G + G * G * (gamma - beta * beta)
    b = selected_mean / selected_variance
    H = 1 / G - 1 / selected_variance
    close([b, H], [slope / (1 + curvature * E), -curvature / (1 + curvature * E)])

    # Independent joint integration over A and E checks phenotype mediation.
    ae, population_weights = gaussian_grid(np.diag([G, E]))
    phenotype = ae.sum(axis=1)
    mean, covariance = reproductive_moments(ae[:, :1], population_weights,
                                           slope * phenotype - .5 * curvature * phenotype ** 2)
    close([mean[0], covariance[0, 0]], [selected_mean, selected_variance])

    guide_P, guide_beta, guide_gamma, guide_G = 1.5, .4, -.2, .5
    guide_alpha = 1 - .5 * guide_gamma * guide_P
    guide_selected_variance = guide_G + guide_G ** 2 * (guide_gamma - guide_beta ** 2)
    guide_b = guide_G * guide_beta / guide_selected_variance
    guide_H = 1 / guide_G - 1 / guide_selected_variance
    close([guide_alpha, guide_selected_variance, guide_b, guide_H],
          [1.15, .41, .4878048780487805, -.4390243902439024])
    raw_b = guide_beta / guide_alpha
    raw_H = guide_gamma / guide_alpha - (guide_beta / guide_alpha) ** 2
    assert not np.isclose(raw_b, guide_b) and not np.isclose(raw_H, guide_H)

    # A correlated two-trait example checks off-diagonal terms and matrix order.
    matrix_G = np.array([[.7, .2], [.2, .5]])
    matrix_E = np.array([[.6, -.1], [-.1, .8]])
    matrix_P = matrix_G + matrix_E
    phenotype_slope = np.array([.5, -.3])
    phenotype_curvature = np.array([[.4, .12], [.12, .3]])
    z2, p2 = gaussian_grid(matrix_P)
    W2 = np.exp(z2 @ phenotype_slope - np.einsum("ni,ij,nj->n", z2, phenotype_curvature, z2) / 2)
    w2 = W2 / (p2 @ W2)
    design = np.column_stack((np.ones(len(z2)), z2, .5 * z2[:, 0] ** 2,
                              z2[:, 0] * z2[:, 1], .5 * z2[:, 1] ** 2))
    coefficients2, _, _ = fit(design, w2, p2)
    alpha2, beta2 = coefficients2[0], coefficients2[1:3]
    gamma2 = np.array([[coefficients2[3], coefficients2[4]],
                       [coefficients2[4], coefficients2[5]]])
    close(alpha2, 1 - np.trace(gamma2 @ matrix_P) / 2)
    close((p2 * w2) @ z2, matrix_P @ beta2)
    close((z2.T * (p2 * w2)) @ z2, matrix_P + matrix_P @ gamma2 @ matrix_P)
    matrix_selected_mean = matrix_G @ beta2
    matrix_selected_covariance = matrix_G + matrix_G @ (gamma2 - np.outer(beta2, beta2)) @ matrix_G
    matrix_b = np.linalg.solve(matrix_selected_covariance, matrix_selected_mean)
    matrix_H = np.linalg.inv(matrix_G) - np.linalg.inv(matrix_selected_covariance)
    integrated_environment = np.linalg.inv(np.linalg.inv(matrix_E) + phenotype_curvature)
    exact_b = phenotype_slope - phenotype_curvature @ integrated_environment @ phenotype_slope
    exact_H = -phenotype_curvature + phenotype_curvature @ integrated_environment @ phenotype_curvature
    close(matrix_b, exact_b)
    close(matrix_H, exact_H)

    return dict(positive_fitness_example=dict(G=G, E=E, P=P, phenotype_log_slope=slope,
                                              phenotype_stabilising_curvature=curvature,
                                              regression_alpha=alpha, regression_beta=beta, regression_gamma=gamma,
                                              selected_mean=selected_mean, selected_variance=selected_variance,
                                              conditional_log_slope=b, conditional_log_curvature=H),
                guide_moment_example=dict(alpha=guide_alpha, selected_variance=guide_selected_variance,
                                          b=guide_b, H=guide_H, raw_polynomial_log_slope=raw_b,
                                          raw_polynomial_log_curvature=raw_H),
                two_trait_positive_fitness_example=dict(G=matrix_G, E=matrix_E, beta=beta2,
                                                        gamma=gamma2, b=matrix_b, H=matrix_H,
                                                        selected_mean=matrix_selected_mean,
                                                        selected_covariance=matrix_selected_covariance),
                condition="Joint Gaussian A and phenotype, phenotype mediation, matching coordinates, and positive selected covariance.")


def local_quadratic_and_full_curve():
    """Keep the worked example's local share distinct from a nonquadratic R²."""
    x, p = gaussian_grid([[1.]], order=60)
    x = x[:, 0]
    b, H, quartic = .7, -.7, .08
    ell = b * x + .5 * H * x * x - quartic * x ** 4
    _, _, full_r2 = fit(np.column_stack((np.ones(len(x)), x)), ell, p)
    local_share = components(np.array([b]), np.array([[H]]), np.eye(1))[2]
    # Gaussian moments give Var(c X²-k X⁴)=2c²+96k²-24ck at G=1.
    quadratic_coefficient = H / 2
    exact_variance = b * b + 2 * quadratic_coefficient ** 2 + 96 * quartic ** 2 - 24 * quadratic_coefficient * quartic
    close(full_r2, b * b / exact_variance)
    close(local_share, 2 / 3)
    close(full_r2, .24240625309191652)
    return dict(b=b, H=H, G=1., quartic_strength=quartic,
                local_quadratic_share=local_share, full_curve_linear_R2=full_r2)


CHECKS = {
    "conditional_mean_and_log": conditional_mean_and_log,
    "gaussian_projection": gaussian_projection,
    "noisy_regression_ratio": noisy_regression_ratio,
    "boundaries_and_non_gaussian_cases": boundaries_and_non_gaussian_cases,
    "selected_parent_moments": selected_parent_moments,
    "orientation_and_absolute_scale": orientation_and_absolute_scale,
    "inheritance_matrix_and_limits": inheritance_matrix_and_limits,
    "prediction_shrinkage": prediction_shrinkage,
    "phenotype_regression_conversion": phenotype_regression_conversion,
    "local_quadratic_and_full_curve": local_quadratic_and_full_curve,
}


def json_ready(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/result_checks.json")
    args = parser.parse_args()
    results = {}
    for name, check in CHECKS.items():
        results[name] = dict(passed=True, values=check())
        print(f"Passed: {name}")
    report = dict(schema_version=1, check_groups=len(results), all_checks_passed=True,
                  method="Deterministic Gaussian quadrature, adaptive integration, weighted regression and matrix calculations.",
                  scope="Finite numerical examples illustrate theoretical results and verify calculations; they do not replace proofs.",
                  checks=results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(json_ready(report), indent=2, allow_nan=False) + "\n")
    print(f"All {len(results)} result-check groups passed. Wrote {args.output}.")


if __name__ == "__main__":
    main()
