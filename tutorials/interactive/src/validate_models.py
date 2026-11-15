"""Independent numerical checks for the repository guide's pure JavaScript models.

Run with the configured scientific Python runtime.  The report records independent calculation routes, not an independent human review.  It calls Node for the JavaScript results and compares
them with Gaussian quadrature, adaptive integration, matrix multiplication,
bracketed root finding and the saved results identified by the source manifest, as appropriate.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import subprocess

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import roots_hermitenorm
from reference_integrity import validate_reference

HERE = Path(__file__).resolve().parent
REF = json.loads((HERE / "scientific_reference.json").read_text())
validate_reference(REF)
CASES: list[dict] = []


def add(group, function, args, expected, *, atol=3e-11, rtol=3e-11):
    CASES.append(dict(group=group, function=function, args=args,
                      expected=expected, atol=atol, rtol=rtol))


# A 31-node rule integrates every polynomial used below exactly in theory.
u, w = roots_hermitenorm(31)
w /= math.sqrt(2 * math.pi)


def polynomial_moments(b, H, G, kappa=0.0):
    x = math.sqrt(G) * u
    linear = b * x
    even = .5 * H * x*x - kappa * x**4
    mu_even = float(w @ even)
    lin_var = float(w @ linear**2)
    even_var = float(w @ (even-mu_even)**2)
    total = float(w @ (linear+even-mu_even)**2)
    # Return the variance ratio even when one component is exactly zero.
    share = lin_var / total if total > 0 else None
    return lin_var, even_var, total, mu_even, share


for b, H, G in itertools.product(
        [-3, -1, 0, .5, 2, 10], [-2, -.5, 0, .05, .25, 1, 2],
        [0, .001, .1, 1, 4, 10]):
    L, Q, total, intercept, share = polynomial_moments(b, H, G)
    add("Gaussian decomposition", "components", [b, H, G],
        dict(linear=L, curved=Q, total=total, intercept=intercept, share=share))

for b, H, G, kappa in itertools.product(
        [0, .7, -2], [-.7, 0, .5], [0, .1, 1, 3], [0, .01, .08, .2]):
    L, Q, total, intercept, share = polynomial_moments(b, H, G, kappa)
    local_share = polynomial_moments(b, H, G)[-1]
    add("Quartic generating curve", "quarticComponents", [b, H, G, kappa],
        dict(linear=L, evenVariance=Q, total=total,
             fittedInterceptShift=intercept, fullShare=share,
             localShare=local_share))
add("Quartic canonical reference", "quarticComponents", [.7, -.7, 1, .08],
    dict(localShare=2/3,
         fullShare=REF["estimation"]["nonquadratic_generating_example"]["full_curve_linear_R2"],
         fittedInterceptShift=-.59, evenVariance=1.5314))

# The general grid checks the domain and exact moments.  The separate small
# grid below obtains the weighted moments by integration of the density.
for b, H, G in itertools.product(
        [-3, 0, .5, 2, 10], [-2, -.5, 0, .1, .25, 1, 2],
        [0, .1, 1, 4, 10]):
    d = 1-H*G
    expected = dict(normalisable=d > 0, denominator=d, linear=G*b)
    if d <= 0:
        expected.update(exact=None, variance=None, relativeError=None)
    else:
        exact = G*b/d
        expected.update(exact=exact, variance=G/d,
                        relativeError=abs(H*G) if exact else None,
                        signedRelativeError=-H*G if exact else None,
                        scaledCurvature=abs(H*G))
    add("Selection domains and moments", "selection", [b, H, G], expected)

for b, H, G in itertools.product([-2, 0, 2], [-1, -.5, 0, .25], [.1, 1]):
    def density_without_constant(x):
        return math.exp(-x*x/(2*G) + b*x + .5*H*x*x)
    norm = quad(density_without_constant, -np.inf, np.inf, epsabs=1e-10)[0]
    mu = quad(lambda x: x*density_without_constant(x),
              -np.inf, np.inf, epsabs=1e-10)[0]/norm
    variance = quad(lambda x: (x-mu)**2*density_without_constant(x),
                    -np.inf, np.inf, epsabs=1e-10)[0]/norm
    add("Selection adaptive integration", "selection", [b, H, G],
        dict(exact=mu, variance=variance), atol=3e-9)

for angle in [0, 5, 15, 30, 45, 60, 75, 85, 90, 135, 180]:
    theta = math.radians(angle)
    R = np.array([[math.cos(theta), -math.sin(theta)],
                  [math.sin(theta), math.cos(theta)]])
    G = R @ np.diag([.2, .005]) @ R.T
    H = -.8*np.eye(2)
    b = np.array([math.sqrt(.6525), 0])
    L = float(b @ G @ b)
    Q = .5*float(np.trace(H @ G @ H @ G))
    add("Geometry matrix calculations", "geometry", [angle],
        dict(G=G.tolist(), linear=L, curved=Q, share=L/(L+Q)))
for angle, saved in REF["geometry"]["saved_rotations_with_derived_error_checks"].items():
    add("Geometry archived anchors", "geometry", [float(angle)],
        dict(G=saved["covariance"], linear=saved["L"], curved=saved["Q"], share=saved["Ag"]))

# Root finding uses the recurrence residual, not the implemented root formula.
for B, gamma, rho in itertools.product([.1, 1, 3], [0, .01, .3, .5, 1, 10], [0, .5, .9, .99]):
    residual = lambda g: (1-rho)*B + rho*g/(1+gamma*g) - g
    root = brentq(residual, 0, B, xtol=1e-14)
    add("Inheritance bracketed fixed point", "fixedPoint", [B, gamma, rho], root)
    for g in [0, .1*B, B, 4*B]:
        expected = (1-rho)*B + rho*g/(1+gamma*g)
        add("Inheritance one-step grid", "inheritanceStep", [g, B, gamma, rho], expected)
    # rho=0 and gamma=0 are included in the grid.  Complete retention has
    # a different fixed-point domain, but the individual step remains valid.
for g, B, gamma in itertools.product([0, .1, 1, 4], [.1, 1], [0, .5]):
    add("Inheritance complete-retention step", "inheritanceStep", [g, B, gamma, 1],
        g/(1+gamma*g))
add("Stable negative-coefficient root", "fixedPoint", [1, 1e20, .5], .5)
add("Stable positive-coefficient root", "fixedPoint", [1, 1e-20, .5], 1)

for name in ["main_figure", "teaching_guide"]:
    saved = REF["scalar_inheritance"][name]
    p = saved["parameters"]
    args = dict(B=p["B"], gamma=p["gamma"], rho=p["rho"],
                g0=p["g_initial"], n=p["n_dimensions"], b=p["gradient_norm_initial"])
    path = []
    for row in saved["trajectory"]:
        # The main source trajectory has the externally declining gradient.
        # The browser displays both that history and a maintained gradient.
        maintained_L = p["gradient_norm_initial"]**2*row["g"]
        path.append(dict(t=row["generation"], g=row["g"], selected=row["g_selected"],
                         linear=maintained_L, curved=row["V_quad"],
                         share=maintained_L/(maintained_L+row["V_quad"]),
                         decliningGradient=row["gradient_norm"], decliningShare=row["A_g"]))
    add("Inheritance archived trajectory", "inheritance", [args, p["final_generation"]],
        dict(path=path, fixedPoint=saved["fixed_point"]))

E = REF["estimation"]
theta = [E["estimate"][name] for name in ["alpha", "b", "H"]]
calibration = {name: E["estimate"][name] for name in ["G", "E", "mu"]}
q81 = E["standard_normal_quadrature_81"]
likelihood_by_id = {row["id"]: row for row in E["per_record_likelihood_checks"]}
for row in E["observed_input_excerpt"]["rows"]:
    heights = [row[f"height_{j}"] for j in range(1, 4)]
    record = likelihood_by_id[row["id"]]
    add("Actual-row breeding-value posterior", "posterior", [heights, calibration],
        dict(average=record["average_height"], mean=record["posterior_mean"],
             variance=record["posterior_variance"], reliability=E["estimate"]["reliability"]))
    add("Actual-row expected counts", "expectedCount",
        [record["posterior_mean"], record["posterior_variance"], theta], record["expected_count"])
    for prob in record["count_probabilities"]:
        add("Actual-row integrated count probabilities", "countProbability",
            [prob["count"], record["posterior_mean"], record["posterior_variance"], theta, q81],
            prob["probability_adaptive_integration"], atol=3e-13, rtol=3e-11)

# Check posterior algebra independently through normal-normal precisions,
# using varying replicate counts rather than assuming three.
for heights, G, noise, mu in itertools.product(
        [[-1], [-1, 2], [-2, .5, 1, 2]], [.1, 1, 3], [.1, 1, 4], [-.5, 0, 1]):
    precision = 1/G + len(heights)/noise
    v = 1/precision
    m = v*sum(x-mu for x in heights)/noise
    add("Posterior precision calculation", "posterior", [heights, dict(G=G, E=noise, mu=mu)],
        dict(average=float(np.mean(heights)), mean=m, variance=v,
             reliability=len(heights)*v/noise))

# Integrate the product of the normal density and conditional Poisson mean.
# Positive curvature is allowed here only when this first moment exists.
for m, v, b, H in itertools.product([-1, 0, 1], [0, .1, 1], [-.7, 0, .7], [-1, 0, .5]):
    alpha = 1.2
    if v == 0:
        expectation = math.exp(alpha+b*m+.5*H*m*m)
    else:
        def weighted_mean(u):
            z = m+math.sqrt(v)*u
            return math.exp(alpha+b*z+.5*H*z*z-.5*u*u)/math.sqrt(2*math.pi)
        expectation = quad(weighted_mean, -np.inf, np.inf, epsabs=1e-10)[0]
    add("Expected count adaptive integration", "expectedCount", [m, v, [alpha,b,H]], expectation,
        atol=1e-8, rtol=3e-10)
for H in [1, 2]:
    add("Non-finite count first moment", "expectedCount", [0, 1, [1, 0, H]], None)

for name, interval in E["conditional_95_percent_intervals"].items():
    values = [row[name] for row in E["bootstrap"]["draws"]]
    for p, saved in zip([.025, .975], interval):
        add("Archived bootstrap intervals", "quantile", [values, p], saved,
            atol=7e-12, rtol=7e-12)
        add("Bootstrap NumPy percentile agreement", "quantile", [values, p], float(np.quantile(values,p)))

add("Non-Gaussian two-point construction", "nonGaussianExample", [],
    dict(G=2, linear=2, curved=.5, covariance=1, total=4.5,
         slope=1.5, intercept=1, R2=1, gaussianFormula=.5))

# Node performs only the model evaluations.  The independent expected values
# above stay in Python, so no numerical implementation is shared at runtime.
runner = r"""
const fs = require('fs');
const M = require(process.argv[1]);
const calls = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(calls.map(c => M[c.function](...c.args))));
"""
payload = json.dumps([{k: case[k] for k in ["function", "args"]} for case in CASES])
result = subprocess.run(["node", "-e", runner, str(HERE / "models.js")],
                        input=payload, text=True, capture_output=True, check=True)
actual = json.loads(result.stdout)
assert len(actual) == len(CASES)
errors = []
counts = Counter()
max_error = defaultdict(float)
numeric_values = 0


def compare(got, want, case, label=""):
    global numeric_values
    if isinstance(want, dict):
        for key, value in want.items():
            if key not in got:
                errors.append(f"{case['group']} {label}.{key}: missing")
            else:
                compare(got[key], value, case, f"{label}.{key}")
    elif isinstance(want, list):
        if len(got) != len(want):
            errors.append(f"{case['group']} {label}: unequal lengths")
        else:
            for i, value in enumerate(want):
                compare(got[i], value, case, f"{label}[{i}]")
    elif want is None or isinstance(want, bool):
        if got is not want:
            errors.append(f"{case['group']} {label}: {got!r} != {want!r}")
    else:
        numeric_values += 1
        if got is None or not math.isfinite(got):
            errors.append(f"{case['group']} {label}: non-finite {got!r}")
            return
        absolute = abs(got-want)
        max_error[case["group"]] = max(max_error[case["group"]], absolute)
        if not math.isclose(got, want, abs_tol=case["atol"], rel_tol=case["rtol"]):
            errors.append(f"{case['group']} {label}: {got:.17g} != {want:.17g}")


for case, got in zip(CASES, actual):
    counts[case["group"]] += 1
    compare(got, case["expected"], case)

report = dict(
    all_checks_passed=not errors,
    model_sha256=hashlib.sha256((HERE / "models.js").read_bytes()).hexdigest(),
    source_manifest_sha256=REF["source_identity"]["manifest_sha256"],
    scientific_values_sha256=REF["source_identity"]["scientific_values_sha256"],
    function_evaluations=len(CASES),
    numerical_values_compared=numeric_values,
    groups={name: dict(function_evaluations=count, maximum_absolute_difference=max_error[name])
            for name, count in counts.items()},
    edge_cases=[
        "No variation in the log curve: share is null, not zero or one.",
        "Zero selected shift: relative error is null, while both shifts are zero.",
        "H*G >= 1: the scalar selected density is not normalisable.",
        "gamma=0, rho=0, g0=0 and complete-retention steps are checked.",
        "rho=1 is outside the browser fixed-point function's stated domain.",
        "Both numerically stable quadratic-root branches are checked.",
        "G=0 gives a point distribution; the HTML sliders use positive variance.",
        "Quartic kappa=0 agrees with the local quadratic result; negative kappa is excluded.",
        "The two-point non-Gaussian example has H=+1, total variance 4.5 and actual R2=1.",
    ],
    scope=[
        "Checks numerical functions against independent calculations and archived saved results.",
        "Does not rerun the 500 bootstrap model fits or alter their archived estimates.",
        "Does not test the HTML interface, layout or event handlers.",
    ],
    errors=errors,
)
(HERE / "models_validation.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps({k: report[k] for k in ["all_checks_passed", "function_evaluations",
                                        "numerical_values_compared", "errors"]}, indent=2))
if errors:
    raise SystemExit(1)
