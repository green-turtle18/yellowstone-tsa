"""Additive research and sensitivity analysis. Never writes to original project outputs."""
from pathlib import Path
import sys,json,hashlib,warnings
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import analysis as a
warnings.filterwarnings('ignore')
W='https://home.nps.gov/yell/learn/nature/upload/FINAL-FOR-APPROVAL-WOLF-REPORT-2020_508R.pdf'
T='https://qanr.usu.edu/wild/labs/macnulty-lab/files/tallian-et-al-2017-functional-ecology.pdf'
I='https://www.nps.gov/isro/learn/nature/wolf-moose-populations.htm'
C='https://www.climatologylab.org/terraclimate.html'
base=a.load_data(); candidate=base.copy(); rows=[]
for year,value in {1996:19,1997:32,1998:42,1999:35,2000:65}.items():
    assert base.loc[year,'Wolf_Northern_imputed']==1
    rows.append(dict(Year=year,existing_filled_value=base.loc[year,'Wolf_Northern'],candidate_value=value,source_url=W,source_location='Wolf population retrospective table/figure, 1995–2020',drawbacks='Retrospective series differs from existing observed counts in 2001 and 2008; release dates unavailable.',mitigation='Separate scenario only; no existing observations replaced.'))
    candidate.loc[year,'Wolf_Northern']=value
    candidate.loc[year,'Wolf_Northern_imputed']=0
    candidate.loc[year,'Wolf_Northern_source']='NPS_2020_retrospective_supplement'
pd.DataFrame(rows).to_csv(OUT/'wolf_gap_additions.csv',index=False)
# Preserve original master schema; joins are used only in memory for analysis.
cols=pd.read_csv(ROOT/'data/processed/yellowstone_master_ts_flagged.csv',nrows=0).columns.tolist()[1:]
candidate[cols].to_csv(OUT/'yellowstone_candidate_wolf_gaps.csv')
# Historical values are a source crosswalk, NOT replacements. No-survey values remain modelled.
vals=[(1995,'1994-12-21',16791),(1996,'NA',15062),(1997,'NA',13459),(1998,'1998-01-18;1998-01-27',11736),(1999,'1998-01-30;1999-02-11 [as printed]',11742),(2000,'1999-12-27',14539),(2001,'2000-12-21',13400),(2002,'2001-12-21/23',11969),(2003,'2002-12-24',9215),(2004,'2003-12-18',8335),(2005,'2005-01-05',9545),(2006,'NA',7992),(2007,'2006-12-30',6738),(2008,'2008-02-14',6279),(2009,'2009-01-30;2009-02-09',7109),(2010,'2010-02-26',6070),(2011,'2010-12-21',4635),(2012,'2012-03-07',4174),(2013,'2013-02-18',3915),(2014,'NA',4400),(2015,'2015-01-20',4844)]
h=[]
for y,date,n in vals:
    h.append(dict(publication_year=y,survey_date_as_printed=date,total_uncorrected_elk=n,existing_same_label_value=base.loc[y,'Elk_Count'],same_label_agrees=bool(n==base.loc[y,'Elk_Count']),is_modelled=int(date=='NA'),source_url=T,source_location='Appendix Table S1, PDF page 17',decision='Evidence crosswalk only; do not merge by year label',drawbacks='Winter-year labels can refer to prior December; 1999 date appears inconsistent; no-survey rows are full-series model estimates, not observed counts.'))
pd.DataFrame(h).to_csv(OUT/'historical_elk_source_crosswalk.csv',index=False)
reg=[]
def gap(name,status,source,drawbacks,mitigation,handoff):
    reg.append(dict(gap=name,status=status,source_url=source,drawbacks=drawbacks,mitigation=mitigation,handoff=handoff))
