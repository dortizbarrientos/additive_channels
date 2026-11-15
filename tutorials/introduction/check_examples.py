"""Independent checks of the teaching examples, including a non-Gaussian counterexample."""
import json
from pathlib import Path
import numpy as np
from numpy.polynomial.hermite import hermgauss

def check(label,got,want,tol=1e-10):
    np.testing.assert_allclose(got,want,atol=tol,rtol=tol)
    print(f'PASS: {label}: {got}')
# Quadrature integrates normal expectations without Monte Carlo noise.
q,w=hermgauss(64); x0=q*np.sqrt(2);w=w/np.sqrt(np.pi)
intro_cases=[]
# The first two cases match the broad and narrow populations in the
# one-trait walkthrough. Quadrature checks the fitted line independently
# of the algebraic expressions used to label the teaching figure.
for G,b,h in [(1,1,-1),(.1,1,-1),(1,2,-.5),(1,0,-1),(1,1,0)]:
    x=x0*np.sqrt(G);y=b*x+.5*h*x*x;mu=w@y
    slope=(w*x)@y/G
    fit=mu+slope*x
    r2=1-(w@((y-fit)**2))/(w@((y-mu)**2))
    expected=b*b*G/(b*b*G+.5*h*h*G*G)
    check('slope, intercept, population R²',[slope,mu,r2],[b,.5*h*G,expected])
    if b==1 and h==-1:
        linear=b*x; quadratic=.5*h*x*x
        components=[w@(linear**2),w@((quadratic-w@quadratic)**2)]
        check('broad/narrow variance components',components,
              [1,.5] if G==1 else [.1,.005])
        intro_cases.append({'variance':w@(x**2),'share':r2,
                            'components':components})
    if b==2:
        reproduction=np.exp(y);shift=(w*x)@reproduction/(w@reproduction)
        check('weighted parent shift and relative overestimate',[shift,(G*b-shift)/shift],[4/3,.5])
# The introduction, visual walkthrough and result catalogue describe the
# same comparison. Compare their saved records with these independently
# integrated values so a future edit cannot silently change one resource.
root=Path(__file__).resolve().parents[2]
catalog=json.loads((root/'reference/result_catalog.json').read_text())
expected=next(r for r in catalog['results'] if r['id']=='introductory_examples')['expected']
check('introductory catalogue population variances',
      [c['variance'] for c in intro_cases],expected['population_variances'])
check('introductory catalogue linear shares',
      [c['share'] for c in intro_cases],expected['shares'])
visual=json.loads((root/'tutorials/one_trait_visual/values.json').read_text())['cases']
for key,calculated in zip(['A','B'],intro_cases):
    saved=visual[key]
    check(f'one-trait visual case {key}',
          [calculated['variance'],calculated['share'],*calculated['components']],
          [saved['variance'],saved['linear_share'],saved['V_linear'],saved['V_quadratic']])
# Centred but skewed: Cov(X,X²) is nonzero; |Corr| may be one even when two terms both vary.
p=np.array([2/3,1/3]);x=np.array([-1.,2.]);check('third moment of skewed distribution',p@(x**3),2.)
# Both components zero: no variation and hence no R²; the log odds also require both > 0.
check('constant surface: zero denominator',np.var(np.zeros(9)),0)
