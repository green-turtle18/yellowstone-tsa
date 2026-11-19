"""Complete Q6 descriptively from Eberhardt (2007), without altering existing data."""
from pathlib import Path
import os,json,hashlib,zipfile
os.environ.setdefault('MPLCONFIGDIR','/tmp/yellowstone-mpl')
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]

def main():
    # Transcription of Table 1, printed p.598 / PDF p.5. Rounded adjusted column retained verbatim.
    rows=[(1996,517,134,1400),(1997,591,154,2465),(1998,788,205,1313),
          (1999,1182,307,1683),(2000,1084,282,974),(2001,1773,461,1259),
          (2002,1897,493,1139),(2003,2069,538,718),(2004,2611,679,702)]
    d=pd.DataFrame(rows,columns=['Year','Estimated_wolf_kills','Published_026_wolf_kills','Published_hunting_removals']).set_index('Year')
    d['Winter_season']=[f'{y-1}-{str(y)[2:]}' for y in d.index]
    d['Source_DOI']='10.2193/2005-770'
    d['Source_location']='Table 1; printed p.598; PDF p.5'
    d['Source_library_id']='libfile_13c9a35b65e88191ad6e4ffac08e27d8'
    d['Wolf_measure']='Published estimated total; not observed carcasses'
    d['Uncertainty_note']='Table 1 provides no year-specific confidence intervals'
    d.to_csv(OUT/'eberhardt_2007_table1.csv')
    raw=pd.read_csv(ROOT/'data/raw/elk_harvest_northern.csv',index_col='Year')
    c=d.join(raw[['Season','Fall_Hunt','Late_Hunt','Harvest_Total','Harvest_source','Harvest_imputed','Area']])
    c['Matches_late_hunt']=c.Published_hunting_removals.eq(c.Late_Hunt)
    c['Matches_season_label']=c.Winter_season.eq(c.Season)
    c['Difference_from_existing_total']=c.Harvest_Total-c.Published_hunting_removals
    c['Wolf_to_published_hunting_ratio']=c.Estimated_wolf_kills/c.Published_hunting_removals
    c['Wolf_to_existing_total_ratio']=c.Estimated_wolf_kills/c.Harvest_Total
    c['Drawbacks']='Winter-year alignment follows paper convention; numerical late-hunt match does not independently certify geographic coverage. Existing total includes estimated fall hunt in 1998–2004. No annual wolf-kill uncertainty supplied; headcounts do not measure demographic impact.'
    assert c.Matches_late_hunt.all() and c.Matches_season_label.all()
    assert np.allclose(c.Difference_from_existing_total,c.Fall_Hunt)
    assert np.all(np.abs(c.Published_026_wolf_kills-.26*c.Estimated_wolf_kills)<=.5)
    c.to_csv(OUT/'q6_removals_reconciliation.csv')
    c.to_csv(ROOT/'reports/tables/q6_removals_comparison.csv')
    fig,ax=plt.subplots(figsize=(10,5))
    ax.plot(d.index,d.Estimated_wolf_kills,'o-',label='Estimated total wolf kills (paper)')
    ax.plot(d.index,d.Published_hunting_removals,'s-',label='Hunting removals (paper; matches late hunt)')
    ax.plot(c.index,c.Harvest_Total,'^--',alpha=.65,label='Existing fall + late harvest (partly estimated)')
    ax.set(xlabel='Winter ending year',ylabel='Elk removed',title='Q6: published removals and existing harvest definition')
    ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.text(.02,.01,'Descriptive only. Equal numbers removed do not imply equal demographic effects. No uncertainty bands supplied.',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(OUT/'q6_removals.png',dpi=160);plt.close(fig)
    totals={k:int(d[k].sum()) for k in ['Estimated_wolf_kills','Published_hunting_removals','Published_026_wolf_kills']}
    report=f'''# Q6 completed: descriptive wolf-kill and hunting comparison

The completed comparison is integrated into notebook 03, the main reports and the drivers rebuild. The old q6_removals_pending.csv is retained only as a historical placeholder. Q6's statistical regression remains unchanged; this completes the previously blocked descriptive component.

## Source and definitions

Eberhardt, White, Garrott & Houston (2007), *A Seventy-Year History of Trends in Yellowstone's Northern Elk Herd*, Journal of Wildlife Management 71(2):594–602. DOI https://doi.org/10.2193/2005-770. Table 1 is on printed page 598 / PDF page 5. Source: the user-provided full paper, library ID `libfile_13c9a35b65e88191ad6e4ffac08e27d8`.

The methods (printed p.595) generally label winters by ending year: 1996 denotes 1995–1996. Estimated wolf kills are based on kill rates, not merely carcasses discovered. Table 1's 0.26 column is the authors' adjustment reflecting the fraction of recorded kills in prime adult age classes (3–14); it is **not** the total kill estimate, an independent annual age census, or a confidence bound. Keep the rounded published values separate.

## Reconciliation

All nine published hunting figures exactly match `Late_Hunt`, and all nine winter labels match `Season`. They do **not** match `Harvest_Total`, which includes fall hunting. The difference equals `Fall_Hunt` in each year. For 1998–2004 that fall component is an imputed 359 elk annually. Accordingly, the primary descriptive comparison uses both columns from the paper. The existing broader harvest total appears only as an explicitly labelled alternative. Numerical equality does not independently settle geographic/methodological compatibility.

## Findings

Across 1996–2004 the paper reports **{totals['Estimated_wolf_kills']:,} estimated wolf kills** and **{totals['Published_hunting_removals']:,} hunting removals**. Wolf kills exceed the paper's hunting removals in each of 2000–2004, but are lower in 1996–1999. Against the existing broader fall-plus-late total, the crossover is 2001 rather than 2000. This demonstrates why the harvest definition matters.

The adjusted 0.26 wolf-kill figures remain below the published hunting removals in every year. This reflects the paper's adjustment assumptions; it does not establish a causal ranking from our time series. Wolves and hunters remove different age classes, so total headcounts alone do not establish which has the larger effect on population growth. No year-specific wolf-kill intervals are provided in Table 1; none were invented. No values were extrapolated outside 1996–2004.

## Deliverables and reproduction

- `eberhardt_2007_table1.csv`: source transcription, separate total/adjusted columns and provenance.
- `q6_removals_reconciliation.csv`: year/season check, existing late/fall/total harvest, ratios and drawbacks.
- `q6_removals.png`: descriptive comparison.
- `q6_removals.ipynb`: viewable, reproducible notebook with embedded results.
- `validation.json`: transcription arithmetic and preservation checks.

Run from repository root: `.venv/bin/python person1/supplements/q6_removals/build_q6.py`.

No existing raw data, candidate dataset or regression results are changed. The current descriptive comparison is also exported to reports/tables/q6_removals_comparison.csv. Other ecological provenance gaps and the full team comparison remain outstanding. The Q6 source-access handoff is now resolved; broad claims about causal or age-specific effects remain unsupported by this descriptive table.
'''
    (OUT/'README.md').write_text(report)
    hashes=json.loads((ROOT/'supplements/gap_research/original_file_hashes.json').read_text())
    hashes={f:h for f,h in hashes.items() if f.startswith('data/')}
    changed=[f for f,h in hashes.items() if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h]
    assert not changed,changed
    checks={'rows':len(d),'years':list(map(int,d.index)),'late_hunt_matches':int(c.Matches_late_hunt.sum()),'season_matches':int(c.Matches_season_label.sum()),'published_adjustment_rounding_verified':True,'original_files_checked':len(hashes),'original_files_changed':changed,'totals':totals}
    (OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
    import base64
    cells=[{'cell_type':'markdown','metadata':{},'source':report.splitlines(True)},
      {'cell_type':'code','metadata':{},'execution_count':1,'source':['from pathlib import Path\n','import pandas as pd\n',"candidates = [Path.cwd(), Path.cwd()/'supplements/q6_removals', Path.cwd()/'person1/supplements/q6_removals']\n","folder = next(p for p in candidates if (p/'q6_removals_reconciliation.csv').exists())\n","pd.read_csv(folder/'q6_removals_reconciliation.csv')"], 'outputs':[{'output_type':'execute_result','execution_count':1,'metadata':{},'data':{'text/plain':[c.reset_index().to_string(index=False)],'text/html':[c.reset_index().to_html(index=False)]}}]},
      {'cell_type':'code','metadata':{},'execution_count':2,'source':['from IPython.display import Image, display\n',"display(Image(filename=str(folder/'q6_removals.png')))"],'outputs':[{'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode((OUT/'q6_removals.png').read_bytes()).decode(),'text/plain':['Q6 descriptive removals comparison']}}]}]
    (OUT/'q6_removals.ipynb').write_text(json.dumps({'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}},'nbformat':4,'nbformat_minor':4},indent=1)+'\n')
    with zipfile.ZipFile(OUT/'q6_completion_handoff.zip','w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.iterdir()):
            if f.is_file() and f.suffix!='.zip':z.write(f,f.name)
    print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
