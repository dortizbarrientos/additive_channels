"""Compare numerical outputs against the reference data shipped with this repository."""
import json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def equal(got,want,where):
    if isinstance(want,dict):
        if not isinstance(got,dict) or set(got)!=set(want):raise ValueError(f'Fields differ: {where}')
        for k,v in want.items():equal(got[k],v,where+'/'+k)
    elif isinstance(want,list):
        if len(got)!=len(want):raise ValueError(f'Length differs: {where}')
        for i,(x,y) in enumerate(zip(got,want)):equal(x,y,f'{where}/{i}')
    elif isinstance(want,(float,int)) and not isinstance(want,bool):
        if not math.isclose(got,want,abs_tol=1e-8,rel_tol=1e-7):raise ValueError(f'{where}: {got} vs {want}')
    elif got!=want:raise ValueError(f'{where}: values differ')
def main():
    out=ROOT/'outputs';ref=read(ROOT/'reference/figures.json');fig=read(out/'figure_results.json')
    for name,table in ref.items():
        for section in ('parameters','results'):equal(fig[name][section],table[section],name+'/'+section)
    sims=read(out/'simulation_summary.json');equal(sims['n_rows'],4000,'SLiM generation rows')
    equal(sims['median_abs_Ag_minus_R2'],0.015667885704792002,'median |share − R²|')
    equal(read(out/'mathematics_checks.json')['scalar_fixed_point'],0.47235323490240977,'fixed covariance')
    print('Verified all four figure records, the covariance equilibrium and the 4,000-row SLiM result.')
    if sys.argv[1:]!=['default']:return
    # Compare individual bootstrap draws, not only the final percentiles.
    expected=ROOT/'examples/estimating_variance_share/results';actual=out/'estimation'
    for name in ('observed_data','simulation_truth','estimates','bootstrap_draws'):
        a=pd.read_csv(actual/(name+'.csv'));b=pd.read_csv(expected/(name+'.csv'))
        pd.testing.assert_index_equal(a.columns,b.columns)
        if a.shape!=b.shape:raise ValueError(f'{name}: dimension mismatch')
        for k in b:
            if pd.api.types.is_numeric_dtype(b[k]):np.testing.assert_allclose(a[k],b[k],rtol=2e-5,atol=2e-6,err_msg=f'{name}.{k}')
            else:pd.testing.assert_series_equal(a[k],b[k])
    z=read(actual/'summary.json')
    if z['bootstrap_replicates']!=500 or z['bootstrap_failed']:raise ValueError('Bootstrap did not complete all 500 refits.')
    lo,hi=z['intervals']['A_g']
    print(f"Verified the observations and all 500 bootstrap refits: share {z['estimate']['A_g']:.4f} (95% interval {lo:.4f}–{hi:.4f}).")
if __name__=='__main__': main()
