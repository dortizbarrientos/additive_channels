"""Reproduce numerical checks of the manuscript's mathematical identities."""
from pathlib import Path
import json
import numpy as np
from figures import variance_components, first_order_share, scalar_fixed_point

ROOT = Path(__file__).resolve().parents[1]

def main():
    rng = np.random.default_rng(20261004)
    coordinate_errors, moment_errors, bound_gaps = [], [], []
    for n in (2, 4, 8):
        for _ in range(10):
            M = rng.normal(size=(n, n))
            G = M @ M.T / n + 0.2 * np.eye(n)
            M = rng.normal(size=(n, n))
            Gamma = 0.1 * M @ M.T / n
            H, b = -Gamma, rng.normal(size=n)
            L, Q = variance_components(b, H, G)
            P, _ = np.linalg.qr(rng.normal(size=(n,n)))
            P = P @ np.diag(rng.uniform(0.5, 2, size=n))
            Pinv = np.linalg.inv(P)
            Lt, Qt = variance_components(Pinv.T @ b, Pinv.T @ H @ Pinv, P @ G @ P.T)
            coordinate_errors.append(max(abs(L-Lt), abs(Q-Qt)))
            assert np.allclose([L,Q],[Lt,Qt],rtol=1e-11,atol=1e-11)
            Gsel = np.linalg.inv(np.linalg.inv(G)+Gamma)
            assert np.linalg.eigvalsh(G-Gsel).min() > -1e-12
            full, linear = Gsel @ b, G @ b
            Ginv = np.linalg.inv(G)
            relative = np.sqrt((linear-full) @ Ginv @ (linear-full) / (full @ Ginv @ full))
            vals, vecs = np.linalg.eigh(G)
            root = (vecs * np.sqrt(vals)) @ vecs.T
            bound = np.linalg.norm(root @ Gamma @ root,2)
            assert relative <= bound + 1e-11
            bound_gaps.append(float(bound-relative))
            selected = rng.multivariate_normal(full,Gsel,size=20000)
            moment_errors.append(float(np.max(np.abs(selected.mean(axis=0)-full))))
            for s in (0.1,0.5,2.0):
                Ls,Qs = variance_components(b,H,s*G)
                assert np.allclose([Ls,Qs],[s*L,s*s*Q])
                assert np.isclose(first_order_share(Ls,Qs), L/(L+s*Q))
    b,H = np.array([1.,0.]),-np.eye(2)
    shares=[first_order_share(*variance_components(b,H,G)) for G in (np.eye(2),np.diag([0.1,0.9]))]
    assert np.allclose(shares,[0.5,0.1/0.51])
    B,gamma,rho = 1.,0.3,0.9
    fixed = scalar_fixed_point(B,gamma,rho)
    update=lambda g:(1-rho)*B+rho*g/(1+gamma*g)
    assert np.isclose(update(fixed),fixed)
    assert update(0.1)>0.1
    for g in (0.1,4.):
        for _ in range(500):g=update(g)
        assert np.isclose(g,fixed)
    result={
        'seed':20261004,'matrix_cases':30,
        'max_coordinate_invariance_error':max(coordinate_errors),
        'minimum_displacement_bound_gap':min(bound_gaps),
        'monte_carlo_selected_mean_max_absolute_error':max(moment_errors),
        'anisotropic_contraction_shares':shares,
        'scalar_fixed_point':fixed,'scalar_update_from_0_1':update(0.1),
        'all_deterministic_checks_passed':True
    }
    (ROOT/'outputs').mkdir(exist_ok=True)
    (ROOT/'outputs/mathematics_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Mathematics: coordinate invariance, scaling, selection bounds and scalar dynamics passed.')

if __name__=='__main__':main()
