"""Reproducible Person 1 analyses. All results provisional pending survey harmonisation."""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
from scipy.special import log_ndtr
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller, kpss, grangercausalitytests
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch, breaks_cusumolsresid
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.statespace.mlemodel import MLEModel
from statsmodels.tsa.statespace.sarimax import SARIMAX
ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT/'reports/tables'; FIG = ROOT/'reports/figures'
for p in (TABLE, FIG): p.mkdir(parents=True, exist_ok=True)
SEED = 20261119


def save(rows, name):
    d = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    d.to_csv(TABLE/f'{name}.csv', index=False)
    return d


def load_data(path=None):
    d = pd.read_csv(path or ROOT/'data/processed/yellowstone_master_ts_flagged.csv', index_col='Year')
    if not d.index.is_unique or not np.all(np.diff(d.index.to_numpy()) == 1):
        raise ValueError('Master must have unique, consecutive annual rows; retain missing values on the annual grid.')
    d = d.join(pd.read_csv(ROOT/'data/raw/elk_harvest_northern.csv', index_col='Year'))
    return d.join(pd.read_csv(ROOT/'data/processed/winter_severity_index.csv', index_col='Year'))


def stationarity(x):
    # ADF/KPSS require equally spaced observations: never join across missing years.
    x = x.dropna()
    if len(x):
        groups = pd.Series(np.r_[0, np.cumsum(np.diff(x.index.to_numpy()) != 1)], index=x.index)
        longest = groups.value_counts(sort=False).idxmax()
        x = x.loc[groups.eq(longest)]
    if len(x)<10 or x.std()==0:
        return dict(n=len(x), verdict='insufficient', ADF_p0=np.nan, ADF_p1=np.nan, ADF_p2=np.nan, KPSS_p=np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        ps = [adfuller(x, maxlag=l, autolag=None)[1] for l in (0,1,2)]
        kp = kpss(x, regression='c', nlags='auto')[1]
    return dict(n=len(x), ADF_p0=ps[0], ADF_p1=ps[1], ADF_p2=ps[2], KPSS_p=kp,
                verdict='stationary' if sum(p<.05 for p in ps)>=2 and kp>=.05 else 'not_clearly_stationary')


def features(d, cutoff=None):
    """Learn differencing decisions and scaling on training years only if cutoff supplied."""
    y = np.log(d.Elk_Count).diff().rename('dlog_elk')
    x = pd.DataFrame({'d_wolves':d.Wolf_Northern.diff().shift(1)/10,
        'd_logbison':np.log(d.Bison_Count).diff().shift(1),
        'ndvi':d.NDVI.shift(1), 'precip':d.Precip_Annual.shift(1),
        'pdsi':d.PDSI_Annual.shift(1), 'harvest_rate':d.Harvest_Total/d.Elk_Count.shift(1),
        'severity':d.Severity_index}, index=d.index)
    audit=[]
    for c in x:
        train=x[c] if cutoff is None else x.loc[x.index<cutoff,c]
        st=stationarity(train); diff=c not in ('d_wolves','d_logbison') and st['verdict']!='stationary'
        audit.append(dict(variable=c, stage='before', difference_applied=diff, **st))
        if diff: x[c]=x[c].diff()
        train=x[c] if cutoff is None else x.loc[x.index<cutoff,c]
        audit.append(dict(variable=c, stage='after', difference_applied=diff, **stationarity(train)))
        if c not in ('d_wolves','d_logbison'):
            sd=train.std()
            x[c]=(x[c]-train.mean())/(sd if sd>0 else 1)
    return y,x,pd.DataFrame(audit)


def fit_arimax(y, X=None, order=(0,0,0)):
    d=pd.concat([y,X],axis=1).dropna() if X is not None and len(X.columns) else y.dropna().to_frame()
    if order != (0,0,0) and not np.all(np.diff(d.index)==1):
        raise ValueError('ARMA errors require a contiguous annual index; do not compress missing years.')
    ex=d.drop(columns=y.name)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        r=ARIMA(d[y.name],exog=ex if len(ex.columns) else None,order=order,trend='c').fit()
    return r,d


def coef_rows(r,d,model):
    ci=r.conf_int()
    return [dict(model=model,term=k,estimate=float(r.params[k]),se=float(r.bse[k]),
        ci_low=float(ci.loc[k,0]),ci_high=float(ci.loc[k,1]),p=float(r.pvalues[k]),
        n=int(r.nobs),years=f'{d.index.min()}–{d.index.max()}',aic=r.aic,bic=r.bic,
        converged=r.mle_retvals.get('converged',True) if hasattr(r,'mle_retvals') else True)
        for k in r.params.index]


def diagnose(r,name,number=None):
    e=np.asarray(r.resid); e=e[np.isfinite(e)]
    lb=acorr_ljungbox(e,lags=[5,8],return_df=True)
    if number:
        fig,axs=plt.subplots(1,3,figsize=(12,3))
        axs[0].plot(e);axs[0].set_title(name)
        plot_acf(e,lags=min(10,len(e)//2-1),ax=axs[1]);sm.qqplot(e,line='s',ax=axs[2])
        fig.tight_layout();fig.savefig(FIG/f'{number}_{name}.png',dpi=140);plt.close(fig)
    return dict(model=name,LB5_p=lb.lb_pvalue.loc[5],LB8_p=lb.lb_pvalue.loc[8],ARCH_p=het_arch(e,nlags=2)[1],n=len(e))


def real_mask(d, strict=False):
    ok=d.Elk_Count_imputed.eq(0)
    if strict: ok &= d.get('Elk_Count_coverage_unresolved',pd.Series(0,index=d.index)).eq(0)
    return ok & ok.shift(1,fill_value=False)


def rolling(d):
    """Conditional retrospective predictions, no future interpolation in training data."""
    rows=[]; audits=[]
    for t in range(2011,2026):
        if d.loc[t,'Elk_Count_imputed'] or not real_mask(d,True).loc[t]: continue
        # Remove fills BEFORE using training data. Past-only carries for exogenous gaps;
        # never backfill or interpolate with a later observation.
        past=d.loc[:t].copy()
        for c in ['Elk_Count','Wolf_Northern','Bison_Count','NDVI','Precip_Annual','PDSI_Annual']:
            past.loc[past[c+'_imputed'].eq(1),c]=np.nan
            if c!='Elk_Count': past[c]=past[c].ffill()
        past.loc[past.Harvest_imputed.eq(1),'Harvest_Total']=np.nan
        past.Harvest_Total=past.Harvest_Total.ffill()
        # Relearn the station-normalisation baseline within each fold.
        station_scores=[]
        for station in ['northeast_entrance','canyon','parker_peak']:
            cc=[f'{v}__{station}' for v in ['Peak_SWE_in','Accum_SWE_in_d','Snow_days']]
            if all(c in past for c in cc):
                vals=past[cc]; ref=vals.loc[vals.index<t]
                station_scores.append(((vals-ref.mean())/ref.std()).mean(axis=1,skipna=False))
        if station_scores: past['Severity_index']=pd.concat(station_scores,axis=1).mean(axis=1)
        y,x,a=features(past,cutoff=t);audits.extend(a.assign(origin=t).to_dict('records'))
        train=(past.index<t)&real_mask(past,True)
        for name,cols in [('naive',None),('drift',[]),('wolves_only',['d_wolves']),('full_conditional',list(x))]:
            if cols and x.loc[t,cols].isna().any(): continue
            if cols is None: yh=0.;n=0
            else:
                r,z=fit_arimax(y.loc[train],x.loc[train,cols] if cols else None)
                yh=float(r.params['const']+sum(x.loc[t,c]*r.params[c] for c in cols));n=len(z)
            rows.append(dict(year=t,model=name,actual=d.loc[t,'Elk_Count'],
                predicted=d.loc[t-1,'Elk_Count']*np.exp(yh),train_n=n,
                evaluation='conditional retrospective; release dates unavailable'))
    f=pd.DataFrame(rows)
    # Score all models on identical eligible years.
    common=f.groupby('year').model.nunique();f=f[f.year.isin(common[common==4].index)]
    scores=[]
    for name,g in f.groupby('model'):
        err=g.predicted-g.actual
        scores.append(dict(model=name,MAE=err.abs().mean(),RMSE=np.sqrt((err**2).mean()),
            MAPE=100*(err.abs()/g.actual).mean(),n=len(g),years=','.join(g.year.astype(str))))
    save(f,'q3_predictions');s=save(scores,'q3_scores');save(audits,'q3_training_transform_audit')
    p=f.pivot(index='year',columns='model',values='predicted');p['actual']=f.groupby('year').actual.first()
    ax=p.plot(marker='o',figsize=(10,4),title='Conditional retrospective predictions; matched real-count years')
    ax.set_ylabel('Elk');plt.tight_layout();plt.savefig(FIG/'13_predictions.png',dpi=140);plt.close()
    return s


def drivers():
    d=load_data();y,x,a=features(d);save(a,'q1_stationarity')
    rows=[];diagnostics=[];fits={}
    for name,cols in [('drift',[])]+[(c,[c]) for c in x]+[('full',list(x))]:
        r,z=fit_arimax(y,x[cols]);fits[name]=r;rows+=coef_rows(r,z,name)
        diagnostics.append(diagnose(r,name,'11' if name in ('full','d_wolves') else None))
    out=pd.DataFrame(rows);out['p_bonferroni_screen']=np.where(out.model.eq(out.term),np.minimum(1,out.p*x.shape[1]),np.nan)
    save(out,'q1_coefficients');save(diagnostics,'q1_diagnostics')
    # Compare IC only on the common full-model sample.
    idx=pd.concat([y,x],axis=1).dropna().index;ic=[]
    for name,cols in [('drift',[])]+[(c,[c]) for c in x]+[('full',list(x))]:
        r,z=fit_arimax(y.loc[idx],x.loc[idx,cols]);ic.append(dict(model=name,aic=r.aic,bic=r.bic,n=len(z)))
    save(ic,'q1_common_sample_ic')
    rob=[]
    for label,yy,xx,order in [
        ('real_counts',y.where(real_mask(d)),x,(0,0,0)),
        ('verified_coverage',y.where(real_mask(d,True)),x,(0,0,0)),
        ('through_2015',y.loc[:2015],x.loc[:2015],(0,0,0)),
        ('wolves_levels',y,x.drop(columns='d_wolves').assign(wolves_level=d.Wolf_Northern.shift(1)/10),(0,0,0)),
        ('MA2',y,x,(0,0,2))]:
        r,z=fit_arimax(yy,xx,order);rob+=coef_rows(r,z,label)
    save(rob,'q1_robustness')
    sensitivity=[]
    for label,year,value in [('2016_late_classification',2016,7510),('2023_late_classification',2023,6651),('2023_bison_narrative_average',2023,3819)]:
        alternate=d.copy();col='Bison_Count' if 'bison' in label else 'Elk_Count'
        alternate.loc[year,col]=value
        ay,ax,_=features(alternate);ar,az=fit_arimax(ay,ax)
        sensitivity += coef_rows(ar,az,label)
    save(sensitivity,'q1_survey_alternatives')
    v=pd.DataFrame({'dlog_elk':y,'d_wolves':d.Wolf_Northern.diff()/10}).loc[1997:].dropna()
    if not np.all(np.diff(v.index.to_numpy()) == 1):
        raise ValueError('VAR sample has calendar gaps; do not compress missing annual observations.')
    sel=VAR(v).select_order(2);save([dict(criterion=k,lag=i,score=val) for k,vals in sel.ics.items() for i,val in enumerate(vals)],'q2_lag_selection')
    save([dict(variable=c, **stationarity(v[c])) for c in v], 'q2_stationarity')
    vr=VAR(v).fit(1);g=[]
    for lag in (1,2):
        vv=VAR(v).fit(lag)
        for caused,causing in [('dlog_elk','d_wolves'),('d_wolves','dlog_elk')]:
            t=vv.test_causality(caused,[causing],kind='f')
            g.append(dict(model=f'VAR({lag})',direction=f'{causing} -> {caused}',p=t.pvalue,statistic=t.test_statistic,n=vv.nobs,years='1997–2025'))
    save(g,'q2_granger');ir=vr.irf(5)
    save(pd.DataFrame({'horizon':range(6),'elk_response_log':ir.irfs[:,0,1]}),'q2_irf_10_wolves')
    fig=ir.plot(orth=False,figsize=(9,6));fig.suptitle('VAR(1), non-orthogonal innovation: wolf unit = 10 wolves')
    fig.tight_layout();fig.savefig(FIG/'12_var_irf.png',dpi=140);plt.close(fig)
    score=rolling(d)
    s=(d.Severity_index-d.Severity_index.mean())/d.Severity_index.std()
    w=d.Wolf_Northern.shift(1)/10;w=w-w.mean();xx=pd.DataFrame({'wolves_centered':w,'severity':s,'interaction':w*s})
    q4=[]
    for label,years,xxi in [('pre1996',slice(1985,1995),xx[['severity']]),('post1995',slice(1996,2025),xx[['severity']]),('interaction',slice(None),xx)]:
        r,z=fit_arimax(y.loc[years],xxi.loc[years]);q4+=coef_rows(r,z,label)
        diagnostics.append(diagnose(r,'q4_'+label,'14' if label=='interaction' else None))
    save(q4,'q4_interaction');save(diagnostics,'q1_q4_diagnostics')
    z=pd.concat([y,d.Wolf_Northern.diff().shift(1)/10,(d.Harvest_Total/d.Elk_Count.shift(1))],axis=1).dropna()
    z.columns=['y','wolves','harvest'];xx=(z[['wolves','harvest']]-z[['wolves','harvest']].mean())/z[['wolves','harvest']].std()
    r=sm.OLS(z.y,sm.add_constant(xx)).fit();rr=coef_rows(r,z,'wolves_and_harvest')
    for row in rr:
        c=row['term']
        if c in xx:
            reduced=sm.OLS(z.y,sm.add_constant(xx.drop(columns=c))).fit()
            row['incremental_R2']=r.rsquared-reduced.rsquared
            row['partial_R2']=(reduced.ssr-r.ssr)/reduced.ssr
            row['VIF']=variance_inflation_factor(sm.add_constant(xx).values,list(sm.add_constant(xx)).index(c))
            row['wolves_harvest_r']=xx.corr().iloc[0,1]
    save(rr,'q6_hunting_vs_wolves')
    # Rebuild the separate published Table 1 comparison without changing regression inputs.
    import runpy
    runpy.run_path(str(ROOT/'supplements/q6_removals/build_q6.py'))['main']()
    return out,score


def segment_search(y, max_breaks=3, min_size=5):
    """Exact L2 dynamic programming, jump=1. Includes no-break model."""
    a=np.asarray(y);n=len(a);cs=np.r_[0,np.cumsum(a)];cs2=np.r_[0,np.cumsum(a*a)]
    cost=lambda i,j:max(0.,cs2[j]-cs2[i]-(cs[j]-cs[i])**2/(j-i))
    dp=np.full((max_breaks+2,n+1),np.inf);dp[0,0]=0;paths={(0,0):[]};rows=[]
    for k in range(1,max_breaks+2):
        for j in range(k*min_size,n+1):
            candidates=[(dp[k-1,i]+cost(i,j),i) for i in range((k-1)*min_size,j-min_size+1)]
            val,i=min(candidates);dp[k,j]=val
            if np.isfinite(val):paths[k,j]=paths[k-1,i]+[j]
        rss=dp[k,n];bounds=paths[k,n][:-1]
        rows.append(dict(breaks=k-1,RSS=rss,BIC=n*np.log(max(rss/n,1e-15))+(2*k)*np.log(n),
            break_years=','.join(str(y.index[b]) for b in bounds),n=n,years=f'{y.index.min()}–{y.index.max()}'))
    return pd.DataFrame(rows)


class GrowthStateModel(MLEModel):
    """x[t+1] = x[t] + mu + beta*z[t+1] + eta; log_count[t]=x[t]+eps."""
    def __init__(self,y,z):
        self.z=np.asarray(z);self.names=list(z.columns)
        super().__init__(y,k_states=1,k_posdef=1,initialization='approximate_diffuse')
        self.ssm['design']=[[1.]];self.ssm['transition']=[[1.]];self.ssm['selection']=[[1.]]
        self.loglikelihood_burn=1
    @property
    def start_params(self):return np.r_[-.02,np.zeros(len(self.names)),.02,.01]
    @property
    def param_names(self):return ['drift']+self.names+['var_process','var_observation']
    def transform_params(self,p):
        p=np.array(p).copy();p[-2:]=p[-2:]**2;return p
    def untransform_params(self,p):
        p=np.array(p).copy();p[-2:]=np.sqrt(p[-2:]);return p
    def update(self,p,**kwargs):
        p=super().update(p,**kwargs)
        self.ssm['state_cov',0,0]=p[-2];self.ssm['obs_cov',0,0]=p[-1]
        zz=np.vstack([self.z[1:],np.zeros((1,self.z.shape[1]))])
        self.ssm['state_intercept']=(p[0]+zz@p[1:-2])[None,:]


def breaks_state():
    d=load_data();y,x,_=features(d);yy=y.dropna();br=save(segment_search(yy),'q5_mean_breaks')
    ly=np.log(d.Elk_Count);tt=ly.index.to_numpy()-ly.index.min();trend=[]
    for b in range(1990,2016):
        m=sm.OLS(ly,sm.add_constant(np.column_stack([tt,np.maximum(ly.index.to_numpy()-b,0)]))).fit()
        trend.append(dict(break_year=b,RSS=m.ssr,BIC=m.bic,n=len(ly)))
    tr=save(trend,'q5_trend_breaks');cu=breaks_cusumolsresid(yy-yy.mean(),ddof=1)
    save([dict(test='CUSUM drift residuals',statistic=cu[0],p=cu[1],n=len(yy),years='1985–2025')],'q5_cusum')
    fig,ax=plt.subplots(1,2,figsize=(10,4));ax[0].plot(br.breaks,br.BIC,'o-');ax[0].set_title('Mean breaks: BIC (lower is better)')
    ax[1].plot(tr.break_year,tr.RSS);ax[1].set_title('Continuous trend break: RSS')
    fig.tight_layout();fig.savefig(FIG/'15_breaks.png',dpi=140);plt.close(fig)
    # Keep missing observations on the full annual grid. Exogenous fills remain provisional.
    xx=x.dropna();idx=xx.index;obs=ly.loc[idx].where(d.loc[idx,'Elk_Count_imputed'].eq(0)&d.loc[idx,'Elk_Count_coverage_unresolved'].eq(0))
    if not np.all(np.diff(idx.to_numpy()) == 1):
        raise ValueError('State-model covariates have calendar gaps; preserve the annual state transitions.')
    model=GrowthStateModel(obs,xx)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore');r=model.fit(disp=False,maxiter=1500)
    tab=save(coef_rows(r,obs.to_frame(),'growth_state'),'r_state_coefficients')
    mu=r.smoothed_state[0];se=np.sqrt(np.maximum(r.smoothed_state_cov[0,0],0))
    path=save(pd.DataFrame({'Year':idx,'elk_median':np.exp(mu),'ci_low':np.exp(mu-1.96*se),'ci_high':np.exp(mu+1.96*se),'observed':np.exp(obs)}),'r_smoothed_path')
    fig,ax=plt.subplots(figsize=(10,4));ax.fill_between(idx,path.ci_low,path.ci_high,alpha=.2);ax.plot(idx,path.elk_median,label='smoothed latent median');ax.scatter(idx,path.observed,label='verified coverage observations');ax.legend()
    ax.set_title('Growth state model; conditional state uncertainty');fig.tight_layout();fig.savefig(FIG/'16_state_path.png',dpi=140);plt.close(fig)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore');dd=SARIMAX(obs,order=(1,0,0),trend='c',measurement_error=True).fit(disp=False,maxiter=1000)
    save(coef_rows(dd,obs.to_frame(),'density_dependence_measurement_error'),'r_density_dependence')
    q1=pd.read_csv(TABLE/'q1_coefficients.csv');comp=q1[q1.model.eq('full')][['term','estimate','ci_low','ci_high','p']].merge(tab[['term','estimate','ci_low','ci_high','p']],on='term',suffixes=('_Q1','_state'))
    save(comp,'r_q1_comparison')
    save([dict(sigma_process=np.sqrt(r.params['var_process']),sigma_observation=np.sqrt(r.params['var_observation']),observed_n=int(obs.notna().sum()),grid_n=len(obs),converged=r.mle_retvals['converged'])],'r_variance_components')
    return br,tr,tab


def first_passage(mu,sigma,n0,nc,T):
    if nc>=n0:return np.ones_like(np.asarray(mu),dtype=float)
    d=np.log(n0/nc);s=np.asarray(sigma)*np.sqrt(T)
    return np.clip(stats.norm.cdf((-d-np.asarray(mu)*T)/s)+np.exp(-2*np.asarray(mu)*d/np.asarray(sigma)**2+log_ndtr((-d+np.asarray(mu)*T)/s)),0,1)


def gbm_sim(mu,sigma,n0,nc,T,rng,paths=10000):
    """Annual skeleton plus Brownian-bridge crossings gives continuous first passage."""
    logn=np.full(paths,np.log(n0));bar=np.log(nc);annual=logn<=bar;continuous=annual.copy()
    for _ in range(T):
        nxt=logn+rng.normal(mu,sigma,paths)
        below=nxt<=bar
        bridge=np.exp(np.minimum(0,-2*np.maximum(logn-bar,0)*np.maximum(nxt-bar,0)/sigma**2))
        annual|=below;continuous|=below|(rng.random(paths)<bridge);logn=nxt
    return annual.mean(),continuous.mean()


def viability():
    d=load_data();rng=np.random.default_rng(SEED);all_y=np.log(d.Elk_Count).diff()
    y=all_y[real_mask(d,True)].dropna();mu=y.mean();sd=y.std(ddof=1);n=len(y);n0=d.Elk_Count.iloc[-1]
    boot=rng.normal(mu,sd,size=(2000,n));mus=boot.mean(axis=1);sds=boot.std(axis=1,ddof=1)
    previous=np.log(d.Elk_Count.shift(1)).loc[y.index];z=pd.DataFrame({'log_previous':previous})
    ou=sm.OLS(y,sm.add_constant(z)).fit();a=ou.params['const'];phi=1+ou.params['log_previous'];noise=np.sqrt(ou.ssr/len(y))
    stable=0<phi<1
    rows=[]
    for nc in [2000,4000]:
        for T in [10,25,50]:
            prob=first_passage(mu,sd,n0,nc,T);lo,hi=np.quantile(first_passage(mus,sds,n0,nc,T),[.025,.975])
            annual,bridge=gbm_sim(mu,sd,n0,nc,T,rng)
            logn=np.full(10000,np.log(n0));hit=logn<=np.log(nc)
            for _ in range(T):
                logn=a+phi*logn+rng.normal(0,noise,len(logn));hit|=logn<=np.log(nc)
            rows.append(dict(threshold=nc,horizon=T,GBM_continuous=prob,ci_low=lo,ci_high=hi,GBM_annual_sim=annual,GBM_bridge_sim=bridge,
                bridge_mc_se=np.sqrt(bridge*(1-bridge)/10000),Gompertz_annual_sim=hit.mean(),OU_stable=stable,n=n,years=','.join(map(str,y.index)),N0=n0))
    out=save(rows,'q7_threshold_probabilities')
    # Unit-root null makes chi-square LR calibration invalid: parametric bootstrap LR.
    def lr_stat(series):
        dy=np.diff(series);base=sm.OLS(dy,np.ones((len(dy),1))).fit();alt=sm.OLS(dy,sm.add_constant(series[:-1])).fit()
        return max(0,2*(alt.llf-base.llf))
    full_log=np.log(d.Elk_Count);valid=real_mask(d,True).to_numpy()[1:]
    def masked_lr(series):
        dy=np.diff(series)[valid];prev=series[:-1][valid]
        r0=sm.OLS(dy,np.ones((len(dy),1))).fit();r1=sm.OLS(dy,sm.add_constant(prev)).fit()
        return max(0,2*(r1.llf-r0.llf))
    obs_lr=masked_lr(full_log.to_numpy());sim=[]
    for _ in range(1000):
        series=np.r_[full_log.iloc[0],full_log.iloc[0]+np.cumsum(rng.normal(mu,sd,len(d)-1))];sim.append(masked_lr(series))
    save([dict(mu=mu,sigma=sd,n=n,N0=n0,phi=phi,OU_stable=stable,OU_rate=-np.log(phi) if stable else np.nan,
        log_equilibrium=a/(1-phi) if stable else np.nan,LR=obs_lr,LR_bootstrap_p=(1+sum(v>=obs_lr for v in sim))/1001,
        bootstrap_reps=1000,seed=SEED,mu_all_filled=all_y.mean(),sigma_all_filled=all_y.std())],'q7_parameters')
    save(coef_rows(ou,y.to_frame(),'Gompertz_growth'),'q7_gompertz_coefficients')
    fig,axs=plt.subplots(1,2,figsize=(10,4),sharey=True)
    for ax,nc in zip(axs,[2000,4000]):
        g=out[out.threshold.eq(nc)];ax.errorbar(g.horizon,g.GBM_continuous,yerr=[g.GBM_continuous-g.ci_low,g.ci_high-g.GBM_continuous],label='GBM continuous ± bootstrap',capsize=3)
        ax.plot(g.horizon,g.Gompertz_annual_sim,'o--',label='Gompertz annual monitoring');ax.set_title(f'Threshold {nc:,}');ax.set_ylim(0,1);ax.set_xlabel('Years')
    axs[0].set_ylabel('Probability');axs[1].legend(fontsize=8);fig.tight_layout();fig.savefig(FIG/'17_viability.png',dpi=140);plt.close(fig)
    return out


if __name__=='__main__':
    import sys
    for name in (sys.argv[1:] or ['drivers','breaks_state','viability']):
        print('Running',name,flush=True);globals()[name]()
