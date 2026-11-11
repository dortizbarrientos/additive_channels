"""Recompute the Appendix S4 summary from archived generation-level diagnostics."""
from pathlib import Path
import argparse,json
from compare_simulations import summary as diagnostic_summary
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'slim/diagnostics')
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/simulation_summary.json')
    args=parser.parse_args()
    files=sorted(args.input.glob('rep_*_4trait_moving_diag.csv'))
    if len(files)!=20:raise ValueError(f'Expected 20 replicate tables; found {len(files)}')
    frames=[]
    for path in files:
        df=pd.read_csv(path)
        if len(df)!=200 or not np.array_equal(df.gen,np.arange(1,201)):
            raise ValueError(f'Expected generations 1–200 in {path.name}')
        if not np.isfinite(df.select_dtypes('number')).all().all():
            raise ValueError(f'Nonfinite diagnostic in {path.name}')
        assert np.allclose(df.A_g,df.V_lin/(df.V_lin+df.V_quad))
        assert np.allclose(df.Ag_minus_R2,df.A_g-df.R2_empirical)
        df['rep']=path.stem.split('_')[1]
        frames.append(df)
    df=pd.concat(frames,ignore_index=True)
    err=np.abs(2*df.V_quad-(df[[f'mu_{i}' for i in range(1,5)]]**2).sum(axis=1))
    if err.max()>1e-10:raise ValueError('Quadratic-variance identity failed')
    value=float(np.median(np.abs(df.Ag_minus_R2)))
    result={
        'n_replicates':20,'n_generations_per_replicate':200,'n_rows':len(df),
        'median_abs_Ag_minus_R2':value,'max_abs_Ag_minus_R2':float(np.max(np.abs(df.Ag_minus_R2))),
        'max_abs_2Vquad_minus_sum_mu_squared':float(err.max()),
        'data_source':'archived diagnostic tables' if args.input.resolve()==(ROOT/'slim/diagnostics').resolve() else 'fresh simulation diagnostic tables',
        'replicate_seeds':list(range(42,62))
    }
    if result['data_source']=='archived diagnostic tables':
        if not np.isclose(value,0.015667885704792002,atol=1e-12,rtol=0):
            raise ValueError('Archived-data summary differs from the manuscript value')
    metrics=diagnostic_summary(df)
    result['diagnostic_summary']=metrics
    if result['data_source']=='archived diagnostic tables':
        expected=pd.read_csv(args.input/'reference_summary.csv').set_index('quantity').value
        if set(metrics)!=set(expected.index) or not all(np.isclose(metrics[k],expected[k],atol=1e-12,rtol=0) for k in metrics):
            raise ValueError('Replicate summary does not match the reference table.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(f'Simulation archive: 20 replicates, 4,000 rows; median |A_g - R²| = {value:.10f}.')

if __name__=='__main__':main()
