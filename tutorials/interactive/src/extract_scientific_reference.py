"""Extract checked reference values for the additional repository teaching HTML.

This script reads the supplied files only when their SHA-256 hashes match the
reviewed source manifest. It requires no Git history. It does not alter source
files, rerun an estimator, or substitute a fresh simulation for saved
observations. Extra trajectory rows are explicitly labelled as calculations
reconstructed from the supplied generating code.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
from numpy.polynomial.hermite import hermgauss
from scipy.integrate import quad
from scipy.special import roots_hermitenorm
from reference_integrity import (
    MANIFEST_PATH, SOURCE_BASE, load_manifest, read_checked_source,
    sha256, validate_reference,
)

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MANIFEST = load_manifest()
BASE_URL = SOURCE_BASE
sources = {}
checks = []


def source(path):
    raw = read_checked_source(path, MANIFEST)
    sources[path] = {
        'path': path, 'github_url': BASE_URL + path,
        'sha256': hashlib.sha256(raw).hexdigest(),
    }
    return raw.decode('utf-8')


def read_json(path):
    return json.loads(source(path))


def reference(path, section=None):
    if path not in sources:
        source(path)
    out = dict(sources[path])
    if section:
        out['section_or_symbol'] = section
    return out


def verify(name, calculated, saved, atol=3e-10, rtol=3e-10):
    a, b = np.asarray(calculated, dtype=float), np.asarray(saved, dtype=float)
    np.testing.assert_allclose(a, b, atol=atol, rtol=rtol, err_msg=name)
    checks.append({'check': name, 'passed': True,
                   'maximum_absolute_discrepancy': float(np.max(np.abs(a-b)))})


def convert_csv(path):
    reader = csv.DictReader(io.StringIO(source(path)))
    columns = list(reader.fieldnames)
    rows = []
    for raw in reader:
        row = {}
        for k, v in raw.items():
            if k in ('id', 'offspring', 'replicate'):
                row[k] = int(v)
            elif v in ('True', 'False'):
                row[k] = v == 'True'
            else:
                row[k] = float(v)
        rows.append(row)
    return columns, rows


def fixed_point(B, gamma, rho):
    """Independent, numerically stable solution of the scalar quadratic."""
    if rho == 1:
        return 0.0 if gamma > 0 else None  # No single equilibrium if both zero.
    if gamma == 0:
        return B
    c = (1-rho)*(1-gamma*B)
    d = (1-rho)*B
    disc = math.sqrt(c*c + 4*gamma*d)
    return 2*d/(c+disc) if c >= 0 else (-c+disc)/(2*gamma)


def trajectory(params):
    g = params['g_initial']
    rows = []
    for t in range(params['final_generation']+1):
        decay_time = max(0, t-params['maintained_gradient_through_generation'])
        bnorm = params['gradient_norm_initial'] * math.exp(
            -params['gradient_decay_after_maintenance']*decay_time)
        vl = bnorm**2*g
        vq = .5*params['n_dimensions']*params['gamma']**2*g*g
        gs = g/(1+params['gamma']*g)
        gn = (1-params['rho'])*params['B'] + params['rho']*gs
        rows.append({'generation': t, 'g': g, 'g_selected': gs,
                     'next_g': gn, 'gradient_norm': bnorm,
                     'V_lin': vl, 'V_quad': vq,
                     'A_g': vl/(vl+vq) if vl+vq > 0 else None})
        g = gn
    return rows


figures = read_json('reference/figures.json')
geometry_saved = read_json('tutorials/geometry/values.json')
one_trait_saved = read_json('tutorials/one_trait_visual/values.json')
estimation_summary = read_json('examples/estimating_variance_share/results/summary.json')
boot_columns, boot_rows = convert_csv('examples/estimating_variance_share/results/bootstrap_draws.csv')
data_columns, data_rows = convert_csv('examples/estimating_variance_share/results/observed_data.csv')
truth_columns, truth_rows = convert_csv('examples/estimating_variance_share/results/simulation_truth.csv')

main_parameters = figures['figure4']['parameters']
main_path = trajectory(main_parameters)
main_saved = figures['figure4']['results']
main_fixed = fixed_point(main_parameters['B'], main_parameters['gamma'], main_parameters['rho'])
verify('Main Figure 4 fixed point', main_fixed, main_saved['scalar_fixed_point'])
verify('Main Figure 4 saved landmarks',
       [main_path[0]['A_g'],main_path[40]['A_g'],main_path[100]['A_g'],
        main_path[40]['V_lin'],main_path[40]['V_quad'],main_path[100]['g']],
       [main_saved['A_g_initial'],main_saved['A_g_at_end_of_maintained_gradient'],
        main_saved['A_g_final'],main_saved['V_lin_at_end_of_maintained_gradient'],
        main_saved['V_quad_at_end_of_maintained_gradient'],main_saved['g_at_final_generation']])
guide_parameters = dict(B=1.0,gamma=.5,rho=.5,g_initial=1.0,n_dimensions=1,
                        gradient_norm_initial=2.0,
                        maintained_gradient_through_generation=40,
                        gradient_decay_after_maintenance=0.0,final_generation=40)
guide_path = trajectory(guide_parameters)
guide_fixed = fixed_point(1,.5,.5)
verify('Teaching guide first four updates', [x['g'] for x in guide_path[1:5]],
       [5/6,27/34,149/190,827/1058])
verify('Teaching guide fixed point',guide_fixed,(math.sqrt(17)-1)/4)

inheritance = {
    'formula': 'g[t+1] = (1-rho)*B + rho*g[t]/(1+gamma*g[t])',
    'selected_variance_formula': 'g_sel[t] = g[t]/(1+gamma*g[t])',
    'notation': {'g': 'Breeding-value variance in one trait, or the common variance in an isotropic model.',
                 'B': 'Fixed genic variance baseline, not mutation input.',
                 'gamma': 'Nonnegative stabilising curvature, equal to -H in one trait.',
                 'rho': 'Fraction of the selected covariance departure from B retained after reproduction.'},
    'allowed_domain': {'B': 'finite, B>0','gamma': 'finite, gamma>=0',
                       'rho': '0<=rho<=1; rho=1 is a separate boundary case',
                       'g_initial': 'finite, g_initial>=0'},
    'assumptions': [
        'Fixed allelic effects and fixed genic baseline B are separate assumptions.',
        'Fixed stabilising curvature and the stated association-retention closure.',
        'The scalar recurrence omits mutation, migration, drift and changes in allele frequencies that alter B.',
        'It does not calculate a changing population mean or fitness gradient.',
        'The Gaussian selected covariance formula is exact under an exact log-quadratic conditional mean.',
    ],
    'fixed_point': {
        'quadratic': 'gamma*g_star^2 + (1-rho)*(1-gamma*B)*g_star - (1-rho)*B = 0',
        'positive_root': '[-(1-rho)*(1-gamma*B) + sqrt((1-rho)^2*(1-gamma*B)^2 + 4*gamma*(1-rho)*B)]/(2*gamma)',
        'positive_root_domain': 'B>0, gamma>0, 0<=rho<1',
        'bounds': '(1-rho)*B <= g_star <= B',
        'convergence': '|g[t]-g_star| <= rho^t*|g[0]-g_star| for 0<=rho<1',
        'initial_condition_note': 'A start below g_star increases; a start above it decreases. A starting variance above B need not enter [(1-rho)*B,B] in one step.',
        'gamma_zero': 'If gamma=0 and rho<1, g_star=B and g[t]=B+rho^t*(g[0]-B).',
        'rho_zero': 'If rho=0, the next variance is B.',
        'rho_one': 'If rho=1, g[t]=g[0]/(1+t*gamma*g[0]). If gamma>0 the limit is zero; if gamma=0 every starting variance is fixed. Zero initial variance remains zero.',
        'matrix_scope': 'The matrix proof establishes existence and bounds. The unique equilibrium and global convergence statements here are scalar results.'
    },
    'main_figure': {
        'parameters': main_parameters,'saved_results':main_saved,
        'fixed_point':main_fixed,'trajectory':main_path,
        'trajectory_provenance':'Reconstructed from supplied code/figures.py, make_figure_4; its file hash is recorded in the source manifest. Checked against every saved landmark. The repository saves landmarks, not all generation rows.',
        'gradient_schedule': '||b_t||=1 for t<=40, then exp[-0.06*(t-40)]. This schedule is imposed, not predicted.',
        'isotropic_components':'G_t=g_t I_n, Gamma=gamma I_n; V_lin=||b_t||^2*g_t; V_quad=n*gamma^2*g_t^2/2.',
    },
    'teaching_guide': {
        'parameters':guide_parameters,'fixed_point':guide_fixed,
        'saved_first_four_variances':[5/6,27/34,149/190,827/1058],
        'saved_exact_fixed_point':'(sqrt(17)-1)/4',
        'trajectory':guide_path,
        'trajectory_provenance':'g updates reconstructed from the guide recurrence and checked against the first four exact fractions and saved fixed point. The optional component columns use the guide selection example b=2, maintained throughout; the guide covariance iteration itself does not require b.'
    },
    'sources':[
        reference('code/figures.py','scalar_fixed_point; make_figure_4'),
        reference('reference/figures.json','figure4'),
        reference('tutorials/mathematics/guide.tex','sec:s3; scalar recurrence, fixed point and complete-retention boundary'),
    ]
}

selection = {
    'model':'A=mu+X, X~N(0,G); log E[W|A=mu+x]=ell0+b^T x-(1/2)x^T Gamma x; Gamma=-H symmetric.',
    'normalisability':{
        'positive_definite_G':'J=G^{-1}+Gamma must be positive definite; equivalently I+G^{1/2}Gamma G^{1/2} must be positive definite.',
        'singular_G':'Restrict all vectors and matrices to the subspace with positive variance. Test combined precision only on that occupied support.',
        'scalar':'For g>0, 1+gamma*g>0, equivalently 1-H*g>0.',
        'boundary':'A zero eigenvalue of combined precision is not integrable, even if the gradient is zero in that direction.',
    },
    'selected_covariance':'G_sel=(G^{-1}+Gamma)^{-1}',
    'selected_mean':'mu_sel=mu+Delta_full',
    'selected_displacement':'Delta_full=(G^{-1}+Gamma)^{-1} b = (I+G Gamma)^{-1} G b',
    'linear_displacement':'Delta_lin=G b',
    'scalar':{
        'selected_variance':'g_sel=g/(1+gamma*g)',
        'selected_displacement':'Delta_full=g*b/(1+gamma*g)=g*b/(1-H*g)',
        'relative_error':'|Delta_lin-Delta_full|/|Delta_full|=|gamma*g| for b!=0 and g>0',
    },
    'error_bound':{
        'metric':'||v||_{G^{-1}}=sqrt(v^T G^{-1} v)',
        'definition':'E=||Delta_lin-Delta_full||_{G^{-1}} / ||Delta_full||_{G^{-1}}',
        'T':'T=G^{1/2} Gamma G^{1/2}',
        'bound':'E <= ||T||_2 <= ||T||_F = sqrt(2*V_quad)',
        'V_quad':'V_quad=tr(H G H G)/2',
        'domain':'Exact Gaussian/log-quadratic model, positive combined precision, and a nonzero gradient component on the occupied support.',
        'zero_gradient':'If the gradient on the occupied support is zero, both shifts and their absolute discrepancy are zero. Their relative error is undefined (0/0); display null or a labelled dash.',
        'scope':'This is a covariance-scaled relative error, not a general Euclidean relative error. Stabilising curvature suffices but is not necessary; integrable saddle cases are included.',
        'orientation_formula':'E^2 = sum_i[tau_i^2*c_i^2/(1+tau_i)^2] / sum_i[c_i^2/(1+tau_i)^2], where c=G^{1/2}b in the eigenbasis of T.',
    },
    'examples':[
        {'label':'97 percent share and 50 percent shift error','g':1,'b':2,'H':-.5,'gamma':.5,
         'V_lin':4,'V_quad':.125,'A_g':32/33,'g_selected':2/3,
         'Delta_full':4/3,'Delta_lin':2,'absolute_error':2/3,'relative_error':.5},
        {'label':'Larger slope with unchanged relative error','g':1,'b':10,'H':-.5,'gamma':.5,
         'V_lin':100,'V_quad':.125,'A_g':100/100.125,'g_selected':2/3,
         'Delta_full':20/3,'Delta_lin':10,'relative_error':.5},
        {'label':'Zero gradient','g':1,'b':0,'H':-.5,'gamma':.5,
         'V_lin':0,'V_quad':.125,'A_g':0,'g_selected':2/3,
         'Delta_full':0,'Delta_lin':0,'absolute_error':0,'relative_error':None},
    ],
    'sources':[reference('tutorials/mathematics/guide.tex',
                        'sec:s2; reproductive weighting, selected-parent moments and curvature error'),
               reference('tutorials/introduction/notes.tex','Why a 97% fit can still miss selection by 50%')],
}

# Independent integration of the scalar selection example.
nodes, weights = hermgauss(80)
x = np.sqrt(2)*nodes
w = weights/np.sqrt(np.pi)
ell = 2*x-.25*x*x
rw = w*np.exp(ell-ell.max()); rw /= rw.sum()
numeric_shift = rw@x
numeric_var = rw@((x-numeric_shift)**2)
verify('97/50 example from direct Gaussian quadrature',[numeric_shift,numeric_var],[4/3,2/3])

# Verify archived bootstrap identities and percentile intervals without refitting.
assert len(boot_rows)==500
assert [r['replicate'] for r in boot_rows]==list(range(1,501))
for key in ['b','H','G','V_lin','V_quad','A_g']:
    verify('Saved bootstrap percentile interval: '+key,
           np.quantile([r[key] for r in boot_rows],[.025,.975]),
           estimation_summary['intervals'][key])
verify('Every bootstrap linear component',
       [r['b']**2*r['G'] for r in boot_rows],[r['V_lin'] for r in boot_rows])
verify('Every bootstrap curved component',
       [.5*r['H']**2*r['G']**2 for r in boot_rows],[r['V_quad'] for r in boot_rows])
verify('Every bootstrap linear share',
       [r['V_lin']/(r['V_lin']+r['V_quad']) for r in boot_rows],[r['A_g'] for r in boot_rows])
assert sources['examples/estimating_variance_share/results/observed_data.csv']['sha256'] == estimation_summary['observed_data_sha256']
assert len(data_rows)==800 and sum(r['offspring']==0 for r in data_rows)==88
Y=np.array([[r[f'height_{k}'] for k in (1,2,3)] for r in data_rows])
ybar=Y.mean(axis=1)
ehat=np.sum((Y-ybar[:,None])**2)/(800*2)
ghat=np.var(ybar,ddof=1)-ehat/3
reliability=ghat/(ghat+ehat/3)
verify('Calibration reconstructed from saved noisy heights',
       [ybar.mean(),ehat,ghat,reliability],
       [estimation_summary['estimate'][k] for k in ['mu','E','G','reliability']])
verify('Saved naive variance equals variance of shrunk predictions',
       np.var(reliability*(ybar-ybar.mean()),ddof=1),estimation_summary['naive']['G'])

# Standard-normal Hermite integration permits per-record count-probability
# exploration in the browser. Validate the actual archived cases against
# adaptive integration, rather than checking the same quadrature twice.
normal_nodes, normal_weights = roots_hermitenorm(81)
normal_weights /= math.sqrt(2*math.pi)
verify('81-node normal quadrature mass, mean and variance',
       [normal_weights.sum(), normal_weights@normal_nodes,
        normal_weights@(normal_nodes**2)], [1,0,1])
fitted = estimation_summary['estimate']
alpha, slope, curvature = [fitted[k] for k in ['alpha','b','H']]
likelihood_cases=[]
for row in data_rows[:12]:
    average=sum(row[f'height_{k}'] for k in (1,2,3))/3
    postmean=fitted['reliability']*(average-fitted['mu'])
    postvar=fitted['G']*(1-fitted['reliability'])
    latent=postmean+math.sqrt(postvar)*normal_nodes
    eta=alpha+slope*latent+curvature*latent**2/2
    d=1-curvature*postvar
    expected_count=math.exp(alpha+slope*postmean+curvature*postmean**2/2+
                            postvar*(slope+curvature*postmean)**2/(2*d))/math.sqrt(d)
    verify(f'Observed ID {row["id"]}: closed-form conditional mean',
           expected_count,normal_weights@np.exp(eta))
    probabilities=[]
    for count in sorted(set([0,row['offspring'],10])):
        log_factorial=math.lgamma(count+1)
        quadrature_probability=float(normal_weights@np.exp(count*eta-np.exp(eta)-log_factorial))
        def integrand(u):
            z=postmean+math.sqrt(postvar)*u
            e=alpha+slope*z+curvature*z*z/2
            return math.exp(count*e-math.exp(e)-log_factorial-u*u/2)/math.sqrt(2*math.pi)
        adaptive_probability, estimated_error=quad(integrand,-np.inf,np.inf,
                                                   epsabs=1e-12,epsrel=1e-12,limit=200)
        verify(f'Observed ID {row["id"]}: count {count} probability',
               quadrature_probability,adaptive_probability,atol=2e-11,rtol=2e-9)
        probabilities.append({'count':count,'probability_81_nodes':quadrature_probability,
                              'probability_adaptive_integration':adaptive_probability,
                              'adaptive_estimated_absolute_error':estimated_error})
    likelihood_cases.append({'id':row['id'],'average_height':average,
                             'posterior_mean':postmean,'posterior_variance':postvar,
                             'expected_count':expected_count,'count_probabilities':probabilities})

estimation = {
    'evidence_type':'Archived simulated teaching dataset and fitted results. These are not empirical observations.',
    'generating_model':{
        'A':'A_i~N(0,G)',
        'heights':'Y_ij=A_i+e_ij, e_ij~N(0,E), independent across genotypes and replicates.',
        'counts':'W_i|A_i=a~Poisson(exp(alpha+b*a+H*a^2/2)); the count assay is conditionally independent of height-measurement errors.',
        'alpha':'alpha=log(mean_output); mean_output is expected output at breeding value zero, not mean output over the population.',
        'settings':estimation_summary['settings'],
        'assumptions':['800 unrelated genotypes, three independent clonal trait replicates and one reproductive count each.',
                       'The trait is wholly additive in this example; dominance, epistasis and permanent environmental effects are absent.',
                       'Clonal replication alone does not generally identify additive genetic variance.',
                       'All 88 observed zero offspring counts enter the Poisson likelihood. No logarithm of an individual count is taken.'],
    },
    'estimation_method':{
        'name':'Two-stage measurement calibration followed by integrated Poisson likelihood.',
        'E_hat':'sum_ij(Y_ij-Ybar_i)^2 / [n*(m-1)]',
        'G_hat':'sample_variance(Ybar_i, ddof=1)-E_hat/m',
        'mu_hat':'mean_i(Ybar_i)',
        'reliability':'r=G_hat/(G_hat+E_hat/m)',
        'latent_distribution':'Z_i=A_i-mu_hat | Y_i ~ N(M_i,v), M_i=r*(Ybar_i-mu_hat), v=G_hat*(1-r)',
        'likelihood':'L_i(alpha,b,H)=integral Poisson(W_i; exp(alpha+b*z+H*z^2/2))*Normal(z;M_i,v) dz',
        'calibration_failure':'G_hat<=1e-8 stops the repository implementation; it is not silently truncated.',
        'fitting_domain':'The primary fitted H lies in [-6,0]; alpha in [-7,7] and b in [-5,5] are numerical optimisation bounds. These bounds are implementation choices, not universal biological constraints.',
        'integration':estimation_summary['integration'],
        'quadrature_change':estimation_summary['quadrature_change'],
        'scope':'A teaching estimator under the stated model. It is not a joint genomic/pedigree model and does not predict descendants.',
    },
    'truth':estimation_summary['truth'],
    'estimate':estimation_summary['estimate'],
    'conditional_95_percent_intervals':estimation_summary['intervals'],
    'naive_estimate':estimation_summary['naive'],
    'naive_method':'Refit fitness against shrunk breeding-value predictions as though exact; set latent variance to zero and use their sample variance as G. Both slope and curvature are refitted, so the bias has no general direction.',
    'quartic_fit_to_default_data':{'share_components':estimation_summary['alternative'],
                                  'quartic_minus_quadratic_AIC':estimation_summary['delta_aic']},
    'nonquadratic_generating_example':{
        'kappa':.08,'log_mean':'alpha+b*a+H*a^2/2-kappa*a^4',
        'local_quadratic_share':2/3,
        'full_curve_linear_R2':.49/(.49+.245-12*(-.7)*.08+96*.08**2),
        'even_component_variance':'H^2*G^2/2 - 12*H*kappa*G^3 + 96*kappa^2*G^4',
        'scope':'Analytical generating-curve comparison. These are not a new fitted-data result or a fresh bootstrap.',
    },
    'bootstrap':{
        'replicates':len(boot_rows),'seed':20261006,
        'method':'Parametric bootstrap: generate latent centred A from the fitted G; regenerate all height replicates with fitted mu and E, and counts from fitted alpha,b,H; then repeat both estimation stages.',
        'interval_definition':'2.5th and 97.5th percentiles of the 500 saved refits, conditional on the fitted model.',
        'quantile_algorithm':'Sort values; let h=(N-1)*p; linearly interpolate between floor(h) and ceil(h).',
        'scope':'These draws describe uncertainty for this fitted dataset and model. They do not become a new bootstrap merely because a different slider setting or generating curve is displayed.',
        'failed':estimation_summary['bootstrap_failed'],
        'boundary_count':estimation_summary['bootstrap_boundary'],
        'columns':boot_columns,'draws':boot_rows,
        'column_meanings':{'replicate':'Saved bootstrap replicate number, 1 to 500.',
                           'b':'Fitted slope at the estimated population mean.',
                           'H':'Fitted second derivative; coefficient of z^2 is H/2.',
                           'G':'Calibrated breeding-value variance.',
                           'V_lin':'b^2*G.', 'V_quad':'H^2*G^2/2.',
                           'A_g':'V_lin/(V_lin+V_quad).',
                           'alpha':'Fitted log conditional expected output at centred breeding value zero.',
                           'mu':'Calibrated mean of the trait observations.',
                           'E':'Estimated variance of each height measurement error.',
                           'reliability':'G/(G+E/m).',
                           'boundary':'Whether a fitted parameter approached an optimisation bound.',
                           'loglik':'Integrated Poisson log likelihood at the fit.'},
        'rounding_note':'CSV floats were saved to 12 significant digits; summary.json retains higher-precision intervals. Recomputed percentile differences are checked within 3e-10.',
    },
    'observed_input_excerpt':{
        'label':'First 12 rows of the archived simulated observed_data.csv, in original order.',
        'columns':data_columns,'rows':data_rows[:12],
        'full_dataset_rows':len(data_rows),'full_dataset_zero_counts':88,
        'units':{'height_1':'centimetres relative to the generating population mean',
                 'height_2':'centimetres relative to the generating population mean',
                 'height_3':'centimetres relative to the generating population mean',
                 'offspring':'count of surviving offspring in the separate reproductive assay'},
        'use':'Display only. The saved estimator and confidence intervals used all 800 rows, not this excerpt.',
        'sha256_full_csv':estimation_summary['observed_data_sha256'],
    },
    'separate_simulation_truth_excerpt':{
        'label':'Generating breeding values for the same 12 IDs. These were withheld from the estimator.',
        'columns':truth_columns,'rows':truth_rows[:12],
    },
    'reference_environment':estimation_summary['versions'],
    'standard_normal_quadrature_81':{
        'distribution':'standard normal N(0,1)',
        'nodes':normal_nodes.tolist(),'weights':normal_weights.tolist(),
        'use':'For Z~N(m,v), evaluate f(m+sqrt(v)*nodes[i]) and sum weights[i]*f. Weights sum to one; do not multiply nodes by sqrt(2) again.',
        'source_implementation':'scipy.special.roots_hermitenorm(81), with weights divided by sqrt(2*pi); this is the checked order used by the source estimator.',
        'scope':'These nodes approximate a likelihood contribution. They do not refit model parameters, and accuracy is not guaranteed for arbitrary extreme sliders.',
    },
    'per_record_likelihood_checks':likelihood_cases,
    'sources':[reference('examples/estimating_variance_share/model.py','Settings; calibrate; fit_surface; analyse; bootstrap; truth'),
               reference('examples/estimating_variance_share/run_case.py','main'),
               reference('examples/estimating_variance_share/worked_example.tex'),
               reference('examples/estimating_variance_share/results/summary.json'),
               reference('examples/estimating_variance_share/results/bootstrap_draws.csv'),
               reference('examples/estimating_variance_share/results/observed_data.csv'),
               reference('examples/estimating_variance_share/results/simulation_truth.csv')],
}

# Recompute all seven geometry reference populations independently of the
# repository's implementation, including their weighted parental means.
peak=np.array(geometry_saved['model']['peak_in_original_trait_coordinates'])
gamma=.8
for family in ['rotations','comparison_cases']:
    for label,case in geometry_saved[family].items():
        G=np.array(case['covariance']); mu=np.array(case['mean'])
        theta=np.array([np.linalg.norm(peak),0]) if family=='rotations' else peak
        b=gamma*(theta-mu); H=-gamma*np.eye(2)
        vl=b@G@b; vq=.5*np.trace(H@G@H@G)
        shift=np.linalg.solve(np.linalg.inv(G)+gamma*np.eye(2),b)
        verify(f'Geometry {family} {label} components and selected displacement',
               [vl,vq,vl/(vl+vq),*shift],
               [case['L'],case['Q'],case['Ag'],*case['curved_shift']])
        q,qw=hermgauss(40)
        mesh=np.array(np.meshgrid(q,q,indexing='ij')).reshape(2,-1).T
        pts=np.sqrt(2)*mesh@np.linalg.cholesky(G).T
        pw=np.outer(qw,qw).ravel()/np.pi
        logs=-gamma*np.sum((mu+pts-theta)**2,axis=1)/2
        rw=pw*np.exp(logs-logs.max());rw/=rw.sum()
        verify(f'Geometry {family} {label} direct reproductive quadrature',rw@pts,shift)
        invG=np.linalg.inv(G); delta_lin=G@b; err=delta_lin-shift
        if vl>1e-28:
            error=float(math.sqrt((err@invG@err)/(shift@invG@shift)))
        else:
            error=None
        # gamma is scalar in this module, so T and G share eigenvectors.
        spectral=gamma*float(np.max(np.linalg.eigvalsh(G)))
        case['derived_relative_error_in_G_inverse_norm']=error
        case['derived_spectral_error_bound']=spectral
        case['derived_Frobenius_error_bound']=math.sqrt(2*vq)
        if error is not None:
            assert error <= spectral+1e-12 <= math.sqrt(2*vq)+1e-12

geometry = {
    'model':geometry_saved['model'],
    'parameters':{'gamma':.8,'H':[[-.8,0],[0,-.8]],
                  'peak_original_coordinates':peak.tolist(),
                  'peak_distance':float(np.linalg.norm(peak)),
                  'gradient_norm_for_rotations':float(.8*np.linalg.norm(peak)),
                  'principal_variances':[.2,.005],
                  'baseline_covariance':[[1,.3],[.3,.6]],
                  'narrow_covariance_multiplier':.11},
    'rotation_definition':'R(theta)=[[cos(theta),-sin(theta)],[sin(theta),cos(theta)]]; G(theta)=R diag(0.2,0.005) R^T. In this displayed basis the peak is (||peak_original||,0), so b=(0.8077747210701756,0).',
    'comparisons':{'A':'Broad distribution at mean zero.',
                   'B':'Same mean, G multiplied by 0.11.',
                   'C':'Same narrow G as B, mean moved to the peak.',
                   'D':'Same broad G as A, distance from mean to peak multiplied by 1/sqrt(0.11). Shares B and D match, but their absolute components differ.'},
    'saved_rotations_with_derived_error_checks':geometry_saved['rotations'],
    'saved_comparison_cases_with_derived_error_checks':geometry_saved['comparison_cases'],
    'formulas':{'log_mean':'ell(a)=-gamma*||a-peak||^2/2, up to a common constant.',
                'gradient':'b=gamma*(peak-mu)',
                'linear_variance':'b^T G b',
                'quadratic_variance':'gamma^2*tr(G^2)/2',
                'fitted_intercept_at_mu':'ell(mu)-gamma*tr(G)/2',
                'selected_shift':'(I+gamma*G)^{-1} G b'},
    'angle_warning':'The saved field angle is the projection angle atan2(sqrt(Q),sqrt(L)) in degrees, not the physical rotation of G. At L=0 the stored 90 degrees is a limiting variance-triangle value; the ordinary angle with the zero fitted component is undefined.',
    'sources':[reference('tutorials/geometry/code/geometry.py'),
               reference('tutorials/geometry/values.json'),
               reference('reference/figures.json','figure3')],
}

document = {
    'schema_version':2,
    'repository':'dortizbarrientos/additive_channels',
    'source_identity':{
        'kind':'file-content SHA-256 manifest',
        'manifest':'tutorials/interactive/src/reference_sources.json',
        'manifest_sha256':sha256(MANIFEST_PATH.read_bytes()),
        'scientific_values_sha256':MANIFEST['scientific_values_sha256'],
        'version_guide':'docs/VERSION_GUIDE.md',
        'link_scope':'Public links open current source paths; the manifest hashes identify the exact file contents used here.',
    },
    'purpose':'Scientific constants, archived examples and validation references for the additional offline repository guide.',
    'scalar_inheritance':inheritance,
    'selection':selection,
    'estimation':estimation,
    'geometry':geometry,
    'one_trait':{'saved_values':one_trait_saved,
                 'source':reference('tutorials/one_trait_visual/values.json')},
    'validation':{'all_checks_passed':True,'checks':checks,
                  'not_performed':'The estimator and 500 bootstrap refits were not rerun. Their actual archived outputs were extracted and independently checked for calibration, component identities and percentiles.'},
    'source_manifest':list(sources.values()),
}
OUT.mkdir(parents=True,exist_ok=True)
validate_reference(document)
target=OUT/'scientific_reference.json'
target.write_text(json.dumps(document,indent=2,allow_nan=False)+'\n')
(OUT/'scientific_reference_validation.json').write_text(
    json.dumps(document['validation'],indent=2,allow_nan=False)+'\n')
print(json.dumps({'file':str(target),'bytes':target.stat().st_size,
                  'bootstrap_rows':len(boot_rows),'input_excerpt_rows':12,
                  'checks_passed':len(checks),
                  'main_fixed_point':main_fixed,'guide_fixed_point':guide_fixed},indent=2))
