"""Independent checks of the teaching examples, including a non-Gaussian counterexample."""
import numpy as np
from numpy.polynomial.hermite import hermgauss

def check(label,got,want,tol=1e-10):
    np.testing.assert_allclose(got,want,atol=tol,rtol=tol)
    print(f'PASS: {label}: {got}')
# Quadrature integrates normal expectations without Monte Carlo noise.
q,w=hermgauss(64); x0=q*np.sqrt(2);w=w/np.sqrt(np.pi)
for G,b,h in [(1,1,-1),(.25,1,-1),(1,2,-.5),(1,0,-1),(1,1,0)]:
    x=x0*np.sqrt(G);y=b*x+.5*h*x*x;mu=w@y
    slope=(w*x)@y/G
    fit=mu+slope*x
    r2=1-(w@((y-fit)**2))/(w@((y-mu)**2))
    expected=b*b*G/(b*b*G+.5*h*h*G*G)
    check('slope, intercept, population R²',[slope,mu,r2],[b,.5*h*G,expected])
    if b==2:
        reproduction=np.exp(y);shift=(w*x)@reproduction/(w@reproduction)
        check('weighted parent shift and relative overestimate',[shift,(G*b-shift)/shift],[4/3,.5])
# Centred but skewed: Cov(X,X²) is nonzero; |Corr| may be one even when two terms both vary.
p=np.array([2/3,1/3]);x=np.array([-1.,2.]);check('third moment of skewed distribution',p@(x**3),2.)
# Both components zero: no variation and hence no R²; the log odds also require both > 0.
check('constant surface: zero denominator',np.var(np.zeros(9)),0)