gap('Northern wolves 1996–2000','Five observed counts recovered; separate candidate dataset',W,'Retrospective definitions/revisions may differ from original series.','Test baseline against gap-only candidate on identical evaluation years.','Source owner: clarify retrospective vs contemporaneous census definitions before production adoption.')
gap('Northern wolves 2001 and 2008','Conflict: NPS 70/57 vs existing 77/56',W,'Changing observed data would violate preservation instruction; early park totals also disagree.','Keep all existing values; record conflict and isolate proposed additions.','NPS Wolf Project: confirm geographic assignment and revisions for 1996–2001 and 2008.')
gap('Historical elk provenance 1995–2015','21-row source crosswalk recovered',T,'Winter-year alignment, modelled rows and sightability adjustments cannot be mixed; 1998/1999 source counts 11736/11742 differ from existing 11748/11748.','Retain uncorrected total column and survey dates separately; no automatic replacements.','Elk data owner: reconcile survey dates and original 1984–2003 records; validate apparent 1999 date typo.')
gap('Whole-herd elk 2020','Unresolved; 5738 in 2020 compilation is a 2018 survey','https://www.montana.edu/smrc/supercharge_your_classroom/supercharge_datasets/supercharge_elk/supercharge_elk_materials/2020%20Montana%20elk%20population%20chart%20Accessible.pdf','Compilation year is not observation year.','Do not promote stale count to observation.','FWP/NPS: actual 2020 survey date, full coverage and count, or confirmation no survey occurred.')
gap('Whole-herd elk 2021','Unresolved; 4609 covers HD313 only','https://fwp.mt.gov/binaries/content/assets/fwp/conservation/elk/2021-montana-elk-count-completed.pdf','Partial geographic coverage; published park-only values cannot safely be added across mismatched methods/dates.','Keep coverage flag; no invented whole-herd sum.','FWP/NPS: synchronized park and outside-park count or full-herd total.')
gap('Elk 2024','Explicit 5597 confirmed; later percentage discrepancy unresolved','https://www.nps.gov/yell/learn/nature/upload/2024-YELL-Wolf-Cougar-and-Elk-Report.pdf','2025 percentage implies a different denominator; helicopter and fixed-wing surveys may differ.','Keep explicit count; never reverse-engineer an observation from rounded percent.','NPS: denominator behind 2025 24.5% comparison and any revised 2024 count.')
gap('Bison 2023','Existing alternative remains unresolved','https://www.nps.gov/yell/learn/nature/bison.htm','Narrative average 3819 vs selected survey 3616 reflects aggregation choice, not a missing observation.','No substitution; existing sensitivity analysis retained.','Bison data owner: survey dates and preferred annual statistic.')
gap('2025 precipitation/PDSI','No compatible endpoint established',C,'Unknown Polygon1 boundary and product version; maintainers advise against mixing TerraClimate v1.0 and v1.1.','Require original polygon, version, units and annual aggregation; do not append arbitrary park mean. Lagged 2025 prediction uses 2024 climate.','Original exporter: polygon GeoJSON, extraction script, version and aggregation; re-export consistently if needed.')
gap('2025 NDVI','No compatible endpoint established','https://www.usgs.gov/landsat-missions/landsat-normalized-difference-vegetation-index','Unknown Polygon1, mask, sensor harmonisation and compositing settings.','Do not replace summer Landsat metric with another satellite or annual vegetation index.','Original exporter: geometry, June–August masking/compositing and scaling settings.')
gap('Annual wolf-kill estimates 1996–2004','Resolved: uploaded Table 1 transcribed and compared','https://doi.org/10.2193/2005-770','No annual confidence intervals; hunting matches late hunt, not total harvest; age composition differs.','Separate total and adjusted kills; compare within paper and label broader harvest separately.','Completed in supplements/q6_removals; no source-access request remains.')
gap('Isle Royale comparison','Official CSV recovered; project window extracted',I,'N/A in 2021 and 2025; 2026 beyond study window; moose estimates differ from elk counts; wolf restoration creates structural break.','Preserve missing values and annual spacing; exclude 2026; report contiguous and pre-2018 comparisons separately.','Person 4: review harmonisation and regime interpretation before final comparative claims.')
pd.DataFrame(reg).to_csv(OUT/'gap_register.csv',index=False)
coeff=[]; scores=[]
for name,d in [('baseline',base),('wolf_gap_candidate',candidate)]:
    folder=OUT/name;folder.mkdir(exist_ok=True); a.TABLE=folder;a.FIG=folder
    scores.append(a.rolling(d).assign(scenario=name))
    y,x,_=a.features(d)
    for model,cs in [('wolf_only',['d_wolves']),('full',list(x))]:
        r,z=a.fit_arimax(y,x[cs]);coeff.extend([dict(scenario=name,**v) for v in a.coef_rows(r,z,model)])
pd.concat(scores).to_csv(OUT/'forecast_sensitivity.csv',index=False)
pd.DataFrame(coeff).to_csv(OUT/'coefficient_sensitivity.csv',index=False)
ir=pd.read_csv(OUT/'isle_royale_nps_download.csv',na_values=['N/A']).set_index('Year').rename(columns={'Number of Moose':'prey','Number of Wolves':'wolves'})
ir=ir.loc[1984:2025].reindex(range(1984,2026));ir.index.name='Year';ir.to_csv(OUT/'isle_royale_project_window.csv')
comparisons=[]
for system,d in [('Isle Royale',ir),('Yellowstone baseline',base.rename(columns={'Elk_Count':'prey','Wolf_Northern':'wolves'}))]:
    v=pd.DataFrame({'prey_growth':np.log(d.prey).diff(),'wolf_change':d.wolves.diff()/10})
    for end in [2017,2020]:
        z=v.loc[1997:end];assert z.notna().all().all() and (np.diff(z.index)==1).all()
        fit=a.VAR(z).fit(1)
        for caused,causing in [('prey_growth','wolf_change'),('wolf_change','prey_growth')]:
            test=fit.test_causality(caused,[causing],kind='f')
            comparisons.append(dict(system=system,start=1997,end=end,n=fit.nobs,direction=f'{causing} -> {caused}',F=test.test_statistic,p=test.pvalue,drawbacks='Exploratory VAR(1), identical calendar window; Yellowstone includes filled counts; not causal proof. 2017 cutoff avoids later Isle Royale restoration.'))
pd.DataFrame(comparisons).to_csv(OUT/'isle_royale_comparison_preliminary.csv',index=False)
hashes=json.loads((OUT/'original_file_hashes.json').read_text());hashes={p:h for p,h in hashes.items() if p.startswith('data/')};bad=[p for p,h in hashes.items() if not (ROOT/p).exists() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
assert not bad,bad
checks={'original_files_checked':len(hashes),'original_files_changed':bad,'five_additions_only':int((candidate.Wolf_Northern!=base.Wolf_Northern).sum())==5,'isle_royale_missing_preserved':bool(ir.loc[[2021,2025]].isna().all().all()),'isle_royale_max_year':int(ir.index.max())}
(OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
print(pd.concat(scores).to_string(index=False));print(json.dumps(checks))
