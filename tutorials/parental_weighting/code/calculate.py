"""Recover the original Figure 2 random stream; measure selection on one fixed parental cloud."""
from pathlib import Path
import numpy as np, json, csv
import matplotlib
from scipy.special import softmax
from scipy.stats import norm
from manuscript_figures import _draw_current_state, variance_components, first_order_share, SEED
root=Path(__file__).resolve().parents[1]; data=root/'data'; out=root/'figures'
sample_n=20000; scenario=25
def fit(x,y):
    z=np.column_stack((np.ones(len(x)),x))
    beta=np.linalg.lstsq(z,y,rcond=None)[0]; model=z@beta
    return beta,model,float(1-np.sum((y-model)**2)/np.sum((y-y.mean())**2))
def calc():
    import gzip
    rng=np.random.default_rng(SEED+2); errors=[]
    ref=json.loads((data/'manuscript_figure_results.json').read_text())['figure2']['results']
    # Repeat the ordered draws from the reference script; don't seed a new cloud.
    for n in [2,4,8]:
        for j in range(120):
            b,H,G=_draw_current_state(rng,n,j%2==0)
            X=rng.standard_normal((sample_n,n))@np.linalg.cholesky(G).T
            linear=X@b; quad=(np.einsum('ni,ij,nj->n',X,H,X)-np.trace(H@G))/2
            analytic=first_order_share(*variance_components(b,H,G))
            empirical=float(np.corrcoef(linear,linear+quad)[0,1]**2)
            errors.append(abs(empirical-analytic))
            if n==2 and j+1==scenario: picked=(X.copy(),b.copy(),H.copy(),G.copy(),analytic,empirical)
    tests={'median_absolute_error':np.median(errors),'p95_absolute_error':np.quantile(errors,.95),'maximum_absolute_error':max(errors)}
    for k,v in tests.items():
        keys=[k,k.replace('maximum','max'),k.replace('p95','percentile_95')]
        found=next((t for t in keys if t in ref),None)
        assert found is not None,(k,ref.keys())
        assert abs(v-ref[found])<1e-10,(k,v,ref[found])
    X,b,H,G,analytic,empirical=picked
    # A constant in log expected fitness cannot affect normalised parental weights.
    # The original manuscript centres its quadratic term; the identical convention is used here.
    f=X@b+.5*(np.einsum('ni,ij,nj->n',X,H,X)-np.trace(H@G))
    coef,fl,r2=fit(X,f); weights=np.array([np.full(len(X),1/len(X)),softmax(f),softmax(fl)])
    # Express both axes in the starting cloud's own SD so distances do not depend on trait units.
    m=X.mean(0);s=X.std(0);z=(X-m)/s;cent=weights@z; group=z[:,0]<-1
    dist=np.linalg.norm(cent-cent[0],axis=1)
    threshold=z[:,0]<-1
    # The Price selection differential is the same weighted mean change.
    for i in (1,2):
        assert np.allclose((z-z.mean(0)).T@(weights[i]-.0),cent[i]-cent[0],atol=1e-12)
        assert np.isclose(sum(weights[i]),1)
    shape={'scenario':scenario,'n':len(X),'b':b.tolist(),'H':H.tolist(),'G':G.tolist(),
        'sample_mean':m.tolist(),'sample_sd':s.tolist(),'r2_sample_plane':r2,'published_analytic_share':float(analytic),
        'empirical_corr2_published_method':float(empirical),'fitted_plane_coefficients':coef.tolist(),
        'group_n':int(group.sum()),'group_shares':(weights@group).tolist(),'mean_shifts_sd':cent.tolist(),
        'shift_lengths':dist.tolist(),'relative_overestimate':float(dist[2]/dist[1]-1),'original_validation':{k:float(v) for k,v in tests.items()}}
    mask=np.zeros(len(X),bool); mask[np.random.default_rng(2511).choice(len(X),size=600,replace=False)]=True
    with gzip.open(data/'parent_cloud.csv.gz','wt') as fh:
        np.savetxt(fh,np.column_stack((np.arange(1,len(X)+1),X,z,f,fl,*weights,group,mask)),
        delimiter=',',header='parent_id,a1,a2,z1,z2,log_expected_output,linear_log_prediction,equal_weight,curved_weight,plane_weight,group_below_minus_1SD,displayed',comments='',
        fmt=['%d']+['%.15g']*9+['%d']*2)
    return shape
def observed():
    tab=np.genfromtxt(data/'observed_data.csv',names=True,delimiter=','); t=np.genfromtxt(data/'simulation_truth.csv',names=True,delimiter=',')
    assert np.array_equal(t['id'], tab['id']) and len(t)==800
    x=t['true_breeding_value'];k=tab['offspring']; m=x.mean();sd=x.std();z=(x-m)/sd
    f=np.log(4)+.7*x-.35*x*x; beta,fl,r2=fit(x[:,None],f)
    w=np.array([np.ones(len(x))/len(x),softmax(f),softmax(fl),k/k.sum()])
    group=z>1; means=w@z
    return dict(n=len(x),total_offspring=int(k.sum()),n_zero=int(sum(k==0)),group_n=int(group.sum()),
       offspring_from_group=int(k[group].sum()),r2_sample=r2,group_shares=(w@group).tolist(),means_sd=means.tolist(),
       fitted_line=beta.tolist(),initial_mean=m,initial_sd=sd)
if __name__=='__main__':
    result={'cloud':calc(),'tutorial':observed()}; (data/'results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=1))
