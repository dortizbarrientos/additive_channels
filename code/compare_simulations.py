"""Compare a fresh 20-replicate SLiM run with the archived diagnostics."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summary(df):
    eig = np.clip(df[[f'eig_G_{i}' for i in range(1, 5)]].to_numpy(), 1e-15, None)
    df = df.copy()
    df['trace_G'] = eig.sum(axis=1)
    df['keff'] = df.trace_G**2 / (eig**2).sum(axis=1)
    df['kappa_G'] = eig[:, 0] / eig[:, -1]
    peak = df[df.gen == 40]
    error = np.abs(2 * df.V_quad - (df[[f'mu_{i}' for i in range(1, 5)]]**2).sum(axis=1))
    values = {
        'n_replicates': df.rep.nunique(), 'n_generations': df.gen.nunique(),
        'min_generation': df.gen.min(), 'max_generation': df.gen.max(),
        'median_abs_Ag_minus_R2_all': np.median(np.abs(df.Ag_minus_R2)),
        'max_abs_Ag_minus_R2_all': np.max(np.abs(df.Ag_minus_R2)),
        'max_abs_2Vquad_minus_sum_mu2': error.max(),
        'mean_Ag_peak': peak.A_g.mean(), 'mean_R2_peak': peak.R2_empirical.mean(),
        'mean_b_norm_peak': peak.b_norm.mean(),
        'mean_trace_G_gen1': df.loc[df.gen == 1, 'trace_G'].mean(),
        'mean_trace_G_gen200': df.loc[df.gen == 200, 'trace_G'].mean(),
        'mean_keff_gen1': df.loc[df.gen == 1, 'keff'].mean(),
        'mean_keff_peak': peak.keff.mean(), 'mean_kappa_peak': peak.kappa_G.mean(),
        'mean_kappa_gen200': df.loc[df.gen == 200, 'kappa_G'].mean(),
    }
    for col in ['A_g', 'R2_empirical', 'keff', 'kappa_G'] + [f'eig_G_{i}' for i in range(1, 5)]:
        values[f'CV_{col}_peak'] = peak[col].std(ddof=1) / abs(peak[col].mean())
    return {key: float(value) for key, value in values.items()}


def validate_diagnostics(df, name):
    if len(df) != 200 or not np.array_equal(df.gen, np.arange(1, 201)):
        raise ValueError(f'{name}: expected generations 1–200')
    if not np.isfinite(df.to_numpy(dtype=float)).all() or not (df.N == 2000).all():
        raise ValueError(f'{name}: invalid values or population size')
    optimum = np.zeros((200, 4))
    optimum[:, 0] = 0.3 * np.minimum(np.arange(200), 40)
    if not np.allclose(df[[f'z_opt_{i}' for i in range(1, 5)]], optimum, atol=1e-12, rtol=0):
        raise ValueError(f'{name}: unexpected optimum history')
    if not np.allclose(df.A_g, df.V_lin / (df.V_lin + df.V_quad), atol=1e-12, rtol=0):
        raise ValueError(f'{name}: variance-share identity failed')
    if not np.allclose(df.Ag_minus_R2, df.A_g - df.R2_empirical, atol=1e-12, rtol=0):
        raise ValueError(f'{name}: discrepancy identity failed')


def validate_raw(directory, tag):
    bv = pd.read_csv(directory / f'{tag}_bv.csv')
    opt = pd.read_csv(directory / f'{tag}_opt.csv')
    if len(bv) != 400000 or not np.isfinite(bv.to_numpy(dtype=float)).all():
        raise ValueError(f'{tag}: invalid breeding-value records')
    if not np.array_equal(bv.generation, np.repeat(np.arange(1, 201), 2000)):
        raise ValueError(f'{tag}: expected 2,000 individuals per generation')
    if not np.array_equal(bv.individual, np.tile(np.arange(2000), 200)):
        raise ValueError(f'{tag}: individual identifiers are incomplete or duplicated')
    if len(opt) != 200 or not np.array_equal(opt.generation, np.arange(1, 201)):
        raise ValueError(f'{tag}: incomplete optimum history')
    expected = np.zeros((200, 4))
    expected[:, 0] = 0.3 * np.minimum(np.arange(200), 40)
    if not np.allclose(opt.iloc[:, 1:], expected, atol=1e-12, rtol=0):
        raise ValueError(f'{tag}: invalid raw optimum history')
    return len(bv)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fresh', type=Path, default=ROOT / 'outputs/simulation')
    parser.add_argument('--archive', type=Path, default=ROOT / 'slim/diagnostics')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check-raw', action='store_true')
    parser.add_argument('--atol', type=float, default=1e-12)
    args = parser.parse_args()
    if args.atol <= 0:
        parser.error('--atol must be positive')
    output = args.output or args.fresh / 'verification'
    output.mkdir(parents=True, exist_ok=True)
    names = [f'rep_{i:02d}_4trait_moving_diag.csv' for i in range(1, 21)]
    for directory in (args.archive, args.fresh):
        if sorted(p.name for p in directory.glob('rep_*_4trait_moving_diag.csv')) != names:
            raise ValueError(f'{directory}: expected precisely 20 replicate diagnostic tables')
    frames, rows, columns = [], [], []
    raw_count = 0
    for rep, name in enumerate(names, 1):
        archive_path, fresh_path = args.archive / name, args.fresh / name
        archive, fresh = pd.read_csv(archive_path), pd.read_csv(fresh_path)
        if list(archive.columns) != list(fresh.columns):
            raise ValueError(f'{name}: diagnostic columns differ')
        validate_diagnostics(archive, name)
        validate_diagnostics(fresh, name)
        difference = np.abs(fresh.to_numpy() - archive.to_numpy())
        close = difference <= args.atol
        rows.append({'replicate': rep, 'seed': 41 + rep, 'rows': len(fresh),
                     'max_abs_difference': float(difference.max()),
                     'cells_outside_tolerance': int((~close).sum()),
                     'median_abs_Ag_minus_R2': float(np.median(np.abs(fresh.Ag_minus_R2))),
                     'archive_sha256': sha256(archive_path), 'fresh_sha256': sha256(fresh_path)})
        for idx, column in enumerate(fresh.columns):
            columns.append({'column': column, 'max_abs_difference': float(difference[:, idx].max()),
                            'cells_compared': len(fresh), 'cells_outside_tolerance': int((~close[:, idx]).sum())})
        frames.append(fresh.assign(rep=rep))
        if args.check_raw:
            raw_count += validate_raw(args.fresh, name.removesuffix('_diag.csv'))
    per_rep = pd.DataFrame(rows)
    per_column = pd.DataFrame(columns).groupby('column', sort=False).agg(
        {'max_abs_difference': 'max', 'cells_compared': 'sum', 'cells_outside_tolerance': 'sum'}).reset_index()
    values = summary(pd.concat(frames, ignore_index=True))
    archived_summary = pd.read_csv(args.archive / 'reference_summary.csv').set_index('quantity').value
    comparisons = pd.DataFrame([{'quantity': key, 'archived': float(archived_summary[key]),
                                 'fresh': value, 'absolute_difference': abs(value - archived_summary[key])}
                                for key, value in values.items()])
    comparisons['within_tolerance'] = comparisons.absolute_difference <= args.atol
    result = {
        'status': 'pass' if per_rep.cells_outside_tolerance.sum() == 0 and comparisons.within_tolerance.all() else 'fail',
        'replicates': 20, 'seeds': list(range(42, 62)), 'generations_per_replicate': 200,
        'diagnostic_rows_compared': 4000, 'diagnostic_columns_compared': len(frames[0].columns) - 1,
        'diagnostic_cells_compared': int(per_column.cells_compared.sum()),
        'absolute_tolerance': args.atol, 'relative_tolerance': 0,
        'max_abs_diagnostic_difference': float(per_rep.max_abs_difference.max()),
        'diagnostic_cells_outside_tolerance': int(per_rep.cells_outside_tolerance.sum()),
        'byte_identical_diagnostic_files': int((per_rep.archive_sha256 == per_rep.fresh_sha256).sum()),
        'summary_quantities_compared': len(comparisons),
        'max_abs_summary_difference': float(comparisons.absolute_difference.max()),
        'raw_records_validated': raw_count if args.check_raw else None,
        'fresh_summary': values,
        'reported_median_abs_Ag_minus_R2': 0.0157,
        'fresh_median_rounded_to_four_decimal_places': round(values['median_abs_Ag_minus_R2_all'], 4),
        'summary_definition': 'Historical summary keys ending in _peak refer to generation 40, not an estimated maximum.',
        'scope': 'Same-seed numerical reproduction; not an additional independent set of replicates or a test of evolutionary response accuracy.',
    }
    per_rep.to_csv(output / 'comparison_by_replicate.csv', index=False)
    per_column.to_csv(output / 'comparison_by_column.csv', index=False)
    comparisons.to_csv(output / 'comparison_summary.csv', index=False)
    (output / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"Fresh/archive comparison: {result['status']}; {result['diagnostic_cells_compared']:,} cells; "
          f"largest absolute difference {result['max_abs_diagnostic_difference']:.3g}; "
          f"median |A_g - R²| {values['median_abs_Ag_minus_R2_all']:.10f}.")
    if result['status'] != 'pass':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
